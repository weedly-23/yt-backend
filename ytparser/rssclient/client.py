import feedparser
import httpx

from ytparser.rssclient.model import Article


class RssClient:

    url = 'https://www.youtube.com/feeds/videos.xml'

    def get(self, channel_id: str) -> list[Article]:
        response = httpx.get(self.url, params={'channel_id': channel_id})
        response.raise_for_status()
        feed = feedparser.parse(response.text)
        return [Article(**article) for article in feed['entries']]
