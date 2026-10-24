import os
import re
import asyncio
from typing import Optional

try:
    from mcp.server.mcpserver import MCPServer
    mcp = MCPServer("gemini-media-pass")
except ImportError:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("gemini-media-pass")

from .runner import execute_query, execute_tts
from .config import resolve_model_name, get_default_tier, get_video_tier

@mcp.tool(
    name="ask_gemini_pro",
    description="Consult Google Gemini 3.1 Pro (via Antigravity subscription or API) for deep reasoning, mathematical proofs, alternative approaches, multi-step code planning, or a second opinion. No extra cost on an Antigravity subscription."
)
async def ask_gemini_pro(prompt: str) -> str:
    """Consult Gemini 3.1 Pro for deep reasoning and second opinions."""
    return await execute_query("gemini-3.1-pro-high", prompt)

@mcp.tool(
    name="ask_gemini_flash",
    description="Fast, low-latency task delegation to Google Gemini 3.8 Flash. Ideal for quick summarization, data extraction, and high-speed batch tasks. No extra cost on an Antigravity subscription."
)
async def ask_gemini_flash(prompt: str) -> str:
    """Fast task delegation to Gemini 3.8 Flash."""
    return await execute_query("gemini-3.8-flash-high", prompt)

@mcp.tool(
    name="gemini_vision",
    description="Inspect and analyze an image file (PNG, JPG, WebP, screenshots, diagrams, UI mockups) using Google Gemini's multimodal vision capabilities. Provide the absolute local file path."
)
async def gemini_vision(
    image_path: str,
    question: str = "Analyze this image in detail and describe everything visible.",
    model_tier: Optional[str] = None
) -> str:
    """Inspect and analyze an image file using Gemini Vision."""
    norm_path = os.path.abspath(image_path).replace("\\", "/")
    if not os.path.exists(norm_path):
        return f"Error: Image file not found at '{norm_path}'"

    instruction = (
        f"Please inspect the image file at `{norm_path}` using view_file.\n"
        f"User question / instruction: {question}"
    )
    model = resolve_model_name(model_tier)
    return await execute_query(model, instruction)

@mcp.tool(
    name="gemini_video",
    description=(
        "Watch and analyze a video file (MP4, MOV, MKV, WebM, AVI, short-form shorts/reels, screencasts, animation clips). "
        "Ideal for scene transitions, cut pacing, B-roll discovery, and dialogue verification. "
        "model_tier: 'flash' (default, ultra-fast, 97% cheaper, perfect for scene finding and timestamps) or 'pro' (deep thematic critique and complex narrative reasoning)."
    )
)
async def gemini_video(
    video_path: str,
    question: str = "Watch and analyze this video in detail, describing the visual flow, pacing, and key scenes.",
    model_tier: Optional[str] = None
) -> str:
    """Watch and analyze a video file using Gemini Multimodal Video."""
    norm_path = os.path.abspath(video_path).replace("\\", "/")
    if not os.path.exists(norm_path):
        return f"Error: Video file not found at '{norm_path}'"

    instruction = (
        f"Please inspect and watch the video file at `{norm_path}` using view_file.\n"
        f"User question / instruction: {question}"
    )
    model = resolve_model_name(model_tier, default_to_video=True)
    return await execute_query(model, instruction)

@mcp.tool(
    name="gemini_audio",
    description=(
        "Listen to and analyze an audio file (MP3, WAV, M4A, AAC, FLAC, voice recordings, podcasts, speech, sound effects). "
        "Transcribe spoken words, analyze vocal tone/pacing, identify background sounds, or critique audio quality. "
        "model_tier: 'flash' (default, fast, low-cost) or 'pro' (deep analysis)."
    )
)
async def gemini_audio(
    audio_path: str,
    question: str = "Transcribe and analyze this audio in detail, noting speech, tone, and sound events.",
    model_tier: Optional[str] = None
) -> str:
    """Listen to and analyze an audio file using Gemini Multimodal Audio."""
    norm_path = os.path.abspath(audio_path).replace("\\", "/")
    if not os.path.exists(norm_path):
        return f"Error: Audio file not found at '{norm_path}'"

    instruction = (
        f"Please inspect and listen to the audio file at `{norm_path}` using view_file.\n"
        f"User question / instruction: {question}"
    )
    model = resolve_model_name(model_tier)
    return await execute_query(model, instruction)

@mcp.tool(
    name="gemini_read_document",
    description=(
        "Offload reading and analyzing massive documents, PDFs, logs, or large code files to Google Gemini's 2,000,000 token context window. "
        "model_tier: 'flash' (default, fast, 97% cheaper) or 'pro' (deep reasoning)."
    )
)
async def gemini_read_document(
    file_path: str,
    question: str = "Summarize the key information and extract the most relevant details.",
    model_tier: Optional[str] = None
) -> str:
    """Read and analyze massive documents using Gemini's 2M token context window."""
    norm_path = os.path.abspath(file_path).replace("\\", "/")
    if not os.path.exists(norm_path):
        return f"Error: Document file not found at '{norm_path}'"

    instruction = (
        f"Please inspect the document file at `{norm_path}` using view_file.\n"
        f"User question / instruction: {question}"
    )
    model = resolve_model_name(model_tier)
    return await execute_query(model, instruction)

@mcp.tool(
    name="gemini_multimodal_inspect",
    description=(
        "Universal multimodal inspector for ANY media file: image, audio, video, PDF, or code. "
        "model_tier: 'flash' (default, fast, 97% cheaper) or 'pro' (deep analysis)."
    )
)
async def gemini_multimodal_inspect(
    file_path: str,
    question: str = "Analyze this file in detail and answer any questions.",
    model_tier: Optional[str] = None
) -> str:
    """Inspect any media file (image, audio, video, document) using Gemini Multimodal."""
    norm_path = os.path.abspath(file_path).replace("\\", "/")
    if not os.path.exists(norm_path):
        return f"Error: File not found at '{norm_path}'"

    instruction = (
        f"Please inspect the media file at `{norm_path}` using view_file.\n"
        f"User question / instruction: {question}"
    )
    model = resolve_model_name(model_tier)
    return await execute_query(model, instruction)

@mcp.tool(
    name="gemini_generate_image",
    description="Generate high-resolution photorealistic images, concept art, UI mockups, or digital illustrations using Google Imagen via active Antigravity/Gemini subscription. Supports aspect ratios: '1:1', '16:9', '9:16', '4:3', '3:4', '3:2', '2:3'."
)
async def gemini_generate_image(
    prompt: str,
    aspect_ratio: str = "1:1",
    image_name: str = "generated_image"
) -> str:
    """Generate images using Google Imagen via Antigravity session."""
    clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', image_name).strip('_') or "generated_image"
    valid_ratios = ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"]
    ratio = aspect_ratio if aspect_ratio in valid_ratios else "1:1"

    instruction = (
        f"Please use the generate_image tool to generate an image with:\n"
        f"Prompt: '{prompt}'\n"
        f"ImageName: '{clean_name}'\n"
        f"AspectRatio: '{ratio}'\n"
        f"Once generated, report the exact file path where it was saved."
    )

    response = await execute_query("gemini-3.8-flash-high", instruction, writes=True)
    img_path = find_image_path(response)
    if img_path and os.path.isfile(img_path):
        return f"Image saved: `{img_path}`\n\n{response}"
    if img_path:
        return f"Gemini reported `{img_path}`, but no file exists there.\n\n{response}"
    return response

IMAGE_PATH = re.compile(r"([A-Za-z]:[\\/][^`\r\n\"']+?\.(?:png|jpe?g|webp)|/[^`\r\n\"' ]+?\.(?:png|jpe?g|webp))", re.I)

def find_image_path(text: str) -> Optional[str]:
    """The first image file path in a reply (Windows or POSIX, png, jpg or webp), with forward slashes."""
    m = IMAGE_PATH.search(text or "")
    return m.group(1).replace("\\", "/") if m else None

@mcp.tool(
    name="gemini_text_to_speech",
    description="Convert text into natural spoken audio (.mp3 / .wav) using Google Gemini multimodal audio generation. Choose from voices ('Puck', 'Charon', 'Kore', 'Fenrir', 'Aoede') and customize delivery tone and pacing."
)
async def gemini_text_to_speech(
    text: str,
    voice: str = "Puck",
    output_path: str = "generated_speech.wav",
    style_instruction: str = ""
) -> str:
    """Generate spoken audio from text using Gemini Audio / Neural Speech."""
    return await execute_tts(text, voice, output_path, style_instruction)

@mcp.tool(
    name="gemini_media_pass_guide",
    description=(
        "Interactive settings, cost optimization guide, and troubleshooting assistant for Gemini Media Pass MCP. "
        "Call this to inspect active settings, learn how to switch between Flash and Pro, understand subscription vs API billing, "
        "and get recommended workflows for documentary/video research. Topics: 'overview', 'models', 'billing', 'settings', 'workflows', 'all'."
    )
)
async def gemini_media_pass_guide(topic: str = "overview") -> str:
    """Return interactive help, settings documentation, and cost-saving guidelines."""
    t = topic.strip().lower()
    sections = []

    current_default = get_default_tier()
    current_video = get_video_tier()

    if t in ("overview", "all"):
        sections.append(
            "=== 🎬 Gemini Media Pass: Overview ===\n"
            "This MCP gives Claude and other AI agents access to Google's media stack:\n"
            "• Video & Audio Understanding: gemini_video, gemini_audio\n"
            "• Document & Multimodal Inspection: gemini_read_document, gemini_multimodal_inspect\n"
            "• Image Generation: gemini_generate_image (Imagen 3)\n"
            "• Speech Generation: gemini_text_to_speech\n"
            "• Veo Video Generation: flow_generate_video, flow_extend_video, flow_image_to_video\n"
            "• Google Stitch UI: stitch_create_project, stitch_generate_screen\n"
        )

    if t in ("models", "all"):
        sections.append(
            "=== ⚡ Flash vs. Pro: Cost & Quality Optimization ===\n"
            f"• Current Default Tier : {current_default.upper()}\n"
            f"• Current Video Tier   : {current_video.upper()}\n\n"
            "1. Gemini 1.5 Flash (Recommended for 90% of tasks):\n"
            "   - Cost: ~$0.075 / 1M input tokens (< 1 cent per 5-min video).\n"
            "   - Best for: Timestamp indexing, scene search, OCR/text in video, dialogue transcription,\n"
            "     and high-volume documentary B-roll research (e.g. Simpsons gag sourcing).\n\n"
            "2. Gemini 1.5 Pro:\n"
            "   - Cost: ~$3.50 - $7.00 / 1M input tokens (~$0.35 - $0.70 per 5-min video, ~35-70x more expensive).\n"
            "   - Best for: Deep thematic critique, narrative subtext, subtle animation style comparisons,\n"
            "     and complex multi-step reasoning across hours of footage.\n\n"
            "Tip: You can pass model_tier='flash' or model_tier='pro' directly to any tool call,\n"
            "or set GMP_VIDEO_TIER=flash in your .env file."
        )

    if t in ("billing", "all"):
        sections.append(
            "=== 💳 Subscription Credits vs. Google Cloud API Credits ===\n"
            "1. Google AI Subscription (Free via Antigravity / agy):\n"
            "   - Analysis tools prioritize the Antigravity CLI (agy) under your signed-in Google AI subscription.\n"
            "   - Costs $0.00 in Google Cloud API credits.\n"
            "2. Google Flow (Veo):\n"
            "   - Uses your subscription credits pool. Run 'python -m gemini_media_pass_mcp.auth' to log in.\n"
            "3. Google Cloud API Fallback (GEMINI_API_KEY):\n"
            "   - Only used if agy is not installed or times out.\n"
            "   - Billed pay-as-you-go against your Google Cloud project (gen-lang-client-XXXXXXXXXX).\n"
            "   - To prevent any surprise API charges, comment out GEMINI_API_KEY in ~/.gemini_media_pass.env."
        )

    if t in ("settings", "all"):
        sections.append(
            "=== ⚙️ Configuration & Environment Settings ===\n"
            "Configure these variables in your .env or ~/.gemini_media_pass.env file:\n\n"
            "• GMP_DEFAULT_TIER = flash | pro        (Default model tier for all tools. Default: flash)\n"
            "• GMP_VIDEO_TIER   = flash | pro        (Override model tier specifically for video. Default: flash)\n"
            "• GEMINI_API_MODEL_FLASH = <model_name> (Default: gemini-3.8-flash-high or gemini-1.5-flash)\n"
            "• GEMINI_API_MODEL_PRO   = <model_name> (Default: gemini-3.1-pro-high or gemini-1.5-pro)\n"
            "• GMP_TIMEOUT_SECONDS    = 180          (Timeout for agy and API calls)\n"
            "• GMP_FLOW_MAX_CREDITS   = 40           (Safety limit per video generation call)\n"
            "• GEMINI_API_KEY         = <your_key>   (Optional API key fallback)"
        )

    if t in ("workflows", "all"):
        sections.append(
            "=== 📽️ Best Practice: Documentary & Video Sourcing Workflow ===\n"
            "When sourcing footage (e.g., The Simpsons, historical archives, tutorials):\n\n"
            "Step 1: Rapid Ingestion with Flash (Save 97%):\n"
            "  Use gemini_video(video_path, 'Index timestamps where Homer falls down the gorge', model_tier='flash')\n"
            "  Flash extracts exact seconds, spoken dialogue, and scene tags for pennies.\n\n"
            "Step 2: Narrative Synthesis with Claude / Pro:\n"
            "  Feed only the extracted timestamps, transcripts, and short candidate clips into Claude or Gemini Pro\n"
            "  to write the documentary script or critique the editorial pacing."
        )

    return "\n\n".join(sections) if sections else (
        f"Unknown topic '{topic}'. Available topics: 'overview', 'models', 'billing', 'settings', 'workflows', 'all'."
    )

from .flow import register_flow_tools
register_flow_tools(mcp)

from .stitch import register_stitch_tools
register_stitch_tools(mcp)

def main():
    """Runs the MCP server over stdio transport."""
    asyncio.run(mcp.run_stdio_async())

if __name__ == "__main__":
    main()
