import httpx
from app.mongo import db
from app.otel import get_meter_provider, get_propagator, get_trace_provider
from app.settings import settings
from flask import Flask, request
from opentelemetry.instrumentation.wsgi import OpenTelemetryMiddleware

tracer_provider = get_trace_provider(settings.WEB_FLASK_NAME)
meter_provider = get_meter_provider(settings.WEB_FLASK_NAME)

trace = tracer_provider.get_tracer(__name__)
meter = meter_provider.get_meter(__name__)
propagator = get_propagator()

app = Flask(__name__)
app.wsgi_app = OpenTelemetryMiddleware(
    app.wsgi_app, tracer_provider=tracer_provider, meter_provider=meter_provider
)


@app.route("/")
def hello():
    context = request.headers.get("context")
    if context:
        context = propagator.extract(context)

    with trace.start_as_current_span("flask.hello", context=context) as span:
        name = request.args.get("name", "World")
        span.set_attribute("name", name)

        record = db.names.find_one({"name": name})
        count = record["count"] if record else 0

        span.set_attributes({"name": name, "current_count": count})

        return f"Hello, {name}!"


if __name__ == "__main__":
    app.run(host=settings.HOST, port=settings.PORT_FASTAPI1, debug=settings.DEBUG)
