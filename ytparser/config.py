import os
from pathlib import Path

from pydantic import BaseModel
from ruamel.yaml.main import YAML


class ChannelConfig(BaseModel):
    uid: int
    youtube_id: str
    title: str


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
