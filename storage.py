"""Append structured research summaries to a local text file."""

from datetime import datetime, timezone
from pathlib import Path


def save_to_txt(report: str, filename: str | Path = "outputs/research_output.txt") -> Path:
    """Append a timestamped report; create parent directories when needed."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"--- Research Output ---\nTimestamp: {timestamp}\n\n{report}\n\n")
    return path
