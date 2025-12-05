import time
import asyncio
import httpx
from fastapi import APIRouter

router = APIRouter()
SERVICE_NAME = "mock_llm"

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
    # Mock LLM has no external dependencies
    from fastapi.responses import JSONResponse
    return JSONResponse(content={"status": "ok", "service": SERVICE_NAME}, status_code=200)
