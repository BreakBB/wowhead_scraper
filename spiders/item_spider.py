from typing import Union, Dict

import scrapy
from scrapy import signals, Spider
from scrapy.shell import inspect_response

from ids import ITEM_IDS
from utils.formatter import Formatter


class ItemSpider(scrapy.Spider):

    name = "item_scraper"
    start_urls = []
    npc_names = []
    lang = ""
    base_url = "https://{}.classic.wowhead.com/item={}/"

    xpath_name = "//h1[@class='heading-size-1']//text()"

    def __init__(self, lang="en", **kwargs) -> None:
        super().__init__(**kwargs)
        self.lang = lang
        if lang == "mx":
            self.base_url = "https://db.wowlatinoamerica.com/?item={}"
            self.start_urls = [self.base_url.format(iid) for iid in ITEM_IDS]
            self.xpath_name = "//h1/text()"
        else:
            self.start_urls = [self.base_url.format(lang, iid) for iid in ITEM_IDS]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs) -> Spider:
        spider = super(ItemSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response) -> Dict[str, Union[int, str]]:
        if "?notFound=" in response.url:
            item_id = response.url[response.url.index("?notFound="):]
            self.logger.warning("Item with ID '{}' could not be found.".format(item_id))
            return
        if self.lang == "mx":
            item_id = response.url.split("/")[-1][6:]  # It is /?item=
        else:
            item_id = response.url.split("/")[-2][5:]

        # inspect_response(response, self)
        name = self.__parse_name(response)

        if not name:
            return

        result = {
            "id": int(item_id),
            "name": name
        }
        self.logger.info(result)

        yield result

    def spider_closed(self, spider) -> None:
        self.logger.info("Spider closed. Starting formatter")

        f = Formatter()
        f(self.lang, "item")

        self.logger.info("Formatting done!")

    def __parse_name(self, response) -> str:
        name = response.xpath(self.xpath_name).get()

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
