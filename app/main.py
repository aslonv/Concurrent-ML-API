## Copyright 2025 Begali Aslonov
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import asyncio
import time
import structlog
from .model import SingletonModel
from .config import settings
from .prometheus import setup_prometheus, MODEL_LATENCY
from .middleware import monitoring_middleware

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
logger = structlog.get_logger("api")

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

app.middleware("http")(monitoring_middleware)
setup_prometheus(app)

model = SingletonModel()

class PredictionRequest(BaseModel):
    question: str
    is_philosophy_related: bool
    metadata: dict | None = None

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Concurrent ML API!",
        "author": "Bekali Aslonov"
    }

@app.post("/predict")
@limiter.limit("100/hour")
async def predict(request: Request, data: PredictionRequest):
    start_time = time.time()
    try:
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(model._executor, model.predict, data.dict()),
            timeout=settings.model_timeout,
        )
        duration = time.time() - start_time
        MODEL_LATENCY.labels(endpoint="/predict").observe(duration)
        logger.info(
            "prediction_success",
            duration=duration,
            question=data.question,
        )
        return result
    except asyncio.TimeoutError:
        duration = time.time() - start_time
        logger.warning("prediction_timeout", duration=duration)
        raise HTTPException(504, "Model response timeout")
    except ValidationError as e:
        duration = time.time() - start_time
        logger.error("validation_error", error=str(e), duration=duration)
        raise HTTPException(422, detail=e.errors())
    except Exception as e:
        duration = time.time() - start_time
        logger.error("prediction_failed", error=str(e), duration=duration)
        raise HTTPException(500, "Internal server error")

@app.get("/health")
async def health():
    logger.debug("health_check")
    return {"status": "healthy"}