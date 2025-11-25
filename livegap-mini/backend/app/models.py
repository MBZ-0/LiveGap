from enum import Enum
from typing import List
from pydantic import BaseModel


class Goal(str, Enum):
    SALES_CONTACT = "I’m trying to talk to sales — can you help me get in touch with someone?"
    PRICING_INFO = "Can you find out how much this product costs?"
    ACCOUNT_CREATION = "How do I create an account on this website?"
    JOB_OPENINGS = "Where can I see job openings for this company?"
    SUPPORT_HELP = "Where do I go if I need help or support on this website?"


class RunRequest(BaseModel):
    goal: Goal
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
    overall_success_rate: float  # 0–100
    total_sites: int
    successful_sites: int
    failed_sites: int
    results: List[SiteResult]
