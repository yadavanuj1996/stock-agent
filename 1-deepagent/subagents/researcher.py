import yaml
import yfinance as yf
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage

from dotenv import load_dotenv
load_dotenv()

# load skill instructions
SKILL_PATH = Path(__file__).parent.parent / "skills" / "stock-research" / "SKILL.md"
SKILL = SKILL_PATH.read_text()

# load subagent config
CONFIG_PATH = Path(__file__).parent.parent / "subagents.yaml"
CONFIG = yaml.safe_load(CONFIG_PATH.read_text())
MODEL = CONFIG["subagents"]["researcher"]["model"]

# initialise LLM
llm = ChatOpenAI(model=MODEL)

@tool
def get_stock_price(ticker: str) -> str:
    """Get current stock price and basic info for a given ticker symbol."""
    stock = yf.Ticker(ticker)
    info = stock.info
    return f"""
    Company: {info.get('longName')}
    Current Price: ${info.get('currentPrice')}
    52 Week High: ${info.get('fiftyTwoWeekHigh')}
    52 Week Low: ${info.get('fiftyTwoWeekLow')}
    Market Cap: ${info.get('marketCap')}
    P/E Ratio: {info.get('trailingPE')}
    EPS: {info.get('trailingEps')}
    Dividend Yield: {info.get('dividendYield')}
    """

@tool
def get_stock_history(ticker: str) -> str:
    """Get last 6 months of historical OHLCV data for a given ticker symbol."""
    stock = yf.Ticker(ticker)
    history = stock.history(period="6mo")
    return history.to_string()

@tool
def get_stock_news(ticker: str) -> str:
    """Get latest news headlines for a given ticker symbol."""
    stock = yf.Ticker(ticker)
    news = stock.news[:5]
    result = ""
    for item in news:
        result += f"- {item['content']['title']}\n"
    return result

@tool
def get_stock_fundamentals(ticker: str) -> str:
    """Get key fundamental data for a given ticker symbol."""
    stock = yf.Ticker(ticker)
    info = stock.info
    return f"""
    Revenue (TTM): ${info.get('totalRevenue')}
    Profit Margin: {info.get('profitMargins')}
    Return on Equity: {info.get('returnOnEquity')}
    Debt to Equity: {info.get('debtToEquity')}
    Free Cash Flow: ${info.get('freeCashflow')}
    """

tools = [get_stock_price, get_stock_history, get_stock_news, get_stock_fundamentals]
llm_with_tools = llm.bind_tools(tools)

def run(ticker: str) -> dict:
    """Run the researcher agent for a given ticker."""
    
    # fetch raw data directly
    import yfinance as yf
    stock = yf.Ticker(ticker)
    history = stock.history(period="6mo")
    
    messages = [
        SystemMessage(f"""
        You are a stock research agent.
        Follow these instructions carefully:
        {SKILL}
        """),
        HumanMessage(f"Research the stock with ticker symbol: {ticker}")
    ]

    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)
        if not response.tool_calls:
            break
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_fn = next(t for t in tools if t.name == tool_name)
            tool_result = tool_fn.invoke(tool_args)
            messages.append({
                "role": "tool",
                "content": str(tool_result),
                "tool_call_id": tool_call["id"]
            })

    return {
        "summary": response.content,
        "csv": history.to_csv(),         # real 6 month data as CSV
        "ticker": ticker
    }
if __name__ == "__main__":
    result = run("AAPL")
    print(result)