import asyncio
import json
from datetime import datetime, timedelta, timezone

import pytest

from gemini_media_pass_mcp import flow, receipts, usage
from test_first_try import FakeMCP


@pytest.fixture(autouse=True)
def no_local_ledger(monkeypatch, tmp_path):
    monkeypatch.setenv("GMP_FLOW_LEDGER", str(tmp_path / "missing.jsonl"))
    monkeypatch.delenv("GMP_FLOW_DAILY_BUDGET", raising=False)
    monkeypatch.delenv("GMP_FLOW_ACCOUNT", raising=False)


@pytest.mark.parametrize("balance", [0, 50])
def test_live_query_works_without_local_history(monkeypatch, balance):
    profiles = []
    async def fetch(profile):
        profiles.append(profile)
        return {"authenticated": True, "credits": balance, "email": "work@example.com"}
    monkeypatch.setattr(flow, "_fetch_credits_raw", fetch)
    monkeypatch.setattr(flow.CreditTracker, "load", lambda: {"current_credits": 9999})
    result = asyncio.run(usage.usage_report(profile="work"))
    assert profiles == ["work"]
    assert f"Flow balance: {balance} cr (live" in result
    assert "9999" not in result
    assert "local usage unknown" in result
    assert "one.google.com/ai/activity" in result
    assert "work@example.com" in result


def test_account_mismatch_withholds_other_accounts_balance(monkeypatch):
    async def fetch(profile):
        return {"authenticated": True, "credits": 671, "email": "other@example.com"}
    monkeypatch.setattr(flow, "_fetch_credits_raw", fetch)
    result = asyncio.run(usage.usage_report(account_email="wanted@example.com"))
    assert "Account mismatch" in result and "Balance withheld" in result
    assert "671" not in result


def test_expected_account_matches_case_insensitively(monkeypatch):
    async def fetch(profile):
        return {"authenticated": True, "credits": 50, "email": "Me@example.com"}
    monkeypatch.setattr(flow, "_fetch_credits_raw", fetch)
    assert "Flow balance: 50 cr" in asyncio.run(usage.usage_report(account_email="me@example.com"))


def test_configured_account_and_explicit_override(monkeypatch):
    async def fetch(profile):
        return {"authenticated": True, "credits": 50, "email": "me@example.com"}
    monkeypatch.setattr(flow, "_fetch_credits_raw", fetch)
    monkeypatch.setenv("GMP_FLOW_ACCOUNT", "other@example.com")
    assert "Account mismatch" in asyncio.run(usage.usage_report())
    assert "Flow balance: 50 cr" in asyncio.run(usage.usage_report(account_email="me@example.com"))


@pytest.mark.parametrize("data", [
    {"authenticated": True}, {"authenticated": True, "credits": None},
    {"authenticated": True, "credits": True}, {"authenticated": True, "credits": -1},
    {"authenticated": True, "credits": float("nan")},
    {"authenticated": True, "credits": 0, "balance_unknown": True},
    {"authenticated": False, "credits": 50},
])
def test_unavailable_balance_never_becomes_zero(monkeypatch, data):
    async def fetch(profile):
        return data
    monkeypatch.setattr(flow, "_fetch_credits_raw", fetch)
    result = asyncio.run(usage.usage_report())
    assert "Flow balance: unavailable" in result
    assert "Flow balance: 0" not in result
    assert "flow.google.com" in result


def test_provider_failure_retains_browser_fallback(monkeypatch):
    async def fetch(profile):
        raise FileNotFoundError("missing cli")
    monkeypatch.setattr(flow, "_fetch_credits_raw", fetch)
    result = asyncio.run(usage.usage_report())
    assert "Flow balance: unavailable" in result
    # The default Windows console must be able to print the recovery message.
    result.encode("cp1252")


def test_mcp_and_cli_use_live_report(monkeypatch, capsys):
    async def fetch(profile):
        return {"authenticated": True, "credits": 50}
    monkeypatch.setattr(flow, "_fetch_credits_raw", fetch)
    mcp = FakeMCP()
    receipts.register_receipt_tools(mcp)
    assert "Flow balance: 50 cr" in asyncio.run(mcp.tools["gemini_usage"]())
    monkeypatch.setattr("sys.argv", ["gemini-usage"])
    receipts.main()
    assert "Flow balance: 50 cr" in capsys.readouterr().out


def test_image_catalog_counts_unique_assets_in_rolling_windows():
    now = datetime(2026, 10, 24, 5, tzinfo=timezone.utc)
    def row(asset, hours, profile="work"):
        return json.dumps({"media_id": asset, "profile": profile,
                           "created_at": (now - timedelta(hours=hours)).isoformat()})
    body = "\n".join([row("a", .5), row("a", .5), row("b", 2), row("c", 25),
                       row("other", .5, "other"), row("future", -1), "null"])
    result = usage.image_catalog_summary(body, "work", now=now)
    assert "1 in rolling 1h; 2 in rolling 24h" in result
    assert "3 invalid/unscoped rows excluded" in result
    assert "not verified generation-call counts" in result


def test_naive_image_timestamp_is_not_assumed_to_be_utc():
    body = json.dumps({"media_id": "a", "profile": "work", "created_at": "2026-10-24T05:00:00"})
    assert "1 invalid/unscoped" in usage.image_catalog_summary(body, "work")


def test_image_activity_uses_resolved_profile_and_no_generation_commands(monkeypatch):
    calls = []
    async def run(cmd, timeout):
        calls.append((cmd, timeout))
        return 0, b"", b""
    monkeypatch.setattr(flow, "_find_gflow", lambda: ["gflow"])
    monkeypatch.setattr(flow, "_run", run)
    result = asyncio.run(usage.image_activity("work"))
    assert calls == [(["gflow", "data", "list", "images", "--profile", "work", "--limit", "1000", "--json"], 30)]
    assert "0 in rolling 1h" in result
    assert "unavailable" in asyncio.run(usage.image_activity(None))


def test_catalog_cap_is_explicit():
    row = json.dumps({"media_id": "a", "profile": "work", "created_at": datetime.now(timezone.utc).isoformat()})
    assert "latest 1 rows only" in usage.image_catalog_summary(row, "work", limit=1)
