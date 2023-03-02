from pathlib import Path

import fastapi
import httpx
from app.celery_app import celery_app
from app.dramatiq_app import Message
from app.dramatiq_app import broker as dramatiq_broker
from app.otel import (
    FastAPIInstrumentor,
    RedisInstrumentor,
    get_meter_provider,
    get_propagator,
    get_trace_provider,
)
from app.settings import settings

app = fastapi.FastAPI()


service_name = settings.WEB_FASTAPI1_NAME

tracer = get_trace_provider(service_name).get_tracer(__name__)
meter = get_meter_provider(service_name).get_meter(__name__)
propagator = get_propagator()

total_requests = meter.create_counter(
    name="total_requests",
    description="Total requests",
    unit="1",
)


FastAPIInstrumentor.instrument_app(app)
RedisInstrumentor().instrument()


@app.get("/")
async def index(name: str | None = "World"):
    total_requests.add(1, {"name": name})
    with tracer.start_as_current_span("web.index") as span:
        span.set_attribute("name", name)

        context = {}
        propagator.inject(context)

        celery_app.send_task("hello", args=[name], kwargs={"context": context})

        dramatiq_broker.enqueue(
            Message(
                queue_name="default",
                actor_name="hello",
                args=[name],
                kwargs={"context": context},
                options={},
            )
        )

        async with httpx.AsyncClient(
            base_url=f"http://{settings.HOST}:{settings.PORT_FASTAPI2}",
            headers=context,
        ) as client:
            response = await client.get("/", params={"name": name})
            span.set_attribute("fastapi2.status_code", response.status_code)
            response.raise_for_status()

        async with httpx.AsyncClient(
            base_url=f"http://{settings.HOST}:{settings.PORT_FLASK}",
            headers=context,
        ) as client:
            response = await client.get("/", params={"name": name})
            span.set_attribute("flask.status_code", response.status_code)
            response.raise_for_status()

        return {"message": f"hello {name}"}


if __name__ == "__main__":
    import uvicorn

    HERE = Path(__file__).parent
    uvicorn.run(
        "web:app",
        host="0.0.0.0",
        port=settings.PORT_FASTAPI1,
        reload=settings.DEBUG,
        reload_dirs=[HERE],
    )
