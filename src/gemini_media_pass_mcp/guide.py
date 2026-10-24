"""Offline operating guide, exposed as a discoverable MCP tool."""
from typing import Literal

from . import runner

TOPICS = ("all", "models", "billing", "settings", "workflows")


def guide_text(topic: str = "all") -> str:
    sections = {
        "models": (
            "For video search/indexing (scenes, timestamps, B-roll, character actions, transcription), "
            "ALWAYS call gemini_video(model_tier='flash'). Flash is the default. Select model_tier='pro' "
            "only when the user explicitly requests deep artistic critique, nuanced subtext or subtle "
            "directorial/thematic comparisons. Audio also defaults to Flash. No automatic tier escalation.\n"
            f"Configured agy Flash alias: {runner.AGY_FLASH}; Pro alias: {runner.AGY_PRO}. "
            f"Paid API Flash model: {runner.API_FLASH}; Pro: {runner.API_PRO or 'not configured'}.\n"
            "Gemini supports native video input; context capacity depends on the selected model and "
            "backend. 1M-context models can handle long video, but this wrapper does not guarantee "
            "full context through every subscription client. Static sampling may miss fast actions. "
            "https://ai.google.dev/gemini-api/docs/video-understanding"
        ),
        "billing": (
            "Video/audio and generic multimodal analysis use local agy first under your Google AI "
            "subscription. They do not call the paid API or bridge unless allow_paid_api=True is "
            "explicitly passed with user authorization. An agy failure stops without paid fallback. "
            "Subscription limits still apply; this route makes no direct API-key charge through this server.\n"
            "Do not route heavy batch media processing to paid API keys unless instructed. API prices "
            "depend on model, modality, resolution, input/output and reasoning tokens. Do not promise "
            "a fixed 97% saving or <$0.01 per 5-minute clip. "
            "https://ai.google.dev/gemini-api/docs/pricing\n"
            "Veo generation uses flow_* tools and Flow credits. Check flow_doctor or flow_get_credits "
            "first; use gemini_usage once after a batch. Image quotas and reset times are separate "
            "from the Flow balance. Unavailable counters are not zero."
        ),
        "settings": (
            "gemini_video / gemini_audio / gemini_multimodal_inspect: model_tier='flash'|'pro' "
            "(default flash), allow_paid_api=False (default; blocks both API and bridge).\n"
            "AGY_PATH selects agy. GMP_AGY_MODEL_FLASH / GMP_AGY_MODEL_PRO override agy aliases. "
            "GEMINI_API_MODEL_FLASH / GEMINI_API_MODEL_PRO select external fallback models. "
            "A Pro API model must be configured explicitly; it is never silently mapped to Flash. "
            "GEMINI_API_KEY alone does not authorize paid fallback for media analysis. "
            "BRIDGE_URL alone does not override the media fallback block. These rules apply to "
            "analysis, not gemini_text_to_speech, whose API-key/edge-tts behavior is unchanged.\n"
            "GMP_TIMEOUT_SECONDS and GMP_AGY_PING_SECONDS control timeouts; analysis runs in "
            "agy's read-only sandbox. GMP_FLOW_ACCOUNT checks the expected usage account. "
            "GMP_CREDIT_RECEIPTS defaults off; show one batch-end usage report instead."
        ),
        "workflows": (
            "For help/settings/tool options, call gemini_media_pass_guide(topic='all') or one of "
            "models, billing, settings, workflows. The guide is local and makes no provider call.\n"
            "Search/index video: gemini_video(video_path=..., question=..., model_tier='flash'). "
            "Explicit deep critique: same tool with model_tier='pro'. Audio transcription: "
            "gemini_audio(audio_path=..., model_tier='flash'). Leave allow_paid_api=False unless "
            "the user authorizes external fallback. Do not switch to the generic inspector to bypass it.\n"
            "Generate Veo: check flow_doctor or flow_get_credits, then flow_generate_video / "
            "flow_extend_video. After the requested batch finishes, call gemini_usage once. "
            "Verify the account; use the signed-in browser workflow for provider transaction history."
        ),
    }
    if topic not in TOPICS:
        return "Error: topic must be all, models, billing, settings, or workflows."
    selected = sections if topic == "all" else {topic: sections[topic]}
    return "\n\n".join(f"{name.upper()}\n{text}" for name, text in selected.items())


def register_guide_tools(mcp):
    @mcp.tool(name="gemini_media_pass_guide", description=(
        "Call first for help, settings, model selection, billing or tool options. "
        "Topics: all, models, billing, settings, workflows. Local guide; no provider calls."))
    async def gemini_media_pass_guide(
        topic: Literal["all", "models", "billing", "settings", "workflows"] = "all"
    ) -> str:
        return guide_text(topic)
