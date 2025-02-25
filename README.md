# FastAPI Model Inference Service
This project implements a FastAPI-based HTTP service that interacts with a simulated large machine learning model. The model is slow (10-40 seconds per prediction) and resource-constrained to a single instance, requiring careful concurrency handling for multiple clients.

## Architecture
- Endpoint: /predict (POST) accepts JSON input and returns a mocked prediction.
- Concurrency: Managed via a ThreadPoolExecutor with one worker, ensuring serial model access.
- Observability: Structured logs with structlog and metrics via prometheus_client.
- Rate Limiting: Enforced with slowapi at 100 requests/hour per client.
- Deployment: Dockerized with a docker-compose.yml for app and Prometheus services.

## Setup
1. Prerequisites: Docker and Docker Compose installed.
2. Build: Run docker-compose build.
3. Run: Execute docker-compose up.
4. Access: API at http://localhost:8000, metrics at http://localhost:8000/metrics, Prometheus at http://localhost:9090.

## Usage
- Root Endpoint
```bash
curl http://localhost:8000
```

- Predict
```bash
Invoke-WebRequest -Uri "http://localhost:8000/predict" -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"question": "What is life?", "is_philosophy_related": true, "metadata": null}'
```

- Health
```bash
curl http://localhost:8000/health
```

## Monitoring
- Logs: JSON-formatted, viewable via docker-compose logs.
- Metrics: Exposed at /metrics, scraped by Prometheus.

## Notes
- MODEL_TIMEOUT in docker-compose.yml can be adjusted if needed.

The default CORS_ORIGINS = '*' allows any origin, which is insecure. Consider restricting origins to specific domains in production. Add a note in the README to modify CORS_ORIGINS for security.

