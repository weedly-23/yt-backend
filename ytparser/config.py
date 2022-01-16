import os
from datetime import datetime
from pathlib import Path

import arrow
from pydantic import BaseModel, Field, validator
from ruamel.yaml.main import YAML


class ChannelConfig(BaseModel):
    uid: int
    youtube_id: str
    title: str
    last_published: arrow.Arrow = Field(default_factory=arrow.Arrow.now)

    @validator('last_published', pre=True)
    def validate_published(cls, value):  # noqa: N805
        if isinstance(value, arrow.Arrow):
            return value

        return arrow.get(value)

    class Config:
        arbitrary_types_allowed = True


class AppConfig(BaseModel):
    youtube_key: str
    period: int = 60
    channels: list[ChannelConfig] = []


def load_channels(filename: str) -> list[ChannelConfig]:
    yaml = YAML()
    data = Path(filename).read_bytes()
    config = yaml.load(data)
    return [
        ChannelConfig(**channel)
        for channel in config['channels']
    ]


def load_from_env() -> AppConfig:
    return AppConfig(
        youtube_key=os.getenv('YT_API_KEY'),
        channels=load_channels('.data/channels.yml'),
    )
