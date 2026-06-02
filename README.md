# Stock Agent

A multi-agent stock research system. Type a company name, get a full technical analysis with 5 charts.

## Interactive architecture explainer

> GitHub doesn't run JavaScript in README files, so the explainer is hosted separately.
>
> **[Open interactive explainer](https://htmlpreview.github.io/?https://raw.githubusercontent.com/yadavanuj1996/stock-agent/master/docs/architecture.html)**
>
> Walks through: Orchestrator → Data flow → Researcher → Analyst → Sandbox → Full lifecycle

## Stages

| Stage | Folder | Status |
|---|---|---|
| 1 — LangChain multi-agent | `1-deepagent/` | ✅ Done |
| 2 — MCP server | `2-mcp-server/` | ✅ Done |
| 3 — Agent-to-agent (A2A) | `3-a2a/` | ✅ Done · **[Open interactive explainer](https://htmlpreview.github.io/?https://raw.githubusercontent.com/yadavanuj1996/stock-agent/master/docs/architecture-a2a.html)** |

## TODO

### Multimodal chart analysis (`1-deepagent`)

After charts are generated in the Docker sandbox, feed the PNG files back to a vision-capable LLM (GPT-4o with image input). The LLM should visually analyse the charts and add pattern-based observations to the technical analysis — e.g. head and shoulders patterns, support/resistance levels, trend channels — things that are easier to spot visually than to calculate from raw numbers.

**Current behaviour:** charts generated for human viewing only; LLM analyst reasons purely from text summary.

**Target behaviour:** charts generated → fed to GPT-4o vision → visual pattern analysis appended to final report.

Where to add it: `1-deepagent/subagents/analyst.py`, after `execute_code` returns chart paths and before the text analysis LLM call. Read each PNG as base64, pass to GPT-4o with `image_url` content blocks, append the visual observations to the system prompt for the analysis step.
