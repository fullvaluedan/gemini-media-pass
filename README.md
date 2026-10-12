# ⚡ GeminiZero MCP

> **Zero-cost Multimodal Gemini Superpowers for Claude, Hermes, and Cursor.**  
> Native Video Analysis, Imagen Image Generation, Audio Critique, 2M Context Document Reading, and Pro Reasoning.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Standard](https://img.shields.io/badge/MCP-Protocol-purple.svg)](https://modelcontextprotocol.io/)

---

## 💡 Why GeminiZero?

Most Gemini MCP tools require paid Google AI Studio or Vertex AI API keys. When you analyze a 10-minute video or batch-generate images, token and inference costs add up fast.

**GeminiZero bridges your active Google Antigravity / Gemini subscription** directly into your favorite AI environments (**Claude Desktop**, **Claude Code**, **Hermes**, **Cursor**, **Windsurf**).

- **$0 Extra API Cost** — Runs over your active subscription session.
- **True Video Understanding** — Scene transitions, B-roll timing, camera pacing, visual flow.
- **Imagen Image Generation** — Generate photorealistic assets and UI concepts in any aspect ratio.
- **2,000,000 Token Context** — Hand off massive PDFs, codebases, or logs to Gemini.
- **Plug & Play** — Auto-detects your local installation across Windows, macOS, and Linux.

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
| `ask_gemini_pro` | Deep reasoning, mathematical proofs, alternative approaches, and second opinions via Gemini 3.1 Pro. |
| `ask_gemini_flash` | Low-latency task delegation via Gemini 3.8 Flash for high-speed batch work and summarization. |

---

## 🚀 Quickstart & Setup

### Option 1: Claude Desktop (Recommended)

Add GeminiZero to your `claude_desktop_config.json`:

* **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
* **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gemini-zero": {
      "command": "uvx",
      "args": [
        "git+https://github.com/<your-username>/gemini-zero-mcp"
      ]
    }
  }
}
```

*(If you clone the repo locally, replace the command with `python` and args with `["-m", "gemini_zero_mcp.server"]` inside your virtual environment).*

---

### Option 2: Claude Code CLI

Add the server in a single terminal command:

```bash
claude mcp add gemini-zero -- uvx git+https://github.com/<your-username>/gemini-zero-mcp
```

---

### Option 3: Hermes Agent

Add to your Hermes configuration file or MCP settings:

```yaml
mcp_servers:
  gemini_zero:
    command: uvx
    args:
      - "git+https://github.com/<your-username>/gemini-zero-mcp"
```

---

### Option 4: Cursor / Windsurf

Go to **Settings** -> **Features** -> **MCP Servers** -> **Add New MCP Server**:
- **Name:** `gemini-zero`
- **Type:** `command`
- **Command:** `uvx git+https://github.com/<your-username>/gemini-zero-mcp`

---

## ⚙️ How It Works & Configuration

GeminiZero automatically tries the following execution strategies in order:

1. **Active Local Bridge:** If you are running a local bridge daemon at `http://127.0.0.1:8000`, it connects to it.
2. **Direct Antigravity CLI (`agy`):** Automatically locates the `agy` binary across default locations on Windows, macOS, and Linux to run queries against your active Google subscription session at $0 cost.
3. **API Key Fallback:** If `agy` is not installed, it falls back to the `GEMINI_API_KEY` environment variable.

### Optional Environment Variables

| Variable | Description |
|---|---|
| `AGY_PATH` | Explicit path to your `agy` or `agy.exe` binary if installed in a non-standard directory. |
| `BRIDGE_URL` | Custom endpoint for a local OpenAI-compatible bridge (defaults to `http://127.0.0.1:8000/v1/chat/completions`). |
| `GEMINI_API_KEY` | Optional Google AI Studio API key used if `agy` is not installed on the system. |

---

## 📦 Local Development

```bash
git clone https://github.com/<your-username>/gemini-zero-mcp.git
cd gemini-zero-mcp
pip install -e .
```

Run test:
```bash
python -m gemini_zero_mcp.server
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
