"""Opt-in local Flow receipts. No provider calls or account-balance claims."""
from __future__ import annotations

import json
import math
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from . import ledger


def credit_receipt(cost_this_call: Optional[int] = None, *, estimated: bool = False,
                   daily_budget: Optional[int] = None) -> str:
    """Summarize rolling windows, excluding malformed records and future timestamps.

    Legacy naive ledger timestamps are interpreted in the host's local timezone.
    A missing ledger means no locally recorded spend, not a verified zero balance.
    """
    if daily_budget is not None and daily_budget <= 0:
        raise ValueError("daily_budget must be greater than zero")
    now = datetime.now(timezone.utc)
    day_spent = month_spent = 0
    day_estimated = month_estimated = False
    try:
        lines = ledger.ledger_path().read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        lines = []
    except (OSError, UnicodeError):
        return "[Flow local receipt unavailable: ledger unreadable]"
    skipped = 0
    for line in lines:
        try:
            entry = json.loads(line)
            stamp = datetime.fromisoformat(entry["time"]).astimezone(timezone.utc)
            cost = entry["credits"]
            if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost < 0:
                raise ValueError("invalid credits")
            if not entry["tool"].startswith("flow_") or entry.get("status") != "ok":
                continue
            age = now - stamp
            if timedelta(0) <= age < timedelta(days=30):
                month_spent += cost
                month_estimated |= bool(entry.get("estimated"))
                if age < timedelta(hours=24):
                    day_spent += cost
                    day_estimated |= bool(entry.get("estimated"))
        except (ValueError, KeyError, TypeError, AttributeError, OverflowError):
            skipped += 1
    def amount(value, is_estimated):
        return f"{'~' if is_estimated else ''}{value:g}"
    fields = []
    if cost_this_call is not None:
        fields.append(f"Job: {amount(cost_this_call, estimated)} cr")
    fields.extend([f"24h spent: {amount(day_spent, day_estimated)} cr",
                   f"30d spent: {amount(month_spent, month_estimated)} cr"])
    if daily_budget is not None:
        fields.append(f"24h budget left: {amount(max(0, daily_budget - day_spent), day_estimated)}/{daily_budget} cr")
    if skipped:
        fields.append(f"{skipped} invalid record(s) skipped")
    return "[Flow local only | " + " | ".join(fields) + "]"


def append_credit_footer(result_text: str, cost_this_call: Optional[int] = None, *,
                         estimated: bool = False, enabled: Optional[bool] = None) -> str:
    """Explicit per-call choice overrides GMP_CREDIT_RECEIPTS (off by default).

    Telemetry errors never replace a generation result with an exception.
    """
    if enabled is None:
        enabled = os.environ.get("GMP_CREDIT_RECEIPTS", "off").lower() in {"1", "true", "on"}
    if not enabled:
        return result_text
    try:
        raw_budget = os.environ.get("GMP_FLOW_DAILY_BUDGET")
        budget = int(raw_budget) if raw_budget else None
        receipt = credit_receipt(cost_this_call, estimated=estimated, daily_budget=budget)
    except (ValueError, OSError):
        receipt = "[Flow local receipt unavailable: check ledger/budget configuration]"
    return result_text + "\n---\n" + receipt


def register_receipt_tools(mcp):
    @mcp.tool(name="flow_credit_receipt", description=(
        "Compact local Flow spend for rolling 24h/30d windows; no network calls. "
        "Optional daily_budget is your own target, not a provider allowance. "
        "Excludes external spending, image quotas and chat token usage; ~ means estimated."))
    async def flow_credit_receipt(daily_budget: Optional[int] = None) -> str:
        try:
            raw_budget = os.environ.get("GMP_FLOW_DAILY_BUDGET")
            budget = daily_budget if daily_budget is not None else (int(raw_budget) if raw_budget else None)
            return credit_receipt(daily_budget=budget)
        except ValueError:
            return "Error: daily_budget / GMP_FLOW_DAILY_BUDGET must be a positive integer."
