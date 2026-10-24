"""Local ledger accounting and opt-in behavior; no devices or provider calls."""
import asyncio
import json
from datetime import datetime, timedelta, timezone

import pytest

from gemini_media_pass_mcp import ledger, receipts
from test_first_try import FakeMCP, fake_gflow, tools


@pytest.fixture
def history(monkeypatch, tmp_path):
    path = tmp_path / "ledger.jsonl"
    monkeypatch.setenv("GMP_FLOW_LEDGER", str(path))
    monkeypatch.delenv("GMP_CREDIT_RECEIPTS", raising=False)
    monkeypatch.delenv("GMP_FLOW_DAILY_BUDGET", raising=False)
    now = datetime.now(timezone.utc)
    entries = [
        {"time": (now - timedelta(hours=hours)).isoformat(), "tool": "flow_generate_video",
         "status": status, "credits": cost, "estimated": estimated}
        for hours, cost, status, estimated in [(1, 10, "ok", False), (25, 20, "ok", True),
                                               (721, 99, "ok", False), (-1, 99, "ok", False),
                                               (2, 100, "failed", False)]
    ]
    path.write_text("\n".join(json.dumps(e) for e in entries), encoding="utf-8")
    return path


def test_rolling_windows_and_personal_budget(history):
    result = receipts.credit_receipt(10, daily_budget=50)
    assert "Job: 10 cr" in result
    assert "24h spent: 10 cr" in result
    assert "30d spent: ~30 cr" in result
    assert "24h budget left: 40/50 cr" in result
    assert "Flow Left" not in result and "Img" not in result


def test_opt_in_and_explicit_override(history, monkeypatch):
    assert receipts.append_credit_footer("result") == "result"
    monkeypatch.setenv("GMP_CREDIT_RECEIPTS", "on")
    assert receipts.append_credit_footer("result", enabled=False) == "result"
    assert "\n---\n[Flow local only" in receipts.append_credit_footer("result")
    monkeypatch.setenv("GMP_CREDIT_RECEIPTS", "off")
    assert "Job: ~20 cr" in receipts.append_credit_footer("result", 20, estimated=True, enabled=True)


def test_bad_records_are_visible_but_do_not_break_generation(history):
    with history.open("a", encoding="utf-8") as f:
        f.write('\nnull\n{"time": "oops"}\nnot-json\n')
    assert "3 invalid record(s) skipped" in receipts.credit_receipt()
    assert receipts.append_credit_footer("saved", enabled=True).startswith("saved\n")


def test_missing_and_unreadable_history(history):
    history.unlink()
    assert "usage unknown" in receipts.credit_receipt()
    assert "0 cr" not in receipts.credit_receipt()
    history.mkdir()
    assert "unavailable" in receipts.credit_receipt()


def test_usage_cli(history, monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["gemini-usage", "--local-only", "--daily-budget", "50"])
    receipts.main()
    assert "40/50 cr" in capsys.readouterr().out
    monkeypatch.setattr("sys.argv", ["gemini-usage", "--daily-budget", "0"])
    with pytest.raises(SystemExit) as error:
        receipts.main()
    assert error.value.code == 2


def test_invalid_budget_does_not_replace_result(history, monkeypatch):
    monkeypatch.setenv("GMP_FLOW_DAILY_BUDGET", "oops")
    assert receipts.append_credit_footer("saved", enabled=True).startswith("saved\n---\n")
    mcp = FakeMCP()
    receipts.register_receipt_tools(mcp)
    assert asyncio.run(mcp.tools["flow_credit_receipt"]()).startswith("Error:")
    assert "40/50 cr" in asyncio.run(mcp.tools["flow_credit_receipt"](50))
    assert asyncio.run(mcp.tools["flow_credit_receipt"](0)).startswith("Error:")


@pytest.mark.parametrize("tool", ["flow_generate_video", "flow_extend_video"])
def test_generation_receipt_uses_reported_cost(tools, monkeypatch, tmp_path, tool):
    fake_gflow(monkeypatch, out=b'{"files": [], "credits_spent": 10}')
    kwargs = {"prompt": "a quiet beach", "include_credit_receipt": True}
    if tool == "flow_generate_video":
        kwargs["output_dir"] = str(tmp_path)
    else:
        kwargs.update(media_id="clip", project_id="project")
    result = asyncio.run(tools[tool](**kwargs))
    assert "Job: 10 cr" in result and "24h spent: 10 cr" in result
    assert "~10" not in result


def test_generation_default_off_and_failure_keeps_error(tools, monkeypatch, tmp_path):
    fake_gflow(monkeypatch, out=b'{"files": []}')
    result = asyncio.run(tools["flow_generate_video"]("beach", output_dir=str(tmp_path)))
    assert "Flow local only" not in result
    fake_gflow(monkeypatch, rc=1, err=b"socket closed")
    result = asyncio.run(tools["flow_generate_video"]("beach", output_dir=str(tmp_path), include_credit_receipt=True))
    assert "failed" in result and "Job:" not in result
