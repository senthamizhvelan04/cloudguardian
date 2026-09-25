from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from starlette.responses import Response

from app.api.v1 import audit, aws, events, health, incidents
from app.config import get_settings
from app.logging_config import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

REQUESTS = Counter("cloudguardian_requests_total", "Total CloudGuardian API requests")

app = FastAPI(
    title="CloudGuardian API",
    version="1.0.1",
    description="AI-assisted CloudOps incident detection, diagnosis, controlled remediation and recovery verification.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(incidents.router)
app.include_router(aws.router)
app.include_router(events.router)
app.include_router(audit.router)

@app.middleware("http")
async def count_requests(request, call_next):
    response = await call_next(request)
    REQUESTS.inc()
    return response

@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/", include_in_schema=False)
def root():
    path = Path(__file__).resolve().parents[2] / "dashboard" / "index.html"
    return FileResponse(path) if path.exists() else {"service": "CloudGuardian", "docs": "/docs"}
