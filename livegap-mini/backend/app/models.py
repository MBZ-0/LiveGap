from enum import Enum
from typing import List
from pydantic import BaseModel


class Goal(str, Enum):
    TALK_TO_SALES = "I’m trying to talk to sales — can you help me reach the sales team?"
    PRICING = "Can you show me the pricing or plans for this company?"
    SIGN_UP = "How do I create an account or get started?"
    HELP = "Where can I find documentation or help resources?"
    CUSTOMERS = "Can you show me what customers say about this product?"


class RunRequest(BaseModel):
    goal: Goal


class Step(BaseModel):
    index: int
    action: str
    target: str | None = None
    observation: str | None = None
    reasoning: str | None = None
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
    report: str | None = None  # human-readable markdown report


class RunResponse(BaseModel):
    goal: Goal
    overall_success_rate: float  # 0–100
    total_sites: int
    successful_sites: int
    failed_sites: int
    results: List[SiteResult]
