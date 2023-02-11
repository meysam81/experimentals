from uuid import uuid4

from pydantic import BaseModel, Field


class IdMixin(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))


class BaseBook(BaseModel):
    name: str
    author: str
    year: int


class BookWriter(BaseBook):
    pass


class BookReader(BaseBook, IdMixin):
    pass
