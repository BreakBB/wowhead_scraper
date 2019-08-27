from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path

from scrapy.crawler import CrawlerProcess

from spiders import NPCSpider, QuestSpider


class Runner:
    lang: str = ""
    target: str = ""
    output_dir: Path = None

    def __init__(self, lang, target):
        self.lang = lang
        self.target = target
        self.logger = getLogger(__name__)
        self.output_dir = self.__create_output_dir()

    @staticmethod
    def __create_output_dir():
        out = Path("output")
        if not out.exists():
            out.mkdir()
        return out

    def run(self):
        feed_uri = self.__build_feed_uri()
        if feed_uri is None:
            return

        process = CrawlerProcess(settings={
            "LOG_LEVEL": "INFO",
            "FEED_EXPORT_ENCODING": "utf-8",
            "FEED_FORMAT": "json",
            "CONCURRENT_REQUESTS": 32,
            "FEED_URI": str(feed_uri),
            "COOKIES_ENABLED": False
        })

        self.logger.info("Starting {} crawler".format(self.target))
        if self.target == "npc":
            process.crawl(NPCSpider, lang=self.lang)
        elif self.target == "quest":
            process.crawl(QuestSpider, lang=self.lang)

        process.start()

    def __build_feed_uri(self):
        if self.target == "npc":
            feed_uri = self.output_dir / "{}_npc_data.json".format(self.lang)
        elif self.target == "quest":
            feed_uri = self.output_dir / "{}_quest_data.json".format(self.lang)
        else:
            self.logger.error("Unknown target '{}'".format(self.target))
            return None
        return feed_uri


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-l", "--lang", help="The language you want to scrape. Default: 'en'",
                        type=str)
    parser.add_argument("-t", "--target", help="The target you want to scrape. Either 'npc' or 'quest'. Default: 'npc'",
                        type=str)
    args = parser.parse_args()

    if args.lang is None:
        args.lang = "en"
    if args.target is None:
        args.target = "npc"

    runner = Runner(args.lang, args.target)
    runner.run()
