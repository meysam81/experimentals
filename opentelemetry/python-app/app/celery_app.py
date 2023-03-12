import celery
from app.otel import CeleryInstrumentor
from app.settings import settings
from celery.signals import worker_process_init

celery_app = celery.Celery("tasks", broker=settings.CELERY_BROKER_URL)


@worker_process_init.connect(weak=False)
def init_celery_tracing(*args, **kwargs):
    CeleryInstrumentor().instrument()
