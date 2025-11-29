"""
In-memory store for tracking background reality check runs.
For production, consider using a database (PostgreSQL, Redis, etc.)
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict
from .models import RunResponse

@dataclass
class RunRecord:
    id: str
    created_at: datetime
    status: str  # "pending" | "running" | "done" | "error"
    result: Optional[RunResponse] = None
    error: Optional[str] = None

# Global in-memory storage (not suitable for multi-worker deployments)
RUNS: Dict[str, RunRecord] = {}

def to_dict(run: RunRecord) -> dict:
    """Convert RunRecord to JSON-serializable dict"""
    d = {
        "id": run.id,
        "created_at": run.created_at.isoformat(),
        "status": run.status,
    }
    if run.result:
        d["result"] = run.result.model_dump()
    if run.error:
        d["error"] = run.error
    return d

def create_run(run_id: str) -> RunRecord:
    """Create a new run record in pending state"""
    run = RunRecord(
        id=run_id,
        created_at=datetime.utcnow(),
        status="pending",
    )
    RUNS[run_id] = run
    return run

def get_run(run_id: str) -> Optional[RunRecord]:
    """Retrieve a run record by ID"""
    return RUNS.get(run_id)

def update_run_status(run_id: str, status: str, result: Optional[RunResponse] = None, error: Optional[str] = None):
    """Update run status and result/error"""
    if run_id in RUNS:
        RUNS[run_id].status = status
        if result:
            RUNS[run_id].result = result
        if error:
            RUNS[run_id].error = error

def get_all_runs() -> list[RunRecord]:
    """Get all runs, sorted by creation time (newest first)"""
    return sorted(RUNS.values(), key=lambda r: r.created_at, reverse=True)
