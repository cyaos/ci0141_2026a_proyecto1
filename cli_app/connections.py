"""Gestion de conexiones persistentes en ~/.dbclient/connections.json"""
from pathlib import Path
import json
from typing import Dict, Any, List, Optional


# Anchor to repo root so the API and REPL share one connection state.
CONFIG_DIR = Path(__file__).parent.parent / ".dbclient"
CONN_FILE = CONFIG_DIR / "connections.json"
# file to store metadata like currently active connection name
_META_FILE = CONFIG_DIR / "meta.json"


def ensure_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_connections() -> List[Dict[str, Any]]:
    ensure_dir()
    if not CONN_FILE.exists():
        return []
    with CONN_FILE.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []


def save_connections(conns: List[Dict[str, Any]]):
    ensure_dir()
    with CONN_FILE.open("w", encoding="utf-8") as f:
        json.dump(conns, f, indent=2)


def add_connection(name: str, engine: str, uri: str, metadata: Dict[str, Any] = None):
    conns = load_connections()
    entry = {"name": name, "engine": engine, "uri": uri}
    if metadata:
        entry["meta"] = metadata
    conns.append(entry)
    save_connections(conns)


def remove_connection(name: str) -> bool:
    conns = load_connections()
    new = [c for c in conns if c.get("name") != name]
    if len(new) == len(conns):
        return False
    save_connections(new)
    return True


def list_connections() -> List[Dict[str, Any]]:
    return load_connections()


def _load_meta() -> Dict[str, Any]:
    ensure_dir()
    if not _META_FILE.exists():
        return {}
    try:
        with _META_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_meta(meta: Dict[str, Any]):
    ensure_dir()
    with _META_FILE.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def set_active(name: str) -> bool:
    """Set a connection by name as the active connection. Returns True if set, False if not found."""
    conns = load_connections()
    if not any(c.get("name") == name for c in conns):
        return False
    meta = _load_meta()
    meta["active"] = name
    _save_meta(meta)
    return True


def get_active_name() -> Optional[str]:
    meta = _load_meta()
    return meta.get("active")


def get_active_connection() -> Optional[Dict[str, Any]]:
    name = get_active_name()
    if not name:
        return None
    for c in load_connections():
        if c.get("name") == name:
            return c
    return None

