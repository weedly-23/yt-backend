import arrow
from pydantic import BaseModel, Field, validator


class Rating(BaseModel):
    count: int
    average: float
    minimal: int = Field(alias='min')
    maximum: int = Field(alias='max')


class Statistics(BaseModel):
    views_count: int = Field(alias='views')


class Article(BaseModel):
    uid: str = Field(alias='id')
    video_id: str = Field(alias='yt_videoid')
    media_starrating: Rating
    media_statistics: Statistics
    author: str
    published: arrow.Arrow
    link: str
    title: str
    summary: str

    @validator('published', pre=True)
    def validate_published(cls, value):  # noqa: N805
        if isinstance(value, arrow.Arrow):
            return value

        return arrow.get(value)

    def __str__(self) -> str:
        return f'[{self.uid}] {self.author} {self.title}'

    class Config:
        arbitrary_types_allowed = True
