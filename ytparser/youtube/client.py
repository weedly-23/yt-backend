from typing import Optional

import httpx

from ytparser.youtube.model import Video


class YoutubeClient:
    url = 'https://youtube.googleapis.com/youtube/v3/videos'

    def __init__(self, apikey: str) -> None:
        self.apikey = apikey

    def get_video(self, uid: str) -> Optional[Video]:
        response = httpx.get(self.url, params=(
            ('id', uid),
            ('key', self.apikey),
            ('part', 'contentDetails'),
            ('part', 'snippet'),
        ))
        response.raise_for_status()
        data = response.json()
        items = data['items']
        if not items:
            return None

        return Video(**items[0])
