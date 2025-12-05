import time
import asyncio
import httpx
from fastapi import APIRouter

router = APIRouter()
SERVICE_NAME = "encoder_service"

REDIS_URL = "http://redis:6379"

async def _check_http(url: str, timeout: float = 0.8):
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=timeout) as c:
            r = await c.get(url)
        if r.status_code == 200:
            return {"status": "ok", "latency_ms": int((time.time() - start) * 1000)}
        return {"status": "degraded", "status_code": r.status_code}
    except Exception as e:
        return {"status": "down", "error": str(e)}

@router.get("/live")
async def live():
    return {"status": "ok", "service": SERVICE_NAME, "ts": time.time()}

@router.get("/ready")
async def ready():
    # Encoder depends on Redis for job queue
    from fastapi.responses import JSONResponse
    try:
        from redis import Redis
        import os
        redis_host = os.getenv("REDIS_HOST", "redis")
        r = Redis(host=redis_host, port=6379, decode_responses=True, socket_connect_timeout=1)
        r.ping()
        # Also check if model can load
        from sentence_transformers import SentenceTransformer
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        checks = {"redis": {"status": "ok"}, "model": {"status": "ok", "name": model_name}}
        return JSONResponse(content={"status": "ok", "checks": checks, "service": SERVICE_NAME}, status_code=200)
    except Exception as e:
        checks = {"redis": {"status": "down", "error": str(e)}}
        return JSONResponse(content={"status": "down", "checks": checks, "service": SERVICE_NAME}, status_code=503)
