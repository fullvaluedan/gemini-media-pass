# 🎟️ Gemini Media Pass MCP

> **The All-Access Google Media & Multimodal MCP Super-Server for Claude, Hermes, Codex, and Cursor.**  
> Native Video Analysis, Google Flow (Veo 3.1) Video Studio, Google Stitch UI Engine, Flow Music, Imagen 3, Gemini TTS, 2M Document Context, and Gemini Pro Reasoning.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Standard](https://img.shields.io/badge/MCP-Protocol-purple.svg)](https://modelcontextprotocol.io/)
[![Google Veo 3.1](https://img.shields.io/badge/Video-Google%20Veo%203.1-blue.svg)](https://deepmind.google/technologies/veo/)

---

## 💡 What is Gemini Media Pass?

While Claude, Hermes, and Codex are elite reasoning and coding agents, they lack native video comprehension, AI video rendering, UI canvas design, and direct audio synthesis.

**Gemini Media Pass gives your agents an all-access pass to Google's creative and multimodal intelligence stack through a single MCP server**:

- 🎬 **Video Understanding & Flow Analysis** — Ingest raw `.mp4`, `.mov`, `.webm` files. Reviews camera transitions, cut pacing, B-roll timing, and subtitle flow without blowing up context windows.
- 🎥 **Google Flow: Veo 3.1 AI Video Generation** — Render cinematic AI videos (`9:16` vertical or `16:9` widescreen, 4s/6s/8s/10s, Text-to-Video & Image-to-Video) using your Google AI subscription credits.
- 🔄 **Video Extension & Cloud Project Retrieval** — Extend clips by +8s, list your cloud projects on `flow.google.com`, and download past creations by media ID.
- 📱 **Google Stitch: AI UI Design Studio** — Generate mobile/desktop app screens, extract Tailwind/HTML code, and enforce brand design systems directly from chat.
- 🎵 **Flow Music & Soundtracks** — Compose backing tracks, instrumental beats, and ambient soundscapes via Google Flow Music / MusicFX.
- 🗣️ **Gemini Text-to-Speech (TTS)** — Speak scripts aloud into `.mp3`/`.wav` using Gemini's native audio generation with 5 voice personas (`Puck`, `Charon`, `Kore`, `Fenrir`, `Aoede`) plus offline neural fallback.
- 🎨 **Imagen 3 Image Generation** — Generate photorealistic graphics and marketing assets across 7 aspect ratios (`1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`).
- 📚 **2,000,000 Token Document Reading** — Drop massive PDFs, enterprise logs, or 70,000-line codebases into Gemini's 2M-token window.
- 🧠 **Dual-Model Delegation** — Offload deep algorithmic proofs to Gemini 3.1 Pro or batch tasks to Gemini 3.8 Flash.

---

## 🛡️ Security & Authentication: Two Safe Ways to Connect

We built Gemini Media Pass with **security and privacy as first-class citizens**. You choose how you want to connect:

### 🔒 Option 1: Zero-Trust Official API Key (Recommended for Privacy-Conscious Developers)
If you don't want to log in through a browser or connect your personal Google session, simply generate a free API key at [aistudio.google.com](https://aistudio.google.com) (no credit card needed).

* **100% Sandboxed:** Scoped strictly to inference. Never touches your personal Gmail, Google Drive, or account tokens.
* **Revocable in 1-Click:** Delete or cycle the key anytime in Google AI Studio.
* **Setup:** Drop it in a `.env` file (`GEMINI_API_KEY=AIza...`) or pass it directly in your Claude Desktop / Cursor MCP config:
  ```json
  "env": {
    "GEMINI_API_KEY": "AIzaSy..."
  }
  ```
* **What it powers:** Video analysis, Vision, Audio critique, Gemini TTS, Imagen 3, 2M document context, and Pro/Flash reasoning.

---

### 🌐 Option 2: Consumer Google Account Session (`gemini-media-pass-login`)
Only needed if you specifically want to drive **Google Flow (Veo 3.1 AI Video Generation)** using your personal consumer Google AI Pro subscription credits or browse your saved cloud projects:

* **How it works:** Run `gemini-media-pass-login`. An official Google Chrome window opens to sign into `flow.google.com`.
* **Where tokens are stored:** Credentials are saved locally on your own machine in `~/.gflow` (never sent to third-party servers).
* **What it unlocks:** Veo 3.1 video generation, clip extensions, Flow credit tracking, and downloading past cloud creations.

---

## ❓ Plan Tiers: Free ($0) vs. Google AI Plus ($5/mo) vs. Google AI Pro ($20/mo)

### **You can use the Free Plan! No paid subscription is required.**

Gemini Media Pass supports all three Google ecosystem tiers, allowing users to start for $0 and scale up as their workload grows:

| Resource / Feature | 🆓 Free Plan | ⚡ Google AI Plus (~$5/mo) | 💎 Google AI Pro ($20/mo) |
|---|---|---|---|
| **Monthly Cost** | **$0 / Free** (No credit card needed) | **~$5 / month** (Starter AI Tier) | **$20 / month** (Google One AI Premium) |
| **Daily Questions & Tasks** | **1,500 questions / day** (~1 every 4 sec) | **3,000+ questions / day** (~2 req/sec) | 🚀 **Unlimited / Instant priority queue** |
| **Memory per Prompt (Context)** | **750,000 words** (~1,500 book pages) | **750,000 words** (~1,500 book pages) | **1,500,000 words** (~3,000 book pages) |
| **Claude Token Saver** | **Reads 500-page PDFs / 35k lines code** (Saves 100% of Claude tokens) | **Reads 500-page PDFs** (Fast parallel processing) | **Reads 1,000+ pages / 70k lines** in a single pass |
| **Video Understanding** | **1-hour video clip / prompt** (~3–5 hrs analyzed/day) | **1-hour video clip / prompt** (~10–15 hrs analyzed/day) | **Up to 2-hour video clip** (~30+ hrs analyzed/day) |
| **Veo 3.1 AI Video Generation** | **10–20 credits** (~1–2 preview clips) | **~100 credits / month** (~10 full videos or 20 extensions) | **~1,000 credits / month** (~100 videos or 200 extensions) |
| **Text-to-Speech (Voice)** | **20–40 mins audio / day** (5 natural voices + Neural) | **2–3 hours audio / day** (Commercial voiceovers) | **Unlimited voice generation** (Audiobooks & podcasts) |
| **Flow Music (MusicFX)** | **30-second loops & beats** (Background, game loops) | **1–2 minute compositions** (Arranged tracks) | **Full tracks & studio stem export** (Uncapped scoring) |
| **Google Stitch UI Studio** | **5 screen designs / day** (Responsive + Tailwind) | **25 screen designs / day** (Multi-screen flows) | **Unlimited screens & design systems** (Complete apps) |
| **Imagen 3 Image Gen** | **30–50 images / day** (7 aspect ratios, photoreal) | **150–200 images / day** (Faster rendering) | **500+ images / day** (High-throughput marketing) |
| **Gemini 3.1 Pro Reasoning** | **~50 complex queries / day** | **200–300 queries / day** | 🧠 **Uncapped deep reasoning** |
| **Setup & Security** | **Zero-Trust API Key OR Google Login** | **API Key OR Browser session** | `gemini-media-pass-login` (Unlocks Veo credits) |

<p align="center">
  <img src="assets/comparison_chart.png" alt="Gemini Media Pass Comparison Chart" width="100%">
</p>

---

## 🎯 Plain-English Explainer: 3 Everyday Examples for Every Feature

If terms like "tokens", "RPM", and "context windows" sound like AI jargon, here is what each feature actually does for you in everyday life:

---

### 1. 🧠 Memory & Context (1M to 2M Tokens)
*The Problem with Most AIs:* After chatting for a while, most AIs get "brain fog." They forget what you told them an hour ago, contradict earlier rules, or the app forces a "compact session" summary that erases details. As memory fills up, the AI gets dumber.

* 🏟️ **The Stadium Whiteboard vs. The Sticky Note:** Most AIs have a tiny desk covered in sticky notes that get thrown away as new ones arrive. Gemini gives you a football-stadium-sized whiteboard where every single instruction, character rule, or code architecture stays permanently in view.
* 🧘 **No AI Dementia / No Session Compacting:** Work on a creative writing project, a business plan, or a software app for days in the same chat without having to remind the AI who the characters are or what was decided yesterday.
* 📚 **"Drop the Entire Library In":** Drag and drop a 500-page employee handbook, a legal lease, or an entire app codebase in one prompt and ask: *"Find every clause that mentions cancellation penalties."*

---

### 2. 💸 The "Claude Token Saver" (Document & Code Reading)
*The Problem:* Claude is brilliant, but expensive with tight message limits. If you upload a 200-page PDF directly to Claude, you burn through your usage limit after 2 or 3 prompts and get locked out until 4:00 PM.

* 👔 **The CEO & The Speed-Reading Assistant:** Think of Claude as a $500/hr executive, and Gemini as an Olympic speed-reader assistant with free coffee. You don't make the CEO spend 4 hours reading a 400-page financial filing. Gemini reads the entire stack for free, and hands Claude a 1-page summary. The CEO stays fresh and ready for high-level work.
* 🛡️ **Usage Cap Insurance:** By having Gemini read heavy files off-meter, your Claude message allowance isn't wasted on reading raw text. Claude stays available all day long for real brainstorming and writing.
* 💰 **Zero Dollar Bills:** Pasting 200,000 tokens into Claude can cost $0.60 to $3.00 on an API key. Gemini does that exact reading job for **$0.00**.

---

### 3. 👁️ Video Understanding (1-Hour File vs. Daily Quota)
*The Distinction:* **1-Hour File per Prompt** is how long a *single* video can be. **3 to 5 Hours Daily** is how many *total* hours of video you can send in a 24-hour day.

* 🎬 **The YouTube / Podcast Editor:** You recorded a 50-minute podcast. You don't have to slice it into ten 5-minute files. Drop the entire 50-minute `.mp4` into the prompt: *"Find the 3 funniest moments, give me exact timestamps, and write short viral titles for TikTok."*
* 📹 **The Security Camera Inspector:** Drop a 45-minute continuous security camera recording in and ask: *"At what exact minute does the delivery truck arrive, and what color was the driver's jacket?"* Gemini watches every frame and gives the exact timestamp.
* 📅 **Daily Free Workload:** Review four 45-minute lecture recordings or five 30-minute tutorials *every single day* on the free tier without paying a dime.

---

### 4. 🎬 Veo 3.1 AI Video (Arcade Token Math)
*How Credits Work:* Think of credits like arcade tokens: **1 new video (5–8 sec) = 10 tokens**. **Extending a clip (+8 sec) = 5 to 10 tokens**.

* 🕹️ **The Arcade Machine:** Free includes **10–20 tokens** (1–2 test clips). Google AI Plus ($5/mo) gives **~100 tokens/mo** (~10 complete scenes). Google AI Pro ($20/mo) gives **~1,000 tokens/mo** (~100 scenes—enough to storyboard a whole short film).
* ☕ **Instant B-Roll Creator:** Making a video about coffee shops? Prompt: *"Cinematic slow-motion shot of espresso pouring into a glass cup with morning sunlight."* 60 seconds later, you have 1080p footage instead of buying $50 Shutterstock footage.
* 🔄 **The Scene Extender (No Awkward Cuts):** Love an 8-second video of a car driving in the rain? Hit **extend** twice to turn it into a continuous 24-second seamless tracking shot without changing the car or background.

---

### 5. 🎵 Flow Music (MusicFX): Free vs. Paid
*The Difference:* Free generates background loops that seamlessly repeat. Paid generates arranged songs that build up and end.

* 🎮 **The Streamer & Game Loop (Free):** Prompt: *"Lofi chillhop beats with soft rain and mellow piano."* You get a seamless 30-second loop that repeats forever in your game or stream with zero copyright strikes.
* 🎶 **The YouTube Intro / Outro Track (Paid):** Generate an energetic 2-minute synthwave song that starts soft, builds up to a beat drop, and fades out cleanly for your video intro and outro.
* 🛡️ **100% Royalty-Free:** Unlike using Spotify tracks that get your videos muted or demonetized, every track is generated fresh and safe to monetize anywhere.

---

### 6. 📱 Google Stitch UI Studio (Design to Code)
*What It Does:* Converts text descriptions or napkin sketches into real, interactive mobile and desktop screens and outputs clean code.

* ✍️ **Napkin Sketch to Working App:** Type: *"Design an Airbnb listing card for a mountain cabin with a photo gallery, star rating, price per night, and a 'Book Now' button."* It hands you actual React and Tailwind CSS code you can paste into your project.
* ⏱️ **The 5-Minute Client Pitch:** A client asks for a fitness app idea. Instead of spending 8 hours dragging boxes in Figma, prompt Stitch to generate 5 mobile screens (Login, Activity, Workouts, Profile, Checkout) and show them interactive mockups in 10 minutes.
* 🎨 **Free (5 screens/day) vs. Pro (Unlimited Apps):** Free gives you 5 screen mockups a day for weekend side-projects. Pro gives you unlimited screens and keeps colors, fonts, and button styles consistent across a whole 50-screen application.

---

### 7. 🗣️ Text-to-Speech (Gemini Expressive Voice)
*What It Does:* Converts written text into expressive, realistic human speech.

* 🎧 **Turn Articles into Personal Podcasts:** Don't have time to read a 15-page article? Have Gemini read it in the `Puck` or `Aoede` voice, save it as an MP3, and listen while driving or doing dishes.
* 🎙️ **Faceless YouTube Channel Voiceovers:** Write a video script, run `gemini_text_to_speech`, and get clean, professional studio narration in seconds with no microphone needed.
* 🎭 **Real Human Expression:** These voices pause naturally for punctuation, whisper when telling a secret, and inflect their pitch like real human voice actors instead of robotic 2010 navigation voices.

---

## 📊 Token Savings: Claude vs. Gemini Media Pass

Claude cannot read video files natively. In order for Claude to "see" a video, frames must be extracted as static images:

| Video Length | Claude Frame Extraction (1 fps) | Gemini Media Pass External Processing | Claude Tokens Saved | Cost / Context Impact |
|---|---|---|---|---|
| **30 Seconds** | 30 images = **48,000 tokens** | **~500 tokens** (markdown report) | **~47,500 tokens** | Saves ~$0.15 |
| **2 Minutes** | 120 images = **192,000 tokens** *(Near 200k limit!)* | **~750 tokens** (markdown report) | **~191,250 tokens** | Saves Claude context crash (~$0.58) |
| **5 Minutes** | 300 images = **480,000 tokens** *(CRASHES Claude)* | **~1,000 tokens** (markdown report) | **479,000 tokens** | Prevents context overflow |
| **15 Minutes** | 900 images = **1,440,000 tokens** *(Impossible)* | **~1,200 tokens** (markdown report) | **1,438,800 tokens** | Unlocks impossible workflows |

---

## 🛠️ Complete Tool Inventory (24 Tools)

### 👁️ Multimodal Understanding & Analysis (Gemini Flash / Pro)
| Tool | Parameters | Description |
|---|---|---|
| `gemini_video` | `video_path`, `question` | Watch & analyze video files (`.mp4`, `.mov`, `.webm`, `.mkv`). Inspects temporal scene flow, cut pacing, B-roll timing, camera movement, and on-screen text. |
| `gemini_vision` | `image_path`, `question` | Inspect UI screenshots, wireframes, architectural diagrams, and photos with high-precision multimodal vision. |
| `gemini_audio` | `audio_path`, `question` | Listen to and analyze raw audio (`.mp3`, `.wav`, `.m4a`). Transcribes speech, critiques vocal delivery/pacing, identifies emotion/tone, and flags background sounds. |
| `gemini_read_document` | `file_path`, `question` | Ingest massive documents, books, compliance manuals, and logs using Gemini's 2,000,000 token context window. |
| `gemini_multimodal_inspect` | `file_path`, `question` | Universal router: automatically inspects any media file (video, audio, image, PDF, or code) and returns a detailed analysis. |
| `ask_gemini_pro` | `prompt` | Delegate complex tasks to Google Gemini 3.1 Pro. Deep multi-step reasoning, mathematical proofs, alternative architecture options, and second opinions. |
| `ask_gemini_flash` | `prompt` | High-speed task delegation to Google Gemini 3.8 Flash. Low latency, rapid extraction, and batch operations. |

### 🎙️ Voice & Audio Generation
| Tool | Parameters | Description |
|---|---|---|
| `gemini_text_to_speech` | `text`, `voice`, `output_path`, `style_instruction` | Convert text and scripts into high-quality spoken audio (`.mp3` / `.wav`) using Gemini multimodal audio output or neural speech. Supports voices: `Puck`, `Charon`, `Kore`, `Fenrir`, `Aoede`. |
| `flow_generate_music` | `prompt`, `duration`, `output_path` | Compose background music, instrumental beats, and ambient soundscapes via Google Flow Music / MusicFX. |

### 🎨 Visual & Creative Generation
| Tool | Parameters | Description |
|---|---|---|
| `gemini_generate_image` | `prompt`, `aspect_ratio`, `image_name` | Generate photorealistic images and concept art via Google Imagen across 7 aspect ratios (`1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`). |

### 🎬 Google Flow: Veo 3.1 Video Studio & Asset Retrieval
| Tool | Parameters | Description |
|---|---|---|
| `flow_generate_video` | `prompt`, `orientation`, `duration`, `model`, `mode`, `initial_frame`, `end_frame` | Generate cinematic AI videos using Google Flow (**Veo 3.1** & **Omni Flash** with native audio). Supports `9:16` vertical & `16:9` widescreen, 4s/6s/8s/10s, Text-to-Video and Image-to-Video. Feeds live credit balances. |
| `flow_extend_video` | `media_id`, `prompt`, `project_id`, `orientation` | Extends an existing Google Flow video by an extra +8 seconds with continuous motion and sound. |
| `flow_list_projects` | `limit` | List your existing Google Flow projects and folders created on `flow.google.com` or via CLI. |
| `flow_download_media` | `media_id`, `output_path` | Fetch an already-generated video or audio asset from Google Flow by its media ID directly into your local workspace. |
| `flow_sync_catalog` | None | Reconcile and sync your local media catalog with your remote Google Flow project history. |
| `flow_get_credits` | `force_refresh` | Check live Google Flow credit balance, monthly subscription pool, and daily burn rate with milestone alerts. |
| `flow_list_models` | None | Displays all available video models (`veo-fast`, `veo-quality`, `veo-lite`, `omni-flash`) and their credit costs. |
| `flow_auth_status` | None | Checks Google Flow session health and verifies the connected Google account. |

### 📱 Google Stitch: AI UI Design Studio
| Tool | Parameters | Description |
|---|---|---|
| `stitch_generate_screen` | `project_id`, `prompt`, `device_type`, `design_system_id` | Generate a new mobile or desktop UI screen and frontend code in a Google Stitch project from a text prompt. |
| `stitch_list_projects` | `filter` | Lists all Google Stitch UI design projects owned by or shared with your Google account. |
| `stitch_create_project` | `title` | Creates a new Google Stitch project container for app screens, design systems, and frontend code. |
| `stitch_list_screens` | `project_id` | List all screens, UI mockups, and components inside a specific Google Stitch project. |
| `stitch_get_screen` | `project_id`, `screen_id` | Retrieve the full UI layout, components, and code for an existing screen inside a Google Stitch project. |
| `stitch_apply_design_system` | `project_id`, `design_system_id` | Apply an existing design system (color tokens, typography, layout specs) to a Google Stitch project. |

---

## 🚀 Quickstart & Setup

### 1. Interactive One-Time Google Login (For Flow & Stitch)

```bash
gemini-media-pass-login
```
*(Or run `python -m gemini_media_pass_mcp.auth`). A Chrome window opens to sign into your Google account, linking your Google Flow credits and personal asset libraries.*

---

### 2. Configure Claude Desktop

Add Gemini Media Pass to your `claude_desktop_config.json`:

* **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
* **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gemini-media-pass": {
      "command": "uvx",
      "args": [
        "git+https://github.com/fullvaluedan/gemini-media-pass"
      ]
    }
  }
}
```

---

### 3. Configure Claude Code (CLI)

```bash
claude mcp add gemini-media-pass -- uvx git+https://github.com/fullvaluedan/gemini-media-pass
```

---

### 4. Configure Codex / Cursor / Windsurf

In your IDE's **Settings** -> **Features** -> **MCP Servers** -> **Add New MCP Server**:
- **Name:** `gemini-media-pass`
- **Type:** `command`
- **Command:** `uvx git+https://github.com/fullvaluedan/gemini-media-pass`

---

### 5. Configure Hermes Agent

Add to your Hermes `config.yaml` or MCP section:
```yaml
mcp_servers:
  gemini_media_pass:
    command: uvx
    args:
      - "git+https://github.com/fullvaluedan/gemini-media-pass"
```

---

## 📦 Local Development

```bash
git clone https://github.com/fullvaluedan/gemini-media-pass.git
cd gemini-media-pass
pip install -e .
```

Verify all 24 tools:
```bash
python -c "from gemini_media_pass_mcp.server import mcp; print(len(mcp._tool_manager._tools), 'tools active')"
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
