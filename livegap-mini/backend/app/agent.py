import asyncio
import traceback
from typing import List, Dict, Any

from playwright.async_api import async_playwright

from .models import Goal, SiteResult, Step
from .llm import plan_next_action, classify_success

MAX_STEPS = 6

async def run_llm_agent_on_site(site, goal: Goal) -> SiteResult:
    steps: List[Step] = []
    success = False
    reason = "LLM agent did not start"
    video_url = None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(record_video_dir=str(site.__class__.__module__))  # fallback dir; actual videos handled by runner previously
            page = await context.new_page()
            await page.goto(site.url, timeout=60000)

            recent: List[Dict[str, Any]] = []
            for i in range(MAX_STEPS):
                text = await page.locator("body").inner_text()
                plan = plan_next_action(goal, page.url, text, recent, i, MAX_STEPS)
                action = plan.get("action")
                target = plan.get("target")
                obs_note = None

                if action == "CLICK" and target:
                    locator = page.get_by_text(target, exact=False).first
                    try:
                        await locator.click(timeout=4000)
                        await page.wait_for_timeout(800)
                        obs_note = f"Clicked '{target}'"
                    except Exception as e:
                        obs_note = f"Click failed: {e!r}"
                elif action == "SCROLL" and target:
                    try:
                        amount = int(target)
                    except Exception:
                        amount = 800
                    await page.mouse.wheel(0, amount)
                    await page.wait_for_timeout(400)
                    obs_note = f"Scrolled {amount} px"
                elif action == "TYPE":
                    # Attempt to type into first input matching target substring
                    inputs = page.locator('input').all()
                    chosen = None
                    for inp in inputs[:10]:
                        try:
                            placeholder = await inp.get_attribute('placeholder')
                        except Exception:
                            placeholder = None
                        if placeholder and target.lower() in placeholder.lower():
                            chosen = inp
                            break
                    if not chosen and inputs:
                        chosen = inputs[0]
                    if chosen:
                        try:
                            await chosen.fill(target[:80])
                            obs_note = f"Typed '{target[:30]}'"
                        except Exception as e:
                            obs_note = f"Type failed: {e!r}"
                    else:
                        obs_note = "No input field found"
                elif action == "DONE":
                    reason = plan.get("reason", "DONE")
                    # Await async success classifier to avoid coroutine assignment
                    success = await classify_success_stub(goal, page)
                    steps.append(Step(index=i, action=action, target=target, observation=reason, succeeded=success, done=True))
                    break

                # Evaluate success mid-loop (optional)
                if action != "DONE":
                    success_mid = await classify_success(page, goal)
                    if success_mid:
                        success = True
                        reason = f"Goal satisfied after {action} {target or ''}".strip()
                        steps.append(Step(index=i, action=action, target=target, observation=obs_note, succeeded=True, done=True))
                        break

                steps.append(Step(index=i, action=action, target=target, observation=obs_note, succeeded=None, done=False))
                recent.append({"action": action, "target": target, "observation": obs_note})
            else:
                # Max steps exhausted
                success = False
                reason = "Max steps exhausted without success"

            # Attempt to capture video path if supported (stub for now)
            try:
                if page.video:
                    raw_path = await page.video.path()
                    from pathlib import Path as _P
                    video_url = f"/videos/{_P(raw_path).name}"  # may not exist if different context dir
            except Exception:
                video_url = None

            await context.close()
            await browser.close()

    except Exception as e:
        tb = traceback.format_exc(limit=6)
        success = False
        reason = f"LLM agent crashed: {e!r} | {tb.splitlines()[-1]}"

    return SiteResult(
        site_id=site.id,
        site_name=site.name,
        url=site.url,
        success=success,
        reason=reason,
        video_url=video_url,
        steps=steps or None,
    )

# Simple stub to decide success at DONE if not already handled
async def classify_success_stub(goal: Goal, page):  # type: ignore
    # Reuse classify_success async version if needed
    from .llm import classify_success as _cs
    return await _cs(page, goal)
