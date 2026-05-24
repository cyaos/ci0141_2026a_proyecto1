"""Write-Ahead Log implemented as JSONL at .dbclient/wal.jsonl"""
import json
from pathlib import Path
from datetime import datetime
import asyncio
from typing import Optional, List, Dict, Any

# Store runtime files in the current working directory (project-local) instead of the user's home.
CONFIG_DIR = Path.cwd() / ".dbclient"
WAL_FILE = CONFIG_DIR / "wal.jsonl"
_wal_lock = asyncio.Lock()


def ensure_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


async def append(entry: Dict[str, Any]):
    """Append a WAL entry (dict) as a JSON line. Thread-safe with an asyncio.Lock."""
    ensure_dir()
    async with _wal_lock:
        entry.setdefault("timestamp", datetime.utcnow().isoformat() + "Z")
        line = json.dumps(entry, default=str)
        # Use binary write to avoid encoding issues
        with WAL_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


def _read_lines() -> List[Dict[str, Any]]:
    ensure_dir()
    if not WAL_FILE.exists():
        return []
    out = []
    with WAL_FILE.open("r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                out.append(json.loads(ln))
            except Exception:
                continue
    return out


def query(tid: Optional[str] = None, since: Optional[str] = None, until: Optional[str] = None) -> List[Dict[str, Any]]:
    """Query WAL entries with simple filters: tid and ISO timestamps since/until (strings)."""
    rows = _read_lines()
    def _filter(r):
        if tid and r.get("tid") != tid:
            return False
        ts = r.get("timestamp")
        if since and ts and ts < since:
            return False
        if until and ts and ts > until:
            return False
        return True

    return [r for r in rows if _filter(r)]
