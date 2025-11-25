# LiveGap
See how badly your AI agent fails on real websites.

## LiveGap Mini

This subproject (`livegap-mini/`) is a minimal end-to-end demo:

- Backend: FastAPI + simple Chromium Playwright "agent" + Lambda compatibility via Mangum.
- Frontend: Next.js single page that triggers a run and displays per-site results.
- Goals supported (literal user utterances used verbatim when planning):
	1. I’m trying to talk to sales — can you help me get in touch with someone?
	2. Can you find out how much this product costs?
	3. How do I create an account on this website?
	4. Where can I see job openings for this company?
	5. Where do I go if I need help or support on this website?

	(Heuristic mode removed) Single LLM planner loop drives all runs.

### Directory Layout

```
livegap-mini/
	backend/
		app/
			__init__.py
			main.py            # FastAPI + /health + /run-reality-check + Lambda handler
			runner.py          # Launches Chromium, fetches HTML, applies heuristic judge
			llm.py             # Stub judge (replace with real LLM later)
			models.py          # Pydantic schemas
			sites.json         # 10 sample target sites
		requirements.txt
	frontend/
		app/
			page.tsx           # Main UI (goal picker + run + results table)
		package.json
		tsconfig.json
		next.config.mjs
```

### Backend Setup (Local)

Requires Python 3.10+.

```
cd livegap-mini/backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium

uvicorn app.main:app --reload --port 8000
```

Health check:

```
curl http://localhost:8000/health
```

Run endpoint (example):

```
curl -X POST http://localhost:8000/run-reality-check \
  -H "Content-Type: application/json" \
  -d '{"goal": "Can you find out how much this product costs?"}'
```

### Frontend Setup (Local)

Requires Node 18+.

```
cd livegap-mini/frontend
npm install
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env.local
npm run dev
```

Visit: http://localhost:3000/

### AWS Lambda Deployment (Backend)

Point your Lambda handler to `app.main.handler`.

High-level steps:
1. Package dependencies (Playwright in Lambda requires custom layer or container image; for quick demo you can use a Lambda container image based on Amazon Linux with Chromium dependencies installed).
2. Ensure Chromium libs are present (standard Lambda runtime does not include them). For production, consider using a prebuilt Playwright Lambda layer.
3. Deploy code + layer, set up API Gateway proxy integration.
4. Expose `/run-reality-check` and `/health` routes.
5. Set `NEXT_PUBLIC_API_BASE_URL` on the frontend to your API Gateway base URL.

### LLM Planner Loop

The agent runs an iterative observe → plan → act → judge loop (max ~6 steps) using an LLM to decide the next action. Each plan step returns JSON `{action, target, reason}` where action ∈ `CLICK | SCROLL | TYPE | DONE`. After performing an action the agent evaluates simple success heuristics and halts early if satisfied.

Prompt template (conceptual):
```
Goal: <goal>
URL: <current_url>
Page excerpt: <truncated_body_text>
Recent: <last_actions>
Allowed: CLICK(text), TYPE(selector|text), SCROLL(amount_px), DONE(reason)
Respond ONLY with JSON: {"action":"CLICK","target":"Book a demo","reason":"Found CTA"}
```
The response is parsed; if parsing fails a minimal safe fallback action (e.g. SCROLL) is applied.

### Extending the Agent

Future upgrades you can add:
- Multi-step navigation (click CTAs, fill forms).
- Capture full-resolution screenshots per step.
- Screenshots or video capture (store in S3, surface `video_url`).
- Better error taxonomy (timeout, network, rendering, captcha, cookie wall, geo restriction).
- Parallel execution of sites for speed (currently sequential for simplicity).
- Configurable site lists / user-supplied lists.
- Real LLM judge (OpenAI, Anthropic, local model) with structured reasoning.
- Replace planner stub with actual LLM calls for more nuanced multi-step flows.

### Troubleshooting

- Playwright import errors: ensure venv activated and `python -m playwright install chromium` ran.
- All sites failing with `Agent crashed`: verify browser binary exists: `python -m playwright doctor`.
- Windows `NotImplementedError` when launching browser: add in `main.py` before creating the app:
	```python
	import asyncio, sys
	if sys.platform == "win32":
			asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
	```
	This switches to the selector loop which supports subprocesses required by Playwright.
	If errors persist on Python 3.13, consider using Python 3.11 or 3.12 (Playwright official support) and start with `python run_dev.py` which sets the loop policy early.
- Chromium launch failures on Lambda: missing shared libs; confirm layer includes dependencies (fonts, libatk, libnss, etc.).
- CORS issues: adjust `allow_origins` in `main.py`.
- Frontend 500/404: verify `.env.local` contains correct `NEXT_PUBLIC_API_BASE_URL`.

### Quick Test Script (Optional)

From backend directory after starting uvicorn:
```
python - <<'PY'
import httpx, json
resp = httpx.post('http://localhost:8000/run-reality-check', json={'goal': 'Can you find out how much this product costs?'})
print(resp.status_code)
print(json.dumps(resp.json(), indent=2)[:500])
PY
```

### License / Notes

Internal prototype; no license specified yet. Add one before sharing publicly.

---
LiveGap Mini baseline complete. Iterate from here.
Videos are stored in `livegap-mini/backend/app/videos/` (git-ignored by default). Serve them statically (e.g. add FastAPI StaticFiles) or upload to S3 for production.
With the static mount now in place they are accessible at `GET /videos/<filename>.webm` and the frontend builds a full URL as `${NEXT_PUBLIC_API_BASE_URL}/videos/<filename>.webm` for playback in an HTML5 `<video>` element.

### LLM Planner (Real API)

Set `OPENAI_API_KEY` in `livegap-mini/backend/.env` (or environment) and optionally `OPENAI_MODEL` (default `gpt-4o-mini`). The planner calls OpenAI Chat Completions to decide actions. If the key is missing or an error occurs it falls back to a minimal internal exploration (e.g. scrolling) — not the old heuristic mode.

Environment vars:
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_ENDPOINT=https://api.openai.com/v1/chat/completions  # override if needed
```

Planner response must be a JSON object with fields: `action` (CLICK|SCROLL|TYPE|DONE), `target` (string or null), `reason`.

Error handling: If JSON parse fails or action unknown, the system reverts to heuristic step for that iteration.
