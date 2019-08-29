import re

import scrapy
from scrapy import signals

from utils import Filter
from utils.formatter import Formatter

from lang_data import get_quest_str_by_lang, get_filter_list_by_lang, get_regex_list_by_lang


class QuestSpider(scrapy.Spider):

    name = "quest_scraper"
    start_urls = []
    quest_data = []
    lang = ""
    base_url = "https://{}.classic.wowhead.com/quest={}/"

    def __init__(self, lang="en", **kwargs):
        super().__init__(**kwargs)
        self.lang = lang

        f = Filter()
        quest_ids = f("quest")
        self.start_urls = [self.base_url.format(lang, qid) for qid in quest_ids]

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

        title = self.__parse_title(response)
        objective = self.__parse_objective(response)
        description = self.__parse_description(response)

        result = {
            "id": int(qid),
            "title": title,
            "objective": objective,
            "description": description
        }
        self.logger.info(result)

        yield result

    def __parse_title(self, response) -> str:
        title: str = response.selector.xpath("//title/text()").get()

        title = self.__filter_title(title)
        return title

    def __filter_title(self, title: str) -> str:
        quest_str = get_quest_str_by_lang(self.lang)
        quest_str = " - {} -".format(quest_str)

        if quest_str not in title:
            return ""
        title = title[:title.index(quest_str)]
        if title.startswith("[DEPRECATED]"):
            title = title[13:]
        elif title.startswith("["):
            title = title[1:-1]
        return title.strip()

    def __parse_description(self, response) -> str:
        text_parts = response.selector.xpath("//div[@class='text']/h2/following-sibling::text()").getall()
        desc = " ".join(d.strip() for d in text_parts)
        desc = desc.strip()

        desc = self.__filter_response_text(desc)
        return desc

    def __parse_objective(self, response) -> str:
        obj = response.selector.xpath("//meta[@name='description']/@content").get()

        objective = self.__filter_response_text(obj)
        return objective

    def __filter_response_text(self, text: str) -> str:
        filter_list = get_filter_list_by_lang(self.lang)
        regex_list = get_regex_list_by_lang(self.lang)

        for r in regex_list:
            text = re.sub(r, "", text)
        text = text.strip()

        for f in filter_list:
            if text.startswith(f):
                return ""
            elif f in text:
                text = text[:text.index(f)].strip()
                break
        if "\n" in text:
            text = text[:text.index("\n")]
        if "|n" in text:
            text = text[:text.index("|n")]
        if text.endswith("\\"):
            text = text[:-1]
        text = text.replace("  ", " ").strip()
        if text.startswith("["):
            text = text[1:]
        if text.endswith("]"):
            text = text[:-1]
        if not text.endswith(".") and not text.endswith("?") and not text.endswith("!"):
            text += "."
        return text.strip()

    def spider_closed(self, spider):
        self.logger.info("Spider closed. Starting formatter...")

        f = Formatter()
        f(self.lang, "quest")

        self.logger.info("Formatting done!")
