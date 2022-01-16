from datetime import timedelta
from enum import Enum, IntEnum
from typing import Optional

import arrow
from pydantic import BaseModel, Field, validator


class Dimension(Enum):
    TWOD = '2d'
    THREED = '3d'


class Definition(Enum):
    SD = 'sd'
    HD = 'hd'


class Projection(Enum):
    RECTANGULAR = 'rectangular'


class ContentDetails(BaseModel):
    duration: timedelta
    dimension: Dimension
    definition: Definition
    projection: Projection
    caption: bool
    licensed: bool = Field(alias='licensedContent')


class Categories(IntEnum):
    FILM = 1
    VEHICLES = 2
    MUSIC = 10
    PETS = 15
    SPORTS = 17
    TRAVEL = 19
    GAMING = 20
    BLOGS = 22
    COMEDY = 23
    ENTERTAINMENT = 24
    POLITICS = 25
    HOWTO = 26
    EDUCATION = 27
    SCIENCE = 28
    NONPROFIT = 29


class LiveContents(Enum):
    LIVE = 'live'
    UPCOMING = 'upcoming'
    NONE = 'none'


class Snippet(BaseModel):
    published: arrow.Arrow = Field(alias='publishedAt')
    title: str
    description: str
    tags: list[str] = []
    category: Categories = Field(alias='categoryId')
    live: LiveContents = Field(alias='liveBroadcastContent')
    language: str = Field(alias='defaultAudioLanguage')

    @validator('published', pre=True)
    def validate_published(cls, value):  # noqa: N805
        if isinstance(value, arrow.Arrow):
            return value

        return arrow.get(value)

    class Config:
        arbitrary_types_allowed = True


class Video(BaseModel):
    kind: str
    uid: str = Field(alias='id')
    details: ContentDetails = Field(alias='contentDetails')
    snippet: Snippet
