from meysam_utils import BaseSettings


class Settings(BaseSettings):
    WEB_FASTAPI1_NAME: str = "otel-demo-web-fastapi1"
    WEB_FASTAPI2_NAME: str = "otel-demo-web-fastapi2"
    WEB_FLASK_NAME: str = "otel-demo-web-flask"
    WORKER_CELERY_NAME: str = "otel-demo-worker-celery"
    WORKER_DRAMATIQ_NAME: str = "otel-demo-worker-dramatiq"
    PORT_FASTAPI1: int = 42000
    PORT_FASTAPI2: int = 42100
    PORT_FLASK: int = 42200
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    DRAMATIQ_BROKER_URL: str = "redis://localhost:6379/1"
    MONGO_CONNECTION_URI: str = "mongodb://localhost:27017/otel?authSource=admin"
    MONGO_DATABASE_NAME: str = "otel"
    OTLP_EXPORTER_ENDPOINT: str = "http://localhost:4317"


settings = Settings()
