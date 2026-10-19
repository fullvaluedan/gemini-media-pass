"""No network, no agy, no gflow: every external call is replaced."""
import asyncio
import io
import wave

import pytest

from gemini_media_pass_mcp import config, flow, runner


def test_agy_never_skips_permissions_by_default(monkeypatch):
    monkeypatch.delenv("GMP_AGY_UNSAFE", raising=False)
    read = runner.agy_command("agy", "m")
    write = runner.agy_command("agy", "m", writes=True)
    assert "--dangerously-skip-permissions" not in read + write
    assert "--sandbox" in read and "--sandbox" in write
    assert read[read.index("--mode") + 1] == "plan"          # analysis tools are read-only
    assert "--mode" not in write                             # only file-creating tools may write


def test_unsafe_mode_is_explicit_opt_in(monkeypatch):
    monkeypatch.setenv("GMP_AGY_UNSAFE", "1")
    assert "--dangerously-skip-permissions" in runner.agy_command("agy", "m")


def test_bridge_is_off_unless_configured(monkeypatch):
    monkeypatch.delenv("BRIDGE_URL", raising=False)
    assert config.get_bridge_url() == ""
    called = []
    monkeypatch.setattr(runner.urllib.request, "urlopen", lambda *a, **k: called.append(a))
    assert runner._bridge("m", "hello") == ""
    assert called == []


def test_api_key_goes_in_header_not_url(monkeypatch):
    seen = {}

    class Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(req, timeout=None):
        seen["url"], seen["headers"] = req.full_url, dict(req.header_items())
        return Resp(b'{"candidates": [{"content": {"parts": [{"text": "hi"}]}}]}')

    monkeypatch.setenv("GEMINI_API_KEY", "SECRET123")
    monkeypatch.setattr(runner.urllib.request, "urlopen", fake_urlopen)
    assert runner._api("gemini-flash", "hello") == "hi"
    assert "SECRET123" not in seen["url"] and "key=" not in seen["url"]
    assert seen["headers"].get("X-goog-api-key") == "SECRET123"


def test_all_backends_failing_reports_each_error(monkeypatch):
    monkeypatch.delenv("BRIDGE_URL", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    async def boom(*a, **k):
        raise TimeoutError("agy gave no answer")

    monkeypatch.setattr(runner, "_agy", boom)
    out = asyncio.run(runner.execute_query("m", "hi"))
    assert out.startswith("Error: Gemini did not answer") and "agy: TimeoutError" in out


def test_pcm_becomes_a_real_wav():
    pcm = b"\x00\x00\x10\x00" * 2400
    with wave.open(io.BytesIO(runner.pcm_to_wav(pcm, 24000))) as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (1, 2, 24000, 4800)


def test_flow_spend_cap_refuses_before_spending():
    assert flow.spend_check(20, None) is None
    msg = flow.spend_check(80, None)
    assert msg.startswith("Refused") and "Nothing was spent" in msg
    assert flow.spend_check(80, 80) is None


def test_gflow_timeout_is_reported(monkeypatch):
    rc, out, err = asyncio.run(flow._run(["python", "-c", "import time; time.sleep(5)"], timeout=1))
    assert rc == 124 and b"did not finish" in err


@pytest.mark.parametrize("text,path", [
    ("Saved to C:\\Users\\me\\img.png done", "C:/Users/me/img.png"),
    ("saved at /home/me/out/cover.jpeg", "/home/me/out/cover.jpeg"),
    ("no file here", None),
])
def test_image_path_found_on_any_os(text, path):
    from gemini_media_pass_mcp.server import find_image_path
    assert find_image_path(text) == path


def test_unreadable_balance_is_not_signed_out(monkeypatch, tmp_path):
    # gflow issue #795: the session works but the credits call fails. That must not block generation.
    async def fake_run(cmd, timeout=120):
        return 1, b'{"status": "fail", "error": {"type": "https://gflow-cli.dev/errors/aisandbox-auth"}}', b""

    monkeypatch.setattr(flow, "_run", fake_run)
    monkeypatch.setattr(flow, "TRACKER_FILE", tmp_path / "tracker.json")
    data = asyncio.run(flow.CreditTracker.get_or_sync(force=True))
    assert data["authenticated"] is True and data["balance_unknown"] is True
    assert not (tmp_path / "tracker.json").exists()     # no fake balance stored


def test_missing_profile_is_still_signed_out(monkeypatch):
    async def fake_run(cmd, timeout=120):
        return 1, b"", b"No profiles found"

    monkeypatch.setattr(flow, "_run", fake_run)
    assert asyncio.run(flow._fetch_credits_raw())["authenticated"] is False
