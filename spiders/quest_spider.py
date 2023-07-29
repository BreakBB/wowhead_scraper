import scrapy
from scrapy import signals
from scrapy.shell import inspect_response

from ids import QUEST_IDS
from utils import Merger
from utils.formatter import Formatter

from lang_data import get_filter_list_by_lang

import re
import json


class QuestSpider(scrapy.Spider):
    name = "quest_scraper"
    start_urls = []
    quest_data = []
    lang = ""
    version = ""
    base_url_retail = "https://{}.wowhead.com/quest={}/"
    base_url_tbc = "https://{}.tbc.wowhead.com/quest={}/"
    base_url_classic = "https://{}.classic.wowhead.com/quest={}/"

    xpath_title = "//div[@class='text']/h1[@class='heading-size-1']/text()"
    xpath_objective_and_description = "//div[@class='block-block-bg is-btf']//following-sibling::text()"

    def __init__(self, lang, version, **kwargs):
        super().__init__(**kwargs)
        self.lang = lang
        self.version = version

        base_url = self.base_url_classic
        if version == "tbc":
            base_url = self.base_url_tbc

        if lang == "mx":
            base_url = "https://db.wowlatinoamerica.com/?quest={}"
            self.start_urls = [base_url.format(qid) for qid in QUEST_IDS]
            self.xpath_title = "//div[@class='text']/h1/text()"
            self.xpath_objective_and_description = "//div[@class='text']/h1//following-sibling::text()"
        else:
            self.start_urls = [base_url.format(lang, qid) for qid in QUEST_IDS]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuestSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response):
        if "?notFound=" in response.url:
            qid = response.url[response.url.index("?notFound=") + 10:]
            self.logger.warning("Quest with ID '{}' could not be found.".format(qid))
            self.__retry_on_retail(response, qid)
            return
        if self.lang == "mx":
            qid = response.url.split("/")[-1][7:]  # It is /?quest=
        else:
            qid = response.url.split("/")[-2][6:]
        # inspect_response(response, self)

        title = self.__parse_title(response)

        description, objective = self.__parse_objective_and_description(response)
        minLevel = self.__parse_required_level(response)
        experience = self.__parse_experience(response)

        if (description == "" or objective == ""):
            self.__retry_on_retail(response, qid)

        result = {
            "id": int(qid),
            "minLevel": minLevel,
            "experience": experience,
            "title": title,
            "objective": objective,
            "description": description
        }
        # self.logger.info(result)

        yield result

    def __retry_on_retail(self, response, qid):
        if self.version == "tbc" and response.url.startswith("https://{}.tbc".format(self.lang)):
            print("Retrying Retail url for", qid)
            yield response.follow(self.base_url_retail.format(self.lang, qid), self.parse)

    def __parse_title(self, response) -> str:
        title: str = response.xpath(self.xpath_title).get()

        title = self.__filter_title(title)
        return title

    @staticmethod
    def __filter_title(title: str) -> str:
        if title.startswith("[DEPRECATED]"):
            title = title[13:]
        elif title.startswith("["):
            return ""
        elif "<NYI>" in title:
            return ""

        if title.startswith("« "):
            title = title[1:]
        if title.endswith(" »"):
            title = title[:-2]
        return title.strip()

    def __parse_experience(self, response) -> int:
        body = str(response.body)
        #Archive
        rest = re.search("(\d+,\d+,\d+,\d+|\d+,\d+,\d+|\d+,\d+|\d+) experience", body)
        if(rest is not None):
            #print(rest.group(1))
            experience = rest.group(1)
            return str(experience).replace(",", "")
        #else:
        #    print("Something wong?")

        #WoWhead
        rest = re.search("g_quests\[\d+\], {(.*?)}", body)
        if(rest is not None):
            dataString = "{"+str(rest.group(1))+"}"
            dataString = dataString.replace("\\", "")
            questJsonData = json.loads(dataString)
            #print(rest.group(1))
            if "xp" in questJsonData:
                experience = questJsonData["xp"]
                return experience
            else:
                return None
        return None

    def __parse_required_level(self, response) -> int:
        body = str(response.body)
        rest = re.search("Requires level (\d+)", body)
        if(rest is not None):
            #print(rest.group(1))
            minLevel = rest.group(1)
            return minLevel
        
        rest = re.search("Requires level: (\d+)", body)
        if(rest is not None):
            #print(rest.group(1))
            minLevel = rest.group(1)
            return minLevel

        #"reqlevel":1
        rest = re.search('"reqlevel":(\d+)', body)
        if(rest is not None):
            #print(rest.group(1))
            minLevel = rest.group(1)
            return minLevel
        return None

    def __parse_objective_and_description(self, response):
        text_snippets = response.xpath(self.xpath_objective_and_description).extract()
        data_list = self.__filter_text_snippets(text_snippets)
        if len(data_list) < 2:
            self.logger.warning("Wrong structured HTML for {}".format(response.url))
            objective = ""
            description = ""
        else:
            objective = data_list[0]
            description = data_list[1]
        return description, objective

    def __filter_text_snippets(self, text_snippets):
        data_list = []
        last_text_segment = False  # This is True if the segment is the last of the current category
        for t in text_snippets:
            t = self.__filter_text(t)
            if not t.strip():  # Segment just contains whitespaces/linebreaks
                continue

            if last_text_segment or not data_list:  # The previous segment was the last of a category (objective/description)
                last_text_segment = t.endswith("\n")
                t = t.replace("\n", "")
                data_list.append([t.strip()])
            else:
                last_text_segment = t.endswith("\n")
                t = t.replace("\n", "")
                data_list[-1].append(t.strip())  # Append to the existing list
        return list(filter(None, data_list))

    def __filter_text(self, text: str) -> str:
        filter_list = get_filter_list_by_lang(self.lang)

        # Don't include untranslated text pieces
        if self.lang != "en" and (
                "You" in text or "you" in text or " the " in text or " I " in text or " to " in text or "[" in text or "]" in text):
            return ""

        # text = text.replace("\n", "")
        for f in filter_list:
            if text.startswith(f):
                return ""
            elif f in text:
                text = text[:text.index(f)]

        text = text.replace("  ", " ")
        if text.endswith("\\"):
            text = text[:-1]
        return text

    def spider_closed(self, spider):
        self.logger.info("Spider closed.")

        f = Formatter()
        f(self.lang, "quest")

        # m = Merger(self.lang, "Quests")
        # m()
        # self.logger.info("New lookup file at '{}'".format(m.target_dir))
