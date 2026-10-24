import pytest
import asyncio
from gemini_media_pass_mcp import config, server

def test_resolve_model_name_explicit():
    assert config.resolve_model_name("flash") == "gemini-3.8-flash-high"
    assert config.resolve_model_name("pro") == "gemini-3.1-pro-high"

def test_resolve_model_name_env_defaults(monkeypatch):
    monkeypatch.delenv("GMP_DEFAULT_TIER", raising=False)
    monkeypatch.delenv("GMP_VIDEO_TIER", raising=False)
    # Default is flash
    assert config.resolve_model_name() == "gemini-3.8-flash-high"

    # Set default tier to pro
    monkeypatch.setenv("GMP_DEFAULT_TIER", "pro")
    assert config.resolve_model_name() == "gemini-3.1-pro-high"

    # Video tier overrides default
    monkeypatch.setenv("GMP_VIDEO_TIER", "flash")
    assert config.resolve_model_name(default_to_video=True) == "gemini-3.8-flash-high"
    assert config.resolve_model_name(default_to_video=False) == "gemini-3.1-pro-high"

@pytest.mark.anyio
async def test_gemini_media_pass_guide_topics():
    overview = await server.gemini_media_pass_guide("overview")
    assert "Gemini Media Pass: Overview" in overview
    assert "gemini_video" in overview

    models = await server.gemini_media_pass_guide("models")
    assert "Flash vs. Pro" in models
    assert "Gemini 1.5 Flash" in models

    billing = await server.gemini_media_pass_guide("billing")
    assert "Subscription Credits" in billing

    settings = await server.gemini_media_pass_guide("settings")
    assert "GMP_DEFAULT_TIER" in settings

    workflows = await server.gemini_media_pass_guide("workflows")
    assert "Documentary" in workflows or "Simpsons" in workflows

    all_topics = await server.gemini_media_pass_guide("all")
    assert "Flash vs. Pro" in all_topics
    assert "Subscription Credits" in all_topics

    unknown = await server.gemini_media_pass_guide("nonexistent_topic")
    assert "Unknown topic" in unknown

@pytest.mark.anyio
async def test_gemini_video_passes_model_tier(monkeypatch, tmp_path):
    video_file = tmp_path / "test.mp4"
    video_file.write_bytes(b"dummy video data")

    called_models = []

    async def fake_execute_query(model, instruction, writes=False):
        called_models.append(model)
        return "Fake video response"

    monkeypatch.setattr(server, "execute_query", fake_execute_query)

    # Call with explicit flash
    res1 = await server.gemini_video(str(video_file), "Find Homer", model_tier="flash")
    assert res1 == "Fake video response"
    assert called_models[-1] == "gemini-3.8-flash-high"

    # Call with explicit pro
    res2 = await server.gemini_video(str(video_file), "Analyze director style", model_tier="pro")
    assert res2 == "Fake video response"
    assert called_models[-1] == "gemini-3.1-pro-high"
