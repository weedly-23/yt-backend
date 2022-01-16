from datetime import datetime

import arrow
from pydantic import BaseModel, Field, validator


class Article(BaseModel):
    uid: str = Field(alias='id')
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
