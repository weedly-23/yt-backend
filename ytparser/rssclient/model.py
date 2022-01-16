from datetime import datetime

from pydantic import BaseModel


class Article(BaseModel):
    author: str
    published: datetime
    link: str
    title: str
    summary: str
