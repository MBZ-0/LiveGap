from enum import Enum
from typing import List
from pydantic import BaseModel


class Goal(str, Enum):
    SIGN_UP = "sign_up"
    BOOK_DEMO = "book_demo"
    ADD_TO_CART = "add_to_cart"
    EXTRACT_PRICING = "extract_pricing"


class RunMode(str, Enum):
    HEURISTIC = "heuristic"
    LLM = "llm"


class RunRequest(BaseModel):
    goal: Goal
    mode: RunMode = RunMode.HEURISTIC  # selects agent style
    # repo_url: Optional[str] = None  # reserved for future


class Step(BaseModel):
    index: int
    action: str
    target: str | None = None
    observation: str | None = None
    succeeded: bool | None = None
    done: bool = False


class SiteResult(BaseModel):
    site_id: str
    site_name: str
    url: str
    success: bool
    reason: str
    video_url: str | None = None
    steps: List[Step] | None = None  # populated in LLM mode


class RunResponse(BaseModel):
    goal: Goal
    mode: RunMode
    overall_success_rate: float  # 0–100
    total_sites: int
    successful_sites: int
    failed_sites: int
    results: List[SiteResult]
