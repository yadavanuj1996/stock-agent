# Stock Agent

A multi-agent stock research system. Type a company name, get a full technical analysis with 5 charts.
> Walks through: Orchestrator → Data flow → Researcher → Analyst → Sandbox → Full lifecycle

## Stages

| Stage | Folder | Status |
|---|---|---|
| 1 — LangChain multi-agent | `1-deepagent/` | ✅ Done |
| 2 — MCP server | `2-mcp-server/` | ✅ Done · **[Open interactive explainer](https://htmlpreview.github.io/?https://raw.githubusercontent.com/yadavanuj1996/stock-agent/master/docs/architecture.html)** | 
| 3 — Agent-to-agent (A2A) | `3-a2a/` | ✅ Done · **[Open interactive explainer](https://htmlpreview.github.io/?https://raw.githubusercontent.com/yadavanuj1996/stock-agent/master/docs/architecture-a2a.html)** |


<img width="930" height="804" alt="Screenshot 2026-06-03 at 1 43 44 AM" src="https://github.com/user-attachments/assets/21941c3b-4f5e-4b73-b79d-0324ae535979" />
<img width="930" height="804" alt="Screenshot 2026-06-03 at 1 44 10 AM" src="https://github.com/user-attachments/assets/79adcd76-7a91-4ab1-8754-af3a81a4e59c" />
<img width="978" height="648" alt="Screenshot 2026-06-03 at 1 44 19 AM" src="https://github.com/user-attachments/assets/d1a64f2f-0172-4e53-8614-552348032a84" />
<img width="978" height="648" alt="Screenshot 2026-06-03 at 1 44 29 AM" src="https://github.com/user-attachments/assets/31376800-6536-45c5-9b6f-1aba53887da8" />


**Part 1 of this project is complete.** All three stages (LangChain multi-agent, MCP server, A2A protocol) are fully working.

**Part 2 is underway** — AWS-hosted, continuously evolving with new agents.

## Architecture (3-a2a)

The system runs five independent A2A services coordinated by an orchestrator:

```
User query
    │
    ▼
Orchestrator (main.py)
    │
    ├── Researcher Agent  (port 8001) — fetches price, fundamentals, news via MCP
    │
    ├── Analyst Agent     (port 8002) — technical analysis + 5 charts
    │
    └── Sentiment Agent   (port 8003) — StockTwits sentiment (runs in parallel with analyst)
```

### Sentiment Agent

`subagents/sentiment_agent.py` — A2A service on port 8003.

Fetches social media data from StockTwits and uses GPT-4o-mini to extract investment-relevant sentiment:

- Fetches 2 pages (up to 60 messages) per ticker — safe rate limit for bulk use (40 req/2 min, well within the ~200/hr free tier)
- Tags each message as Bullish, Bearish, or Neutral based on StockTwits metadata
- GPT-4o-mini extracts overall sentiment, confidence level, and 3–5 key themes from the messages
- Result includes counts and themes displayed in a dedicated panel on the dashboard
- Runs in parallel with the Analyst agent to keep total latency down

## Version 2 — Roadmap

### Phase 1 — AWS Hosting ✅
- Deployed on AWS EC2 (t3.small, ap-south-1)
- Docker + Docker Compose for container orchestration
- ECR for Docker image registry
- GitHub Actions CI/CD pipeline (auto deploy on push to main)
- AWS Parameter Store for secrets management
- Nginx reverse proxy

### Phase 2 — StockTwits Sentiment Agent ✅
- `sentiment_agent.py` — A2A service on port 8003
- Fetches StockTwits messages per ticker (2 pages = 60 messages)
- GPT-4o-mini extracts themes and overall sentiment
- Sentiment panel displayed on dashboard
- Runs in parallel with researcher + analyst

### Phase 3 — Value Investment Agent (Alpaca) 🔄
- Alpaca paper trading account integration
- `trading_agent.py` — A2A service
- Value screening: P/E, ROE, profit margins, free cash flow
- Position sizing rules (max 10% per stock, 20% cash reserve)
- Stop loss (-15%) and take profit (+30%) rules
- Paper trades on Alpaca

### Phase 4 — Portfolio Summary + WhatsApp Notifications
- Connect to Alpaca API directly
- Daily + weekly portfolio performance summary
- P&L breakdown per position
- All buy/sell orders fetched from Alpaca (no separate DB needed)
- WhatsApp notifications via Twilio Sandbox (free, personal use)
  - EOD report sent to your WhatsApp automatically
  - Buy/sell execution alerts in real time
  - On demand portfolio summary

### Phase 5 — Multimodal Chart Analysis
- Feed generated charts to GPT-4o vision
- Visual pattern observations (head & shoulders, support/resistance)
- Pattern analysis added to final report

### Phase 6 — Trading Suggestion Agent
- Short term trade suggestions (2-4hr or 1-3 day timeline)
- Separate from value investment (Phase 3 is long term)
- Based on technical indicators + sentiment signals

