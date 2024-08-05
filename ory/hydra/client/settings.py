from pathlib import Path
from urllib.parse import urljoin

from meysam_utils import BaseSettings, generate_random_string, root_validator


class Settings(BaseSettings):
    APP_NAME: str = "Hydra Client"
    APP_FULL_HOST: str | None
    HOST: str = "localhost"

    HYDRA_ADMIN_URL: str = "http://localhost:41100"
    HYDRA_PUBLIC_URL: str = "http://localhost:41101"
    HYDRA_LOGIN_REQUEST_URL: str = "/admin/oauth2/auth/requests/login"
    HYDRA_LOGIN_ACCEPT_URL: str = "/admin/oauth2/auth/requests/login/accept"
    HYDRA_LOGIN_REJECT_URL: str = "/admin/oauth2/auth/requests/login/reject"
    HYDRA_CONSENT_REQUEST_URL: str = "/admin/oauth2/auth/requests/consent"
    HYDRA_CONSENT_ACCEPT_URL: str = "/admin/oauth2/auth/requests/consent/accept"
    HYDRA_CONSENT_REJECT_URL: str = "/admin/oauth2/auth/requests/consent/reject"
    HYDRA_OAUTH2_AUTH_URL: str = "/oauth2/auth"
    HYDRA_OAUTH2_TOKEN_URL: str = "/oauth2/token"

    COOKIE_ENCRYPTION_KEY_PATH: str = "/tmp/cookie_encryption_key"
    COOKIE_ENCRYPTION_KEY: bytes | None
    COOKIE_ENCRYPTION_KEY_SIZE: int = 32
    COOKIE_ENCRYPTION_ALGORITHM: str = "AES"

    INDEX_URL: str = "/"
    LOGIN_URL: str = "/oauth2/login"
    LOGIN_CALLBACK_URL: str = "/oauth2/callback"
    LOGIN_CALLBACK_SUCCESS_URL: str = "/oauth2/callback/success"
    ERROR_URL: str = "/error"

    HYDRA_FLOW_STATE_COOKIE_NAME: str = "hydra_client_flow_state"
    HYDRA_FLOW_ACCESS_TOKEN_COOKIE_NAME: str = "hydra_client_access_token"
    HYDRA_FLOW_REFRESH_TOKEN_COOKIE_NAME: str = "hydra_client_refresh_token"
    HYDRA_FLOW_ID_TOKEN_COOKIE_NAME: str = "hydra_client_id_token"

    HYDRA_FLOW_REQUIRED_SCOPE: str = "openid offline_access"
    HYDRA_FLOW_STATE_LENGTH: int = 16
    HYDRA_FLOW_RESPONSE_TYPE: str = "code"
    HYDRA_FLOW_REDIRECT_URL: str | None
    HYDRA_CLIENT_ID: str = "change-me"
    HYDRA_CLIENT_SECRET: str = "change-me"
    HYDRA_FLOW_GRANT_TYPE: str = "authorization_code"

    @root_validator(allow_reuse=True)
    def validate_settings(cls, values):
        super().validate_settings(values)

        if not values["COOKIE_ENCRYPTION_KEY"]:
            key_path = Path(values["COOKIE_ENCRYPTION_KEY_PATH"])

            if key_path.exists() and not key_path.is_file():
                raise ValueError(
                    f"COOKIE_ENCRYPTION_KEY_PATH: {key_path} is not a file"
                )

            if not (key_path.exists() and key_path.stat().st_size):
                cookie_key = generate_random_string(
                    values["COOKIE_ENCRYPTION_KEY_SIZE"]
                )
                key_path.write_text(cookie_key)
            else:
                cookie_key = key_path.read_text()

            values["COOKIE_ENCRYPTION_KEY"] = cookie_key.encode()

        if not values["APP_FULL_HOST"]:
            values["APP_FULL_HOST"] = (
                f"{values['SCHEME']}://{values['HOST']}:{values['PORT']}"
            )

        if not values["HYDRA_FLOW_REDIRECT_URL"]:
            values["HYDRA_FLOW_REDIRECT_URL"] = urljoin(
                values["APP_FULL_HOST"], values["LOGIN_CALLBACK_URL"]
            )

        return values


settings = Settings()
