"""Live Flow balance, kept separate from partial local spend history."""
from __future__ import annotations

import math
import os
import json
from datetime import datetime, timedelta, timezone
from typing import Optional

from .receipts import credit_receipt


def image_catalog_summary(stdout: str, profile: str, *, now: Optional[datetime] = None,
                          limit: int = 1000) -> str:
    """Count distinct catalog assets, not API calls or provider quota consumption."""
    now = now or datetime.now(timezone.utc)
    hour = day = invalid = rows = 0
    seen = set()
    for line in stdout.splitlines():
        if not line.strip():
            continue
        rows += 1
        try:
            row = json.loads(line)
            if row["profile"] != profile:
                raise ValueError("profile mismatch")
            asset = row["media_id"]
            if not isinstance(asset, str) or not asset:
                raise ValueError("missing asset id")
            stamp = datetime.fromisoformat(row["created_at"])
            if stamp.tzinfo is None:
                raise ValueError("timestamp timezone unknown")
            age = now - stamp.astimezone(timezone.utc)
            if age < timedelta(0):
                raise ValueError("future timestamp")
            if asset in seen:
                continue
            seen.add(asset)
            day += age < timedelta(hours=24)
            hour += age < timedelta(hours=1)
        except (ValueError, TypeError, KeyError, AttributeError):
            invalid += 1
    coverage = f" (latest {limit} rows only)" if rows >= limit else ""
    problems = f"; {invalid} invalid/unscoped rows excluded" if invalid else ""
    return (f"Image assets recorded locally: {hour} in rolling 1h; {day} in rolling 24h"
            f"{coverage}{problems}. Catalog timestamps; may include uploads/imports, "
            "not verified generation-call counts or account-wide usage.")


async def image_activity(profile: Optional[str]) -> str:
    if not profile:
        return "Image activity: unavailable (provider profile identity missing)."
    from .flow import _find_gflow, _run
    try:
        rc, out, _ = await _run(_find_gflow() + ["data", "list", "images", "--profile", profile,
                                               "--limit", "1000", "--json"], timeout=30)
        if rc == 0:
            return image_catalog_summary(out.decode("utf-8"), profile)
    except Exception:
        pass
    return "Image activity: unavailable (gflow image catalog could not be read)."


async def usage_report(daily_budget: Optional[int] = None, profile: str = "default",
                       account_email: Optional[str] = None) -> str:
    # Fetch directly: a same-day tracker value is not a live provider balance.
    from .flow import _fetch_credits_raw

    account_email = account_email or os.environ.get("GMP_FLOW_ACCOUNT") or None
    local = credit_receipt(daily_budget=daily_budget)
    checked = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        data = await _fetch_credits_raw(profile)
    except Exception:
        data = {}
    balance = data.get("credits") if isinstance(data, dict) else None
    email = data.get("email") if isinstance(data, dict) else None
    if account_email and (not isinstance(email, str) or email.casefold() != account_email.casefold()):
        return (f"Account mismatch: requested {account_email}; gflow profile {profile} reports "
                f"{email or 'unidentified account'}. Balance withheld. Select the matching profile "
                "or use the browser account switcher at https://flow.google.com. "
                "Do not combine these accounts' usage.")
    valid = (isinstance(balance, (int, float)) and not isinstance(balance, bool)
             and math.isfinite(balance) and balance >= 0)
    if isinstance(data, dict) and data.get("authenticated") and not data.get("balance_unknown") and valid:
        live = (f"Account: {email or 'unidentified (verify before use)'}\n"
                f"Flow balance: {balance:g} cr (live gflow query; profile: {profile}; checked {checked})")
        images = await image_activity(data.get("profile"))
    else:
        images = "Image activity: unavailable (live account/profile not verified)."
        live = ("Flow balance: unavailable via gflow. Check the signed-in Flow account menu in your browser. "
                "The CLI needs an installed, current gflow-cli and its own signed-in profile; "
                "a signed-in normal browser is a separate session.")
    return (live + "\n" + images + "\n"
            "Images remaining / image reset: unavailable; no verified provider quota or reset timestamp. "
            "Local counts cannot establish remaining images.\n"
            "Daily Flow reset: exact time/timezone not returned by gflow; check this account's Flow menu. "
            "Google says the 50-credit daily refresh is triggered by the first generation, not a "
            "documented universal midnight. Monthly credits refresh on the billing cycle.\n"
            "Unscoped local history (not account-filtered): " + local + "\n"
            "Provider activity: read https://one.google.com/ai/activity in the same signed-in account. "
            "Local totals exclude external spending and cannot substitute for this history.\n"
            "Browser fallback: https://flow.google.com (Account details > credits > activity). "
            "Report charges and refunds separately; do not infer spend from remaining balance. "
            "Gemini/image quotas and chat tokens are not measured.")
