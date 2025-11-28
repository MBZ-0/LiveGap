from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from mangum import Mangum
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .models import RunRequest, RunResponse
from .agent import run_llm_agent_on_site
from .runner import Site, load_sites  # dataclass + loader

# Windows asyncio subprocess fix for Playwright (requires selector loop for subprocesses).
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

# Debug: print loop policy and loop implementation once at import.
try:
    loop = asyncio.get_event_loop()
    print(f"[another.ai] Event loop policy: {type(asyncio.get_event_loop_policy()).__name__}; loop: {type(loop).__name__}")
except Exception as _e:
    print(f"[another.ai] Could not introspect event loop: {_e!r}")

app = FastAPI(title="another.ai Mini API")

# API router with /api prefix to align with CloudFront path routing
api_router = APIRouter(prefix="/api")
# Serve recorded videos (webm files) as static content
try:
    from pathlib import Path
    videos_dir = Path(__file__).with_name("videos")
    if videos_dir.exists():
        app.mount("/videos", StaticFiles(directory=str(videos_dir)), name="videos")
except Exception as _mount_err:
    print(f"[another.ai] Warning: could not mount /videos static directory: {_mount_err!r}")

# CORS: allow local dev + Amplify/etc.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can lock this down later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}

@api_router.get("/health")
async def api_health():
    return {"status": "ok"}


@app.post("/run-reality-check", response_model=RunResponse)
@api_router.post("/run-reality-check", response_model=RunResponse)
async def run_reality_check_endpoint(req: RunRequest):
    # Single LLM agent mode only (heuristic removed)
    try:
        print(f"[API] Starting reality check for goal: {req.goal}")
        sites = load_sites()
        # Limit sites for testing if env var is set
        max_sites = int(os.getenv("MAX_SITES", "0"))
        if max_sites > 0:
            sites = sites[:max_sites]
            print(f"[API] Limited to first {max_sites} sites for testing")
        results = []
        for idx, site in enumerate(sites, 1):
            print(f"[API] Processing site {idx}/{len(sites)}: {site.id}")
            r = await run_llm_agent_on_site(site, req.goal)
            results.append(r)

        total = len(results)
        successes = sum(1 for r in results if r.success)
        failed = total - successes
        success_rate = (successes / total * 100.0) if total > 0 else 0.0

        response = RunResponse(
            goal=req.goal,
            overall_success_rate=success_rate,
            total_sites=total,
            successful_sites=successes,
            failed_sites=failed,
            results=results,
        )
        print(f"[API] Completed reality check. Success rate: {success_rate:.1f}% ({successes}/{total})")
        print(f"[API] Response contains {len(results)} results")
        # Check response size
        import json
        response_json = response.model_dump_json()
        print(f"[API] Response size: {len(response_json)} bytes ({len(response_json)/1024:.1f} KB)")
        return response
    except Exception as e:
        print(f"[API] ERROR in run_reality_check_endpoint: {e!r}")
        import traceback
        traceback.print_exc()
        raise


# For AWS Lambda
app.include_router(api_router)

handler = Mangum(app)
