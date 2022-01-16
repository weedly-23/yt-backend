import arrow
import feedparser
import httpx

from ytparser.rssclient.model import Article


class RssClient:

    url = 'https://www.youtube.com/feeds/videos.xml'

    def get(self, channel_id: str, last_published: arrow.Arrow) -> list[Article]:
        response = httpx.get(self.url, params={'channel_id': channel_id})
        response.raise_for_status()
        feed = feedparser.parse(response.text)
        articles = [Article(**article) for article in feed['entries']]
        new_articles = [article for article in articles if article.published > last_published]
        return sorted(new_articles, key=lambda article: article.published)
