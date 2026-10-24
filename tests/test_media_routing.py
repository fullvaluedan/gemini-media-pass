"""Verify subscription-first routing and paid fallback boundaries without spending."""
import asyncio

import pytest

from gemini_media_pass_mcp import guide, runner
from test_first_try import FakeMCP


def test_media_does_not_call_external_backends_with_key_and_bridge_configured(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("BRIDGE_URL", "http://localhost:9999")
    calls = []
    async def failed_agy(*args):
        calls.append("agy")
        raise runner.AgyEmpty("subscription unavailable")
    def forbidden(*args):
        pytest.fail("media request reached an external backend without opt-in")
    monkeypatch.setattr(runner, "_agy_checked", failed_agy)
    monkeypatch.setattr(runner, "find_agy_binary", lambda: "agy")
    monkeypatch.setattr(runner, "_bridge", forbidden)
    monkeypatch.setattr(runner, "_api", forbidden)
    result = asyncio.run(runner.execute_media_query("find B-roll"))
    assert calls == ["agy"]
    assert "No paid fallback was attempted" in result
    assert "subscription unavailable" in result


def test_paid_opt_in_still_tries_agy_first(monkeypatch):
    calls = []
    async def agy(*args):
        calls.append("agy")
        return "subscription answer"
    def bridge(*args):
        calls.append("bridge")
        return "paid answer"
    monkeypatch.setattr(runner, "_agy_checked", agy)
    monkeypatch.setattr(runner, "_bridge", bridge)
    assert asyncio.run(runner.execute_media_query("video", allow_paid_api=True)) == "subscription answer"
    assert calls == ["agy"]


def test_explicit_pro_and_api_opt_in_preserve_tier_with_custom_agy_alias(monkeypatch):
    calls = []
    monkeypatch.setattr(runner, "AGY_PRO", "custom-deep-alias")
    async def agy(model, content, writes):
        calls.append(("agy", model))
        return ""
    def api(model, content):
        calls.append(("api", model))
        return "deep answer"
    monkeypatch.setattr(runner, "_agy_checked", agy)
    monkeypatch.setattr(runner, "_bridge", lambda *args: "")
    monkeypatch.setattr(runner, "_api", api)
    assert asyncio.run(runner.execute_media_query("critique", "pro", True)) == "deep answer"
    assert calls == [("agy", "custom-deep-alias"), ("api", "pro")]


@pytest.mark.parametrize("tool,suffix,path_arg", [
    ("gemini_video", ".mp4", "video_path"),
    ("gemini_audio", ".wav", "audio_path"),
    ("gemini_multimodal_inspect", ".mp4", "file_path"),
])
def test_public_media_tools_default_flash_and_allow_explicit_pro(monkeypatch, tmp_path, tool, suffix, path_arg):
    from gemini_media_pass_mcp import server
    path = tmp_path / ("clip" + suffix)
    path.write_bytes(b"test")
    calls = []
    async def capture(content, model_tier, allow_paid_api):
        calls.append((model_tier, allow_paid_api))
        return "answer"
    monkeypatch.setattr(server, "execute_media_query", capture)
    fn = getattr(server, tool)
    assert asyncio.run(fn(**{path_arg: str(path)})) == "answer"
    assert asyncio.run(fn(**{path_arg: str(path)}, model_tier="pro", allow_paid_api=True)) == "answer"
    assert calls == [("flash", False), ("pro", True)]


def test_invalid_tier_does_not_dispatch(monkeypatch):
    async def forbidden(*args, **kwargs):
        pytest.fail("invalid tier was dispatched")
    monkeypatch.setattr(runner, "execute_query", forbidden)
    assert "model_tier must be" in asyncio.run(runner.execute_media_query("video", "invalid"))


def test_pro_api_never_silently_substitutes_flash(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test")
    monkeypatch.setattr(runner, "API_PRO", "")
    with pytest.raises(ValueError, match="refusing silent Flash substitution"):
        runner._api("pro", "hello")


def test_guide_registered_and_all_topics_are_callable():
    mcp = FakeMCP()
    guide.register_guide_tools(mcp)
    fn = mcp.tools["gemini_media_pass_guide"]
    for topic in guide.TOPICS:
        assert not asyncio.run(fn(topic)).startswith("Error:")
    assert "allow_paid_api=False" in asyncio.run(fn("settings"))
    assert "ALWAYS call gemini_video(model_tier='flash')" in asyncio.run(fn("models"))
    assert asyncio.run(fn("invalid")).startswith("Error:")
