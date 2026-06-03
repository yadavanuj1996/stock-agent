import os
import yaml
import asyncio
import calendar as _cal
from datetime import date, timedelta
import yfinance as yf
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
from dotenv import load_dotenv

load_dotenv()

SKILL = (Path(__file__).parent.parent / "skills" / "stock-research" / "SKILL.md").read_text()

CONFIG = yaml.safe_load((Path(__file__).parent.parent / "subagents.yaml").read_text())
MODEL = CONFIG["subagents"]["researcher"]["model"]

MCP_URL = os.getenv("MCP_URL", "http://localhost:8050/mcp")


def _get_6mo_range() -> tuple[date, date]:
    """Return (start_date, end_date) where end is the latest trading day
    and start is exactly 6 calendar months before end."""
    today = date.today()
    recent = yf.Ticker("SPY").history(
        start=(today - timedelta(days=5)).strftime("%Y-%m-%d"),
        end=(today + timedelta(days=1)).strftime("%Y-%m-%d"),
        auto_adjust=False,
    )
    end_date = recent.index[-1].date()

    month = end_date.month - 6
    year = end_date.year
    if month <= 0:
        month += 12
        year -= 1
    max_day = _cal.monthrange(year, month)[1]
    start_date = date(year, month, min(end_date.day, max_day))
    attempted = today.strftime("%Y-%m-%d")
    status = "found" if end_date == today else f"no data — using {end_date} instead"
    print(f"  → End date attempted: {attempted} ({status})")
    print(f"  → 6-month window: {start_date} → {end_date}")
    return start_date, end_date

llm = ChatOpenAI(model=MODEL)


async def _run_async(ticker: str) -> dict:
    # CSV fetched directly — not through MCP
    start_6mo, end_date = _get_6mo_range()
    start_str = start_6mo.strftime("%Y-%m-%d")
    end_str = (end_date + timedelta(days=1)).strftime("%Y-%m-%d")

    stock = yf.Ticker(ticker)
    csv_data = stock.history(start=start_str, end=end_str, auto_adjust=False).to_csv()
    csv_1y_data = stock.history(period="1y", auto_adjust=False).to_csv()

    async with streamablehttp_client(MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # discover tools dynamically from MCP server — no hardcoded definitions
            mcp_tools = (await session.list_tools()).tools
            lc_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description or t.name,
                        "parameters": t.inputSchema,
                    },
                }
                for t in mcp_tools
            ]

            llm_with_tools = llm.bind_tools(lc_tools)

            messages = [
                SystemMessage(f"""
                You are a stock research agent.
                Follow these instructions carefully:
                {SKILL}
                """),
                HumanMessage(f"Research the stock with ticker symbol: {ticker}"),
            ]

            response = None
            while True:
                response = await llm_with_tools.ainvoke(messages)
                messages.append(response)
                if not response.tool_calls:
                    break
                for tc in response.tool_calls:
                    result = await session.call_tool(tc["name"], tc["args"])
                    content = result.content[0].text if result.content else ""
                    messages.append({
                        "role": "tool",
                        "content": content,
                        "tool_call_id": tc["id"],
                    })

    return {
        "summary": response.content if response else "",
        "csv": csv_data,
        "csv_1y": csv_1y_data,
        "ticker": ticker,
    }


def run(ticker: str) -> dict:
    return asyncio.run(_run_async(ticker))
