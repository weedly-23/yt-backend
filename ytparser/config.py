import os

from pydantic import BaseModel


class AppConfig(BaseModel):
    youtube_key: str
    period: int = 60


def load_from_env() -> AppConfig:
    return AppConfig(
        youtube_key=os.getenv('YT_API_KEY'),
    )
