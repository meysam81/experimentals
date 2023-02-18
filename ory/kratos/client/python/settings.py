from meysam_utils import BaseSettings, root_validator


class Settings(BaseSettings):
    APP_NAME: str = "Kratos Client"
    
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
    VERIFICATION_URI: str = "/verification"
    REGISTRATION_URI: str = "/registration"
    LOGOUT_URI: str = "/logout"
    RECOVERY_URI: str = "/recovery"
    SETTINGS_URI: str = "/settings"

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

    HYDRA_LOGIN_URL: str = "/oauth2/login"
    HYDRA_LOGIN_SUBMIT_URL: str = "/oauth2/login/callback"
    HYDRA_CONSENT_URL: str = "/oauth2/consent"
    HYDRA_STATE_LENGTH: int = 16
    HYDRA_REDIRECT_URI: str = "http://localhost:4455/oauth2/callback"
    HYDRA_CLIENT_ID: str = "0090f793-9831-4e5d-beed-df5c3f0dc64c"

    HYDRA_LOGIN_CHALLENGE_COOKIE_NAME: str = "hydra_login_challenge"
    HYDRA_FLOW_STATE_COOKIE_NAME: str = "hydra_flow_state"
    NEXT_LOCATION_COOKIE_NAME: str = "next_location"

    HOST: str = "localhost"

    @root_validator
    def validate_settings(cls, values):
        super().validate_settings(values)
        return values


settings = Settings()
