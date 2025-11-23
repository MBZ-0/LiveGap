"""Local dev launcher ensuring Windows selector event loop before starting uvicorn.
Usage:
  python run_dev.py            # starts with reload
  python run_dev.py --no-reload

On Windows + Python >=3.12 Playwright may misbehave; prefer Python 3.11.
"""
from __future__ import annotations
import asyncio, sys, argparse
import uvicorn

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload (avoids multiprocessing spawn issues)")
  args = parser.parse_args()

  if sys.platform == "win32":
    try:
      asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
      print("[LiveGap] Applied WindowsSelectorEventLoopPolicy before uvicorn run.")
    except Exception as e:
      print(f"[LiveGap] Failed to set selector loop policy: {e!r}")

  config = uvicorn.Config(
    "app.main:app",
    host="127.0.0.1",
    port=8000,
    reload=not args.no_reload,
    workers=1,
    log_level="info",
  )
  server = uvicorn.Server(config)
  server.run()


if __name__ == "__main__":
  main()
