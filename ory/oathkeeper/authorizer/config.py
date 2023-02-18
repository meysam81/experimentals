from meysam_utils import BaseSettings, LogLevel, root_validator


class Settings(BaseSettings):
    LOG_LEVEL: LogLevel = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 9400
    DEBUG: bool = True

    @root_validator
    def validate_settings(cls, values):
        if values["DEBUG"]:
            values["LOG_LEVEL"] = "DEBUG"
        return values


settings = Settings()
