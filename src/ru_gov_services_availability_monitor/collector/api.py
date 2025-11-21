from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from .storage import Storage, Metric

app = FastAPI(title="RU Gov Services Monitor Collector")

# Global storage instance (initialized in startup)
storage: Optional[Storage] = None


class MetricIn(BaseModel):
    service_id: str
    region_id: str
    timestamp: float
    status_code: Optional[int] = None
    latency_ms: float
    available: bool
    error: Optional[str] = None
    tls_info: Optional[Dict[str, Any]] = None


@app.on_event("startup")
def startup_event():
    global storage
    # In a real app, path comes from config
    storage = Storage("./data/monitor.db")


@app.post("/api/v1/metrics")
async def receive_metric(metric: MetricIn):
    if not storage:
        raise HTTPException(status_code=500, detail="Storage not initialized")

    storage.save_metric(
        Metric(
            service_id=metric.service_id,
            region_id=metric.region_id,
            timestamp=metric.timestamp,
            status_code=metric.status_code,
            latency_ms=metric.latency_ms,
            available=metric.available,
            error=metric.error,
            tls_info=metric.tls_info,
        )
    )
    return {"status": "ok"}


@app.get("/api/v1/metrics")
async def get_metrics(service_id: Optional[str] = None, limit: int = 100):
    if not storage:
        raise HTTPException(status_code=500, detail="Storage not initialized")
    return storage.get_metrics(service_id, limit)
