"""A local spend ledger for Flow. gflow often cannot read the balance (issue #795), so every request is logged.

One JSON line per request in ~/.gemini_media_pass/flow_spend.jsonl (or GMP_FLOW_LEDGER).
`credits` is the cost gflow reported when it reported one, else this server's estimate (`estimated: true`).
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


def ledger_path() -> Path:
    return Path(os.environ.get("GMP_FLOW_LEDGER") or Path.home() / ".gemini_media_pass" / "flow_spend.jsonl")


def reported_cost(gflow_stdout: str) -> Optional[int]:
    """The credits gflow says it spent, from its JSON output, or None when it did not say."""
    try:
        data = json.loads(gflow_stdout)
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    for key in ("credits_spent", "credits_used", "cost"):
        if isinstance(data.get(key), (int, float)):
            return int(data[key])
    return None


def log_request(tool: str, model: str, prompt: str, estimate: int, status: str,
                gflow_stdout: str = "", note: str = "") -> Dict[str, Any]:
    """Append one request. status is ok, failed, blocked or refused. Failed and blocked cost 0 (Flow refunds)."""
    real = reported_cost(gflow_stdout) if status == "ok" else None
    entry = {"time": datetime.now().isoformat(timespec="seconds"), "tool": tool, "model": model,
             "prompt": prompt[:160], "status": status,
             "credits": (real if real is not None else estimate) if status == "ok" else 0,
             "estimated": status == "ok" and real is None, "note": note}
    path = ledger_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass
    return entry


def read_entries(days: int = 1) -> List[Dict[str, Any]]:
    path = ledger_path()
    if not path.exists():
        return []
    since = datetime.now() - timedelta(days=days)
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(line)
            if datetime.fromisoformat(e["time"]) >= since:
                out.append(e)
        except (ValueError, KeyError):
            continue
    return out


def summary(days: int = 1) -> str:
    entries = read_entries(days)
    if not entries:
        return f"No Flow requests logged in the last {days} day(s). Ledger: `{ledger_path().as_posix()}`"
    total = sum(e["credits"] for e in entries)
    est = any(e.get("estimated") for e in entries)
    lines = [f"Flow spend, last {days} day(s): {total} credits{' (some estimated)' if est else ''} "
             f"over {len(entries)} request(s).", "", "| Time | Tool | Model | Status | Credits | Prompt |",
             "|---|---|---|---|---|---|"]
    for e in entries[-30:]:
        cr = f"~{e['credits']}" if e.get("estimated") else str(e["credits"])
        lines.append(f"| {e['time'][11:16]} | {e['tool']} | {e['model']} | {e['status']} | {cr} | {e['prompt'][:50]} |")
    lines.append(f"\nLedger: `{ledger_path().as_posix()}`. Compare with the balance shown in Flow.")
    return "\n".join(lines)
