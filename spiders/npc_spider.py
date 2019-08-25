import scrapy
from scrapy import signals
from scrapy.shell import inspect_response

from utils import Filter
from utils.formatter import Formatter


class NPCSpider(scrapy.Spider):

    name = "npc_scraper"
    start_urls = []
    npc_names = []
    lang = ""
    base_url = "https://{}.classic.wowhead.com/npc={}/"

    def __init__(self, lang="en", **kwargs):
        super().__init__(**kwargs)
        self.lang = lang

        f = Filter()
        npc_ids = f("npc")
        self.start_urls = [self.base_url.format(lang, nid) for nid in npc_ids]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(NPCSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response):
        if "?notFound=" in response.url:
            npc_id = response.url[response.url.index("?notFound="):]
            self.logger.warning("NPC with ID '{}' could not be found.".format(npc_id))
            return
        npc_id = response.url.split("/")[-2][4:]

        # inspect_response(response, self)
        name = self.__parse__title(response)

        result = {
            "id": int(npc_id),
            "name": name
        }
        self.logger.info(result)

        yield result

    def spider_closed(self, spider):
        self.logger.info("Spider closed. Starting formatter")

        f = Formatter()
        f(self.lang, "npc")

        self.logger.info("Formatting done!")

    def __parse__title(self, response):
        title: str = response.selector.xpath("//title/text()").get()
        if self.lang == "en" or self.lang == "de":
            name = title[:title.index(" - NPC -")]
        elif self.lang == "fr":
            name = title[:title.index(" - PNJ -")]
        else:
            return ""

        return name
