import asyncio
import os
import time
from pathlib import Path
from typing import List, Dict, Any

from playwright.async_api import async_playwright

from .models import Goal, Step, SiteResult
from .runner import Site
from .llm import plan_next_action, classify_success
from .url_matcher import normalize_url


def render_report(site: Site, goal: Goal, result: SiteResult) -> str:
    """Produce a human-readable markdown narrative of the agent's attempt."""
    lines: list[str] = []
    lines.append(f"# {site.name} — Goal: {goal.value}")
    lines.append(f"**Final Result:** {'SUCCESS' if result.success else 'FAILURE'}")
    lines.append("")
    for step in (result.steps or []):
        lines.append(f"### Step {step.index + 1}")
        lines.append(f"**Action:** {step.action}")
        if step.target:
            lines.append(f"**Target:** {step.target}")
        lines.append(f"**Observation:** {step.observation or 'No observation recorded'}")
        if step.succeeded is True:
            lines.append("**Success check:** true — goal achieved here")
        elif step.succeeded is False:
            lines.append("**Success check:** false")
        else:
            lines.append("**Success check:** not yet")
        lines.append("")
    if result.success:
        lines.append("### 🎉 Reached success URL:")
        lines.append(f"`{result.reason}`")
    else:
        lines.append("### ⚠ Why it failed:")
        lines.append(result.reason)
    return "\n".join(lines)

MAX_STEPS = int(os.getenv("LLM_MAX_STEPS", "8"))
MAX_SECONDS = int(os.getenv("AGENT_MAX_SECONDS", "30"))  # hard wall for run duration
NAV_TIMEOUT_MS = int(os.getenv("AGENT_NAV_TIMEOUT", "15000"))  # initial navigation cap


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
            start_time = time.monotonic()
            try:
                await page.goto(site.url, timeout=NAV_TIMEOUT_MS)
            except Exception as _nav_err:
                print(f"[Agent] Navigation issue: {_nav_err.__class__.__name__}: {_nav_err}")
                if time.monotonic() - start_time >= MAX_SECONDS:
                    reason = f"Time limit ({MAX_SECONDS}s) reached during initial navigation"
                    success = False
                    result_obj = SiteResult(
                        site_id=site.id,
                        site_name=site.name,
                        url=site.url,
                        success=success,
                        reason=reason,
                        video_url=None,
                        steps=steps or None,
                    )
                    try:
                        result_obj.report = render_report(site, goal, result_obj)
                    except Exception:
                        pass
                    return result_obj

            recent: List[Dict[str, Any]] = []
            last_scroll_amt = 800

            for i in range(MAX_STEPS):
                # Enforce global time limit prior to planning next action
                elapsed = time.monotonic() - start_time
                if elapsed >= MAX_SECONDS:
                    reason = f"Time limit ({MAX_SECONDS}s) reached"
                    print(f"[Agent] Halting at step {i} due to time limit; elapsed={elapsed:.2f}s")
                    break
                body_text = await page.locator("body").inner_text(timeout=5000)
                body_text = _safe_text(body_text)

                plan = plan_next_action(goal, page.url, body_text, recent, i, MAX_STEPS)
                action = (plan.get("action") or "SCROLL").upper()
                target = plan.get("target")
                plan_reason = plan.get("reason") or ""

                observation = ""

                if action == "CLICK":
                    locator = page.get_by_text(str(target), exact=False).first if target else None
                    try:
                        if locator:
                            await locator.scroll_into_view_if_needed()
                            box = await locator.bounding_box()
                            if box:
                                x = box["x"] + box["width"] / 2
                                y = box["y"] + box["height"] / 2
                                await page.mouse.move(x, y)
                                await page.wait_for_timeout(150)
                                # Temporary outline highlight
                                try:
                                    await locator.evaluate("el => { el.style.outline = '3px solid red'; el.style.transition='outline 0.25s'; setTimeout(()=>{el.style.outline='';},800); }")
                                except Exception:
                                    pass
                                await page.mouse.down()
                                await page.mouse.up()
                            else:
                                # Fallback if no bounding box
                                await locator.click(timeout=4000)
                            await page.wait_for_timeout(600)
                            observation = f"Clicked '{str(target)[:50]}'"
                        else:
                            observation = "CLICK failed: no target locator"
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
                    # Enhanced TYPE support with highlight and cursor movement
                    try:
                        inputs = page.locator("input")
                        chosen = None
                        count = await inputs.count()
                        if count:
                            # Attempt placeholder match first
                            for idx in range(min(count, 12)):
                                handle = inputs.nth(idx)
                                try:
                                    placeholder = await handle.get_attribute("placeholder")
                                except Exception:
                                    placeholder = None
                                if placeholder and target and str(target).lower() in placeholder.lower():
                                    chosen = handle
                                    break
                            if chosen is None:
                                chosen = inputs.first
                        if chosen and await chosen.count() > 0:
                            await chosen.scroll_into_view_if_needed()
                            box = await chosen.bounding_box()
                            if box:
                                x = box["x"] + box["width"] / 2
                                y = box["y"] + box["height"] / 2
                                await page.mouse.move(x, y)
                                await page.wait_for_timeout(120)
                            try:
                                await chosen.evaluate("el => { el.style.outline='3px solid blue'; el.style.transition='outline 0.25s'; setTimeout(()=>{el.style.outline='';},1000); }")
                            except Exception:
                                pass
                            await chosen.fill(str(target)[:80])
                            observation = f"Typed '{str(target)[:30]}'"
                        else:
                            observation = "No input found"
                    except Exception as e:
                        observation = f"TYPE failed: {e.__class__.__name__}"
                elif action == "DONE":
                    reason = plan_reason or "Planner indicated DONE"
                    steps.append(Step(index=i, action=action, target=target, observation=reason, reasoning=plan_reason, succeeded=None, done=True))
                    print(f"[Agent] step={i} action={action} target={target} done=True")
                    break
                else:
                    observation = f"Unknown action {action}; treating as NOOP"

                # Success heuristic mid-loop
                success_mid = await classify_success(page, goal, site.id)
                step_obj = Step(index=i, action=action, target=target, observation=observation or plan_reason, reasoning=plan_reason, succeeded=success_mid, done=success_mid)
                steps.append(step_obj)
                print(f"[Agent] step={i} action={action} target={target} success={success_mid}")
                if success_mid:
                    success = True
                    reason = normalize_url(page.url)
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
        # Distinguish cause: time vs steps (time handled earlier)
        reason = "Max steps exhausted without success"

    result_obj = SiteResult(
        site_id=site.id,
        site_name=site.name,
        url=site.url,
        success=success,
        reason=reason,
        video_url=video_url,
        steps=steps or None,
    )
    try:
        result_obj.report = render_report(site, goal, result_obj)
    except Exception as _e:
        print(f"[Agent] Failed to render report for {site.id}: {_e!r}")
    return result_obj

__all__ = ["run_llm_agent_on_site"]
