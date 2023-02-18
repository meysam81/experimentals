from meysam_utils import BaseSettings


class Settings(BaseSettings):
    HYDRA_ADMIN_URL: str = "http://localhost:41100/admin"
    HYDRA_PUBLIC_URL: str = "http://localhost:41101"
    HYDRA_LOGIN_REQUEST_URL: str = "/oauth2/auth/requests/login"
    HYDRA_LOGIN_ACCEPT_URL: str = "/oauth2/auth/requests/login/accept"
    HYDRA_LOGIN_REJECT_URL: str = "/oauth2/auth/requests/login/reject"
    HYDRA_CONSENT_REQUEST_URL: str = "/oauth2/auth/requests/consent"
    HYDRA_CONSENT_ACCEPT_URL: str = "/oauth2/auth/requests/consent/accept"
    HYDRA_CONSENT_REJECT_URL: str = "/oauth2/auth/requests/consent/reject"
    HYDRA_OAUTH2_AUTH_URL: str = "/oauth2/auth"
    HYDRA_OAUTH2_TOKEN_URL: str = "/oauth2/token"


config = Settings()
