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

## Version 2 — Roadmap

### Phase 1 — AWS hosting
- Deploy current system to AWS
- Document + blog + video

### Phase 2 — Portfolio MCP server
- `get_my_portfolio()` tool
- Compare holdings vs research

### Phase 3 — Twitter sentiment agent
- `sentiment_agent.py` (A2A service)
- Feeds sentiment score to analyst

### Phase 4 — Multimodal chart analysis
- Charts → GPT-4o vision
- Pattern observations added to report

### Phase 5 — Trading suggestion agent
- `trading_agent.py` (A2A service)
- Long term strategy
- Short term trade (2-4hr or 1-3 day)

