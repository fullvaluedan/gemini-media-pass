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

## ❓ Plan Tiers: Free ($0) vs. Google AI Plus ($5/mo) vs. Google AI Pro ($20/mo)

### **You can use the Free Plan! No paid subscription is required.**

Gemini Lens supports all three Google ecosystem tiers, allowing users to start for $0 and scale up as their workload grows:

| Resource / Feature | 🆓 Free Plan | ⚡ Google AI Plus (~$5/mo) | 💎 Google AI Pro ($20/mo) |
|---|---|---|---|
| **Monthly Cost** | **$0 / Free** (No credit card) | **~$5 / month** (Starter AI Tier) | **$20 / month** (Google One AI Premium) |
| **Daily Request Limit** | **Up to 1,500 queries / day** (15 req/min) | **3,000+ queries / day** (30 req/min) | 🚀 **High-throughput enterprise priority** |
| **Max Context Window** | **1,000,000 tokens** per query | **1,000,000 tokens** per query | **2,000,000 tokens** per query |
| **Video Understanding** | **Up to ~1 hr video / query** (~900k tokens) | **Up to ~1 hr video / query** (faster queue) | **Up to ~2 hrs video in a single query** |
| **Daily Video Capacity** | **~3–5 hours total video / day** | **~10–15 hours total video / day** | **Continuous automated batch video** |
| **Text-to-Speech (TTS)** | **~20–40 mins audio / day** + Neural | **~2–3 hours finished audio / day** | **Unlimited voiceovers & audiobooks** |
| **Imagen 3 Image Gen** | **~30–50 images / day** (standard caps) | **~150–200 images / day** | **500+ images / day** (high-volume) |
| **Document Reading** | **~500-page PDFs / 35k lines code** | **~500-page PDFs** (higher concurrency) | **1,000+ page docs / 70k lines code** |
| **Gemini 3.8 Flash** | **1,500 calls / day** (fast) | **3,000+ calls / day** (faster) | 🚀 **Top priority queue** |
| **Gemini 3.1 Pro** | **~50 reasoning queries / day** | **~200–300 queries / day** | 🧠 **Uncapped deep reasoning** |
| **Authentication** | `agy login` (Free) OR `GEMINI_API_KEY` | `agy login` OR Google Cloud Pay-As-You-Go | `agy login` with subscribed account |

---

## 🎯 Real-World Production Limits: What Can You Actually Build?

### 1. 🎬 Video Understanding (`gemini_video`)
* **On Free ($0):** Analyze **20–30 short-form clips** (TikToks, Reels, YouTube Shorts) or **3–5 full 20-minute YouTube tutorials** per day. A single video can be up to 45–60 minutes long without clipping.
* **On AI Plus (~$5/mo):** Analyze **50+ short-form clips** or **10–15 full YouTube videos** daily with halved processing wait times.
* **On AI Pro ($20/mo):** Run continuous video QA pipelines. Ingest an entire **2-hour raw podcast recording or gameplay stream in a single prompt** (utilizing the full 2M token window).

### 2. 🗣️ Text-to-Speech Generation (`gemini_text_to_speech`)
* **On Free ($0):** Generate **15,000–30,000 spoken words per day** (about 20–40 minutes of finished narration) via Gemini Audio, plus unlimited keyless generation via the built-in Neural Fallback engine.
* **On AI Plus (~$5/mo):** Generate **100,000+ spoken words per day** (roughly 2–3 hours of finished audio daily) for daily YouTube automation, course lectures, and multi-language narrations.
* **On AI Pro ($20/mo):** Uncapped, high-concurrency generation for full audiobook publishing, interactive voice agents, and real-time gaming dialog.

### 3. 🎨 Imagen 3 Image Generation (`gemini_generate_image`)
* **On Free ($0):** Generate **~30–50 high-resolution images daily** across all 7 aspect ratios. Perfect for blog post headers, app icons, and concept art iterations.
* **On AI Plus (~$5/mo):** Generate **~150–200 images daily** with faster queue times. Ideal for social media content creation and website mockup variants.
* **On AI Pro ($20/mo):** Generate **500+ images daily**. Perfect for game studios generating hundreds of sprite textures, marketing agencies running A/B ad creative batches, and rapid design sprints.

### 4. 📚 Document & Codebase Digestion (`gemini_read_document`)
* **On Free ($0):** Ingest up to **1,000,000 tokens** (~750,000 words) per query. That is an entire 500-page book, an entire company HR manual, or a 35,000-line code repository in a single shot.
* **On AI Plus (~$5/mo):** Process multiple 1M-token documents in parallel without hitting concurrency blocks.
* **On AI Pro ($20/mo):** Double the capacity to **2,000,000 tokens** (~1.5M words). Ingest massive multi-repo architectures, giant SQLite crash dumps, or 1,000+ page technical specifications.

### 5. 🧠 Gemini 3.1 Pro Reasoning Delegation (`ask_gemini_pro`)
* **On Free ($0):** ~50 deep-thinking architectural reviews per day. Ideal for getting a reliable second opinion when Claude or Hermes hits a complex logic bug.
* **On AI Plus (~$5/mo):** ~200–300 deep reasoning queries per day with priority response.
* **On AI Pro ($20/mo):** Uncapped deep reasoning for continuous architectural validation, formal proofs, and complex mathematical algorithms.

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
