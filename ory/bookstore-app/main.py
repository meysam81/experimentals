import sqlite3
from pathlib import Path
from pprint import pformat

import aiosqlite
import errors
from base_utils import get_logger
from fastapi import Depends, FastAPI, Query, Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from models import BookReader, BookWriter, PublisherReader, PublisherWriter
from settings import config

app = FastAPI()
HERE = Path(__file__).parent

logger = get_logger(__name__, level=config.LOG_LEVEL)


def get_publisher(publisher_id, publishers):
    for publisher in publishers:
        if publisher["id"] == publisher_id:
            logger.debug(publisher)
            return publisher
    raise errors.PublisherNotFound


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


@app.get("/")
async def read_root():
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


@app.post("/publishers")
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


@app.patch("/publishers")
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


@app.post("/books")
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


@app.patch("/books")
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
        logger.debug(raw_result)
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


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Listening on {config.HOST}:{config.PORT}...")

    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        log_level=config.LOG_LEVEL.lower(),
        reload=config.DEBUG,
        reload_dirs=[str(HERE)],
    )
