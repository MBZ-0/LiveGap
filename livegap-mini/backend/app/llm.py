from typing import Tuple, Dict, Any, List
from .models import Goal
from .success_config import SUCCESS_URLS
from .url_matcher import normalize_url
import os, json, re
import httpx


# Keyword sets per new natural-language goal (used for heuristic success + planning hints).
GOAL_KEYWORDS: Dict[Goal, List[str]] = {
    Goal.SALES_CONTACT: [
        "sales", "contact sales", "talk to sales", "request a demo", "book a demo", "schedule a demo", "contact us"
    ],
    Goal.PRICING_INFO: [
        "pricing", "plans", "price", "cost", "per month", "per user", "pricing plan"
    ],
    Goal.ACCOUNT_CREATION: [
        "sign up", "signup", "create account", "register", "get started", "start free", "create your account"
    ],
    Goal.JOB_OPENINGS: [
        "careers", "jobs", "open positions", "we're hiring", "hiring", "join our team"
    ],
    Goal.SUPPORT_HELP: [
        "support", "help center", "help", "documentation", "docs", "knowledge base", "contact support"
    ],
}


def judge_success_from_html(goal: Goal, html: str, url: str) -> Tuple[bool, str]:
    lower_html = html.lower()
    hits = [k for k in GOAL_KEYWORDS.get(goal, []) if k in lower_html]
    if hits:
        return True, f"Found related cues: {', '.join(hits[:4])}"
    return False, "No obvious related cues detected"


async def classify_success(page, goal: Goal, site_id: str) -> bool:
    """Success if normalized current URL appears in normalized configured success URLs."""
    current = normalize_url(page.url)
    allowed = SUCCESS_URLS.get(site_id, {}).get(goal, [])
    normalized_allowed = [normalize_url(u) for u in allowed]
    return current in normalized_allowed


ACTION_SET = ["CLICK", "SCROLL", "TYPE", "DONE"]


def summarize_text(raw: str, max_chars: int = 800) -> str:
    cleaned = " ".join(raw.split())
    return cleaned[:max_chars]


def heuristic_plan(
    goal: Goal,
    page_url: str,
    page_text: str,
    recent_actions: List[Dict[str, Any]],
    step_index: int,
    max_steps: int,
) -> Dict[str, Any]:
    lower = page_text.lower()
    if step_index == 0:
        return {"action": "SCROLL", "target": "800", "reason": "Initial scan — scroll"}
    if step_index == 1:
        return {"action": "SCROLL", "target": "1600", "reason": "Broaden view"}
    for kw in GOAL_KEYWORDS.get(goal, []):
        if kw in lower:
            return {"action": "CLICK", "target": kw, "reason": f"Found keyword '{kw}'"}
    if step_index < max_steps - 1:
        return {"action": "SCROLL", "target": "1000", "reason": "Explore further"}
    return {"action": "DONE", "target": "fail", "reason": "No cues after multiple steps"}


def _extract_json_object(text: str) -> Dict[str, Any] | None:
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except Exception:
        return None


def openai_plan(
    goal: Goal,
    page_url: str,
    page_text: str,
    recent_actions: List[Dict[str, Any]],
    step_index: int,
    max_steps: int,
) -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        print("[LLM] No OPENAI_API_KEY present; falling back to heuristic planner.")
        return heuristic_plan(goal, page_url, page_text, recent_actions, step_index, max_steps)
    summary = summarize_text(page_text, max_chars=1200)
    recent_str = "; ".join(
        f"{ra.get('action')}({(ra.get('target') or '')[:40]})" for ra in recent_actions[-4:]
    ) or "(none)"
    prompt = (
        "You are controlling a browser to help a user. Choose the next action.\n"
        f"User goal (literal, do not alter): {goal.value}\nURL: {page_url}\nRecent: {recent_str}\n"
        f"Page excerpt: {summary}\n"
        "Allowed actions: CLICK(text), SCROLL(px), TYPE(text), DONE(reason).\n"
        "Respond ONLY with a single JSON object: {\"action\":\"CLICK\",\"target\":\"Book a demo\",\"reason\":\"Found CTA\"}"
    )
    print(f"[LLM] Calling OpenAI model={model} goal={goal.value} step={step_index}")
    try:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You output only JSON objects."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 120,
        }
        resp = httpx.post(
            os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1/chat/completions"),
            headers=headers,
            json=body,
            timeout=20.0,
        )
        print(f"[LLM] OpenAI response status={resp.status_code}")
        resp.raise_for_status()
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        parsed = _extract_json_object(content)
        if not parsed:
            print("[LLM] Parse failure -> heuristic fallback")
            return heuristic_plan(goal, page_url, page_text, recent_actions, step_index, max_steps)
        action = parsed.get("action")
        target = parsed.get("target")
        reason = parsed.get("reason", "")
        if action not in ACTION_SET:
            print(f"[LLM] Invalid action '{action}' -> heuristic fallback")
            return heuristic_plan(goal, page_url, page_text, recent_actions, step_index, max_steps)
        print(f"[LLM] Plan action={action} target={str(target)[:60]}")
        return {"action": action, "target": target, "reason": reason or "LLM decision"}
    except Exception as e:
        print(f"[LLM] Exception during OpenAI call: {e.__class__.__name__}: {e} -> heuristic fallback")
        return heuristic_plan(goal, page_url, page_text, recent_actions, step_index, max_steps)


def plan_next_action(goal: Goal, page_url: str, page_text: str, recent_actions: List[Dict[str, Any]], step_index: int, max_steps: int) -> Dict[str, Any]:
    """Single planner selecting OpenAI if key present else heuristic."""
    return openai_plan(goal, page_url, page_text, recent_actions, step_index, max_steps)
