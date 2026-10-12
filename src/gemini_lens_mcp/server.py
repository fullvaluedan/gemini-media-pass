import os
import re
import asyncio
from typing import Optional

try:
    from mcp.server.mcpserver import MCPServer
    mcp = MCPServer("gemini-lens")
except ImportError:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("gemini-lens")

from .runner import execute_query, execute_tts

@mcp.tool(
    name="ask_gemini_pro",
    description="Consult Google Gemini 3.1 Pro (via Antigravity subscription or API) for deep reasoning, mathematical proofs, alternative approaches, multi-step code planning, or a second opinion. $0 cost when using subscription."
)
async def ask_gemini_pro(prompt: str) -> str:
    """Consult Gemini 3.1 Pro for deep reasoning and second opinions."""
    return await execute_query("gemini-3.1-pro-high", prompt)

@mcp.tool(
    name="ask_gemini_flash",
    description="Fast, low-latency task delegation to Google Gemini 3.8 Flash. Ideal for quick summarization, data extraction, and high-speed batch tasks. $0 cost when using subscription."
)
async def ask_gemini_flash(prompt: str) -> str:
    """Fast task delegation to Gemini 3.8 Flash."""
    return await execute_query("gemini-3.8-flash-high", prompt)

@mcp.tool(
    name="gemini_vision",
    description="Inspect and analyze an image file (PNG, JPG, WebP, screenshots, diagrams, UI mockups) using Google Gemini's multimodal vision capabilities. Provide the absolute local file path."
)
async def gemini_vision(image_path: str, question: str = "Analyze this image in detail and describe everything visible.") -> str:
    """Inspect and analyze an image file using Gemini Vision."""
    norm_path = os.path.abspath(image_path).replace("\\", "/")
    if not os.path.exists(norm_path):
        return f"Error: Image file not found at '{norm_path}'"

    instruction = (
        f"Please inspect the image file at `{norm_path}` using view_file.\n"
        f"User question / instruction: {question}"
    )
    return await execute_query("gemini-3.8-flash-high", instruction)

@mcp.tool(
    name="gemini_audio",
    description="Listen to and analyze an audio file (MP3, WAV, M4A, AAC, FLAC, voice recordings, podcasts, speech, sound effects) using Google Gemini's native audio understanding. Transcribe spoken words, analyze vocal tone/pacing, identify background sounds, or critique audio quality. Provide the absolute local file path."
)
async def gemini_audio(audio_path: str, question: str = "Transcribe and analyze this audio in detail, noting speech, tone, and sound events.") -> str:
    """Listen to and analyze an audio file using Gemini Multimodal Audio."""
    norm_path = os.path.abspath(audio_path).replace("\\", "/")
    if not os.path.exists(norm_path):
        return f"Error: Audio file not found at '{norm_path}'"

    instruction = (
        f"Please inspect and listen to the audio file at `{norm_path}` using view_file.\n"
        f"User question / instruction: {question}"
    )
    return await execute_query("gemini-3.1-pro-high", instruction)

@mcp.tool(
    name="gemini_video",
    description="Watch and analyze a video file (MP4, MOV, MKV, WebM, AVI, short-form shorts/reels, screencasts, animation clips) using Google Gemini's native video understanding. Analyze visual scene transitions, cut pacing, B-roll timing, on-screen text, presenter body language, and temporal story flow. Provide the absolute local file path."
)
async def gemini_video(video_path: str, question: str = "Watch and analyze this video in detail, describing the visual flow, pacing, and key scenes.") -> str:
    """Watch and analyze a video file using Gemini Multimodal Video."""
    norm_path = os.path.abspath(video_path).replace("\\", "/")
    if not os.path.exists(norm_path):
        return f"Error: Video file not found at '{norm_path}'"

    instruction = (
        f"Please inspect and watch the video file at `{norm_path}` using view_file.\n"
        f"User question / instruction: {question}"
    )
    return await execute_query("gemini-3.1-pro-high", instruction)

@mcp.tool(
    name="gemini_read_document",
    description="Offload reading and analyzing massive documents, PDFs, logs, or large code files to Google Gemini's 2,000,000 token context window. Provide the absolute local file path."
)
async def gemini_read_document(file_path: str, question: str = "Summarize the key information and extract the most relevant details.") -> str:
    """Read and analyze massive documents using Gemini's 2M token context window."""
    norm_path = os.path.abspath(file_path).replace("\\", "/")
    if not os.path.exists(norm_path):
        return f"Error: Document file not found at '{norm_path}'"

    instruction = (
        f"Please inspect the document file at `{norm_path}` using view_file.\n"
        f"User question / instruction: {question}"
    )
    return await execute_query("gemini-3.1-pro-high", instruction)

@mcp.tool(
    name="gemini_multimodal_inspect",
    description="Universal multimodal inspector for ANY media file: image, audio, video, PDF, or code. Automatically routes to Gemini Pro's native multimodal engine. Provide the absolute local file path."
)
async def gemini_multimodal_inspect(file_path: str, question: str = "Analyze this file in detail and answer any questions.") -> str:
    """Inspect any media file (image, audio, video, document) using Gemini Multimodal Pro."""
    norm_path = os.path.abspath(file_path).replace("\\", "/")
    if not os.path.exists(norm_path):
        return f"Error: File not found at '{norm_path}'"

    instruction = (
        f"Please inspect the media file at `{norm_path}` using view_file.\n"
        f"User question / instruction: {question}"
    )
    return await execute_query("gemini-3.1-pro-high", instruction)

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

    response = await execute_query("gemini-3.8-flash-high", instruction)

    # Extract file path if present
    match = re.search(r'([A-Za-z]:\\[^`\r\n]+\.jpg)', response)
    if match:
        img_path = match.group(1).replace("\\", "/")
        return (
            f"### Image Generated Successfully!\n\n"
            f"- **File Path:** `{img_path}`\n"
            f"- **File Link:** [{clean_name}.jpg](file:///{img_path})\n\n"
            f"![{clean_name}](file:///{img_path})\n\n"
            f"{response}"
        )
    return response

@mcp.tool(
    name="gemini_text_to_speech",
    description="Convert text into natural spoken audio (.mp3 / .wav) using Google Gemini multimodal audio generation. Choose from voices ('Puck', 'Charon', 'Kore', 'Fenrir', 'Aoede') and customize delivery tone and pacing. $0 cost."
)
async def gemini_text_to_speech(
    text: str,
    voice: str = "Puck",
    output_path: str = "generated_speech.mp3",
    style_instruction: str = "Speak clearly in a natural, engaging tone."
) -> str:
    """Generate spoken audio from text using Gemini Audio / Neural Speech."""
    return await execute_tts(text, voice, output_path, style_instruction)

from .flow import register_flow_tools
register_flow_tools(mcp)

def main():
    """Runs the MCP server over stdio transport."""
    asyncio.run(mcp.run_stdio_async())

if __name__ == "__main__":
    main()
