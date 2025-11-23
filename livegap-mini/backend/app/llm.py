from typing import Tuple, Dict, Any, List
from .models import Goal
import os, json, re
import httpx


def judge_success_from_html(goal: Goal, html: str, url: str) -> Tuple[bool, str]:
    """
    v0 heuristic judge.
    Replace this with an LLM call later.
    Returns (success, reason).
    """
    lower_html = html.lower()

    if goal == Goal.EXTRACT_PRICING:
        keywords = ["pricing", "plans", "per month", "per user", "plan"]
        hits = [k for k in keywords if k in lower_html]
        if hits:
            return True, f"Found pricing-related keywords: {', '.join(hits[:3])}"
        return False, "Could not find pricing-related keywords."

    if goal == Goal.SIGN_UP:
        keywords = ["sign up", "signup", "create account", "get started", "start free"]
        hits = [k for k in keywords if k in lower_html]
        if hits:
            return True, f"Found signup-related CTA text: {', '.join(hits[:3])}"
        return False, "Could not locate a clear signup CTA."

    if goal == Goal.BOOK_DEMO:
        keywords = ["book a demo", "schedule a demo", "request a demo", "talk to sales"]
        hits = [k for k in keywords if k in lower_html]
        if hits:
            return True, f"Found demo-related CTA text: {', '.join(hits[:3])}"
        return False, "Could not find demo-booking related CTAs."

    if goal == Goal.ADD_TO_CART:
        keywords = ["add to cart", "add to bag", "checkout", "buy now"]
        hits = [k for k in keywords if k in lower_html]
        if hits:
            return True, f"Found ecommerce CTA text: {', '.join(hits[:3])}"
        return False, "Could not find obvious add-to-cart or checkout CTAs."

    return False, "Goal not recognized or not supported yet."


async def classify_success(page, goal: Goal) -> bool:
    """Very simple heuristic success detector based on current page URL/content.
    Replace later with real LLM reasoning.
    """
    url = page.url.lower()
    content = (await page.content()).lower()

    if goal == Goal.BOOK_DEMO:
        return any(k in url or k in content for k in ["calendly", "demo", "contact", "schedule"])
    if goal == Goal.EXTRACT_PRICING:
        return any(k in url or k in content for k in ["pricing", "plan", "plans", "subscription"])
    if goal == Goal.SIGN_UP:
        return any(k in url or k in content for k in ["signup", "sign-up", "register", "create-account", "createaccount"])
    if goal == Goal.ADD_TO_CART:
        return any(k in content for k in ["add to cart", "checkout", "buy now", "add to bag"]) or any(k in url for k in ["cart", "checkout"])
    return False


# --- LLM planner stubs ---

ACTION_SET = ["CLICK", "SCROLL", "TYPE", "DONE"]

def summarize_text(raw: str, max_chars: int = 800) -> str:
    cleaned = " ".join(raw.split())
    return cleaned[:max_chars]


def heuristic_plan(goal: Goal, page_url: str, page_text: str, recent_actions: List[Dict[str, Any]], step_index: int, max_steps: int) -> Dict[str, Any]:
    """Stub that imitates an LLM planner returning an action JSON.
    Replace with real LLM call; keep interface identical.
    """
    lower = page_text.lower()
    # Goal-specific click intents
    goal_to_keywords = {
        Goal.BOOK_DEMO: ["book a demo", "schedule a demo", "talk to sales", "request a demo", "demo"],
        Goal.EXTRACT_PRICING: ["pricing", "plans", "plan"],
        Goal.SIGN_UP: ["sign up", "signup", "create account", "get started"],
        Goal.ADD_TO_CART: ["add to cart", "buy now", "checkout"],
    }
    keywords = goal_to_keywords.get(goal, [])
    for kw in keywords:
        if kw in lower:
            return {"action": "CLICK", "target": kw, "reason": f"Found keyword '{kw}' in page text"}

    # If halfway through attempts and no keyword, try scroll
    if step_index < max_steps - 2:
        return {"action": "SCROLL", "target": "1000", "reason": "Scrolling to reveal more content"}

    # Final attempt: declare done failure
    return {"action": "DONE", "target": "fail", "reason": "No relevant keyword found after exploration"}


def _extract_json_object(text: str) -> Dict[str, Any] | None:
    """Attempt to extract first JSON object from a model response."""
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except Exception:
        return None


def openai_plan(goal: Goal, page_url: str, page_text: str, recent_actions: List[Dict[str, Any]], step_index: int, max_steps: int) -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
    if not api_key:
        return heuristic_plan(goal, page_url, page_text, recent_actions, step_index, max_steps)

    summary = summarize_text(page_text, max_chars=1200)
    recent_str = "; ".join(
        f"{ra.get('action')}({(ra.get('target') or '')[:40]})" for ra in recent_actions[-4:]
    ) or "(none)"
    prompt = (
        "You are controlling a browser. Choose the next action to achieve the goal.\n"
        f"Goal: {goal.value}\nURL: {page_url}\nRecent: {recent_str}\n"
        f"Page excerpt: {summary}\n"
        "Actions allowed: CLICK(text), SCROLL(amount_px), TYPE(text), DONE(reason).\n"
        "Respond ONLY with JSON: {\"action\":\"CLICK\",\"target\":\"Book a demo\",\"reason\":\"Found CTA\"}."
    )

    # Use minimal HTTP call to OpenAI Chat Completions (fallback if library not available)
    try:
        # Newer OpenAI API may use 'responses' or 'chat.completions'; try chat first.
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
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
        resp.raise_for_status()
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        parsed = _extract_json_object(content)
        if not parsed:
            return heuristic_plan(goal, page_url, page_text, recent_actions, step_index, max_steps)
        action = parsed.get("action")
        target = parsed.get("target")
        reason = parsed.get("reason", "")
        if action not in ACTION_SET:
            return heuristic_plan(goal, page_url, page_text, recent_actions, step_index, max_steps)
        return {"action": action, "target": target, "reason": reason or "LLM decision"}
    except Exception:
        return heuristic_plan(goal, page_url, page_text, recent_actions, step_index, max_steps)


def plan_next_action(goal: Goal, page_url: str, page_text: str, recent_actions: List[Dict[str, Any]], step_index: int, max_steps: int) -> Dict[str, Any]:
    """Planner selecting OpenAI if key present else heuristic."""
    return openai_plan(goal, page_url, page_text, recent_actions, step_index, max_steps)
