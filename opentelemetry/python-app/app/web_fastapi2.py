from pathlib import Path

import fastapi
import httpx
from app.mongo import db
from app.otel import (
    FastAPIInstrumentor,
    get_meter_provider,
    get_propagator,
    get_trace_provider,
    instrument,
)
from app.settings import settings
from fastapi import Request

app = fastapi.FastAPI()

service_name = settings.WEB_FASTAPI2_NAME


tracer = get_trace_provider(service_name).get_tracer(__name__)
meter = get_meter_provider(service_name).get_meter(__name__)
propagator = get_propagator()
instrument()

total_requests = meter.create_counter(
    name="total_requests",
    description="Total requests",
    unit="1",
)


FastAPIInstrumentor.instrument_app(app)


@app.get("/")
async def index(request: Request, name: str | None = "World"):
    context = propagator.extract(request.headers)

    total_requests.add(1, {"name": name})
    with tracer.start_as_current_span("web2.index", context=context) as span:
        record = db.names.find_one({"name": name})
        count = record["count"] if record else 0

        span.set_attributes({"name": name, "current_count": count})

        async with httpx.AsyncClient(base_url="https://httpbin.org") as client:
            response = await client.get("/headers")
            span.set_attribute("httpbin.status_code", response.status_code)

        return {"message": f"hello {name}"}


if __name__ == "__main__":
    import uvicorn

    HERE = Path(__file__).parent
    uvicorn.run(
        "web2:app",
        host="0.0.0.0",
        port=settings.PORT_FASTAPI2,
        reload=settings.DEBUG,
        reload_dirs=[HERE],
    )
