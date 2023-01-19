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

    return RedirectResponse(
        url=settings.LOGIN_CALLBACK_URI, status_code=HTTPStatus.SEE_OTHER
    )


@app.get(settings.LOGIN_CALLBACK_URI, response_class=HTMLResponse)
async def login(request: Request, flow: str = None):
    if not flow:
        url = urljoin(
            settings.KRATOS_PUBLIC_URL,
            settings.KRATOS_LOGIN_BROWSER_URI,
        )
        return RedirectResponse(url=url, status_code=HTTPStatus.TEMPORARY_REDIRECT)

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
                "label": input_["meta"]["label"]["text"],
                "required": input_["attributes"].get("required", False),
                "type": input_["attributes"]["type"],
                "value": input_["attributes"].get("value"),
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


@app.get(settings.VERIFICATION_CALLBACK_URI, response_class=HTMLResponse)
async def verification(request: Request, flow: str = None, code: str = ""):
    if not flow:
        url = (
            urljoin(
                settings.KRATOS_PUBLIC_URL,
                settings.KRATOS_VERIFICATION_BROWSER_URI,
            )
            + f"?return_to=/"
        )
        return RedirectResponse(url=url, status_code=HTTPStatus.TEMPORARY_REDIRECT)

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
        return RedirectResponse(
            url=settings.VERIFICATION_CALLBACK_URI, status_code=HTTPStatus.SEE_OTHER
        )

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


@app.get(settings.REGISTRATION_CALLBACK_URI, response_class=HTMLResponse)
async def registration(request: Request, flow: str = None):
    if not flow:
        url = urljoin(
            settings.KRATOS_PUBLIC_URL, settings.KRATOS_REGISTRATION_BROWSER_URI
        )
        return RedirectResponse(url=url, status_code=HTTPStatus.TEMPORARY_REDIRECT)

    logger.debug(await request.body())
    logger.debug(request.headers)

    async with httpx.AsyncClient() as client:
        result = await client.get(
            urljoin(
                settings.KRATOS_PUBLIC_URL, settings.KRATOS_REGISTRATION_BROWSER_URI
            ),
            params={"flow": flow},
            headers={"accept": "application/json"},
            cookies=request.cookies,
        )

    logger.debug(f"{result.status_code} {result.text}")
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
                "label": input_["meta"]["label"]["text"],
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
