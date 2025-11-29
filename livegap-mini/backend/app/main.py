from fastapi import FastAPI, APIRouter, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from mangum import Mangum
import asyncio
import sys
import os
from uuid import uuid4
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .models import RunRequest, RunResponse
from .agent import run_llm_agent_on_site
from .runner import Site, load_sites  # dataclass + loader
from .runs_store import create_run, get_run, update_run_status, to_dict, get_all_runs

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


# Background task function to process the reality check
async def process_reality_check(run_id: str, goal):
    """Run the reality check in the background"""
    try:
        print(f"[API] Starting reality check for run_id={run_id} goal={goal}")
        update_run_status(run_id, "running")
        
        sites = load_sites()
        # Limit sites for testing if env var is set
        max_sites = int(os.getenv("MAX_SITES", "0"))
        if max_sites > 0:
            sites = sites[:max_sites]
            print(f"[API] Limited to first {max_sites} sites for testing")
        
        # Run sites in parallel with concurrency limit
        max_concurrent = int(os.getenv("MAX_CONCURRENT_SITES", "3"))
        semaphore = asyncio.Semaphore(max_concurrent)
        print(f"[API] Running up to {max_concurrent} sites concurrently")

        async def run_for_site(idx: int, site: Site):
            async with semaphore:
                print(f"[API] Processing site {idx}/{len(sites)}: {site.id}")
                return await run_llm_agent_on_site(site, goal)

        # Run all sites concurrently (limited by semaphore)
        tasks = [run_for_site(idx, site) for idx, site in enumerate(sites, 1)]
        results = await asyncio.gather(*tasks)

        total = len(results)
        successes = sum(1 for r in results if r.success)
        failed = total - successes
        success_rate = (successes / total * 100.0) if total > 0 else 0.0

        response = RunResponse(
            goal=goal,
            overall_success_rate=success_rate,
            total_sites=total,
            successful_sites=successes,
            failed_sites=failed,
            results=list(results),
        )
        print(f"[API] Completed reality check run_id={run_id}. Success rate: {success_rate:.1f}% ({successes}/{total})")
        
        # Update run with result
        update_run_status(run_id, "done", result=response)
        
    except Exception as e:
        print(f"[API] ERROR in process_reality_check run_id={run_id}: {e!r}")
        import traceback
        traceback.print_exc()
        update_run_status(run_id, "error", error=str(e))


@app.post("/run-reality-check")
@api_router.post("/run-reality-check")
async def run_reality_check_endpoint(req: RunRequest, background_tasks: BackgroundTasks):
    """Start a reality check job in the background and return immediately"""
    run_id = str(uuid4())
    
    # Create run record
    run = create_run(run_id)
    print(f"[API] Created run_id={run_id} for goal={req.goal}")
    
    # Add background task
    background_tasks.add_task(process_reality_check, run_id, req.goal)
    
    # Return immediately
    return {
        "run_id": run_id,
        "status": "pending",
        "created_at": run.created_at.isoformat(),
    }


@app.get("/run/{run_id}")
@api_router.get("/run/{run_id}")
async def get_run_status(run_id: str):
    """Get the status of a reality check run"""
    run = get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return to_dict(run)


@app.get("/runs")
@api_router.get("/runs")
async def list_runs():
    """List all runs (for debugging/history)"""
    runs = get_all_runs()
    return {"runs": [to_dict(r) for r in runs]}


# For AWS Lambda
app.include_router(api_router)

handler = Mangum(app)
