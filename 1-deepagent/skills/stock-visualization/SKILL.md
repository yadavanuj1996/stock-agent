# Stock Visualization Skill

## Goal
Generate stock charts by calling pre-defined plot functions.
Do not write matplotlib code — only call the functions listed below.

## Available Functions

All functions are pre-defined in the sandbox. Pass `df` (already loaded) and the ticker string.

| Function | Chart |
|---|---|
| `plot_price_ma(df, ticker)` | Closing price + 50 & 200 day moving averages |
| `plot_rsi(df, ticker)` | RSI (14) with overbought/oversold zones |
| `plot_macd(df, ticker)` | MACD line, signal line, histogram |
| `plot_volume(df, ticker)` | Trading volume bar chart |
| `plot_benchmark(df, ticker)` | Stock vs S&P 500 normalized over 6 months |

## How to Call generate_charts

Pass only the function calls — no imports, no definitions, no other code:

```python
plot_price_ma(df, "AAPL")
plot_rsi(df, "AAPL")
plot_macd(df, "AAPL")
plot_volume(df, "AAPL")
plot_benchmark(df, "AAPL")
```

## Rules
- Never write matplotlib or pandas code yourself
- Never redefine any function
- Never add import statements
- Call all five functions unless there is a specific reason to skip one
- Charts are saved automatically to /output/ — no need to handle file paths
