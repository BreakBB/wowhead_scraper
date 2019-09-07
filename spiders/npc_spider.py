from typing import Union, Dict

import scrapy
from scrapy import signals, Spider
from scrapy.shell import inspect_response

from utils import Filter
from utils.formatter import Formatter


class NPCSpider(scrapy.Spider):

    name = "npc_scraper"
    start_urls = []
    npc_names = []
    lang = ""
    base_url = "https://{}.classic.wowhead.com/npc={}/"

    def __init__(self, lang="en", **kwargs) -> None:
        super().__init__(**kwargs)
        self.lang = lang

        f = Filter()
        npc_ids = f("npc")
        self.start_urls = [self.base_url.format(lang, nid) for nid in npc_ids]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs) -> Spider:
        spider = super(NPCSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response) -> Dict[str, Union[int, str]]:
        if "?notFound=" in response.url:
            npc_id = response.url[response.url.index("?notFound="):]
            self.logger.warning("NPC with ID '{}' could not be found.".format(npc_id))
            return
        npc_id = response.url.split("/")[-2][4:]

        # inspect_response(response, self)
        name = self.__parse_name(response)

        result = {
            "id": int(npc_id),
            "name": name
        }
        self.logger.info(result)

        yield result

    def spider_closed(self, spider) -> None:
        self.logger.info("Spider closed. Starting formatter")

        f = Formatter()
        f(self.lang, "npc")

        self.logger.info("Formatting done!")

    @staticmethod
    def __parse_name(response) -> str:
        name = response.xpath("//h1[@class='heading-size-1']//text()").get()

        if name.startswith("[Deprecated for 4.x]"):
            name = name[20:]
        elif name.startswith("[UNUSED]"):
            name = name[8:]
        elif "(Old)" in name:
            name = name[:name.index("(Old)")]
        elif "(Deprecated in 4.x)" in name:
            name = name[:name.index("(Deprecated in 4.x)")]

        return name.strip()
