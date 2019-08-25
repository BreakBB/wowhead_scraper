import scrapy
from scrapy import signals
from scrapy.shell import inspect_response

from utils import Filter
from utils.formatter import Formatter


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
        # self.start_urls = [self.base_url.format(lang, 8714)]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuestSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response):
        if "?notFound=" in response.url:
            qid = response.url[response.url.index("?notFound="):]
            self.logger.warning("Quest with ID '{}' could not be found.".format(qid))
            return
        qid = response.url.split("/")[-2][6:]

        # inspect_response(response, self)

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

    def __parse_description(self, response) -> str:
        text_parts = response.selector.xpath("//div[@class='text']/h2/following-sibling::text()").getall()
        desc = " ".join(d.strip() for d in text_parts)
        desc = desc.strip()
        if self.lang == "en":
            desc = self.__filter_en_description(desc)
        elif self.lang == "de":
            desc = self.__filter_de_description(desc)
        elif self.lang == "fr":
            desc = self.__filter_fr_description(desc)
        desc = desc.replace("  ", " ")
        if desc.startswith("["):
            desc = desc[1:-1]
        return desc.strip()

    def __parse_objective(self, response) -> str:
        obj: str = response.selector.xpath("//meta[@name='description']/@content").get()
        if self.lang == "en":
            objective = self.__filter_en_objective(obj)
        elif self.lang == "de":
            objective = self.__filter_de_objective(obj)
        elif self.lang == "fr":
            objective = self.__filter_fr_objective(obj)
        else:
            objective = obj
        return objective.strip()

    def __parse_title(self, response) -> str:
        title: str = response.selector.xpath("//title/text()").get()
        if self.lang == "en" or self.lang == "de":
            title = self.__filter_en_de_title(title)
        elif self.lang == "fr":
            title = self.__filter_fr_title(title)

        if title.startswith("["):
            title = title[1:-1]
        return title.strip()

    @staticmethod
    def __filter_en_de_title(title: str) -> str:
        if " - Quest -" not in title:
            return ""
        title = title[:title.index(" - Quest -")]
        return title

    @staticmethod
    def __filter_fr_title(title: str) -> str:
        if " - Quête -" not in title:
            return ""
        title = title[:title.index(" - Quête -")]
        return title

    @staticmethod
    def __filter_en_description(desc: str) -> str:
        if "You will learn" in desc:
            desc = desc[:desc.index("You will learn")]
        if "You will receive" in desc:
            desc = desc[:desc.index("You will receive")]
        if "The following spell will be cast on you" in desc:
            desc = desc[:desc.index("The following spell will be cast on you")]
        if "You will be able to choose one of these rewards" in desc:
            desc = desc[:desc.index("You will be able to choose one of these rewards")]
        if "Upon completion of this quest" in desc:
            desc = desc[:desc.index("Upon completion of this quest")]
        if "\n" in desc:
            desc = desc[:desc.index("\n")]
        return desc.strip()

    @staticmethod
    def __filter_de_description(desc: str) -> str:
        if "Ihr erlernt" in desc:
            desc = desc[:desc.index("Ihr erlernt")]
        if "Ihr bekommt" in desc:
            desc = desc[:desc.index("Ihr bekommt")]
        if "Der folgende Zauber wird auf euch gewirkt" in desc:
            desc = desc[:desc.index("Der folgende Zauber wird auf euch gewirkt")]
        if "Auf Euch wartet eine dieser Belohnungen" in desc:
            desc = desc[:desc.index("Auf Euch wartet eine dieser Belohnungen")]
        if "Bei Abschluss dieser Quest" in desc:
            desc = desc[:desc.index("Bei Abschluss dieser Quest")]
        if "\n" in desc:
            desc = desc[:desc.index("\n")]
        return desc.strip()

    @staticmethod
    def __filter_fr_description(desc: str) -> str:
        if "Vous apprendrez" in desc:
            desc = desc[:desc.index("Vous apprendrez")]
        if "Vous recevrez" in desc:
            desc = desc[:desc.index("Vous recevrez")]
        if "Vous allez être la cible du sort suivant" in desc:
            desc = desc[:desc.index("Vous allez être la cible du sort suivant")]
        if "Vous pourrez choisir une" in desc:
            desc = desc[:desc.index("Vous pourrez choisir une")]
        if "Lors de l'achèvement de cette" in desc:
            desc = desc[:desc.index("Lors de l'achèvement de cette")]
        if "\n" in desc:
            desc = desc[:desc.index("\n")]
        return desc.strip()

    @staticmethod
    def __filter_en_objective(obj):
        if obj.startswith("Upon completion of this quest") or obj.startswith("A level "):
            objective = ""
        elif " A level " in obj:
            objective = obj[:obj.index(" A level ")]
        else:
            objective = obj
        if objective.startswith("["):
            objective = objective[1:-1]
        return objective.strip()

    @staticmethod
    def __filter_de_objective(obj):
        if " Ein/eine" in obj:
            objective = obj[:obj.index(" Ein/eine")]
        elif obj.startswith("Ein/eine") or obj.startswith("Bei Abschluss dieser") or obj.startswith("Eine Level "):
            objective = ""
        elif " Eine Level " in obj:
            objective = obj[:obj.index(" Eine Level ")]
        else:
            objective = obj
        if objective.startswith("["):
            objective = objective[1:-1]
        return objective.strip()

    @staticmethod
    def __filter_fr_objective(obj):
        if " Une Quête" in obj:
            objective = obj[:obj.index(" Une Quête")]
        elif " Un/une quête " in obj:
            objective = obj[:obj.index(" Un/une quête ")]
        elif obj.startswith("Une Quête") or obj.startswith("Un/une quête") or obj.startswith("Lors de l'achèvement de cette"):
            objective = ""
        elif " de niveau " in obj:
            objective = obj[:obj.index(" de niveau ")]
        else:
            objective = obj
        if objective.startswith("["):
            objective = objective[1:-1]
        return objective.strip()

    def spider_closed(self, spider):
        self.logger.info("Spider closed. Starting formatter")

        f = Formatter()
        f(self.lang, "quest")

        self.logger.info("Formatting done!")
