from uuid import uuid4

from pydantic import BaseModel as BaseModel_
from pydantic import Field


class BaseModel(BaseModel_):
    class Config:
        orm_mode = True


class IdMixin(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))


class BasePublisher(BaseModel):
    name: str


class PublisherWriter(BasePublisher):
    pass


class PublisherReader(BasePublisher, IdMixin):
    pass


class BaseBook(BaseModel):
    title: str
    author: str
    year: int


class BookWriter(BaseBook):
    publisher_id: str


class BookReader(BaseBook, IdMixin):
    publisher: PublisherReader


class BaseMember(BaseModel):
    subject_id: str


class MemberWriter(BaseMember):
    publisher_id: str


class MemberReader(BaseMember, IdMixin):
    publisher: PublisherReader
