from typing import Union, Dict, Tuple

import scrapy
from scrapy import signals, Spider
from scrapy.shell import inspect_response

from ids import NPC_IDS
from utils.formatter import Formatter


class NPCSpider(scrapy.Spider):

    name = "npc_scraper"
    start_urls = []
    npc_names = []
    lang = ""
    base_url = "https://{}.classic.wowhead.com/npc={}/"

    xpath_name = "//h1[@class='heading-size-1']//text()"

    def __init__(self, lang="en", **kwargs) -> None:
        super().__init__(**kwargs)
        self.lang = lang
        if lang == "mx":
            self.base_url = "https://db.wowlatinoamerica.com/?npc={}"
            self.start_urls = [self.base_url.format(nid) for nid in NPC_IDS]
            # self.start_urls = [self.base_url.format(qid) for qid in [7]]
            self.xpath_name = "//div[@class='text']/h1/text()"
        else:
            self.start_urls = [self.base_url.format(lang, nid) for nid in NPC_IDS]

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
        if self.lang == "mx":
            npc_id = response.url.split("/")[-1][5:]  # It is /?npc=
        else:
            npc_id = response.url.split("/")[-2][4:]

        # inspect_response(response, self)
        name, subname = self.__parse_name(response)

        if name:
            result = {
                "id": int(npc_id),
                "name": name,
                "subname": subname
            }
            self.logger.info(result)

            yield result

    def spider_closed(self, spider) -> None:
        self.logger.info("Spider closed. Starting formatter")

        f = Formatter()
        f(self.lang, "npc")

        self.logger.info("Formatting done!")

    def __parse_name(self, response) -> Tuple[str, str]:
        name = response.xpath(self.xpath_name).get()
        subname = ""

        if not name:
            return ""

        if name.startswith("[Deprecated for 4.x]"):
            name = name[20:]
        elif name.startswith("[UNUSED]"):
            name = name[8:]
        elif "(Old)" in name:
            name = name[:name.index("(Old)")]
        elif "<" in name:
            subname = name[name.index("<")+1:-1]
            name = name[:name.index("<")]
        elif "(Deprecated in 4.x)" in name:
            name = name[:name.index("(Deprecated in 4.x)")]

        return name.strip(), subname.strip()
