import threading
import time
import httpx
import sys
import subprocess

from subagents.researcher_agent import serve as serve_researcher
from subagents.analyst_agent import serve as serve_analyst
from main import run as orchestrator_run


def wait_for_agent(url: str, name: str, retries: int = 15, delay: float = 1.0):
    """Poll agent card endpoint until agent is ready."""
    for i in range(retries):
        try:
            r = httpx.get(f"{url}/.well-known/agent-card.json", timeout=2)
            if r.status_code == 200:
                card = r.json()
                print(f"[run.py] {name} ready — {card.get('name', name)}")
                return
        except Exception:
            pass
        print(f"[run.py] Waiting for {name}... ({i+1}/{retries})")
        time.sleep(delay)
    print(f"[run.py] ERROR: {name} did not start in time. Exiting.")
    sys.exit(1)


if __name__ == "__main__":
    threading.Thread(target=serve_researcher, daemon=True).start()
    threading.Thread(target=serve_analyst, daemon=True).start()

    wait_for_agent("http://localhost:8001", "Researcher Agent")
    wait_for_agent("http://localhost:8002", "Analyst Agent")

    print("\n[run.py] Both agents ready. Starting stock research system...\n")

    print("Stock Research Agent")
    print("-" * 60)

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "quit":
            break

        result = orchestrator_run(user_input)

        print("\n" + "=" * 60)
        print("FINAL RESPONSE:")
        print("=" * 60)
        print(result["response"])

        if result["charts"]:
            print(f"\nCharts generated:")
            for chart in result["charts"]:
                print(f"  → {chart}")
            for chart in result["charts"]:
                subprocess.run(["open", chart])
