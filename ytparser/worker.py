import time

import structlog

from ytparser.config import AppConfig

logger = structlog.getLogger(__name__)


class Worker:

    def __init__(self, config: AppConfig) -> None:
        self.api_key = config.youtube_key
        self.period = config.period
        self.is_working = False

    def start(self) -> None:
        if self.is_working:
            return

        self.is_working = True

        while self.is_working:
            self.check()

            logger.debug(f'sleep for {self.period} seconds')
            time.sleep(self.period)

    def check(self) -> None:
        logger.debug('check youtube content')
        # TODO: call youtube api for new movies

    def stop(self) -> None:
        self.is_working = False
