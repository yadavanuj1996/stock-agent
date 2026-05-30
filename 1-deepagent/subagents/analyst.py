import yaml
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import sys
import yfinance as yf

load_dotenv()

# load skill instructions
ANALYSIS_SKILL = (Path(__file__).parent.parent / "skills" / "stock-analysis" / "SKILL.md").read_text()

# load subagent config
CONFIG_PATH = Path(__file__).parent.parent / "subagents.yaml"
CONFIG = yaml.safe_load(CONFIG_PATH.read_text())
MODEL = CONFIG["subagents"]["analyst"]["model"]

# add sandbox to path
sys.path.append(str(Path(__file__).parent.parent))
from sandbox.executor import execute_code

# initialise LLM (text analysis only — no tools needed)
llm = ChatOpenAI(model=MODEL)

# pre-written chart functions injected into every sandbox run.
_BOILERPLATE = """\
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

plt.style.use('dark_background')

df = pd.read_csv('/data/stock_data.csv', index_col=0, parse_dates=True)
df.index = pd.to_datetime(df.index, utc=True).tz_convert(None)
df.columns = [col.strip() for col in df.columns]
print("Loaded stock data:", df.shape)


def plot_price_ma(df, ticker):
    ma50 = df['Close'].rolling(50).mean()
    ma200 = df['Close'].rolling(200).mean()
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(df.index, df['Close'], color='#00ff88', linewidth=1.5, label='Price')
    ax.plot(df.index, ma50, color='#ffaa00', linewidth=1, label='50 MA')
    ax.plot(df.index, ma200, color='#ff4444', linewidth=1, label='200 MA')
    ax.set_title(f'{ticker} Price + Moving Averages', fontsize=14)
    ax.set_xlabel('Date')
    ax.set_ylabel('Price ($)')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    plt.tight_layout()
    path = f'/output/{ticker}_price_ma.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_rsi(df, ticker, period=14):
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(df.index, rsi, color='#aa88ff', linewidth=1.5, label=f'RSI ({period})')
    ax.axhline(70, color='#ff4444', linestyle='--', linewidth=1, label='Overbought (70)')
    ax.axhline(30, color='#00ff88', linestyle='--', linewidth=1, label='Oversold (30)')
    ax.fill_between(df.index, rsi, 70, where=(rsi >= 70), alpha=0.3, color='#ff4444')
    ax.fill_between(df.index, rsi, 30, where=(rsi <= 30), alpha=0.3, color='#00ff88')
    ax.set_ylim(0, 100)
    ax.set_title(f'{ticker} RSI ({period})', fontsize=14)
    ax.set_xlabel('Date')
    ax.set_ylabel('RSI')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    plt.tight_layout()
    path = f'/output/{ticker}_rsi.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_macd(df, ticker, fast=12, slow=26, signal=9):
    ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    colors = ['#00ff88' if v >= 0 else '#ff4444' for v in histogram]
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(df.index, macd, color='#00aaff', linewidth=1.5, label='MACD')
    ax.plot(df.index, signal_line, color='#ffaa00', linewidth=1, label='Signal')
    ax.bar(df.index, histogram, color=colors, alpha=0.6, label='Histogram', width=1)
    ax.axhline(0, color='white', linewidth=0.5)
    ax.set_title(f'{ticker} MACD ({fast},{slow},{signal})', fontsize=14)
    ax.set_xlabel('Date')
    ax.set_ylabel('MACD')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    plt.tight_layout()
    path = f'/output/{ticker}_macd.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_volume(df, ticker):
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.bar(df.index, df['Volume'], color='#4488ff', alpha=0.7, width=1)
    ax.set_title(f'{ticker} Trading Volume', fontsize=14)
    ax.set_xlabel('Date')
    ax.set_ylabel('Volume')
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    plt.tight_layout()
    path = f'/output/{ticker}_volume.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_benchmark(df, ticker):
    sp500_path = '/data/sp500_data.csv'
    if not os.path.exists(sp500_path):
        print("S&P 500 data not available, skipping benchmark chart")
        return
    sp500_df = pd.read_csv(sp500_path, index_col=0, parse_dates=True)
    sp500_df.index = pd.to_datetime(sp500_df.index, utc=True).tz_convert(None)
    sp500_df.columns = [col.strip() for col in sp500_df.columns]
    stock_norm = df['Close'] / df['Close'].iloc[0] * 100
    sp500_norm = sp500_df['Close'] / sp500_df['Close'].iloc[0] * 100
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(df.index, stock_norm, color='#00ff88', linewidth=1.5, label=ticker)
    ax.plot(sp500_df.index, sp500_norm, color='#ff4444', linewidth=1.5, label='S&P 500')
    ax.axhline(100, color='white', linestyle='--', linewidth=0.5)
    ax.set_title(f'{ticker} vs S&P 500 (6 Month Normalized)', fontsize=14)
    ax.set_xlabel('Date')
    ax.set_ylabel('Normalized Price (Base = 100)')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    plt.tight_layout()
    path = f'/output/{ticker}_benchmark.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


"""

# chart calls injected after the boilerplate — always generate all 5
_CHART_CALLS = """\
plot_price_ma(df, "{ticker}")
plot_rsi(df, "{ticker}")
plot_macd(df, "{ticker}")
plot_volume(df, "{ticker}")
plot_benchmark(df, "{ticker}")
"""


def run(research_data: dict, ticker: str) -> dict:
    """Run the analyst agent on research data for a given ticker."""

    csv_data = research_data.get("csv", "") if isinstance(research_data, dict) else ""
    summary = research_data.get("summary", "") if isinstance(research_data, dict) else str(research_data)

    # step 1 — pre-fetch S&P 500 for benchmark chart
    print("  → Fetching S&P 500 benchmark data...")
    sp500_history = yf.Ticker("^GSPC").history(period="6mo")
    sp500_csv_data = sp500_history.to_csv()
    sp500_return = ((sp500_history['Close'].iloc[-1] - sp500_history['Close'].iloc[0])
                    / sp500_history['Close'].iloc[0]) * 100

    # step 2 — generate all charts directly (no LLM involvement)
    print("  → Generating charts...")
    chart_code = _BOILERPLATE + _CHART_CALLS.format(ticker=ticker)
    result = execute_code(chart_code, csv_data=csv_data, sp500_csv_data=sp500_csv_data)
    charts = result["charts"] if result["success"] else []
    if not result["success"]:
        print(f"  → Chart error: {result['error']}")
    else:
        print(f"  → Charts generated: {len(charts)}")

    # step 3 — LLM writes text analysis only
    print("  → Running text analysis...")
    response = llm.invoke([
        SystemMessage(f"""
        You are a stock analyst. Write a technical analysis of the stock.

        {ANALYSIS_SKILL}

        S&P 500 6 month return: {sp500_return:.2f}%
        Charts have already been generated separately.
        """),
        HumanMessage(f"""
        Analyse {ticker} based on the following research data:

        {summary}
        """)
    ])

    return {
        "analysis": response.content,
        "charts": charts
    }


if __name__ == "__main__":
    stock = yf.Ticker("AAPL")
    history = stock.history(period="6mo")

    sample_data = {
        "summary": """
        Company: Apple Inc.
        Current Price: $309.90
        52 Week High: $313.26
        52 Week Low: $195.07
        Market Cap: $4.55 Trillion
        P/E Ratio: 37.52
        Revenue: $451.44 Billion
        Profit Margin: 27.15%
        """,
        "csv": history.to_csv(),
        "ticker": "AAPL"
    }

    result = run(sample_data, "AAPL")
    print("\n" + "="*50)
    print("FINAL ANALYSIS:")
    print("="*50)
    print(result["analysis"])
