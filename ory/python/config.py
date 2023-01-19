from pydantic import BaseSettings


class Settings(BaseSettings):
    KRATOS_PUBLIC_URL: str = "http://127.0.0.1:4433"
    KRATOS_BROWSER_LOGIN_URI: str = "/self-service/login/browser"
    KRATOS_BROWSER_VERIFICATION_URI: str = "/self-service/verification/browser"
    KRATOS_BROWSER_REGISTRATION_URI: str = "/self-service/registration/browser"
    KRATOS_WHOAMI_URI: str = "/sessions/whoami"

    LOGIN_CALLBACK_URI: str = "/login/callback"
    VERIFICATION_CALLBACK_URI: str = "/verification/callback"
    REGISTRATION_CALLBACK_URI: str = "/registration/callback"

    LOG_LEVEL: str = "INFO"


settings = Settings()
