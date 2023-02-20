import base64
import time
from http import HTTPStatus
from pathlib import Path
from pprint import pformat
from urllib.parse import urlencode, urljoin

import httpx
from cryptography.fernet import Fernet
from fastapi import Cookie, FastAPI, Form, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from meysam_utils import generate_random_string, get_logger
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


class Encyption:
    def __init__(self, encryption_key: str, encryption_algorithm: str):
        self.encryption_key = encryption_key
        self.encryption_algorithm = encryption_algorithm
        self.fernet = Fernet(base64.urlsafe_b64encode(encryption_key))

    async def encrypt(self, value: str):
        return self.fernet.encrypt(value.encode()).decode()

    async def decrypt(self, value: str):
        return self.fernet.decrypt(value.encode()).decode()


csrf_encryptor = Encyption(
    settings.CSRF_ENCRYPTION_KEY, settings.CSRF_ENCRYPTION_ALGORITHM
)


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


@app.get(settings.ERROR_URI)
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


@app.get(settings.LOGIN_URI, response_class=HTMLResponse)
async def login(
    request: Request,
    flow: str = None,
):
    redirect_url = urljoin(
        settings.KRATOS_PUBLIC_URL,
        settings.KRATOS_LOGIN_BROWSER_URI,
    )

    if not flow:
        return RedirectResponse(
            url=redirect_url, status_code=HTTPStatus.TEMPORARY_REDIRECT
        )

    logger.info(pformat(dict(request.headers)))

    async with httpx.AsyncClient(base_url=settings.KRATOS_PUBLIC_URL) as client:
        result = await client.get(
            settings.KRATOS_LOGIN_FLOW_URI,
            params={"id": flow},
            headers={"accept": "application/json"},
            cookies=request.cookies,
        )

    logger.info(pformat(dict(result.headers)))

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

    return response


@app.get(settings.OAUTH2_LOGIN_URI)
async def oauth2_login(login_challenge: str):
    """
    The login logic has already been implemented in settings.LOGIN_URI and we
    only need to save the login challenge to the cookies and redirect.
    """
    response = RedirectResponse(
        url=settings.LOGIN_URI, status_code=HTTPStatus.SEE_OTHER
    )

    # HACK: I have no idea why there's a question mark at the end
    login_challenge = login_challenge.rstrip("?")

    response.set_cookie(
        key=settings.HYDRA_LOGIN_CHALLENGE_COOKIE_NAME, value=login_challenge
    )
    return response


@app.get(settings.OAUTH2_LOGIN_CALLBACK_URI, response_class=RedirectResponse)
async def oauth2_login_callback(
    request: Request,
    login_challenge: str = Cookie("", alias=settings.HYDRA_LOGIN_CHALLENGE_COOKIE_NAME),
):
    if not login_challenge:
        return RedirectResponse(
            url=settings.INDEX_URI, status_code=HTTPStatus.SEE_OTHER
        )

    # get the session from kratos using the cookies from the request
    async with httpx.AsyncClient(base_url=settings.KRATOS_PUBLIC_URL) as client:
        session_response = await client.get(
            settings.KRATOS_WHOAMI_URI,
            headers={"accept": "application/json"},
            cookies=request.cookies,
        )

    logger.info(pformat(dict(session_response.headers)))

    if session_response.status_code == HTTPStatus.OK:
        # if there is a login_challenge, it's an oauth2 request and we need to
        # accept the login request and redirect to the url given by the hydra

        async with httpx.AsyncClient(base_url=settings.HYDRA_ADMIN_URL) as client:
            oauth2_response = await client.put(
                settings.HYDRA_LOGIN_ACCEPT_URI,
                params={"login_challenge": login_challenge},
                json={
                    "subject": session_response.json()["identity"]["id"],
                    "remember": settings.OAUTH2_CLIENT_REMEMBER,
                    "remember_for": settings.OAUTH2_CLIENT_REMEMBER_FOR,
                },
                headers={"accept": "application/json"},
            )

        if oauth2_response.status_code == HTTPStatus.OK:
            redirect_url = oauth2_response.json()["redirect_to"]

            # HACK: exposing hydra admin & public on localhost needs this
            redirect_url = redirect_url.replace("41100", "41101", 1)

            return RedirectResponse(url=redirect_url, status_code=HTTPStatus.SEE_OTHER)

        logger.error(oauth2_response.text)
        return Response(
            "error accepting oauth2 login", status_code=HTTPStatus.BAD_REQUEST
        )

    logger.error(session_response.text)
    return Response("error getting session", status_code=HTTPStatus.BAD_REQUEST)


@app.get(settings.OAUTH2_CONSENT_URI, response_class=HTMLResponse)
async def oauth2_consent(
    request: Request,
    consent_challenge: str,
):
    async with httpx.AsyncClient(base_url=settings.HYDRA_ADMIN_URL) as client:
        consent_response = await client.get(
            settings.HYDRA_CONSENT_REQUEST_URI,
            params={"consent_challenge": consent_challenge},
            headers={"accept": "application/json"},
        )

    if consent_response.status_code != HTTPStatus.OK:
        logger.info(pformat(dict(consent_response.headers)))
        logger.error(consent_response.text)
        return Response("consent doesn't exist", status_code=HTTPStatus.BAD_REQUEST)

    consent_json = consent_response.json()

    if consent_json["skip"]:
        async with httpx.AsyncClient(base_url=settings.HYDRA_ADMIN_URL) as client:
            consent_response = await client.put(
                settings.HYDRA_CONSENT_ACCEPT_URI,
                params={"consent_challenge": consent_challenge},
                json={
                    "grant_scope": consent_json["requested_scope"],
                    "remember": settings.OAUTH2_CLIENT_REMEMBER,
                    "remember_for": settings.OAUTH2_CLIENT_REMEMBER_FOR,
                },
                headers={"accept": "application/json"},
            )

        if consent_response.status_code != HTTPStatus.OK:
            logger.info(pformat(dict(consent_response.headers)))
            logger.error(consent_response.text)
            return Response(
                "error accepting consent", status_code=HTTPStatus.BAD_REQUEST
            )

        redirect_url = consent_response.json()["redirect_to"]

        # HACK: exposing hydra admin & public on localhost needs this
        redirect_url = redirect_url.replace("41100", "41101", 1)

        return RedirectResponse(url=redirect_url, status_code=HTTPStatus.SEE_OTHER)

    requested_scopes = settings.OAUTH2_CLIENT_SCOPE_COOKIE_DELIMITER.join(
        consent_json["requested_scope"]
    )

    inputs = [
        {
            "id": scope,
            "label": scope,
            "required": False,
            "type": "checkbox",
            "value": "on",
        }
        for scope in consent_json["requested_scope"]
    ]

    inputs.extend(
        [
            {
                "id": "approved",
                "label": "Accept",
                "required": False,
                "type": "submit",
                "value": "true",
            },
            {
                "id": "approved",
                "label": "Deny",
                "required": False,
                "type": "submit",
                "value": "false",
            },
        ],
    )

    client_name = consent_json["client"]["client_name"]

    # we can put consent-accept url of hydra in the `action`, but for occasions
    # where the admin page is not exposed to the public, we need to use the
    # callback url and call the consent-accept endpoint ourselves
    action = (
        f"{settings.OAUTH2_CONSENT_CALLBACK_URI}?consent_challenge={consent_challenge}"
    )
    method = settings.CONSENT_SUBMIT_METHOD

    csrf_token = generate_random_string(settings.CSRF_TOKEN_LENTGH)

    response = templates.TemplateResponse(
        "consent.html",
        {
            "action": action,
            "method": method,
            "csrf_token": await csrf_encryptor.encrypt(csrf_token),
            "inputs": inputs,
            "request": request,
            "client_name": client_name,
        },
    )
    for cookie, value in request.cookies.items():
        response.set_cookie(cookie, value)

    response.set_cookie(key=settings.CSRF_TOKEN_COOKIE_NAME, value=csrf_token)
    response.set_cookie(
        key=settings.OAUTH2_CLIENT_SCOPE_COOKIE_NAME, value=requested_scopes
    )

    return response


consent_method = getattr(app, settings.CONSENT_SUBMIT_METHOD.lower())


@consent_method(settings.OAUTH2_CONSENT_CALLBACK_URI)
async def oauth2_consent_callback(
    request: Request,
    consent_challenge: str,
    approved: bool = Form(...),
    csrf_token: str = Form(...),
    csrf_token_from_cookie: str = Cookie("", alias=settings.CSRF_TOKEN_COOKIE_NAME),
    requested_scopes_str: str = Cookie(
        "", alias=settings.OAUTH2_CLIENT_SCOPE_COOKIE_NAME
    ),
):
    if not csrf_token:
        return Response("csrf token is missing", status_code=HTTPStatus.BAD_REQUEST)

    if not csrf_token_from_cookie:
        return Response(
            "csrf token cookie is missing", status_code=HTTPStatus.BAD_REQUEST
        )

    if await csrf_encryptor.decrypt(csrf_token) != csrf_token_from_cookie:
        return Response("csrf token is invalid", status_code=HTTPStatus.BAD_REQUEST)

    if not approved:
        # reject the request using hydra admin api
        async with httpx.AsyncClient(base_url=settings.HYDRA_ADMIN_URL) as client:
            consent_response = await client.put(
                settings.HYDRA_CONSENT_REJECT_URI,
                params={"consent_challenge": consent_challenge},
                json={},
                headers={"accept": "application/json"},
            )

        if consent_response.status_code == HTTPStatus.OK:
            redirect_url = consent_response.json()["redirect_to"]

            response = RedirectResponse(
                url=redirect_url, status_code=HTTPStatus.SEE_OTHER
            )

            response.delete_cookie(key=settings.CSRF_TOKEN_COOKIE_NAME)
            response.delete_cookie(key=settings.OAUTH2_CLIENT_SCOPE_COOKIE_NAME)

            return response

        logger.error(pformat(dict(consent_response.headers)))
        logger.error(consent_response.text)

        return Response("error rejecting consent", status_code=HTTPStatus.BAD_REQUEST)

    submitted_form = await request.form()
    requested_scopes = requested_scopes_str.split(
        settings.OAUTH2_CLIENT_SCOPE_COOKIE_DELIMITER
    )

    logger.debug(submitted_form)

    accepted_grants = []
    for key, value in submitted_form.items():
        if key in requested_scopes and value == "on":
            accepted_grants.append(key)

    async with httpx.AsyncClient(base_url=settings.HYDRA_ADMIN_URL) as client:
        consent_response = await client.put(
            settings.HYDRA_CONSENT_ACCEPT_URI,
            params={"consent_challenge": consent_challenge},
            json={
                "grant_scope": accepted_grants,
                "remember": settings.OAUTH2_CLIENT_REMEMBER,
                "remember_for": settings.OAUTH2_CLIENT_REMEMBER_FOR,
            },
            headers={"accept": "application/json"},
        )

    if consent_response.status_code == HTTPStatus.OK:
        redirect_url = consent_response.json()["redirect_to"]

        # HACK: hydra can't tell admin/public api difference when deployed locally
        redirect_url = redirect_url.replace("41100", "41101", 1)

        response = RedirectResponse(url=redirect_url, status_code=HTTPStatus.SEE_OTHER)

        response.delete_cookie(key=settings.CSRF_TOKEN_COOKIE_NAME)
        response.delete_cookie(key=settings.OAUTH2_CLIENT_SCOPE_COOKIE_NAME)

        return response

    logger.error(pformat(dict(consent_response.headers)))
    logger.error(consent_response.text)

    return Response("error accepting consent", status_code=HTTPStatus.BAD_REQUEST)


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
            url=redirect_url + f"?return_to={settings.LOGIN_URI}",
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
