import yaml
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import sys

load_dotenv()

# load agent memory
AGENTS_MD = (Path(__file__).parent / "AGENTS.md").read_text()

# load config
CONFIG = yaml.safe_load((Path(__file__).parent / "subagents.yaml").read_text())
ORCHESTRATOR_MODEL = CONFIG["orchestrator"]["model"]

# import subagents
sys.path.append(str(Path(__file__).parent))
from subagents.researcher import run as researcher_run
from subagents.analyst import run as analyst_run

# initialise orchestrator LLM
llm = ChatOpenAI(model=ORCHESTRATOR_MODEL)

def extract_ticker(user_input: str) -> str:
    """Use LLM to extract ticker symbol from user input."""
    response = llm.invoke([
        SystemMessage("Extract the stock ticker symbol from the user input. Return ONLY the ticker symbol in uppercase. Nothing else."),
        HumanMessage(user_input)
    ])
    return response.content.strip().upper()

def run(user_input: str) -> dict:
    """Main orchestrator — coordinates researcher and analyst subagents."""

    print("\n" + "="*60)
    print(f"USER: {user_input}")
    print("="*60)

    # step 1 — extract ticker from user input
    print("\n[Orchestrator] Extracting ticker symbol...")
    ticker = extract_ticker(user_input)
    print(f"[Orchestrator] Ticker identified: {ticker}")

    # step 2 — researcher fetches all stock data
    print(f"\n[Researcher] Fetching data for {ticker}...")
    research_data = researcher_run(ticker)
    print(f"[Researcher] Done. Summary length: {len(research_data['summary'])} chars")

    # step 3 — analyst analyses data and generates charts
    print(f"\n[Analyst] Analysing {ticker}...")
    analysis_result = analyst_run(research_data, ticker)
    print(f"[Analyst] Done.")

    # step 4 — orchestrator compiles final response
    print("\n[Orchestrator] Compiling final response...")
    final_response = llm.invoke([
        SystemMessage(f"""
        You are a stock research orchestrator.
        Follow these guidelines:
        {AGENTS_MD}
        """),
        HumanMessage(f"""
        The user asked: {user_input}

        Research data gathered:
        {research_data["summary"]}

        Analysis completed:
        {analysis_result['analysis']}

        Charts already generated: {len(analysis_result['charts'])} charts (price+MA, RSI, MACD, volume, benchmark vs S&P 500)

        Compile a clean, well structured final response for the user.
        Note: Charts have been generated and will be displayed to the user automatically. Do not say charts are pending.
        """)
    ])

    return {
        "response": final_response.content,
        "charts": analysis_result["charts"],
        "ticker": ticker
    }


if __name__ == "__main__":
    print("Stock Research Agent")
    print("-" * 60)

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "quit":
            break

        result = run(user_input)

        print("\n" + "="*60)
        print("FINAL RESPONSE:")
        print("="*60)
        print(result["response"])

        if result["charts"]:
            print(f"\nCharts generated:")
            for chart in result["charts"]:
                print(f"  → {chart}")
            # open charts automatically on Mac
            import subprocess
            for chart in result["charts"]:
                subprocess.run(["open", chart])