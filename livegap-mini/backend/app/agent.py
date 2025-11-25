import asyncio
import os
import time
from pathlib import Path
from typing import List, Dict, Any

from playwright.async_api import async_playwright

from .models import Goal, Step, SiteResult
from .runner import Site
from .llm import plan_next_action, classify_success

MAX_STEPS = int(os.getenv("LLM_MAX_STEPS", "8"))


def _safe_text(text: str | None, limit: int = 1400) -> str:
    if not text:
        return ""
    return " ".join(text.split())[:limit]


async def run_llm_agent_on_site(site: Site, goal: Goal) -> SiteResult:
    """Iterative LLM-driven planning loop using real browser (Playwright)."""
    steps: List[Step] = []
    success = False
    reason = "Not finished"
    video_url = None

    api_present = bool(os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY"))
    print(f"[Agent] Start site_id={site.id} goal={goal.value} openai_key_present={api_present}")

    videos_dir = Path(__file__).with_name("videos")
    videos_dir.mkdir(exist_ok=True)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(record_video_dir=str(videos_dir), viewport={"width":1280,"height":900})
            page = await context.new_page()
            await page.goto(site.url, timeout=60000)

            recent: List[Dict[str, Any]] = []
            last_scroll_amt = 800

            for i in range(MAX_STEPS):
                body_text = await page.locator("body").inner_text(timeout=5000)
                body_text = _safe_text(body_text)

                plan = plan_next_action(goal, page.url, body_text, recent, i, MAX_STEPS)
                action = (plan.get("action") or "SCROLL").upper()
                target = plan.get("target")
                plan_reason = plan.get("reason") or ""

                observation = ""

                if action == "CLICK":
                    # Use text target; fallback to partial match
                    locator = page.get_by_text(str(target), exact=False).first
                    try:
                        await locator.click(timeout=4000)
                        await page.wait_for_timeout(600)
                        observation = f"Clicked text≈{str(target)[:50]}"
                    except Exception as e:
                        observation = f"CLICK failed: {e.__class__.__name__}"
                elif action == "SCROLL":
                    try:
                        amt = int(target) if target and str(target).isdigit() else last_scroll_amt
                    except Exception:
                        amt = last_scroll_amt
                    if steps and steps[-1].action == "SCROLL":
                        amt = int(amt * 1.4)  # escalate repeated scroll
                    last_scroll_amt = amt
                    await page.mouse.wheel(0, amt)
                    await page.wait_for_timeout(300)
                    observation = f"Scrolled {amt}px"
                elif action == "TYPE":
                    # Minimal TYPE support: try first input
                    try:
                        first_input = page.locator("input").first
                        if await first_input.count() > 0:
                            await first_input.fill(str(target)[:80])
                            observation = f"Typed '{str(target)[:30]}'"
                        else:
                            observation = "No input found"
                    except Exception as e:
                        observation = f"TYPE failed: {e.__class__.__name__}"
                elif action == "DONE":
                    reason = plan_reason or "Planner indicated DONE"
                    steps.append(Step(index=i, action=action, target=target, observation=reason, succeeded=None, done=True))
                    print(f"[Agent] step={i} action={action} target={target} done=True")
                    break
                else:
                    observation = f"Unknown action {action}; treating as NOOP"

                # Success heuristic mid-loop
                success_mid = await classify_success(page, goal, site.id)
                step_obj = Step(index=i, action=action, target=target, observation=observation or plan_reason, succeeded=success_mid, done=success_mid)
                steps.append(step_obj)
                print(f"[Agent] step={i} action={action} target={target} success={success_mid}")
                if success_mid:
                    success = True
                    reason = f"Goal satisfied after {action}"
                    break

            # Capture video path
            try:
                if page.video:
                    raw = await page.video.path()
                    video_url = f"/videos/{Path(raw).name}"
            except Exception:
                video_url = None

            await context.close()
            await browser.close()
    except Exception as e:
        reason = f"Agent crashed: {e.__class__.__name__}: {e}" if reason == "Not finished" else reason
        success = False

    if not success and reason == "Not finished":
        reason = "Max steps exhausted without success"

    return SiteResult(
        site_id=site.id,
        site_name=site.name,
        url=site.url,
        success=success,
        reason=reason,
        video_url=video_url,
        steps=steps or None,
    )

__all__ = ["run_llm_agent_on_site"]
