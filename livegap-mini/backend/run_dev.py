"""Local dev launcher ensuring Windows Proactor event loop before starting uvicorn.
Usage:
  python run_dev.py            # starts with reload
  python run_dev.py --no-reload

On Windows Playwright requires Proactor event loop for subprocess support.
"""
from __future__ import annotations
import sys

# CRITICAL: Set event loop policy BEFORE any asyncio imports
if sys.platform == "win32":
  import asyncio
  asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
  print("[another.ai] Applied WindowsProactorEventLoopPolicy before uvicorn run.")

import argparse
import uvicorn

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload (avoids multiprocessing spawn issues)")
  args = parser.parse_args()

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
