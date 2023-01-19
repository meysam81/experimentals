from pydantic import BaseSettings, root_validator


class Settings(BaseSettings):
    KRATOS_PUBLIC_URL: str = "http://127.0.0.1:4433"

    KRATOS_LOGIN_BROWSER_URI: str = "/self-service/login/browser"
    KRATOS_LOGIN_FLOW_URI: str = "/self-service/login/flows"

    KRATOS_VERIFICATION_BROWSER_URI: str = "/self-service/verification/browser"
    KRATOS_VERIFICATION_FLOW_URI: str = "/self-service/verification/flows"

    KRATOS_REGISTRATION_BROWSER_URI: str = "/self-service/registration/browser"

    KRATOS_LOGOUT_BROWSER_URI: str = "/self-service/logout/browser"

    KRATOS_RECOVERY_BROWSER_URI: str = "/self-service/recovery/browser"
    KRATOS_RECOVERY_FLOW_URI: str = "/self-service/recovery/flows"

    KRATOS_SETTINGS_BROWSER_URI: str = "/self-service/settings/browser"
    KRATOS_SETTINGS_FLOW_URI: str = "/self-service/settings/flows"

    KRATOS_WHOAMI_URI: str = "/sessions/whoami"

    LOGIN_URI: str = "/login"
    VERIFICATION_URI: str = "/verification"
    REGISTRATION_URI: str = "/registration"
    LOGOUT_URI: str = "/logout"
    RECOVERY_URI: str = "/recovery"

    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 4455
    DEBUG: bool = True

    @root_validator
    def validate_settings(cls, values):
        if values["DEBUG"]:
            values["LOG_LEVEL"] = "DEBUG"
        return values


settings = Settings()
