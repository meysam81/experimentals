import base64
import time
from http import HTTPStatus
from pathlib import Path
from pprint import pformat
from typing import Callable
from urllib.parse import urlencode, urljoin

import httpx
from cryptography.fernet import Fernet
from fastapi import Cookie, FastAPI, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from meysam_utils import generate_random_string, get_logger
from settings import settings

app = FastAPI()
logger = get_logger(__name__, settings.LOG_LEVEL)

HERE = Path(__file__).parent


class ServerSession:
    session_store: dict = {}

    @classmethod
    async def get(cls, key):
        return cls.session_store.get(key)

    @classmethod
    async def set(cls, key, value):
        cls.session_store[key] = value

    @staticmethod
    def request_identifier(request: Request) -> str:
        return f"{request.client.host}:{request.client.port}"


class Encryption:
    encryption_key: str = settings.COOKIE_ENCRYPTION_KEY
    encryption_algorithm: str = settings.COOKIE_ENCRYPTION_ALGORITHM
    fernet = Fernet(base64.urlsafe_b64encode(encryption_key))

    @classmethod
    async def encrypt(cls, value: str):
        return cls.fernet.encrypt(value.encode()).decode()

    @classmethod
    async def decrypt(cls, value: str):
        return cls.fernet.decrypt(value.encode()).decode()


def decrypt_from_cookie(alias: str, optional: bool = True) -> Callable:
    default = "" if optional else None

    def decorator(encrypted_cookie: str = Cookie(default, alias=alias)) -> str | None:
        if not encrypted_cookie:
            return

        try:
            return Encryption.decrypt(encrypted_cookie)
        except Exception as e:
            logger.debug(encrypted_cookie)
            logger.error(f"Failed to decrypt cookie: {e}")
            return

    return decorator


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
    start = time.time()
    response = await call_next(request)
    processed_time = time.time() - start
    human_readable = convert_seconds_to_human_readable(processed_time)
    response.headers["X-Process-Time"] = human_readable
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}\n{pformat(dict(request.headers))}")
    response: Response = await call_next(request)
    return response


@app.get(settings.INDEX_URL)
async def index():
    return RedirectResponse(
        settings.LOGIN_URL, status_code=HTTPStatus.PERMANENT_REDIRECT
    )


@app.get(settings.LOGIN_URL)
async def oauth2_login(request: Request):
    state = generate_random_string(settings.HYDRA_FLOW_STATE_LENGTH)
    encrypted_state = await Encryption.encrypt(state)

    await ServerSession.set(state, ServerSession.request_identifier(request))

    url = urljoin(settings.HYDRA_PUBLIC_URL, settings.HYDRA_OAUTH2_AUTH_URL)
    params = {
        "client_id": settings.HYDRA_CLIENT_ID,
        "redirect_uri": settings.HYDRA_FLOW_REDIRECT_URL,
        "response_type": settings.HYDRA_FLOW_RESPONSE_TYPE,
        "state": state,
        "scope": settings.HYDRA_FLOW_REQUIRED_SCOPE,
    }
    response = RedirectResponse(url=f"{url}?{urlencode(params)}")
    for key, value in request.cookies.items():
        response.set_cookie(key=key, value=value)

    response.set_cookie(settings.HYDRA_FLOW_STATE_COOKIE_NAME, encrypted_state)

    return response


def error_response(
    error: str, error_description: str, request: Request
) -> RedirectResponse:
    params = {
        "error": error,
        "error_description": error_description,
        "headers": dict(request.headers),
        "cookies": dict(request.cookies),
        "query_params": request.query_params,
    }
    url = f"{settings.ERROR_URL}?{urlencode(params)}"
    return RedirectResponse(url)


@app.get(settings.LOGIN_CALLBACK_URL)
async def oauth2_login_callback(
    request: Request,
    code: str = None,
    state: str = None,
    error: str = None,
    error_description: str = None,
    state_from_cookie: str = Cookie("", alias=settings.HYDRA_FLOW_STATE_COOKIE_NAME),
):
    # HACK: I don't know why there's a question mark at the end
    state = state.rstrip("?")

    decrypted_state_from_cookie = await Encryption.decrypt(state_from_cookie)

    if error:
        return error_response(error, error_description, request)

    if state != decrypted_state_from_cookie:
        return error_response("state_mismatch", "State mismatch", request)

    request_identifier = await ServerSession.get(decrypted_state_from_cookie)
    if request_identifier != ServerSession.request_identifier(request):
        logger.warning(
            f"Request identifier mismatch: {request_identifier} != {ServerSession.request_identifier(request)}"
        )

    data = {
        "grant_type": settings.HYDRA_FLOW_GRANT_TYPE,
        "code": code,
        "redirect_uri": settings.HYDRA_FLOW_REDIRECT_URL,
        # "client_id": settings.HYDRA_CLIENT_ID,
        # "client_secret": settings.HYDRA_CLIENT_SECRET,
    }
    raise Exception("doing on purpose")
    async with httpx.AsyncClient(
        base_url=settings.HYDRA_PUBLIC_URL,
        auth=(settings.HYDRA_CLIENT_ID, settings.HYDRA_CLIENT_SECRET),
        headers={"content-type": "application/x-www-form-urlencoded"},
    ) as client:
        response = await client.post(settings.HYDRA_OAUTH2_TOKEN_URL, data=data)

    if response.status_code != HTTPStatus.OK:
        logger.error(response.text)
        return error_response("token_request_failed", response.text, request)

    logger.info(pformat(dict(response.headers)))
    logger.debug(response.text)

    response_json = response.json()
    access_token = response_json["access_token"]
    id_token = response_json["id_token"]
    refresh_token = response_json.get("refresh_token", "")

    response = RedirectResponse(settings.LOGIN_CALLBACK_SUCCESS_URL)

    encrypted_access_token = await Encryption.encrypt(access_token)
    encrypted_id_token = await Encryption.encrypt(id_token)
    encrypted_refresh_token = await Encryption.encrypt(refresh_token)

    response.set_cookie(
        settings.HYDRA_FLOW_ACCESS_TOKEN_COOKIE_NAME, encrypted_access_token
    )
    response.set_cookie(settings.HYDRA_FLOW_ID_TOKEN_COOKIE_NAME, encrypted_id_token)
    response.set_cookie(
        settings.HYDRA_FLOW_REFRESH_TOKEN_COOKIE_NAME, encrypted_refresh_token
    )

    return response


@app.get(settings.LOGIN_CALLBACK_SUCCESS_URL)
async def oauth2_login_callback_success(
    request: Request,
    access_token: str = Cookie("", alias=settings.HYDRA_FLOW_ACCESS_TOKEN_COOKIE_NAME),
    id_token: str = Cookie("", alias=settings.HYDRA_FLOW_ID_TOKEN_COOKIE_NAME),
    refresh_token: str = Cookie(
        "", alias=settings.HYDRA_FLOW_REFRESH_TOKEN_COOKIE_NAME
    ),
):
    decrypted_access_token = await Encryption.decrypt(access_token)
    decrypted_id_token = await Encryption.decrypt(id_token)
    decrypted_refresh_token = await Encryption.decrypt(refresh_token)

    return JSONResponse(
        dict(
            headers=dict(request.headers),
            cookies=dict(request.cookies),
            query_params=dict(request.query_params),
            access_token=decrypted_access_token,
            id_token=decrypted_id_token,
            refresh_token=decrypted_refresh_token,
        )
    )


@app.get(settings.ERROR_URL)
async def error(request: Request):
    return JSONResponse(
        dict(
            headers=dict(request.headers),
            cookies=dict(request.cookies),
            query_params=dict(request.query_params),
            body=(await request.body()).decode(),
        ),
        status_code=HTTPStatus.BAD_REQUEST,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_dirs=[HERE],
    )
