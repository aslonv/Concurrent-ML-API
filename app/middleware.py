import time
import structlog
from fastapi import Request
from .prometheus import REQUEST_DURATION, REQUEST_COUNT, IN_FLIGHT

logger = structlog.get_logger("middleware")

async def monitoring_middleware(request: Request, call_next):
    start_time = time.time()
    method = request.method
    endpoint = request.url.path

    logger.info(
        "request_started",
        method=method,
        endpoint=endpoint,
        client_ip=request.client.host if request.client else "unknown",
    )
    
    IN_FLIGHT.labels(method=method, endpoint=endpoint).inc()

    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        logger.error(
            "request_failed",
            error=str(e),
            method=method,
            endpoint=endpoint,
        )
        raise
    finally:
        duration = time.time() - start_time
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=str(status_code)).inc()
        IN_FLIGHT.labels(method=method, endpoint=endpoint).dec()
    
    logger.info("request_ended", duration=duration, status_code=status_code)
    return response