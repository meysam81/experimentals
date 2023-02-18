import time
from http import HTTPStatus
from pathlib import Path
from pprint import pformat
from urllib.parse import parse_qs, urljoin, urlparse

import httpx
from meysam_utils import get_logger
from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from settings import config

app = FastAPI()
logger = get_logger(__name__, config.LOG_LEVEL)

HERE = Path(__file__).parent


def convert_seconds_to_human_readable(seconds: float) -> str:
    if seconds < 1e-6:
        nanoseconds = seconds * 1_000_000_000
        return f"{nanoseconds:.3f}ns"
    if seconds < 1e-3:
        microseconds = seconds * 1_000_000
        return f"{microseconds:.3f}µs"
    if seconds < 1:
        milliseconds = seconds * 1_000
        return f"{milliseconds:.3f}ms"
    return f"{seconds:.3f}s"


@app.middleware("http")
async def add_process_time_header(request, call_next):
    logger.debug("add_process_time_header")
    start = time.time()
    response = await call_next(request)
    processed_time = time.time() - start
    human_readable = convert_seconds_to_human_readable(processed_time)
    response.headers["X-Process-Time"] = human_readable
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug("log_requests")
    response: Response = await call_next(request)
    logger.info(f"{request.method} {request.url} {response.status_code}")
    logger.debug(pformat(dict(request.headers)))
    return response


@app.get("/")
async def index():
    return {"message": "Hello From Ory Hydra Client!"}


@app.get("/oauth2/login")
async def login(login_challenge: str):
    async with httpx.AsyncClient() as client:
        url = urljoin(config.HYDRA_ADMIN_URL, config.HYDRA_LOGIN_REQUEST_URL)
        login_request = await client.get(
            url, params={"login_challenge": login_challenge}
        )

    logger.debug(pformat(dict(login_request.headers)))

    if not login_request.status_code == HTTPStatus.OK:
        url = urljoin(config.HYDRA_PUBLIC_URL, config.HYDRA_OAUTH2_AUTH_URL)
        return RedirectResponse(
            url=url,
            status_code=HTTPStatus.SEE_OTHER,
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        reload_dirs=[HERE],
    )
