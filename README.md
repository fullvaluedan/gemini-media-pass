# 🔍 Gemini Lens MCP

> **Give Claude, Hermes, and Cursor native eyes, ears, voice, video understanding, and Imagen creative generation — powered by Google Gemini.**  
> Supports both **100% Free Google Accounts** and **Google AI Pro Subscriptions ($20/mo)**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Standard](https://img.shields.io/badge/MCP-Protocol-purple.svg)](https://modelcontextprotocol.io/)

---

## 💡 What is Gemini Lens?

While Claude and Hermes are elite at coding and deep reasoning, they lack native video comprehension, audio processing, and direct creative generation. Gemini Lens acts as a high-powered multimodal coprocessor:

- 🎬 **Video Flow & Narrative Analysis** — Inspect `.mp4`, `.mov`, `.webm`, `.mkv` files directly. Gemini reviews scene transitions, camera pacing, B-roll timing, and visual continuity without blowing up Claude's token window.
- 🎨 **Imagen Image Generation** — Generate photorealistic assets, UI concepts, and marketing graphics in any aspect ratio (`1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`).
- 🎙️ **Audio & Tone Understanding** — Listen to speech, podcasts, or sound effects (`.mp3`, `.wav`, `.m4a`) for transcription, vocal tone critique, and audio quality checks.
- 🗣️ **Text-to-Speech (TTS) Generation** — Convert text and scripts into natural spoken audio (`.mp3` / `.wav`) using Gemini's native audio generation and neural voices (`Puck`, `Charon`, `Kore`, `Fenrir`, `Aoede`).
- 📚 **2,000,000 Token Document Reading** — Offload massive PDFs, codebases, or dump logs into Gemini's 2M-token window.
- 🧠 **Dual-Model Delegation** — Tap Gemini 3.1 Pro for deep second opinions or Gemini 3.8 Flash for ultra-fast batch processing.

---

## ❓ Do I need a Google AI Pro subscription, or can I use the Free Plan?

### **You can use the Free Plan! No paid subscription is required.**

Gemini Lens is designed so anyone with a standard, free Google account can plug and play without entering a credit card:

| Resource / Feature | 🆓 Free Plan (Standard Google Account) | 💎 Google AI Pro / Subscription ($20/mo) |
|---|---|---|
| **Monthly Cost** | **$0 / Free** (No credit card needed) | **$20 / month** (Google One AI Premium) |
| **Daily Request Limit** | **Up to 1,500 requests / day** (15 req/min) | 🚀 High-throughput priority queue |
| **Max Context Window** | **1,000,000 tokens** per query | **2,000,000 tokens** per query |
| **Video Analysis** | **Up to ~1 hour video per query** (~900k tokens) | High-speed processing for long videos |
| **Audio Understanding** | **Hours of audio** (speech + tone + sounds) | Priority high-throughput processing |
| **Text-to-Speech (TTS)** | ✅ **Free** (Gemini Audio + Neural Fallback) | Priority generation queue / credits |
| **Document Reading** | **~500-page PDFs / massive codebases** | Full 2M-token document digests |
| **Imagen 3 Image Gen** | Supported (standard rate caps, ~30–50/day) | High-throughput generation volume |
| **Gemini 3.8 Flash** | **1,500 calls / day** (ultra-fast) | Priority queue throughput |
| **Gemini 3.1 Pro** | ~50 reasoning queries / day | 🧠 Uncapped deep reasoning & complex proofs |
| **Setup Methods** | `agy login` (Free) OR `GEMINI_API_KEY` (Free) | `agy login` with subscribed Google account |

> **Summary:** A free user gets **1,500 requests per day** and **1 Million tokens per request**. You can analyze dozens of videos, podcasts, and massive documents every single day without paying a cent. The $20/month plan is only needed if you require uncapped Gemini 3.1 Pro deep-reasoning or extreme high-concurrency workloads.

---

## 📊 Token Savings: Claude vs. Gemini Lens

Claude cannot read video files natively. In order for Claude to "see" a video, frames must be extracted as images:

| Video Length | Claude Frame Extraction (1 fps) | Gemini Lens External Processing | Claude Tokens Saved | Cost Saved (Claude Sonnet) |
|---|---|---|---|---|
| **30 Seconds** | 30 images = **48,000 tokens** | **~500 tokens** (markdown report) | **~47,500 tokens** | ~$0.15 |
| **2 Minutes** | 120 images = **192,000 tokens** *(Near 200k limit!)* | **~750 tokens** (markdown report) | **~191,250 tokens** | ~$0.58 |
| **5 Minutes** | 300 images = **480,000 tokens** *(CRASHES Claude)* | **~1,000 tokens** (markdown report) | **479,000 tokens** | Avoids context crash |
| **15 Minutes** | 900 images = **1,440,000 tokens** *(Impossible)* | **~1,200 tokens** (markdown report) | **1,438,800 tokens** | Enables impossible workflows |

---

## 🛠️ Complete Tool Inventory (9 Tools)

| Tool | Parameters | Description | Best For |
|---|---|---|---|
| `gemini_video` | `video_path`, `question` | Watch & analyze video files (`.mp4`, `.mov`, `.webm`, `.mkv`). Inspects temporal scene flow, cut pacing, B-roll timing, camera movement, and on-screen text. | Gameplay reviews, video edit critiques, bug screencasts, tutorial breakdowns. |
| `gemini_text_to_speech` | `text`, `voice`, `output_path`, `style_instruction` | Convert text and scripts into high-quality spoken audio (`.mp3` / `.wav`) using Gemini multimodal audio output or neural speech. Supports voices: `Puck`, `Charon`, `Kore`, `Fenrir`, `Aoede`. | Voiceovers, tutorial narration, accessibility, automated podcast reads. |
| `gemini_generate_image` | `prompt`, `aspect_ratio`, `image_name` | Generate photorealistic images and concept art via Google Imagen. Supports aspect ratios: `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`. | UI mockups, game concept art, website banners, social thumbnails. |
| `gemini_audio` | `audio_path`, `question` | Listen to and analyze raw audio (`.mp3`, `.wav`, `.m4a`). Transcribes speech, critiques vocal delivery/pacing, identifies emotion/tone, and flags background sounds. | Podcast editing, vocal delivery coaching, sound effect inspection. |
| `gemini_vision` | `image_path`, `question` | Inspect UI screenshots, wireframes, architectural diagrams, and photos with high-precision multimodal vision. | Frontend bug hunting, diagram analysis, UI comparison against design specs. |
| `gemini_read_document` | `file_path`, `question` | Ingest massive documents, books, compliance manuals, and logs using Gemini's 2,000,000 token context window. | Giant log analysis, legal/tax document reviews, massive code repositories. |
| `gemini_multimodal_inspect` | `file_path`, `question` | Universal router: automatically inspects any media file (video, audio, image, PDF, or code) and returns a detailed analysis. | Quick inspection when file type varies. |
| `ask_gemini_pro` | `prompt` | Delegate complex tasks to Google Gemini 3.1 Pro. Deep multi-step reasoning, mathematical proofs, alternative architecture options, and second opinions. | Complex algorithm validation, refactoring architecture, code second opinions. |
| `ask_gemini_flash` | `prompt` | High-speed task delegation to Google Gemini 3.8 Flash. Low latency, rapid extraction, and batch operations. | Fast JSON extraction, bulk text summarization, rapid classifications. |

---

## 🗣️ Text-to-Speech (TTS): How It Works for Free vs. Paid

Gemini Lens uses a dual-engine approach to ensure 100% reliable audio generation:

1. **Native Gemini Audio Generation (Gemini 2.0 / 3.8 Flash):**
   - Available via `GEMINI_API_KEY`.
   - **Free Users:** Google AI Studio includes multimodal audio generation in its free tier (up to 1,500 daily requests for $0).
   - **Paid Users:** Google Cloud / AI Studio paid accounts unlock higher rate limits and billing credits.
   - **Voice Characters Available:**
     - `Puck` — Upbeat, energetic, playful.
     - `Charon` — Deep, authoritative, calm, serious.
     - `Kore` — Soothing, warm, natural, gentle.
     - `Fenrir` — Resonant, confident, dynamic.
     - `Aoede` — Expressive, melodious, engaging storyteller.
2. **Neural Offline Fallback (`edge-tts`):**
   - Built into package dependencies.
   - If no API key is configured or rate limits are reached, Gemini Lens automatically falls back to neural voice synthesis with **zero API key and zero cost required**.

---

## 🚀 Quickstart & Setup

### Option 1: Claude Desktop (Recommended)

Add Gemini Lens to your `claude_desktop_config.json`:

* **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
* **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gemini-lens": {
      "command": "uvx",
      "args": [
        "git+https://github.com/<your-username>/gemini-lens-mcp"
      ]
    }
  }
}
```

---

### Option 2: Claude Code CLI

Add the server in a single terminal command:

```bash
claude mcp add gemini-lens -- uvx git+https://github.com/<your-username>/gemini-lens-mcp
```

---

### Option 3: Hermes Agent

Add to your Hermes configuration file or MCP settings:

```yaml
mcp_servers:
  gemini_lens:
    command: uvx
    args:
      - "git+https://github.com/<your-username>/gemini-lens-mcp"
```

---

### Option 4: Cursor / Windsurf

Go to **Settings** -> **Features** -> **MCP Servers** -> **Add New MCP Server**:
- **Name:** `gemini-lens`
- **Type:** `command`
- **Command:** `uvx git+https://github.com/<your-username>/gemini-lens-mcp`

---

## ⚙️ How It Connects

Gemini Lens automatically detects the best connection method available:

1. **Active Local Bridge:** If a local OpenAI-compatible bridge daemon is running (`http://127.0.0.1:8000`), it connects to it.
2. **Direct Antigravity CLI (`agy`):** Automatically finds your local `agy` installation on Windows, macOS, or Linux. If you've run `agy login` (with either a free or pro account), it runs directly through your session at $0 extra cost.
3. **Google AI Studio API Key:** If `agy` is not installed, it falls back to the `GEMINI_API_KEY` environment variable (which is 100% free from [aistudio.google.com](https://aistudio.google.com)).

### Optional Environment Variables

| Variable | Description |
|---|---|
| `AGY_PATH` | Explicit path to your `agy` or `agy.exe` binary if installed in a custom location. |
| `BRIDGE_URL` | Custom endpoint for a local bridge (default: `http://127.0.0.1:8000/v1/chat/completions`). |
| `GEMINI_API_KEY` | Optional free API key fallback if Antigravity CLI is not installed. |

---

## 📦 Local Development

```bash
git clone https://github.com/<your-username>/gemini-lens-mcp.git
cd gemini-lens-mcp
pip install -e .
```

Run test:
```bash
python -m gemini_lens_mcp.server
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
