# MCP Lab — AI Coding Assistants for Tool Use

Two experiments demonstrating Model Context Protocol (MCP) servers that give an LLM persistent memory and real-time external data access.

## Expt 1 — The "Personal Assistant" Memory Server

**What it does:** Gives an LLM persistent memory by connecting it to a local JSON file through MCP. The server exposes two tools — `save_note(content, tags)` and `search_notes(query)` — that read from and write to `notes.json`. The client is a CLI that takes a natural-language query, and the LLM decides on its own whether the query calls for saving a new note or searching existing ones.

**Files:**
- `expt1-memory-server/server.py` — MCP server exposing the two tools
- `expt1-memory-server/client.py` — CLI client + LLM tool-calling loop
- `expt1-memory-server/notes.json` — created automatically on first `save_note` call

**Run it:**
```
python expt1-memory-server/client.py
```
Example interaction:
- `Remember that the project deadline is Nov 5, tag it as deadlines` → triggers `save_note`
- `What did I say about the project deadline?` → triggers `search_notes`

## Expt 2 — The "Data Dashboard" Connector

**What it does:** Connects an LLM to a live external API (wttr.in) to fetch and summarize real-time weather data. The server exposes `get_current_weather(location)`. The client prints the LLM's tool-calling decision and the raw tool result before printing its final natural-language answer, so the client-server interaction is visible rather than hidden.

**Files:**
- `expt2-weather-connector/server.py` — MCP server exposing the weather tool
- `expt2-weather-connector/client.py` — CLI client that surfaces the LLM's decision process

**Run it:**
```
python expt2-weather-connector/client.py
```
Example interaction:
- `What's the weather in Tokyo?`
- `Should I carry an umbrella in Chennai today?`

## Architecture

Both experiments follow the same pattern:

1. The client spawns the server script as a subprocess and opens an MCP session over stdio.
2. The client asks the server what tools it exposes and passes their schemas to the LLM.
3. The user types a natural-language query.
4. The LLM decides, on its own, whether the query needs a tool call — and if so, which one and with what arguments.
5. The client executes that tool call through the MCP session (the server does the actual file I/O or API call).
6. The tool's result is fed back to the LLM, which produces the final answer.

This is what separates MCP from a hardcoded API call: the server just exposes capabilities, and the LLM decides when and how to use them.

## Setup

```
python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_key_here
