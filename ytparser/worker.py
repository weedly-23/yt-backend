import time

import structlog

from ytparser.config import AppConfig, ChannelConfig
from ytparser.rssclient.client import RssClient

logger = structlog.getLogger(__name__)


class Worker:

    def __init__(self, config: AppConfig) -> None:
        self.api_key = config.youtube_key
        self.period = config.period
        self.channels = config.channels
        self.rss = RssClient()
        self.is_working = False

    def start(self) -> None:
        if self.is_working:
            return

        self.is_working = True

        while self.is_working:
            for channel in self.channels:
                self.check_channel(channel)

            logger.debug(f'sleep for {self.period} seconds')
            time.sleep(self.period)

    def check_channel(self, channel: ChannelConfig) -> None:
        logger.debug('check youtube channel', channel=channel.title)

        articles = self.rss.get(channel.youtube_id, channel.last_published)
        if not articles:
            logger.info('No articles found', channel=channel.title)
            return

        channel.last_published = articles[-1].published

        for article in articles:
            logger.info(f'Article {article}', channel=channel.title)

    def stop(self) -> None:
        self.is_working = False
