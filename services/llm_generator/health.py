import time
import asyncio
import httpx
from fastapi import APIRouter

router = APIRouter()
SERVICE_NAME = "llm_generator"

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
    # LLM Generator depends on Redis and Mock LLM service
    from fastapi.responses import JSONResponse
    import os
    checks = {}
    
    # Check Redis
    try:
        from redis import Redis
        redis_host = os.getenv("REDIS_HOST", "redis")
        r = Redis(host=redis_host, port=6379, decode_responses=True, socket_connect_timeout=1)
        r.ping()
        checks["redis"] = {"status": "ok"}
    except Exception as e:
        checks["redis"] = {"status": "down", "error": str(e)}
    
    # Check Mock LLM service
    llm_url = os.getenv("LLM_SERVICE_URL", "http://mock_llm:8000")
    checks["mock_llm"] = await _check_http(f"{llm_url}/health")
    
    if any(c["status"] == "down" for c in checks.values()):
        return JSONResponse(content={"status": "down", "checks": checks, "service": SERVICE_NAME}, status_code=503)
    if any(c["status"] == "degraded" for c in checks.values()):
        return JSONResponse(content={"status": "degraded", "checks": checks, "service": SERVICE_NAME}, status_code=200)
    return JSONResponse(content={"status": "ok", "checks": checks, "service": SERVICE_NAME}, status_code=200)
