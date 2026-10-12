# 🔍 Gemini Lens MCP

> **Give Claude, Hermes, and Cursor native eyes, ears, video understanding, and Imagen creative generation — powered by Google Gemini.**  
> Supports both **100% Free Google Accounts** and **Google AI Pro Subscriptions**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Standard](https://img.shields.io/badge/MCP-Protocol-purple.svg)](https://modelcontextprotocol.io/)

---

## 💡 What is Gemini Lens?

While Claude and Hermes are elite at coding and reasoning, they lack native video comprehension and direct image generation. Gemini Lens acts as a high-powered multimodal coprocessor:

- 🎬 **Video Flow & Narrative Analysis** — Inspect `.mp4`, `.mov`, `.webm`, `.mkv` files directly. Gemini analyzes scene transitions, camera pacing, B-roll timing, and visual continuity.
- 🎨 **Imagen Image Generation** — Generate high-resolution photorealistic images, concept art, and UI mockups in any aspect ratio (`1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`).
- 🎙️ **Audio & Tone Understanding** — Listen to speech, podcasts, or sound effects (`.mp3`, `.wav`, `.m4a`) for transcription, vocal tone critique, and audio quality checks.
- 📚 **2,000,000 Token Document Reading** — Offload massive PDFs, codebases, or dump logs into Gemini's 2M-token window.
- 🧠 **Dual-Model Delegation** — Tap Gemini 3.1 Pro for second opinions or Gemini 3.8 Flash for ultra-fast batch processing.

---

## ❓ Do I need a Google AI Pro subscription, or can I use the Free Plan?

### **You can use the Free Plan! No paid subscription is required.**

Gemini Lens is designed so anyone with a standard, free Google account can plug and play:

| Feature | 🆓 Free Plan (Standard Google Account) | 💎 Google AI Pro / Antigravity Subscription |
|---|---|---|
| **Cost** | **$0 / Free** (No credit card needed) | Included with active Google subscription |
| **Video & Vision Analysis** | ✅ Full access (within standard daily quota) | ✅ High throughput & priority queue |
| **Audio & Document Reading** | ✅ Full access (up to 2M tokens) | ✅ High throughput |
| **Imagen Image Generation** | ✅ Supported (subject to daily rate caps) | ✅ High generation quota |
| **Gemini 3.8 Flash** | ✅ Fast, generous daily limits | ✅ High-speed priority |
| **Gemini 3.1 Pro** | ⚠️ Limited daily reasoning calls | 🚀 Uncapped deep reasoning |
| **Setup Methods** | `agy login` (Free) OR `GEMINI_API_KEY` (Free) | `agy login` with subscribed account |

> **Summary:** If you're on a standard free Google account, Gemini Lens works out of the box with zero cost. If you have an active Google AI Pro / Antigravity subscription, Gemini Lens automatically unlocks higher rate limits and unrestricted Pro reasoning.

---

## 🛠️ Tools Included

| Tool | Description |
|---|---|
| `gemini_video` | Watch & analyze video files (`.mp4`, `.mov`, `.webm`, `.mkv`). Scene pacing, camera transitions, and narrative review. |
| `gemini_generate_image` | High-res photorealistic image generation via Imagen (`1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`). |
| `gemini_vision` | Multimodal inspection of images, UI mockups, screenshots, and architectural diagrams. |
| `gemini_audio` | Listen to and analyze audio (`.mp3`, `.wav`, `.m4a`). Transcription, tone critique, speaker pacing. |
| `gemini_read_document` | Read massive documents and PDFs using Gemini's 2M-token context window. |
| `gemini_multimodal_inspect` | Universal inspector for any media file (image, audio, video, PDF, or code). |
| `ask_gemini_pro` | Deep reasoning, mathematical proofs, and multi-step planning via Gemini 3.1 Pro. |
| `ask_gemini_flash` | Low-latency task delegation via Gemini 3.8 Flash for high-speed batch work and summarization. |

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

1. **Active Local Bridge:** If a local OpenAI-compatible bridge daemon is running (`http://127.0.0.1:8000`), it uses it.
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
