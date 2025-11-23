from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from mangum import Mangum
import asyncio
import sys

from .models import RunRequest, RunResponse, RunMode
from .runner import run_reality_check
from .agent import run_llm_agent_on_site
from .runner import Site  # dataclass reuse

# Windows asyncio subprocess fix for Playwright (requires selector loop for subprocesses).
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

# Debug: print loop policy and loop implementation once at import.
try:
    loop = asyncio.get_event_loop()
    print(f"[LiveGap] Event loop policy: {type(asyncio.get_event_loop_policy()).__name__}; loop: {type(loop).__name__}")
except Exception as _e:
    print(f"[LiveGap] Could not introspect event loop: {_e!r}")

app = FastAPI(title="LiveGap Mini API")
# Serve recorded videos (webm files) as static content
try:
    from pathlib import Path
    videos_dir = Path(__file__).with_name("videos")
    if videos_dir.exists():
        app.mount("/videos", StaticFiles(directory=str(videos_dir)), name="videos")
except Exception as _mount_err:
    print(f"[LiveGap] Warning: could not mount /videos static directory: {_mount_err!r}")

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


@app.post("/run-reality-check", response_model=RunResponse)
async def run_reality_check_endpoint(req: RunRequest):
    if req.mode == RunMode.LLM:
        # LLM-driven agent loop (sequential for clarity)
        from .runner import load_sites
        sites = load_sites()
        results = []
        for site in sites:
            r = await run_llm_agent_on_site(site, req.goal)
            results.append(r)
    else:
        results = await run_reality_check(req.goal)

    total = len(results)
    successes = sum(1 for r in results if r.success)
    failed = total - successes
    success_rate = (successes / total * 100.0) if total > 0 else 0.0

    return RunResponse(
        goal=req.goal,
        mode=req.mode,
        overall_success_rate=success_rate,
        total_sites=total,
        successful_sites=successes,
        failed_sites=failed,
        results=results,
    )


# For AWS Lambda
handler = Mangum(app)
