# expt1-memory-server/server.py
import json
import os
from datetime import datetime, timezone
from mcp.server.fastmcp import FastMCP

NOTES_FILE = os.path.join(os.path.dirname(__file__), "notes.json")

mcp = FastMCP("personal-assistant-memory")


def _load_notes() -> list[dict]:
    if not os.path.exists(NOTES_FILE):
        return []
    with open(NOTES_FILE, "r") as f:
        return json.load(f)


def _save_notes(notes: list[dict]) -> None:
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=2)


@mcp.tool()
def save_note(content: str, tags: list[str] = []) -> str:
    """Save a note with optional tags to persistent memory."""
    notes = _load_notes()
    note = {
        "id": len(notes) + 1,
        "content": content,
        "tags": tags,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    notes.append(note)
    _save_notes(notes)
    return f"Saved note #{note['id']}: \"{content}\""


@mcp.tool()
def search_notes(query: str) -> str:
    """Search saved notes by keyword match against content and tags."""
    notes = _load_notes()
    query_lower = query.lower()
    matches = [
        n for n in notes
        if query_lower in n["content"].lower()
        or any(query_lower in t.lower() for t in n["tags"])
    ]
    if not matches:
        return "No matching notes found."
    return "\n".join(
        f"[#{n['id']}] {n['content']} (tags: {', '.join(n['tags'])})"
        for n in matches
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
