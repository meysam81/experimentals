import random
import string
import time
from http import HTTPStatus
from pathlib import Path
from pprint import pformat
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

import httpx
from fastapi import Cookie, FastAPI, Header, Query, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from meysam_utils import get_logger
from settings import settings

HERE = Path(__file__).parent
STATIC = HERE / "static"
TEMPLATES = HERE / "templates"

logger = get_logger(__name__, settings.LOG_LEVEL)
app = FastAPI(title=settings.APP_NAME)
templates = Jinja2Templates(directory=TEMPLATES)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


REDIRECT_STATUSES = [
    HTTPStatus.SEE_OTHER,
    HTTPStatus.TEMPORARY_REDIRECT,
    HTTPStatus.PERMANENT_REDIRECT,
    HTTPStatus.FOUND,
]


class SessionStore:
    session_store: dict = {}

    @classmethod
    def get(cls, key):
        return cls.session_store.get(key)

    @classmethod
    def set(cls, key, value):
        cls.session_store[key] = value


@app.middleware("http")
async def return_to_query_param_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    params = {}
    if return_to := request.query_params.get("return_to"):
        params["return_to"] = return_to
    if response.status_code in REDIRECT_STATUSES:
        qp = urlencode(params)
        response.headers["Location"] = f"{response.headers['Location']}?{qp}"
    return response


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    if request.query_params:
        request_info = f"{request.method} {request.url}?{request.query_params}"
    else:
        request_info = f"{request.method} {request.url}"
    logger.info(f"{request_info} - {process_time:.2f}s")
    return response


@app.get("/error")
async def error(request: Request):
    logger.error(pformat(dict(request.headers)))
    logger.error(await request.body())
    return {"message": "Error"}


@app.get("/healthz")
async def health():
    return {"message": "OK"}


@app.get(
    settings.INDEX_URI,
    responses={
        HTTPStatus.OK: {
            "description": "The user is already logged in and will gets the session info"
        },
        HTTPStatus.SEE_OTHER: {
            "description": "The user is not logged in and will be redirected to the login page"
        },
    },
)
async def index(request: Request):
    async with httpx.AsyncClient() as client:
        result = await client.get(
            urljoin(settings.KRATOS_PUBLIC_URL, settings.KRATOS_WHOAMI_URI),
            headers={"accept": "application/json"},
            cookies=request.cookies,
        )

    if result.status_code == HTTPStatus.OK:
        return result.json()

    return RedirectResponse(url=settings.LOGIN_URI, status_code=HTTPStatus.SEE_OTHER)


@app.get(settings.HYDRA_LOGIN_URL, response_class=RedirectResponse)
async def hydra_login(request: Request, login_challenge: str = None):
    if not login_challenge:
        state = "".join(
            random.choice(string.ascii_letters + string.digits)
            for _ in range(settings.HYDRA_STATE_LENGTH)
        )
        SessionStore.set(state, f"{request.client.host}:{request.client.port}")
        url = urljoin(settings.HYDRA_PUBLIC_URL, settings.HYDRA_OAUTH2_AUTH_URL)
        params = {
            "client_id": settings.HYDRA_CLIENT_ID,
            "redirect_uri": settings.HYDRA_REDIRECT_URI,
            "response_type": "code",
            "state": state,
        }
        response = RedirectResponse(url=f"{url}?{urlencode(params)}")
        for key, value in request.cookies.items():
            response.set_cookie(key=key, value=value)

        response.set_cookie(settings.HYDRA_FLOW_STATE_COOKIE_NAME, state)
        return response

    async with httpx.AsyncClient() as client:
        result = await client.get(
            urljoin(settings.HYDRA_ADMIN_URL, settings.HYDRA_LOGIN_REQUEST_URL),
            params={"login_challenge": login_challenge},
            headers={"accept": "application/json"},
        )

    if result.status_code != HTTPStatus.OK:
        logger.error(result.text)
        url = urljoin(settings.HYDRA_PUBLIC_URL, settings.HYDRA_OAUTH2_AUTH_URL)
        return RedirectResponse(url=url, status_code=HTTPStatus.SEE_OTHER)

    json_ = result.json()
    if json_["skip"]:
        async with httpx.AsyncClient() as client:
            result = await client.put(
                urljoin(settings.HYDRA_PUBLIC_URL, settings.HYDRA_LOGIN_ACCEPT_URL),
                params={"login_challenge": login_challenge},
                headers={"accept": "application/json"},
            )
        return RedirectResponse(
            url=json_["redirect_to"], status_code=HTTPStatus.SEE_OTHER
        )

    return RedirectResponse(
        url=settings.LOGIN_URI + f"?login_challenge={login_challenge}",
        status_code=HTTPStatus.SEE_OTHER,
    )


@app.get(settings.HYDRA_LOGIN_SUBMIT_URL, response_class=RedirectResponse)
async def hydra_login_callback(
    request: Request,
    login_challenge_from_cookie: str = Cookie(
        "", alias=settings.HYDRA_LOGIN_CHALLENGE_COOKIE_NAME
    ),
    location: str = Header("", alias="Location"),
):
    async with httpx.AsyncClient() as client:
        result = await client.get(
            urljoin(settings.KRATOS_PUBLIC_URL, settings.KRATOS_WHOAMI_URI),
            headers={"accept": "application/json"},
            cookies=request.cookies,
        )

    if result.status_code != HTTPStatus.OK:
        if login_challenge_from_cookie:
            async with httpx.AsyncClient() as client:
                logger.info(login_challenge_from_cookie)
                result = await client.put(
                    urljoin(settings.HYDRA_ADMIN_URL, settings.HYDRA_LOGIN_REJECT_URL),
                    params={"login_challenge": login_challenge_from_cookie},
                    headers={"accept": "application/json"},
                )
                logger.info(pformat(dict(result.headers)))
                logger.info(result.text)
                return RedirectResponse(
                    url=result.json()["redirect_to"], status_code=HTTPStatus.SEE_OTHER
                )
        return RedirectResponse(
            url=settings.LOGIN_URI, status_code=HTTPStatus.SEE_OTHER
        )

    if login_challenge_from_cookie:
        subject = result.json()["identity"]["id"]
        async with httpx.AsyncClient() as client:
            result = await client.put(
                urljoin(settings.HYDRA_PUBLIC_URL, settings.HYDRA_LOGIN_ACCEPT_URL),
                json={"subject": subject, "remember": True, "remember_for": 0},
                params={"login_challenge": login_challenge_from_cookie},
                headers={"accept": "application/json"},
            )
        return RedirectResponse(
            url=result.json()["redirect_to"],
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=location or settings.INDEX_URI, status_code=HTTPStatus.SEE_OTHER
    )


@app.get(settings.LOGIN_URI, response_class=HTMLResponse)
async def login(
    request: Request,
    flow: str = None,
    login_challenge: str = Query(""),
    login_challenge_from_cookie: str = Cookie(
        "", alias=settings.HYDRA_LOGIN_CHALLENGE_COOKIE_NAME
    ),
):
    # I have no idea why there's a question mark at the end of the login_challenge
    hydra_challenge = (login_challenge or login_challenge_from_cookie).rstrip("?")

    redirect_url = urljoin(
        settings.KRATOS_PUBLIC_URL,
        settings.KRATOS_LOGIN_BROWSER_URI,
    )

    if not flow:
        response = RedirectResponse(
            url=redirect_url, status_code=HTTPStatus.TEMPORARY_REDIRECT
        )
        if hydra_challenge:
            response.set_cookie(
                key=settings.HYDRA_LOGIN_CHALLENGE_COOKIE_NAME, value=hydra_challenge
            )
        return response

    logger.debug(pformat(dict(request.headers)))

    async with httpx.AsyncClient() as client:
        result = await client.get(
            urljoin(settings.KRATOS_PUBLIC_URL, settings.KRATOS_LOGIN_FLOW_URI),
            params={"id": flow},
            headers={"accept": "application/json"},
            cookies=request.cookies,
        )

    logger.debug(pformat(dict(result.headers)))

    if result.status_code in [HTTPStatus.NOT_FOUND, HTTPStatus.GONE]:
        return RedirectResponse(
            url=redirect_url, status_code=HTTPStatus.TEMPORARY_REDIRECT
        )

    json_ = result.json()

    inputs = []
    csrf_token = None
    for input_ in json_["ui"]["nodes"]:
        if input_["attributes"]["name"] == "csrf_token":
            csrf_token = input_["attributes"]["value"]
            continue
        inputs.append(
            {
                "id": input_["attributes"]["name"],
                "label": input_["meta"].get("label", {}).get("text"),
                "required": input_["attributes"].get("required", False),
                "type": input_["attributes"]["type"],
                "value": input_["attributes"].get("value", ""),
            }
        )

    action = json_["ui"]["action"]
    method = json_["ui"]["method"]

    # parse the url and the query param stored in `action`
    parsed_url = urlparse(action)
    parsed_query = parse_qs(parsed_url.query)

    response = templates.TemplateResponse(
        "login.html",
        {
            "action": action,
            "method": method,
            "csrf_token": csrf_token,
            "inputs": inputs,
            "request": request,
        },
    )
    for cookie, value in request.cookies.items():
        response.set_cookie(cookie, value)

    response.headers["Location"] = urljoin(
        f"{settings.SCHEME}://{settings.HOST}:{settings.PORT}",
        settings.HYDRA_LOGIN_SUBMIT_URL,
    )
    if return_to := json_.get("return_to"):
        response.set_cookie(settings.NEXT_LOCATION_COOKIE_NAME, return_to)

    return response


@app.get(settings.VERIFICATION_URI, response_class=HTMLResponse)
async def verification(request: Request, flow: str = None, code: str = ""):
    redirect_url = (
        urljoin(
            settings.KRATOS_PUBLIC_URL,
            settings.KRATOS_VERIFICATION_BROWSER_URI,
        )
        + f"?return_to=/"
    )
    if not flow:
        return RedirectResponse(
            url=redirect_url, status_code=HTTPStatus.TEMPORARY_REDIRECT
        )

    logger.debug(pformat(dict(request.headers)))

    async with httpx.AsyncClient() as client:
        result = await client.get(
            urljoin(
                settings.KRATOS_PUBLIC_URL,
                settings.KRATOS_VERIFICATION_FLOW_URI,
            ),
            params={"id": flow},
            headers={"accept": "application/json"},
            cookies=request.cookies,
        )

    if result.status_code in [HTTPStatus.NOT_FOUND, HTTPStatus.GONE]:
        return RedirectResponse(url=redirect_url, status_code=HTTPStatus.SEE_OTHER)

    json_ = result.json()

    if json_.get("state") == "passed_challenge":
        return RedirectResponse(url="/", status_code=HTTPStatus.SEE_OTHER)

    inputs = []
    csrf_token = None
    for input_ in json_["ui"]["nodes"]:
        if input_["attributes"]["name"] == "csrf_token":
            csrf_token = input_["attributes"]["value"]
            continue
        name = input_["attributes"]["name"]
        value = code if name == "code" else input_["attributes"].get("value", "")
        inputs.append(
            {
                "id": name,
                "label": input_["meta"].get("label", {}).get("text"),
                "required": input_["attributes"].get("required", False),
                "type": input_["attributes"]["type"],
                "value": value,
            }
        )

    action = json_["ui"]["action"]
    method = json_["ui"]["method"]

    response = templates.TemplateResponse(
        "verification.html",
        {
            "action": action,
            "method": method,
            "csrf_token": csrf_token,
            "inputs": inputs,
            "request": request,
        },
    )

    for cookie, value in request.cookies.items():
        response.set_cookie(cookie, value)

    return response


@app.get(settings.REGISTRATION_URI, response_class=HTMLResponse)
async def registration(request: Request, flow: str = None):
    redirect_url = urljoin(
        settings.KRATOS_PUBLIC_URL, settings.KRATOS_REGISTRATION_BROWSER_URI
    )
    if not flow:
        return RedirectResponse(
            url=redirect_url, status_code=HTTPStatus.TEMPORARY_REDIRECT
        )

    logger.debug(pformat(dict(request.headers)))

    async with httpx.AsyncClient() as client:
        result = await client.get(
            urljoin(settings.KRATOS_PUBLIC_URL, settings.KRATOS_REGISTRATION_FLOW_URI),
            params={"id": flow},
            headers={"accept": "application/json"},
            cookies=request.cookies,
        )

    if result.status_code in [HTTPStatus.NOT_FOUND, HTTPStatus.GONE]:
        return RedirectResponse(
            url=redirect_url, status_code=HTTPStatus.TEMPORARY_REDIRECT
        )

    json_ = result.json()
    inputs = []
    csrf_token = None
    for input_ in json_["ui"]["nodes"]:
        if input_["attributes"]["name"] == "csrf_token":
            csrf_token = input_["attributes"]["value"]
            continue
        inputs.append(
            {
                "id": input_["attributes"]["name"],
                "label": input_["meta"].get("label", {}).get("text"),
                "required": input_["attributes"].get("required", False),
                "type": input_["attributes"]["type"],
                "value": input_["attributes"].get("value"),
            }
        )

    action = json_["ui"]["action"]
    method = json_["ui"]["method"]

    response = templates.TemplateResponse(
        "registration.html",
        {
            "action": action,
            "method": method,
            "csrf_token": csrf_token,
            "inputs": inputs,
            "request": request,
        },
    )

    for cookie, value in request.cookies.items():
        response.set_cookie(cookie, value)

    return response


@app.get(settings.LOGOUT_URI, response_class=HTMLResponse)
async def logout(request: Request):
    logger.debug(pformat(dict(request.headers)))

    async with httpx.AsyncClient() as client:
        result = await client.get(
            urljoin(settings.KRATOS_PUBLIC_URL, settings.KRATOS_LOGOUT_BROWSER_URI),
            headers={"accept": "application/json"},
            cookies=request.cookies,
        )

    if result.status_code == HTTPStatus.UNAUTHORIZED:
        return RedirectResponse(url="/", status_code=HTTPStatus.SEE_OTHER)

    json_ = result.json()

    response = templates.TemplateResponse(
        "logout.html",
        {
            "request": request,
            "logout_url": json_["logout_url"],
        },
    )

    for cookie, value in request.cookies.items():
        response.set_cookie(cookie, value)

    return response


@app.get(settings.RECOVERY_URI, response_class=HTMLResponse)
async def recovery(request: Request, flow: str = None):
    redirect_url = urljoin(
        settings.KRATOS_PUBLIC_URL, settings.KRATOS_RECOVERY_BROWSER_URI
    )
    if not flow:
        return RedirectResponse(
            url=redirect_url + f"?return_to=/login",
            status_code=HTTPStatus.TEMPORARY_REDIRECT,
        )

    logger.debug(pformat(dict(request.headers)))

    async with httpx.AsyncClient() as client:
        result = await client.get(
            urljoin(settings.KRATOS_PUBLIC_URL, settings.KRATOS_RECOVERY_FLOW_URI),
            params={"id": flow},
            headers={"accept": "application/json"},
            cookies=request.cookies,
        )

    if result.status_code in [HTTPStatus.NOT_FOUND, HTTPStatus.GONE]:
        return RedirectResponse(
            url=redirect_url, status_code=HTTPStatus.TEMPORARY_REDIRECT
        )

    json_ = result.json()
    inputs = []
    csrf_token = None
    for input_ in json_["ui"]["nodes"]:
        if input_["attributes"]["name"] == "csrf_token":
            csrf_token = input_["attributes"]["value"]
            continue
        inputs.append(
            {
                "id": input_["attributes"]["name"],
                "label": input_["meta"].get("label", {}).get("text"),
                "required": input_["attributes"].get("required", False),
                "type": input_["attributes"]["type"],
                "value": input_["attributes"].get("value", ""),
            }
        )

    action = json_["ui"]["action"]
    method = json_["ui"]["method"]

    response = templates.TemplateResponse(
        "recovery.html",
        {
            "action": action,
            "method": method,
            "csrf_token": csrf_token,
            "inputs": inputs,
            "request": request,
        },
    )

    for cookie, value in request.cookies.items():
        response.set_cookie(cookie, value)

    return response


@app.get(settings.SETTINGS_URI, response_class=HTMLResponse, name="settings")
async def profile(request: Request, flow: str = None):
    redirect_url = (
        urljoin(settings.KRATOS_PUBLIC_URL, settings.KRATOS_SETTINGS_BROWSER_URI)
        + f"?return_to={settings.LOGIN_URI}"
    )

    if not flow:
        return RedirectResponse(
            url=redirect_url, status_code=HTTPStatus.TEMPORARY_REDIRECT
        )

    logger.debug(pformat(dict(request.headers)))

    async with httpx.AsyncClient() as client:
        result = await client.get(
            urljoin(settings.KRATOS_PUBLIC_URL, settings.KRATOS_SETTINGS_FLOW_URI),
            params={"id": flow},
            headers={"accept": "application/json"},
            cookies=request.cookies,
        )

    if result.status_code in [HTTPStatus.NOT_FOUND, HTTPStatus.GONE]:
        return RedirectResponse(
            url=redirect_url, status_code=HTTPStatus.TEMPORARY_REDIRECT
        )

    json_ = result.json()
    inputs = []
    csrf_token = None
    for input_ in json_["ui"]["nodes"]:
        name = input_["attributes"].get("name")
        value = input_["attributes"].get("value", "")
        type_ = input_["attributes"].get("type")

        if name == "csrf_token":
            csrf_token = input_["attributes"]["value"]
            continue

        if base64_img := input_["attributes"].get("src"):
            name = input_["attributes"]["id"]
            value = base64_img
            type_ = input_["attributes"]["node_type"]

        elif input_["attributes"].get("id") == "totp_secret_key":
            name = input_["attributes"]["id"]
            type_ = input_["attributes"]["node_type"]
            value = input_["attributes"]["text"]["text"]

        elif input_["attributes"].get("id") == "lookup_secret_codes":
            name = input_["attributes"]["id"]
            type_ = input_["attributes"]["node_type"]
            value = input_["attributes"]["text"]["text"]

        inputs.append(
            {
                "id": name,
                "label": input_["meta"].get("label", {}).get("text"),
                "required": input_["attributes"].get("required", False),
                "type": type_,
                "value": value,
            }
        )

    action = json_["ui"]["action"]
    method = json_["ui"]["method"]

    response = templates.TemplateResponse(
        "settings.html",
        {
            "action": action,
            "method": method,
            "csrf_token": csrf_token,
            "inputs": inputs,
            "request": request,
        },
    )

    for cookie, value in request.cookies.items():
        response.set_cookie(cookie, value)

    return response


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(STATIC / "favicon.jpeg", media_type="image/jpeg")


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Listening on {settings.HOST}:{settings.PORT}")

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_dirs=[HERE],
        log_level=settings.LOG_LEVEL.lower(),
    )
