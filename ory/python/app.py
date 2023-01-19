from http import HTTPStatus
from pathlib import Path
from urllib.parse import urljoin

import httpx
from config import settings
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from logger import get_logger

HERE = Path(__file__).parent
STATIC = HERE / "static"
TEMPLATES = HERE / "templates"

logger = get_logger(__name__)
app = FastAPI()
templates = Jinja2Templates(directory=TEMPLATES)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/error")
async def error(request: Request):
    logger.error(request.headers)
    logger.error(await request.body())
    return {"message": "Error"}


@app.get(
    "/",
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
async def login(request: Request, flow: str = None):
    redirect_url = urljoin(
        settings.KRATOS_PUBLIC_URL,
        settings.KRATOS_LOGIN_BROWSER_URI,
    )

    if not flow:
        return RedirectResponse(
            url=redirect_url, status_code=HTTPStatus.TEMPORARY_REDIRECT
        )

    logger.debug(await request.body())
    logger.debug(request.headers)

    async with httpx.AsyncClient() as client:
        result = await client.get(
            urljoin(settings.KRATOS_PUBLIC_URL, settings.KRATOS_LOGIN_FLOW_URI),
            params={"id": flow},
            headers={"accept": "application/json"},
            cookies=request.cookies,
        )

    logger.debug(f"{result.status_code} {result.text}")

    if result.status_code == HTTPStatus.NOT_FOUND:
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

    logger.debug(await request.body())
    logger.debug(request.headers)

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

    if result.status_code == HTTPStatus.NOT_FOUND:
        return RedirectResponse(url=redirect_url, status_code=HTTPStatus.SEE_OTHER)

    logger.debug(f"{result.status_code} {result.text}")
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

    logger.debug(await request.body())
    logger.debug(request.headers)

    async with httpx.AsyncClient() as client:
        result = await client.get(
            urljoin(settings.KRATOS_PUBLIC_URL, settings.KRATOS_REGISTRATION_FLOW_URI),
            params={"id": flow},
            headers={"accept": "application/json"},
            cookies=request.cookies,
        )

    logger.debug(f"{result.status_code} {result.text}")

    if result.status_code == HTTPStatus.NOT_FOUND:
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
    logger.debug(await request.body())
    logger.debug(request.headers)

    async with httpx.AsyncClient() as client:
        result = await client.get(
            urljoin(settings.KRATOS_PUBLIC_URL, settings.KRATOS_LOGOUT_BROWSER_URI),
            headers={"accept": "application/json"},
            cookies=request.cookies,
        )

    logger.debug(f"{result.status_code} {result.text}")

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

    logger.debug(await request.body())
    logger.debug(request.headers)

    async with httpx.AsyncClient() as client:
        result = await client.get(
            urljoin(settings.KRATOS_PUBLIC_URL, settings.KRATOS_RECOVERY_FLOW_URI),
            params={"id": flow},
            headers={"accept": "application/json"},
            cookies=request.cookies,
        )

    logger.debug(f"{result.status_code} {result.text}")

    if result.status_code == HTTPStatus.NOT_FOUND:
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

    logger.debug(await request.body())
    logger.debug(request.headers)

    async with httpx.AsyncClient() as client:
        result = await client.get(
            urljoin(settings.KRATOS_PUBLIC_URL, settings.KRATOS_SETTINGS_FLOW_URI),
            params={"id": flow},
            headers={"accept": "application/json"},
            cookies=request.cookies,
        )

    logger.debug(f"{result.status_code} {result.text}")

    if result.status_code == HTTPStatus.NOT_FOUND:
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
    return FileResponse(STATIC / "favicon.jpeg")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_dirs=[HERE],
        log_level=settings.LOG_LEVEL.lower(),
    )
