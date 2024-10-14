from pathlib import Path

from meysam_utils import BaseSettings, generate_random_string, root_validator


class Settings(BaseSettings):
    APP_NAME: str = "Kratos Client"
    APP_FULL_HOST: str | None

    KRATOS_PUBLIC_URL: str = "http://127.0.0.1:4433"

    KRATOS_LOGIN_BROWSER_URI: str = "/self-service/login/browser"
    KRATOS_LOGIN_FLOW_URI: str = "/self-service/login/flows"

    KRATOS_VERIFICATION_BROWSER_URI: str = "/self-service/verification/browser"
    KRATOS_VERIFICATION_FLOW_URI: str = "/self-service/verification/flows"

    KRATOS_REGISTRATION_BROWSER_URI: str = "/self-service/registration/browser"
    KRATOS_REGISTRATION_FLOW_URI: str = "/self-service/registration/flows"

    KRATOS_LOGOUT_BROWSER_URI: str = "/self-service/logout/browser"

    KRATOS_RECOVERY_BROWSER_URI: str = "/self-service/recovery/browser"
    KRATOS_RECOVERY_FLOW_URI: str = "/self-service/recovery/flows"

    KRATOS_SETTINGS_BROWSER_URI: str = "/self-service/settings/browser"
    KRATOS_SETTINGS_FLOW_URI: str = "/self-service/settings/flows"

    KRATOS_WHOAMI_URI: str = "/sessions/whoami"

    INDEX_URI: str = "/"
    LOGIN_URI: str = "/login"
    OAUTH2_LOGIN_URI: str = "/oauth2/login"
    OAUTH2_LOGIN_CALLBACK_URI: str = "/oauth2/login/callback"
    OAUTH2_CONSENT_URI: str = "/oauth2/consent"
    CONSENT_SUBMIT_METHOD: str = "POST"
    OAUTH2_CONSENT_CALLBACK_URI: str = "/oauth2/consent"
    VERIFICATION_URI: str = "/verification"
    REGISTRATION_URI: str = "/registration"
    LOGOUT_URI: str = "/logout"
    RECOVERY_URI: str = "/recovery"
    SETTINGS_URI: str = "/settings"
    ERROR_URI: str = "/error"

    HYDRA_ADMIN_URL: str = "http://localhost:41100"
    HYDRA_PUBLIC_URL: str = "http://localhost:41101"
    HYDRA_LOGIN_ACCEPT_URI: str = "/admin/oauth2/auth/requests/login/accept"
    HYDRA_LOGIN_REJECT_URI: str = "/admin/oauth2/auth/requests/login/reject"
    HYDRA_CONSENT_REQUEST_URI: str = "/admin/oauth2/auth/requests/consent"
    HYDRA_CONSENT_ACCEPT_URI: str = "/admin/oauth2/auth/requests/consent/accept"
    HYDRA_CONSENT_REJECT_URI: str = "/admin/oauth2/auth/requests/consent/reject"

    HYDRA_LOGIN_CHALLENGE_COOKIE_NAME: str = "kratos_client_hydra_login_challenge"

    CSRF_TOKEN_LENTGH: int = 32
    CSRF_ENCRYPTION_KEY_PATH: str = "/tmp/csrf_encryption_key"
    CSRF_ENCRYPTION_KEY: bytes | None
    CSRF_ENCRYPTION_KEY_SIZE: int = 32
    CSRF_ENCRYPTION_ALGORITHM: str = "AES"
    CSRF_TOKEN_COOKIE_NAME: str = "kratos_client_csrf_token"

    OAUTH2_CLIENT_REMEMBER: bool = True
    OAUTH2_CLIENT_REMEMBER_FOR: int = 3600 * 24 * 30

    OAUTH2_CLIENT_SCOPE_COOKIE_NAME: str = "kratos_client_oauth2_client_scopes"
    OAUTH2_CLIENT_SCOPE_COOKIE_DELIMITER: str = ","

    @root_validator
    def validate_settings(cls, values):
        super().validate_settings(values)

        if not values["APP_FULL_HOST"]:
            values["APP_FULL_HOST"] = (
                f"{values['SCHEME']}://{values['HOST']}:{values['PORT']}"
            )

        if not values["CSRF_ENCRYPTION_KEY"]:
            key_path = Path(values["CSRF_ENCRYPTION_KEY_PATH"])

            if not (key_path.exists() and key_path.stat().st_size):
                csrf_key = generate_random_string(values["CSRF_ENCRYPTION_KEY_SIZE"])
                key_path.write_text(csrf_key)
            else:
                csrf_key = key_path.read_text()

            values["CSRF_ENCRYPTION_KEY"] = csrf_key.encode()

        return values


settings = Settings()
