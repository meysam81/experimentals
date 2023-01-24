import sys
from base64 import b64decode
from pathlib import Path

import jwt
from fastapi import Cookie, FastAPI, Header, Query, Request, Response

app = FastAPI()

HERE = Path(__file__).parent


@app.get("/cookie")
async def cookie_(request: Request, session: str = Cookie("")):
    passing = session == "valid"
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


# an endpoint for the jwks endpoint
@app.get("/.well-known/jwks.json")
async def jwks():
    return {
        "keys": [
            {
                "kty": "oct",
                "alg": "HS256",
                "use": "sig",
                "kid": "valid",
                "k": "c2VjcmV0",
            },
            {
                "kty": "oct",
                "alg": "HS256",
                "use": "sig",
                "kid": "invalid",
                "k": "c2VjcmV0",
            },
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=9200, reload=True, reload_dirs=[HERE])
