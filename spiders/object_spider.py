from typing import Union, Dict

import scrapy
from scrapy import signals, Spider
from scrapy.shell import inspect_response

from ids import OBJECT_IDS
from utils.formatter import Formatter


class ObjectSpider(scrapy.Spider):

    name = "object_scraper"
    start_urls = []
    npc_names = []
    lang = ""
    base_url = "https://{}.classic.wowhead.com/object={}/"

    def __init__(self, lang="en", **kwargs) -> None:
        super().__init__(**kwargs)
        self.lang = lang
        self.start_urls = [self.base_url.format(lang, nid) for nid in OBJECT_IDS]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs) -> Spider:
        spider = super(ObjectSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response) -> Dict[str, Union[int, str]]:
        if "?notFound=" in response.url:
            obj_id = response.url[response.url.index("?notFound="):]
            self.logger.warning("Object with ID '{}' could not be found.".format(obj_id))
            return
        obj_id = response.url.split("/")[-2][7:]

        # inspect_response(response, self)
        name = self.__parse_name(response)

        if not name:
            return

        result = {
            "id": int(obj_id),
            "name": name
        }
        self.logger.info(result)

        yield result

    def spider_closed(self, spider) -> None:
        self.logger.info("Spider closed. Starting formatter")

        f = Formatter()
        f(self.lang, "object")

        self.logger.info("Formatting done!")

    @staticmethod
    def __parse_name(response) -> str:
        name = response.xpath("//h1[@class='heading-size-1']//text()").get()

        if name.startswith("[Deprecated for 4.x]"):
            name = name[20:]
        elif name.startswith("[UNUSED]"):
            name = name[8:]
        elif name.startswith("["):
            return ""
        elif "(Old)" in name:
            name = name[:name.index("(Old)")]
        elif "(Deprecated in 4.x)" in name:
            name = name[:name.index("(Deprecated in 4.x)")]

        return name.strip()
