"""Live Flow balance, kept separate from partial local spend history."""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Optional

from .receipts import credit_receipt


async def usage_report(daily_budget: Optional[int] = None, profile: str = "default",
                       account_email: Optional[str] = None) -> str:
    # Fetch directly: a same-day tracker value is not a live provider balance.
    from .flow import _fetch_credits_raw

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
    else:
        live = ("Flow balance: unavailable via gflow. Check the signed-in Flow account menu in your browser. "
                "The CLI needs an installed, current gflow-cli and its own signed-in profile; "
                "a signed-in normal browser is a separate session.")
    return (live + "\nUnscoped local history (not account-filtered): " + local + "\n"
            "Provider activity: read https://one.google.com/ai/activity in the same signed-in account. "
            "Local totals exclude external spending and cannot substitute for this history.\n"
            "Browser fallback: https://flow.google.com (Account details > credits > activity). "
            "Report charges and refunds separately; do not infer spend from remaining balance. "
            "Gemini/image quotas and chat tokens are not measured.")
