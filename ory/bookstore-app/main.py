import asyncio
import sqlite3
import typing
from http import HTTPStatus
from pathlib import Path
from pprint import pformat
from urllib.parse import urljoin

import aiosqlite
import errors
import httpx
from meysam_utils import get_logger
from fastapi import Depends, FastAPI, Query, Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from models import (
    BookReader,
    BookUpdate,
    BookWriter,
    MemberReader,
    MemberWriter,
    PublisherReader,
    PublisherWriter,
)
from pydantic import BaseModel
from settings import config

app = FastAPI()
HERE = Path(__file__).parent

logger = get_logger(__name__, level=config.LOG_LEVEL)


SubjectId = typing.NewType("SubjectId", str)


class SubjectSet(BaseModel):
    namespace: str
    object: str
    relation: str


class AuthorizationServer:
    read_url: str
    write_url: str

    def __init__(self, read_url: str, write_url: str):
        self.read_url = read_url
        self.write_url = write_url

    async def ping(self):
        get_url = lambda url: urljoin(url, "/health/alive")

        tasks = [self._do_ping(get_url(url)) for url in (self.read_url, self.write_url)]

        await asyncio.gather(*tasks)

    @staticmethod
    async def _do_ping(url: str):
        async with httpx.AsyncClient() as client:
            method = client.get
            method_name = method.__name__.upper()

            response = await method(url=url)

            logger.info(f"{method_name} {url} {response.status_code}")
            logger.debug(pformat(dict(response.headers)))
            if "application/json" in response.headers.get("content-type"):
                logger.debug(pformat(response.json()))

            response.raise_for_status()

    async def create_relation_tuple(
        self,
        namespace: str,
        obj: str,
        relation: str,
        subject: SubjectSet | SubjectId,
    ):
        async with httpx.AsyncClient() as client:
            json_ = {
                "namespace": namespace,
                "object": obj,
                "relation": relation,
            }
            if isinstance(subject, SubjectSet):
                json_["subject_set"] = {
                    "namespace": subject.namespace,
                    "object": subject.object,
                    "relation": subject.relation,
                }
            else:
                json_["subject_id"] = subject

            url = urljoin(self.write_url, "/admin/relation-tuples")
            method = client.put
            method_name = method.__name__.upper()

            response = await method(url=url, json=json_)

            logger.info(f"{method_name} {url} {response.status_code}")
            logger.debug(pformat(response.headers))
            logger.debug(pformat(response.json()))

            response.raise_for_status()

    async def delete_relation_tuple(
        self,
        namespace: str,
        obj: str,
        relation: str,
        subject: SubjectSet | SubjectId,
    ):
        async with httpx.AsyncClient() as client:
            params = {
                "namespace": namespace,
                "object": obj,
                "relation": relation,
            }
            if isinstance(subject, SubjectSet):
                params["subject_set"] = {
                    "namespace": subject.namespace,
                    "object": subject.object,
                    "relation": subject.relation,
                }
            else:
                params["subject_id"] = subject

            url = urljoin(self.write_url, "/admin/relation-tuples")
            method = client.delete
            method_name = method.__name__.upper()

            response = await method(url=url, params=params)

            logger.info(f"{method_name} {url} {response.status_code}")
            logger.debug(pformat(response.headers))

            response.raise_for_status()


async def deserialize_from_db(
    cursor: sqlite3.Cursor, many=False, make_queriable_dict: bool = False
) -> dict | list[dict]:
    if many and cursor.arraysize < 1:
        return []

    columns = [column[0] for column in cursor.description]
    if many:
        listify = []
        dictify = {}
        for row in await cursor.fetchall():
            current_row = dict(zip(columns, row))
            if make_queriable_dict:
                dictify[current_row["id"]] = current_row
            else:
                listify.append(current_row)

        if make_queriable_dict:
            return dictify

        return listify

    result = await cursor.fetchone()
    return dict(zip(columns, result)) if result else {}


@app.on_event("startup")
async def startup():
    db: aiosqlite.Connection = await aiosqlite.connect(config.DATABASE_URL)
    await db.execute("SELECT 1")
    app.state.db = db
    if config.ENABLE_FOREIGN_KEYS:
        await db.execute("PRAGMA foreign_keys = ON")
        db.commit()

    authz = AuthorizationServer(
        read_url=config.KETO_READ_URL, write_url=config.KETO_WRITE_URL
    )
    app.state.authz = authz
    await authz.ping()


@app.on_event("shutdown")
async def shutdown():
    db: aiosqlite.Connection = app.state.db
    await db.close()


@app.exception_handler(errors.BaseException_)
async def exception_handler(request: Request, exc: errors.BaseException_):
    return JSONResponse(status_code=exc.http_status, content={"error": exc.error})


@app.middleware("http")
async def log_request(request: Request, call_next):
    response: Response = await call_next(request)

    logger.info(f"{request.method} {request.url} {response.status_code}")
    if request.query_params:
        logger.debug(pformat(request.query_params))
    logger.debug(pformat(dict(request.headers)))

    return response


app.add_middleware(GZipMiddleware, minimum_size=1000)


def get_db():
    return app.state.db


def get_authz():
    return app.state.authz


@app.get("/")
async def index():
    return {"Hello": "World"}


@app.get("/publishers")
async def read_publishers(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0, le=100),
    db: aiosqlite.Connection = Depends(get_db),
) -> list[PublisherReader]:
    async with db.cursor() as cursor:
        raw_result = await cursor.execute(
            "SELECT * FROM publishers LIMIT $1 OFFSET $2", (limit, offset)
        )
        result = await deserialize_from_db(raw_result, many=True)

    return result


@app.get("/publishers/{publisher_id}")
async def get_a_publisher(
    publisher_id: str, db: aiosqlite.Connection = Depends(get_db)
) -> PublisherReader | None:
    async with db.cursor() as cursor:
        raw_result = await cursor.execute(
            "SELECT * FROM publishers WHERE id = $1", (publisher_id,)
        )
        result = await deserialize_from_db(raw_result)

    if result:
        return result
    raise errors.PublisherNotFound


@app.post("/publishers", status_code=HTTPStatus.CREATED)
async def create_publisher(
    publisher: PublisherWriter,
    db: aiosqlite.Connection = Depends(get_db),
) -> PublisherReader:
    new_publisher = PublisherReader(**publisher.dict())
    result = await db.execute(
        "INSERT INTO publishers (id, name) VALUES ($1, $2)",
        (
            new_publisher.id,
            new_publisher.name,
        ),
    )

    await db.commit()
    if result.rowcount != 1:
        raise errors.PublisherAlreadyExists

    return new_publisher


@app.patch("/publishers", status_code=HTTPStatus.CREATED)
async def create_publishers(
    publishers: list[PublisherWriter], db: aiosqlite.Connection = Depends(get_db)
) -> list[PublisherReader]:
    new_publishers = list(
        map(lambda publisher: PublisherReader(**publisher.dict()), publishers)
    )
    async with db.cursor() as cursor:
        result = await cursor.executemany(
            "INSERT INTO publishers (id, name) VALUES ($1, $2)",
            (
                (
                    publisher.id,
                    publisher.name,
                )
                for publisher in new_publishers
            ),
        )

        await db.commit()
    if result.rowcount != len(publishers):
        raise errors.PublisherAlreadyExists

    return new_publishers


@app.delete("/publishers/{publisher_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_a_publisher(
    publisher_id: str, db: aiosqlite.Connection = Depends(get_db)
):
    async with db.cursor() as cursor:
        try:
            result = await cursor.execute(
                "DELETE FROM publishers WHERE id = $1", (publisher_id,)
            )
        except sqlite3.IntegrityError as e:
            logger.error(e.sqlite_errorname)
            raise errors.PublisherHasBooks

        await db.commit()

    logger.debug(f"Row count: {result.rowcount}")
    logger.debug(f"Last row id: {result.lastrowid}")
    logger.debug(f"Array size {result.arraysize}")


@app.delete("/publishers", status_code=HTTPStatus.NO_CONTENT)
async def delete_publishers(db: aiosqlite.Connection = Depends(get_db)):
    async with db.cursor() as cursor:
        try:
            result = await cursor.execute("DELETE FROM publishers")
        except sqlite3.IntegrityError as e:
            logger.error(e.sqlite_errorname)
            raise errors.PublisherHasBooks

        await db.commit()

    logger.debug(f"Row count: {result.rowcount}")
    logger.debug(f"Last row id: {result.lastrowid}")
    logger.debug(f"Array size {result.arraysize}")


@app.post("/books", status_code=HTTPStatus.CREATED)
async def create_book(
    book: BookWriter, db: aiosqlite.Connection = Depends(get_db)
) -> BookReader:
    async with db.cursor() as cursor:
        raw_result = await cursor.execute(
            "SELECT * FROM publishers WHERE id = $1", (book.publisher_id,)
        )
        publisher = await deserialize_from_db(raw_result)

        if not publisher:
            raise errors.PublisherNotFound

        new_book = BookReader(publisher=publisher, **book.dict())
        result = await db.execute(
            "INSERT INTO books (id, title, author, year, publisher_id) VALUES ($1, $2, $3, $4, $5)",
            new_book.id,
            new_book.title,
            new_book.author,
            new_book.year,
            book.publisher_id,
        )

        await db.commit()

    if result.rowcount != 1:
        raise errors.BookAlreadyExists

    return new_book


@app.patch("/books/{book_id}")
async def update_book(
    book_id: str,
    book: BookUpdate,
    db: aiosqlite.Connection = Depends(get_db),
) -> BookReader:
    async with db.cursor() as cursor:
        updates = []
        counter = 1
        dictionary = book.dict(exclude_unset=True)

        raw_result = await cursor.execute(
            "SELECT * FROM publishers WHERE id IN (SELECT publisher_id FROM books WHERE id = $1)",
            (book_id,),
        )

        publisher = await deserialize_from_db(raw_result)

        if not dictionary:
            raw_result = await cursor.execute(
                "SELECT * FROM books WHERE id = $1", (book_id,)
            )
            book = await deserialize_from_db(raw_result)
            book["publisher"] = publisher
            return book

        for key in dictionary.keys():
            updates.append(f"{key} = ${counter}")
            counter += 1

        update_sql = (
            "UPDATE books SET {updates} WHERE id = ${counter} RETURNING *".format(
                updates=", ".join(updates), counter=counter
            )
        )
        raw_result = await cursor.execute(update_sql, (*dictionary.values(), book_id))

        book = await deserialize_from_db(raw_result)

        await db.commit()

    if raw_result.rowcount != 1:
        raise errors.BookNotFound

    book["publisher"] = publisher

    return book


@app.patch("/books", status_code=HTTPStatus.CREATED)
async def create_books(
    books: list[BookWriter], db: aiosqlite.Connection = Depends(get_db)
) -> list[BookReader]:
    async with db.cursor() as cursor:
        publisher_ids = set(book.publisher_id for book in books)
        sql = "SELECT * FROM publishers WHERE id in ({seq})".format(
            seq=",".join(["?"] * len(publisher_ids))
        )

        raw_result = await cursor.execute(sql, tuple(publisher_ids))

        publishers = await deserialize_from_db(
            raw_result, many=True, make_queriable_dict=True
        )

        if len(publishers) != len(publisher_ids):
            raise errors.PublisherNotFound

        logger.debug(pformat(publishers))

        new_books = list(
            map(
                lambda book: BookReader(
                    publisher=publishers[book.publisher_id], **book.dict()
                ),
                books,
            )
        )
        result = await cursor.executemany(
            "INSERT INTO books (id, title, author, year, publisher_id) VALUES ($1, $2, $3, $4, $5)",
            (
                (
                    book.id,
                    book.title,
                    book.author,
                    book.year,
                    book.publisher.id,
                )
                for book in new_books
            ),
        )

        await db.commit()

    if result.rowcount != len(books):
        raise errors.BookAlreadyExists

    return new_books


@app.get("/books/{book_id}")
async def get_a_book(
    book_id: str, db: aiosqlite.Connection = Depends(get_db)
) -> BookReader | None:
    async with db.cursor() as cursor:
        raw_result = await cursor.execute(
            "SELECT * FROM publishers WHERE id IN (SELECT publisher_id FROM books WHERE id = $1)",
            (book_id,),
        )
        publisher = await deserialize_from_db(raw_result)

        if not publisher:
            raise errors.PublisherNotFound

        raw_result = await cursor.execute(
            "SELECT * FROM books WHERE id = $1", (book_id,)
        )
        book = await deserialize_from_db(raw_result)

        if not book:
            raise errors.BookNotFound

    book["publisher"] = publisher
    logger.debug(book)
    return book


@app.get("/books")
async def read_books(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, gt=0, le=100),
    db: aiosqlite.Connection = Depends(get_db),
) -> list[BookReader]:
    async with db.cursor() as cursor:
        raw_result = await cursor.execute(
            "SELECT * FROM books LIMIT $1 OFFSET $2", (limit, offset)
        )
        books = await deserialize_from_db(raw_result, many=True)

        publisher_ids = set(book["publisher_id"] for book in books)

        sql = "SELECT * FROM publishers WHERE id in ({seq})".format(
            seq=",".join(["?"] * len(publisher_ids))
        )

        raw_result = await cursor.execute(sql, tuple(publisher_ids))

        publishers = await deserialize_from_db(
            raw_result, many=True, make_queriable_dict=True
        )

    for book in books:
        book["publisher"] = publishers[book["publisher_id"]]

    return books


@app.delete("/books", status_code=HTTPStatus.NO_CONTENT)
async def delete_books(db: aiosqlite.Connection = Depends(get_db)):
    async with db.cursor() as cursor:
        result = await cursor.execute("DELETE FROM books")

        await db.commit()

    logger.debug(f"Row count: {result.rowcount}")
    logger.debug(f"Last row id: {result.lastrowid}")
    logger.debug(f"Array size {result.arraysize}")


@app.delete("/books/{book_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_a_book(book_id: str, db: aiosqlite.Connection = Depends(get_db)):
    async with db.cursor() as cursor:
        result = await cursor.execute("DELETE FROM books WHERE id = $1", (book_id,))

        await db.commit()

    logger.debug(f"Row count: {result.rowcount}")
    logger.debug(f"Last row id: {result.lastrowid}")
    logger.debug(f"Array size {result.arraysize}")


@app.get("/members")
async def read_members(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, gt=0, le=100),
    db: aiosqlite.Connection = Depends(get_db),
) -> list[MemberReader]:
    async with db.cursor() as cursor:
        raw_result = await cursor.execute(
            "SELECT m.*, p.id AS publisher_id, p.name AS publisher_name FROM publishers p JOIN members m ON p.id = m.publisher_id LIMIT $1 OFFSET $2",
            (limit, offset),
        )
        members = await deserialize_from_db(raw_result, many=True)

    for member in members:
        member["publisher"] = PublisherReader(
            id=member["publisher_id"], name=member["publisher_name"]
        )

    return members


@app.post("/members", status_code=HTTPStatus.CREATED)
async def create_member(
    member: MemberWriter,
    db: aiosqlite.Connection = Depends(get_db),
    authz: AuthorizationServer = Depends(get_authz),
) -> MemberReader:
    async with db.cursor() as cursor:
        raw_result = await cursor.execute(
            "SELECT * FROM publishers WHERE id = $1",
            (member.publisher_id,),
        )
        publisher = await deserialize_from_db(raw_result)

        if not publisher:
            raise errors.PublisherNotFound

        new_member = MemberReader(publisher=publisher, **member.dict())

        result = await cursor.execute(
            "INSERT INTO members (id, subject_id, publisher_id) VALUES ($1, $2, $3)",
            (new_member.id, new_member.subject_id, new_member.publisher.id),
        )

        await db.commit()

    await authz.create_relation_tuple(
        namespace=config.MEMBERSHIP_NAMESPACE,
        subject=new_member.subject_id,
        obj=new_member.publisher.id,
        relation=config.MEMBERSHIP_RELATION,
    )

    if result.rowcount != 1:
        raise errors.MemberAlreadyExists

    return new_member


@app.delete("/members", status_code=HTTPStatus.NO_CONTENT)
async def delete_members(
    db: aiosqlite.Connection = Depends(get_db),
    authz: AuthorizationServer = Depends(get_authz),
):
    async with db.cursor() as cursor:
        raw_result = await cursor.execute("DELETE FROM members RETURNING *")

        members = await deserialize_from_db(raw_result, many=True)

        await db.commit()

    for member in members:
        await authz.delete_relation_tuple(
            namespace=config.MEMBERSHIP_NAMESPACE,
            subject=member["subject_id"],
            obj=member["publisher_id"],
            relation=config.MEMBERSHIP_RELATION,
        )

    logger.debug(f"Row count: {raw_result.rowcount}")
    logger.debug(f"Last row id: {raw_result.lastrowid}")
    logger.debug(f"Array size {raw_result.arraysize}")


@app.delete("/members/{member_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_a_member(
    member_id: str,
    db: aiosqlite.Connection = Depends(get_db),
    authz: AuthorizationServer = Depends(get_authz),
):
    async with db.cursor() as cursor:
        raw_result = await cursor.execute(
            "DELETE FROM members WHERE id = $1 RETURNING *",
            (member_id,),
        )

        member = await deserialize_from_db(raw_result)

        await db.commit()

    if not member:
        raise errors.MemberNotFound

    await authz.delete_relation_tuple(
        namespace=config.MEMBERSHIP_NAMESPACE,
        subject=member["subject_id"],
        obj=member["publisher_id"],
        relation=config.MEMBERSHIP_RELATION,
    )

    logger.debug(f"Row count: {raw_result.rowcount}")
    logger.debug(f"Last row id: {raw_result.lastrowid}")
    logger.debug(f"Array size {raw_result.arraysize}")


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Listening on {config.HOST}:{config.PORT}...")

    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        workers=config.WORKERS,
        log_level=config.LOG_LEVEL.lower(),
        reload=config.DEBUG,
        reload_dirs=[str(HERE)],
    )
