from prometheus_client import make_asgi_app, Summary, Counter, Gauge

REQUEST_DURATION = Summary(
    "request_duration_seconds",
    "Time spent processing requests",
    ["method", "endpoint"],
)

REQUEST_COUNT = Counter(
    "request_total",
    "Total request count",
    ["method", "endpoint", "status"],
)

IN_FLIGHT = Gauge(
    "in_flight_requests",
    "Number of in-flight requests",
    ["method", "endpoint"],
)

MODEL_LATENCY = Summary(
    "model_latency_seconds",
    "Time spent in model prediction",
    ["endpoint"],
)

def setup_prometheus(app):
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)