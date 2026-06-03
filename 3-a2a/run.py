import threading
import time
import httpx
import sys
import uvicorn

from server import mcp
from subagents.researcher_agent import serve as serve_researcher
from subagents.analyst_agent import serve as serve_analyst


def serve_mcp():
    mcp.run(transport="streamable-http")


def wait_for_url(url: str, name: str, retries: int = 20, delay: float = 1.0):
    for i in range(retries):
        try:
            r = httpx.get(url, timeout=2)
            if r.status_code < 500:
                print(f"[run.py] {name} ready")
                return
        except Exception:
            pass
        print(f"[run.py] Waiting for {name}... ({i+1}/{retries})")
        time.sleep(delay)
    print(f"[run.py] ERROR: {name} did not start in time. Exiting.")
    sys.exit(1)


def wait_for_agent(url: str, name: str, retries: int = 20, delay: float = 1.0):
    for i in range(retries):
        try:
            r = httpx.get(f"{url}/.well-known/agent-card.json", timeout=2)
            if r.status_code == 200:
                print(f"[run.py] {name} ready — {r.json().get('name', name)}")
                return
        except Exception:
            pass
        print(f"[run.py] Waiting for {name}... ({i+1}/{retries})")
        time.sleep(delay)
    print(f"[run.py] ERROR: {name} did not start in time. Exiting.")
    sys.exit(1)


if __name__ == "__main__":
    threading.Thread(target=serve_mcp, daemon=True).start()
    wait_for_url("http://localhost:8050/mcp", "MCP Server")

    threading.Thread(target=serve_researcher, daemon=True).start()
    threading.Thread(target=serve_analyst, daemon=True).start()

    wait_for_agent("http://localhost:8001", "Researcher Agent")
    wait_for_agent("http://localhost:8002", "Analyst Agent")

    print("\n[run.py] All services ready. Starting web server on http://localhost:8000\n")

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)
