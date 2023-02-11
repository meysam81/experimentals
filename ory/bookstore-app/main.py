from pathlib import Path
from pprint import pformat

import errors
from base_utils import get_logger
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from models import BookReader, BookWriter
from settings import config

app = FastAPI()
HERE = Path(__file__).parent

logger = get_logger(__name__, level=config.LOG_LEVEL)

db = []


@app.exception_handler(errors.BookNotFound)
async def exception_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Book not found"},
    )


@app.middleware("http")
async def log_request(request: Request, call_next):
    response = await call_next(request)
    logger.info(f"{request.method} {request.url} {response.status_code}")
    headers = pformat(dict(request.headers))
    logger.debug(f"{headers}")
    logger.debug(f"{await request.body()}")
    return response


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/books")
def create_book(book: BookWriter) -> BookReader:
    new_book = BookReader(**book.dict())
    db.append(new_book)
    return new_book


@app.get("/books/{book_id}")
def read_book(book_id: str) -> BookReader | None:
    for book in db:
        if book.id == book_id:
            return book
    raise errors.BookNotFound


@app.get("/books")
def read_books() -> list[BookReader]:
    return db


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        log_level=config.LOG_LEVEL.lower(),
        reload=config.DEBUG,
        reload_dirs=[str(HERE)],
    )
