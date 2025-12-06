import time
import httpx
from fastapi import APIRouter

router = APIRouter()
SERVICE_NAME = "api_gateway"

async def _check_http(url: str, timeout: float = 0.8):
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=timeout) as c:
            r = await c.get(url)
        if r.status_code == 200:
            return {"status": "ok", "latency_ms": int((time.time()-start)*1000)}
        return {"status": "degraded", "status_code": r.status_code}
    except Exception as e:
        return {"status": "down", "error": str(e)}

@router.get("/live")
async def live():
    return {"status":"ok","service":SERVICE_NAME,"ts":time.time()}

@router.get("/ready")
async def ready():
    # API Gateway depends on Redis for load tracking
    from fastapi.responses import JSONResponse
    try:
        from redis import Redis
        import os
        redis_host = os.getenv("REDIS_HOST", "redis")
        r = Redis(host=redis_host, port=6379, decode_responses=True, socket_connect_timeout=1)
        r.ping()
        checks = {"redis": {"status": "ok"}}
        return JSONResponse(content={"status": "ok", "checks": checks, "service": SERVICE_NAME}, status_code=200)
    except Exception as e:
        checks = {"redis": {"status": "down", "error": str(e)}}
        return JSONResponse(content={"status": "down", "checks": checks, "service": SERVICE_NAME}, status_code=503)
