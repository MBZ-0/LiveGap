import json
import asyncio
import traceback
import uuid
import os
import sys
from pathlib import Path
from typing import List
from dataclasses import dataclass

from playwright.async_api import async_playwright

from .models import Goal, SiteResult
from .llm import classify_success


@dataclass
class Site:
    id: str
    name: str
    url: str


def load_sites() -> List[Site]:
    sites_path = Path(__file__).with_name("sites.json")
    data = json.loads(sites_path.read_text())
    return [Site(**item) for item in data]


VIDEO_DIR = Path(__file__).with_name("videos")
os.makedirs(VIDEO_DIR, exist_ok=True)

GOAL_KEYWORDS = {
    Goal.EXTRACT_PRICING: ["pricing", "plans", "plan"],
    Goal.BOOK_DEMO: ["book a demo", "schedule demo", "talk to sales", "contact sales", "demo"],
    Goal.SIGN_UP: ["sign up", "signup", "create account", "get started", "join"],
    Goal.ADD_TO_CART: ["add to cart", "add to bag", "checkout", "buy now"],
}


async def run_agent_on_site(site: Site, goal: Goal) -> SiteResult:
    """Open page, record video, attempt simple CTA clicks for goal keywords."""
    video_id = f"{uuid.uuid4()}.webm"
    keywords = GOAL_KEYWORDS.get(goal, [])
    success = False
    reason = "Unknown error"
    video_path: str | None = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                record_video_dir=str(VIDEO_DIR),
                viewport={"width": 1280, "height": 900},
            )
            page = await context.new_page()
            await page.goto(site.url, timeout=60000)

            content_lower = (await page.content()).lower()
            clicked = False
            for word in keywords:
                if word in content_lower:
                    locator = page.get_by_text(word, exact=False).first
                    try:
                        await locator.click(timeout=5000)
                        clicked = True
                        await page.wait_for_timeout(1500)
                        success = await classify_success(page, goal)
                        reason = f"Clicked CTA: {word}" if success else f"Clicked CTA '{word}' but success heuristic failed"
                        break
                    except Exception:
                        # ignore and try next keyword
                        pass

            if not clicked:
                success = False
                reason = "No actionable CTA found for this goal."

            # Obtain video file path (Playwright creates per page folder)
            try:
                if page.video:
                    raw_video_path = await page.video.path()  # absolute path
                    # Normalize to relative public URL served under /videos
                    from pathlib import Path as _P
                    video_filename = _P(raw_video_path).name
                    video_path = f"/videos/{video_filename}"  # relative URL for frontend
            except Exception:
                video_path = None

            await context.close()
            await browser.close()
    except Exception as e:
        tb = traceback.format_exc(limit=6)
        success = False
        reason = f"Agent crashed: {e!r} | Trace: {tb.splitlines()[-1]}"

    return SiteResult(
        site_id=site.id,
        site_name=site.name,
        url=site.url,
        success=success,
        reason=reason,
        video_url=video_path,
    )


async def run_reality_check(goal: Goal) -> List[SiteResult]:
    sites = load_sites()
    loop = asyncio.get_running_loop()
    is_windows = sys.platform == "win32"
    loop_name = type(loop).__name__.lower()

    # If on Windows and still running Proactor (which lacks subprocess support), fall back to sequential.
    if is_windows and "proactor" in loop_name:
        print("[LiveGap] Detected ProactorEventLoop on Windows; running sites sequential to avoid subprocess issues.")
        results: List[SiteResult] = []
        for site in sites:
            results.append(await run_agent_on_site(site, goal))
        return results

    # Otherwise run concurrently.
    tasks = [asyncio.create_task(run_agent_on_site(site, goal)) for site in sites]
    return list(await asyncio.gather(*tasks))
