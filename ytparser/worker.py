import time

import structlog

from ytparser.config import AppConfig, ChannelConfig

logger = structlog.getLogger(__name__)


class Worker:

    def __init__(self, config: AppConfig) -> None:
        self.api_key = config.youtube_key
        self.period = config.period
        self.channels = config.channels
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
        # TODO: call youtube api for new movies

    def stop(self) -> None:
        self.is_working = False
