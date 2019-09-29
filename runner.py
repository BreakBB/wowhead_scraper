from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path
from typing import Union

from scrapy.crawler import CrawlerProcess

from spiders import NPCSpider, ObjectSpider, QuestSpider
from utils.paths import OUTPUT_DIR


class Runner:
    lang: str = ""
    target: str = ""
    lang_dir: Path = None

    def __init__(self, lang: str, target: str) -> None:
        self.lang = lang
        self.target = target
        self.logger = getLogger(__name__)
        self.lang_dir = OUTPUT_DIR / lang
        if not self.lang_dir.exists():
            self.lang_dir.mkdir()
        self.lang_dir = self.lang_dir.relative_to(os.path.dirname(os.path.realpath(__file__)))

    def run(self) -> None:
        feed_uri = self.__build_feed_uri()
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
        if self.target == "npc":
            process.crawl(NPCSpider, lang=self.lang)
        elif self.target == "object":
            process.crawl(ObjectSpider, lang=self.lang)
        elif self.target == "quest":
            process.crawl(QuestSpider, lang=self.lang)

        process.start()

    def __build_feed_uri(self) -> Union[Path, None]:
        if self.target == "npc":
            feed_uri = self.lang_dir / "npc_data.json"
        elif self.target == "object":
            feed_uri = self.lang_dir / "object_data.json"
        elif self.target == "quest":
            feed_uri = self.lang_dir / "quest_data.json"
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
