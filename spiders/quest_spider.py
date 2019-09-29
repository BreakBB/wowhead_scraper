import scrapy
from scrapy import signals
from scrapy.shell import inspect_response

from ids import QUEST_IDS
from utils import Merger
from utils.formatter import Formatter

from lang_data import get_filter_list_by_lang


class QuestSpider(scrapy.Spider):
    name = "quest_scraper"
    start_urls = []
    quest_data = []
    lang = ""
    base_url = "https://{}.classic.wowhead.com/quest={}/"

    def __init__(self, lang="en", **kwargs):
        super().__init__(**kwargs)
        self.lang = lang
        self.start_urls = [self.base_url.format(lang, qid) for qid in QUEST_IDS]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuestSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response):
        if "?notFound=" in response.url:
            qid = response.url[response.url.index("?notFound=") + 10:]
            self.logger.warning("Quest with ID '{}' could not be found.".format(qid))
            return
        qid = response.url.split("/")[-2][6:]
        # inspect_response(response, self)

        title = self.__parse_title(response)

        description, objective = self.__parse_objective_and_description(response)

        result = {
            "id": int(qid),
            "title": title,
            "objective": objective,
            "description": description
        }
        self.logger.info(result)

        yield result

    def __parse_title(self, response) -> str:
        title: str = response.xpath("//div[@class='text']/h1[@class='heading-size-1']/text()").get()

        title = self.__filter_title(title)
        return title

    @staticmethod
    def __filter_title(title: str) -> str:
        if title.startswith("[DEPRECATED]"):
            title = title[13:]
        elif title.startswith("["):
            return ""
        return title.strip()

    def __parse_objective_and_description(self, response):
        text_snippets = response.xpath("//div[@class='block-block-bg is-btf']//following-sibling::text()").extract()
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
        for t in text_snippets:
            t = self.__filter_text(t)
            if not t.strip():
                continue
            if t.startswith("\n") or not data_list:
                t = t.replace("\n", "")
                data_list.append(t.strip())
            else:
                t = t.replace("\n", "")
                data_list[-1] = data_list[-1] + " " + t.strip()
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
        self.logger.info("Spider closed. Starting formatter...")

        f = Formatter()
        f(self.lang, "npc")
        f(self.lang, "quest")

        self.logger.info("Formatting done!")
        m = Merger(self.lang)
        m()
        self.logger.info("Merging done. New lookup file at '{}'".format(m.lang_dir))
