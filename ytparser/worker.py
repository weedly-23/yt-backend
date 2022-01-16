import time

import structlog

from ytparser.config import AppConfig, ChannelConfig
from ytparser.rssclient.client import RssClient
from ytparser.youtube.client import YoutubeClient

logger = structlog.getLogger(__name__)


class Worker:

    def __init__(self, config: AppConfig) -> None:
        self.period = config.period
        self.channels = config.channels
        self.rss = RssClient()
        self.youtube = YoutubeClient(config.youtube_key)
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
            logger.info(f'Article {article}', channel=channel.title, article=article.uid)
            self.check_youtube(article.video_id)

    def check_youtube(self, video_id: str) -> None:
        video = self.youtube.get_video(video_id)
        if not video:
            logger.debug('no video received', video=video_id)
            return

        category = video.snippet.category.name
        logger.debug(f'receive video info: {category}', video=video_id)

    def stop(self) -> None:
        self.is_working = False
