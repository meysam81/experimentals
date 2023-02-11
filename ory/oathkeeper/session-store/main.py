import sys
from base64 import b64decode
from pathlib import Path

import httpx
import jwt
from base_utils import get_logger
from config import settings
from fastapi import Cookie, FastAPI, Header, Query, Request, Response

app = FastAPI()

HERE = Path(__file__).parent
logger = get_logger(__name__)


@app.get("/cookie")
async def cookie_(request: Request):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{settings.KRATOS_PUBLIC_URL}/sessions/whoami",
            cookies=request.cookies,
        )
    passing = res.status_code == 200
    print(request.headers, request.cookies, passing)
    if not passing:
        return Response(status_code=401)
    return {"subject": "foo", "extra": {"bar": "baz"}}


@app.get("/jwt")
async def jwt_(
    request: Request,
    authorization: str = Header(""),
    jwt_cookie: str = Cookie("", alias="jwt"),
    jwt_param: str = Query("", alias="jwt"),
):
    try:
        token = (
            authorization.split(" ")[1] if authorization else jwt_cookie or jwt_param
        )
        type_ = authorization.split(" ")[0] if authorization else "bearer"
        print((token, authorization, jwt_cookie, jwt_param))
        identity = jwt.decode(token, "secret", algorithms=["HS256"])
    except jwt.exceptions.DecodeError as exp:
        type_ = ""
        print(exp, file=sys.stderr, flush=True)
        identity = {}
    passing = identity.get("sub") == "valid"
    print((request.headers, request.cookies, passing))
    if not (type_.lower() == "bearer" and passing):
        return Response(status_code=401)
    return {"subject": "foo", "extra": {"bar": "baz"}}


@app.post("/oauth2")
async def oauth2_(request: Request, authorization: str = Header("")):
    type_ = authorization.split(" ")[0] if authorization else ""
    cred = authorization.split(" ")[1] if authorization else ""
    passing = b64decode(cred).decode("utf-8") == "valid:valid"
    print(request.headers, request.cookies, passing)
    if not (type_.lower() == "basic" and passing):
        return Response(status_code=401)
    return {"access_token": jwt.encode({"sub": "foo"}, "secret")}


@app.get("/.well-known/jwks.json")
async def jwks():
    KEYS = {"keys": [settings.jwk_pubkey]}
    return KEYS


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_dirs=[HERE],
    )
