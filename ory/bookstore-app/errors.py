from abc import ABCMeta, abstractmethod
from http import HTTPStatus


class BaseException_(Exception, metaclass=ABCMeta):
    @property
    @abstractmethod
    def http_status(self) -> int:
        pass

    @property
    @abstractmethod
    def error(self) -> str:
        pass


class BookNotFound(BaseException_):
    http_status = HTTPStatus.NOT_FOUND
    error = "Book not found"


class PublisherNotFound(BaseException_):
    http_status = HTTPStatus.NOT_FOUND
    error = "Publisher not found"


class BookAlreadyExists(BaseException_):
    http_status = HTTPStatus.CONFLICT
    error = "Book already exists"


class PublisherAlreadyExists(BaseException_):
    http_status = HTTPStatus.CONFLICT
    error = "Publisher already exists"


class PublisherHasBooks(BaseException_):
    http_status = HTTPStatus.NOT_ACCEPTABLE
    error = "Publisher has books, delete them first"


class MemberAlreadyExists(BaseException_):
    http_status = HTTPStatus.CONFLICT
    error = "Member already exists"
