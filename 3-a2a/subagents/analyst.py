import os
import io
import tempfile
import calendar as _cal
from datetime import date, timedelta
from pathlib import Path

import yaml
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

ANALYSIS_SKILL = (Path(__file__).parent.parent / "skills" / "stock-analysis" / "SKILL.md").read_text()
CONFIG = yaml.safe_load((Path(__file__).parent.parent / "subagents.yaml").read_text())
MODEL = CONFIG["subagents"]["analyst"]["model"]

llm = ChatOpenAI(model=MODEL)

plt.style.use('dark_background')


def _load_df(csv_str: str) -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(csv_str), index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(None)
    df.columns = [c.strip() for c in df.columns]
    return df


def plot_price_ma(df_6mo: pd.DataFrame, df_1y: pd.DataFrame, ticker: str, output_dir: str) -> str:
    ma50 = df_1y['Close'].rolling(50).mean()
    ma200 = df_1y['Close'].rolling(200).mean()
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(df_1y.index, df_1y['Close'], color='#00ff88', linewidth=1.5, label='Price')
    ax.plot(df_1y.index, ma50, color='#ffaa00', linewidth=1, label='50 MA')
    ax.plot(df_1y.index, ma200, color='#ff4444', linewidth=1, label='200 MA')
    ax.set_title(f'{ticker} Price + Moving Averages', fontsize=14)
    ax.set_xlabel('Date')
    ax.set_ylabel('Price ($)')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    plt.tight_layout()
    path = os.path.join(output_dir, f'{ticker}_price_ma.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


def plot_rsi(df: pd.DataFrame, ticker: str, output_dir: str, period: int = 14) -> str:
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rsi = 100 - (100 / (1 + gain / loss))
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
    path = os.path.join(output_dir, f'{ticker}_rsi.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


def plot_macd(df: pd.DataFrame, ticker: str, output_dir: str, fast: int = 12, slow: int = 26, signal: int = 9) -> str:
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
    path = os.path.join(output_dir, f'{ticker}_macd.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


def plot_volume(df: pd.DataFrame, ticker: str, output_dir: str) -> str:
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.bar(df.index, df['Volume'], color='#4488ff', alpha=0.7, width=1)
    ax.set_title(f'{ticker} Trading Volume', fontsize=14)
    ax.set_xlabel('Date')
    ax.set_ylabel('Volume')
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    plt.tight_layout()
    path = os.path.join(output_dir, f'{ticker}_volume.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


def plot_benchmark(df_6mo: pd.DataFrame, df_sp500: pd.DataFrame, ticker: str, output_dir: str) -> str:
    stock_norm = df_6mo['Close'] / df_6mo['Close'].iloc[0] * 100
    sp500_norm = df_sp500['Close'] / df_sp500['Close'].iloc[0] * 100
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(df_6mo.index, stock_norm, color='#00ff88', linewidth=1.5, label=ticker)
    ax.plot(df_sp500.index, sp500_norm, color='#ff4444', linewidth=1.5, label='S&P 500')
    ax.axhline(100, color='white', linestyle='--', linewidth=0.5)
    ax.set_title(f'{ticker} vs S&P 500 (6 Month Normalized)', fontsize=14)
    ax.set_xlabel('Date')
    ax.set_ylabel('Normalized Price (Base = 100)')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    plt.tight_layout()
    path = os.path.join(output_dir, f'{ticker}_benchmark.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


def _compute_indicators(csv_data: str, csv_1y_data: str, sp500_return: float) -> str:
    df = _load_df(csv_data)
    close = df['Close']

    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rsi = (100 - 100 / (1 + gain / loss)).iloc[-1]

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = (ema12 - ema26).iloc[-1]
    signal = (ema12 - ema26).ewm(span=9, adjust=False).mean().iloc[-1]

    open_price = df['Open'].iloc[0]
    stock_return = ((close.iloc[-1] - open_price) / open_price) * 100

    df1y = _load_df(csv_1y_data)
    ma50 = df1y['Close'].rolling(50).mean().iloc[-1]
    ma200 = df1y['Close'].rolling(200).mean().iloc[-1]
    trend = "Uptrend" if close.iloc[-1] > ma200 else "Downtrend"
    ma_signal = "Golden Cross (bullish)" if ma50 > ma200 else "Death Cross (bearish)"
    macd_signal = "Bullish (MACD above signal)" if macd_line > signal else "Bearish (MACD below signal)"
    vs_benchmark = f"{'Outperforming' if stock_return > sp500_return else 'Underperforming'} by {abs(stock_return - sp500_return):.2f}%"

    return f"""
50 Day MA:      ${ma50:.2f}
200 Day MA:     ${ma200:.2f}
Trend:          {trend} (price {'above' if close.iloc[-1] > ma200 else 'below'} 200 MA)
MA Signal:      {ma_signal}
RSI (14):       {rsi:.1f} ({'Overbought' if rsi > 70 else 'Oversold' if rsi < 30 else 'Neutral'})
MACD Line:      {macd_line:.4f}
Signal Line:    {signal:.4f}
MACD Signal:    {macd_signal}
6 Month Return: {stock_return:.2f}%
S&P 500 Return: {sp500_return:.2f}%
vs Benchmark:   {vs_benchmark}
"""


def run(research_data: dict, ticker: str) -> dict:
    csv_data = research_data.get("csv", "") if isinstance(research_data, dict) else ""
    csv_1y_data = research_data.get("csv_1y", "") if isinstance(research_data, dict) else ""
    summary = research_data.get("summary", "") if isinstance(research_data, dict) else str(research_data)

    # step 1 — fetch S&P 500 benchmark data
    print("  → Fetching S&P 500 benchmark data...")
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
    start_date = date(year, month, min(end_date.day, _cal.monthrange(year, month)[1]))
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = (end_date + timedelta(days=1)).strftime("%Y-%m-%d")
    status = "found" if end_date == today else f"no data — using {end_date}"
    print(f"  → End date attempted: {today} ({status})")
    print(f"  → S&P 500 window: {start_date} → {end_date}")

    sp500_history = yf.Ticker("^GSPC").history(start=start_str, end=end_str, auto_adjust=False)
    sp500_csv_data = sp500_history.to_csv()
    sp500_return = ((sp500_history['Close'].iloc[-1] - sp500_history['Open'].iloc[0])
                    / sp500_history['Open'].iloc[0]) * 100

    # step 2 — generate charts directly
    print("  → Generating charts...")
    output_dir = tempfile.mkdtemp()
    df_6mo = _load_df(csv_data)
    df_1y = _load_df(csv_1y_data)
    df_sp500 = _load_df(sp500_csv_data)

    charts = []
    try:
        charts.append(plot_price_ma(df_6mo, df_1y, ticker, output_dir))
        charts.append(plot_rsi(df_6mo, ticker, output_dir))
        charts.append(plot_macd(df_6mo, ticker, output_dir))
        charts.append(plot_volume(df_6mo, ticker, output_dir))
        charts.append(plot_benchmark(df_6mo, df_sp500, ticker, output_dir))
        print(f"  → Charts generated: {len(charts)}")
    except Exception as e:
        print(f"  → Chart error: {e}")

    # step 3 — LLM writes text analysis
    print("  → Running text analysis...")
    indicators = _compute_indicators(csv_data, csv_1y_data, sp500_return)
    response = llm.invoke([
        SystemMessage(f"""
        You are a stock analyst. Write a technical analysis of the stock.

        {ANALYSIS_SKILL}

        Charts have already been generated separately.
        """),
        HumanMessage(f"""
        Analyse {ticker} based on the following data:

        ## Research Summary
        {summary}

        ## Calculated Technical Indicators
        {indicators}
        """)
    ])

    return {
        "analysis": response.content,
        "charts": charts,
    }
