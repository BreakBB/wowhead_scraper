import scrapy
from scrapy import signals

from ids import QUEST_IDS
from utils.formatter import Formatter

import json


class QuestXpSpider(scrapy.Spider):
    name = "quest_xp_scraper"
    start_urls = []
    quest_data = []
    lang = ""
    base_url = "https://{}.{}.wowhead.com/quest={}/"

    def __init__(self, lang, version, **kwargs):
        super().__init__(**kwargs)
        self.lang = lang
        self.start_urls = [self.base_url.format(lang, version, qid) for qid in QUEST_IDS]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuestXpSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response):
        if "?notFound=" in response.url:
            qid = response.url[response.url.index("?notFound=") + 10:]
            self.logger.warning("Quest with ID '{}' could not be found.".format(qid))
            return
        qid = response.url.split("/")[-2][6:]

        xp = self.__parse_xp(response)

        result = {
            "id": int(qid),
            "xp": xp
        }
        self.logger.info(result)

        yield result

    @classmethod
    def __parse_xp(self, response):
        script: str = response.xpath("//script[contains(., 'g_quest')]/text()").extract_first()
        junks = script.split('\n')
        qid: int = response.url.split("/")[-2][6:]
        json_line: str = ""
        for entry in junks:
            if entry.startswith('$.extend(g_quests['):
                json_line = entry
        prefix_len: int = len("$.extend(g_quests[" + str(qid) + "], ")
        json_text = json_line[prefix_len:len(json_line) - 2]
        json_object = json.loads(json_text)
        if 'xp' in json_object:
            xp = json_object['xp']
        else:
            xp = 0

        return xp

    def spider_closed(self, spider):
        self.logger.info("Spider closed. Starting formatter...")

        f = Formatter()
        f(self.lang, "xp")

        self.logger.info("Formatting done!")