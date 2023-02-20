from http import HTTPStatus
from pathlib import Path
from pprint import pformat

from config import settings
from fastapi import FastAPI, Request, Response
from meysam_utils import get_logger

app = FastAPI()

HERE = Path(__file__).parent
logger = get_logger(__name__)


@app.post("/authorize")
async def authorize(request: Request):
    headers = pformat(dict(request.headers))
    cookies = pformat(dict(request.cookies))
    query_params = pformat(dict(request.query_params))

    for info in (headers, cookies, query_params):
        logger.info(info)
    logger.info(pformat(await request.body()))

    return Response(status_code=HTTPStatus.OK)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_dirs=[HERE],
    )
