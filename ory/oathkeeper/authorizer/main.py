from pathlib import Path

from config import settings
from fastapi import FastAPI, Request
from logger import get_logger

app = FastAPI()

HERE = Path(__file__).parent
logger = get_logger(__name__)


@app.post("/authorize")
async def authorize(request: Request):
    logger.info((request.headers, request.cookies, request.query_params))
    logger.info((await request.body(),))
    return 200


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_dirs=[HERE],
    )
