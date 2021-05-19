import os

from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path

from scrapy.crawler import CrawlerProcess

from spiders import ItemSpider, NPCSpider, ObjectSpider, QuestSpider, QuestXpSpider
from utils.paths import OUTPUT_DIR


class Runner:
    lang: str = ""
    target: str = ""
    version: str = ""
    target_dir: Path = None

    def __init__(self, lang: str, target: str, version: str) -> None:
        self.lang = lang
        self.target = target
        self.version = version
        self.logger = getLogger(__name__)
        self.target_dir = OUTPUT_DIR / target
        if not self.target_dir.exists():
            self.target_dir.mkdir()
        self.target_dir = self.target_dir.relative_to(os.path.dirname(os.path.realpath(__file__)))

    def run(self) -> None:
        feed_uri = self.target_dir / (self.lang + "_data.json")
        if feed_uri is None:
            return None
        if feed_uri.exists():
            self.logger.info("Removing existing '{}' file".format(feed_uri))
            feed_uri.unlink()

        process = CrawlerProcess(settings={
            "LOG_LEVEL": "INFO",
            "FEED_EXPORT_ENCODING": "utf-8",
            "FEED_FORMAT": "json",
            "CONCURRENT_REQUESTS": 32,
            "FEED_URI": str(feed_uri),
            "COOKIES_ENABLED": False
        })

        self.logger.info("Starting {} crawler".format(self.target))
        self.logger.info("Output goes to '{}'".format(feed_uri))
        if self.target == "item":
            process.crawl(ItemSpider, lang=self.lang, version=self.version)
        elif self.target == "npc":
            process.crawl(NPCSpider, lang=self.lang, version=self.version)
        elif self.target == "object":
            process.crawl(ObjectSpider, lang=self.lang, version=self.version)
        elif self.target == "quest":
            process.crawl(QuestSpider, lang=self.lang, version=self.version)
        elif self.target == "xp":
            process.crawl(QuestXpSpider, lang=self.lang, version=self.version)

        process.start()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-l", "--lang", help="The language you want to scrape. Default: 'en'",
                        type=str)
    parser.add_argument("-t", "--target", help="The target you want to scrape. Possible values are 'npc', 'quest', 'item', 'object' and "
                                               "'xp' . Default: 'npc'",
                        type=str)
    parser.add_argument("-v", "--version", help="The version of WoW Classic you want to scrape. Either 'tbc' or 'classic'. Default: 'tbc'",
                        type=str)
    args = parser.parse_args()

    if args.lang is None:
        args.lang = "en"
    if args.target is None:
        args.target = "npc"
    if args.version is None:
        args.version = 'tbc'

    runner = Runner(args.lang, args.target, args.version)
    runner.run()
