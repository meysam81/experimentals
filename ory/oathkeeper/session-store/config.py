import json

from meysam_utils import BaseSettings, LogLevel, root_validator


class Settings(BaseSettings):
    LOG_LEVEL: LogLevel = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 9200
    DEBUG: bool = True

    PUBKEY_PATH: str = "./keys/jwk.pub.json"
    PRIVKEY_PATH: str = "./keys/jwk.json"

    KRATOS_PUBLIC_URL: str = "http://127.0.0.1:4433"

    @root_validator
    def validate_settings(cls, values):
        super().validate_settings(values)
        return values

    @property
    def jwk_pubkey(self):
        with open(self.PUBKEY_PATH, "r") as f:
            return json.load(f)


settings = Settings()
