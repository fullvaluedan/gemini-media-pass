# Gemini Media Pass MCP

One MCP server that gives Claude, Hermes, Codex and Cursor access to Google's media stack: Gemini video, audio,
image and long-document understanding, Gemini text-to-speech, image generation, Google Stitch UI screens, and
Google Flow (Veo) video generation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Protocol-purple.svg)](https://modelcontextprotocol.io/)

## Why

Claude and Codex are strong at reasoning and code but cannot watch a video or listen to audio. Sending frames
as images burns their context fast (a 2 minute video at 1 frame a second is 120 images). This server hands the
file to Gemini and returns a short text report instead.

## How it connects to Gemini

Each call tries these in order and reports every failure it hit:

1. **Antigravity CLI (`agy`)**, on your Google AI subscription. Runs **sandboxed**. Analysis tools run in
   **read-only plan mode**. Only the tools that must create something (image generation, Stitch create and
   generate) may write.
2. **Gemini API** with `GEMINI_API_KEY` (free key from [Google AI Studio](https://aistudio.google.com)). The key
   is sent in the `x-goog-api-key` header, never in the URL. Files up to 20 MB are attached inline.
3. **A local OpenAI-compatible bridge**, only if you set `BRIDGE_URL`. Off by default.

Google Flow (Veo video, extend, credits, projects) uses [`gflow-cli`](https://github.com/ffroliva/gflow-cli) and a
one-time browser sign-in (`gflow auth login`). Its session is stored on your machine in `~/.gflow`.

## Security

- **No auto-approve.** `agy` never gets `--dangerously-skip-permissions` unless you set `GMP_AGY_UNSAFE=1`.
  Without it, text hidden inside a video, PDF or image you analyze cannot make the agent run commands.
- **No silent network calls.** The local bridge is opt-in. With `BRIDGE_URL` unset, prompts only go to `agy` or
  the Gemini API.
- **Spending cap for Flow.** `flow_generate_video` refuses any call that would cost more than 40 credits
  (`GMP_FLOW_MAX_CREDITS`) unless the call passes a higher `max_credits`. After each render the balance is read
  back from Flow instead of estimated.
- **Timeouts everywhere.** Every `agy` and `gflow` call has a time limit (`GMP_TIMEOUT_SECONDS`,
  `GMP_FLOW_TIMEOUT_SECONDS`) and reports what went wrong.
- **Terms of service.** Google offers no public API for Flow. `gflow-cli` drives Flow's web endpoints with your
  signed-in session. That may conflict with Google's terms and can break when Flow changes. Use it at your own
  risk, ideally with an account you are comfortable using this way.

## Plans and limits

Limits depend on your Google plan and change often, so this README does not repeat them. Check the source:
- Gemini API free tier and rate limits: [ai.google.dev/gemini-api/docs/rate-limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- Gemini API pricing: [ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing)
- Google AI plans (Flow credits, Veo access): [one.google.com/about/ai-premium](https://one.google.com/about/ai-premium)
- Your live Flow balance: the `flow_get_credits` tool.

## What you can do with it

- **Review a video edit.** "Watch `D:/edits/v3.mp4` and list every moment the captions cover a face, with timestamps."
- **Read what Claude should not.** "Read this 400-page filing and give me the five numbers that changed since last year."
- **Generate b-roll.** "Make an 8 second vertical clip of espresso pouring in morning light" (Veo, spends Flow credits).
- **Voice a script.** Gemini TTS with five voices, or free edge-tts neural voices when no API key is set.
- **Sketch a UI.** "Generate a mobile booking screen in my Stitch project."

## Tools (29)

### Understanding
| Tool | Parameters | What it does |
|---|---|---|
| `gemini_video` | `video_path`, `question` | Watch and analyze a video file |
| `gemini_vision` | `image_path`, `question` | Inspect an image or screenshot |
| `gemini_audio` | `audio_path`, `question` | Transcribe and analyze audio |
| `gemini_read_document` | `file_path`, `question` | Read a large document, log or codebase file |
| `gemini_multimodal_inspect` | `file_path`, `question` | Any file type |
| `ask_gemini_pro` | `prompt` | Deep reasoning or a second opinion |
| `ask_gemini_flash` | `prompt` | Fast extraction and batch work |

### Generation
| Tool | Parameters | What it does |
|---|---|---|
| `gemini_text_to_speech` | `text`, `voice`, `output_path`, `style_instruction` | Speech to `.wav` (or `.mp3` with ffmpeg). Voices `Puck`, `Charon`, `Kore`, `Fenrir`, `Aoede`; edge-tts fallback (`GMP_EDGE_VOICE` picks any edge voice) |
| `gemini_generate_image` | `prompt`, `aspect_ratio`, `image_name` | Image generation through `agy`; returns the saved path only if the file exists |
| `flow_generate_music` | `prompt`, `duration`, `output_path` | Music through `gflow tools`; reports a failure plainly when nothing was made |

### Google Flow (Veo)
| Tool | Parameters | What it does |
|---|---|---|
| `flow_generate_video` | `prompt`, `orientation`, `duration`, `model`, `mode`, `initial_frame`, `end_frame`, `count`, `max_credits` | Text to video or image to video, 9:16 or 16:9. Refuses calls over the credit cap |
| `flow_extend_video` | `media_id`, `prompt`, `project_id`, `orientation` | Extend a clip by about 8 seconds |
| `flow_list_projects` | `limit` | Your Flow projects |
| `flow_download_media` | `media_id`, `output_path` | Download a past generation |
| `flow_sync_catalog` | none | Sync the local media catalog |
| `flow_get_credits` | `force_refresh` | Live credit balance |
| `flow_list_models` | none | Video and image models with estimated costs |
| `flow_auth_status` | none | Session health |

### Shot lists, avatars and scene remakes
| Tool | Parameters | What it does |
|---|---|---|
| `flow_shoot_shot_list` | `shots`, `orientation`, `model`, `resolution`, `confirm`, `max_credits`, `reference_entity`, `join` | Footage for many shots (reactions, B-roll, avatar shots) as separate trimmed clips plus `shotlist.json`/`.csv` for your editor. Returns a plan and credit estimate first; renders only with `confirm=true` |
| `flow_upscale_video` | `media_id`, `scale` | Flow's own 1080p upscale (measured credit-free by gflow) |
| `flow_list_characters` | `project_id` | Your Flow Characters (avatars) and their `reference_entity` ids |
| `flow_create_character` | `project_id`, `name`, `face_prompt`, `body_prompt`, `voice` | Create an avatar (spends image credits) |
| `flow_remake_scene` | `video_path`, `changes`, `start_seconds`, `end_seconds`, `confirm` | Grab and describe a scene's first and last frame, then render it again from frame to frame with your changes |

How shot lists save generations:
- Each shot renders at the shortest length Flow allows that covers it (4, 6, 8, or 10 s on omni-flash) and is trimmed
  locally, so a 2 s reaction is a 4 s render, not 8 s.
- With `model="auto"` (default), shots of 4 s or less use `veo-lite`, the cheapest model.
- Shots with the same `group` (same subject and setting, for example a run of reactions) are packed into one
  generation as timed beats and cut apart afterwards: four 2 s reactions cost one generation.
- Identical shots render once, and shots already rendered in the output folder are reused on the next run.
- Clips are delivered separately for editing (DaVinci Resolve or similar); `join=true` adds a preview.

Flow cannot render 2 s or 5 s clips or 1080p directly. Short lengths come from trimming, 1080p from Flow's upscale.
ffmpeg comes from the `imageio-ffmpeg` dependency if it is not on your PATH.

### Google Stitch
| Tool | Parameters | What it does |
|---|---|---|
| `stitch_list_projects` | `filter` | List projects |
| `stitch_create_project` | `title` | Create a project |
| `stitch_list_screens` | `project_id` | List screens |
| `stitch_get_screen` | `project_id`, `screen_id` | Screen layout and code |
| `stitch_generate_screen` | `project_id`, `prompt`, `device_type`, `design_system_id` | Generate a screen |
| `stitch_apply_design_system` | `project_id`, `design_system_id` | Apply a design system |

Stitch tools ask `agy` to call Stitch, so `agy` needs the Stitch MCP server configured (`agy mcp add ...`).

## Setup

1. Install the [Antigravity CLI](https://antigravity.google) and sign in, or create a Gemini API key.
2. For Flow: `pip install gflow-cli`, then `gflow auth login` (or `gemini-media-pass-login`).
3. Add the server to your client.

Claude Code:
```bash
claude mcp add gemini-media-pass -- uvx git+https://github.com/fullvaluedan/gemini-media-pass
```

Claude Desktop (`%APPDATA%\Claude\claude_desktop_config.json` on Windows,
`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):
```json
{
  "mcpServers": {
    "gemini-media-pass": {
      "command": "uvx",
      "args": ["git+https://github.com/fullvaluedan/gemini-media-pass"],
      "env": {"GEMINI_API_KEY": "your key, optional"}
    }
  }
}
```

Hermes (`config.yaml`):
```yaml
mcp_servers:
  gemini_media_pass:
    command: uvx
    args: ["git+https://github.com/fullvaluedan/gemini-media-pass"]
```

Cursor, Windsurf, Codex: add an MCP server of type `command` running
`uvx git+https://github.com/fullvaluedan/gemini-media-pass`.

## Settings

| Variable | Default | Meaning |
|---|---|---|
| `GEMINI_API_KEY` | unset | Gemini API key (header auth) |
| `GEMINI_API_MODEL_FLASH` / `GEMINI_API_MODEL_PRO` | `gemini-3.5-flash` | API models when `agy` is unavailable |
| `GEMINI_TTS_MODEL` | `gemini-3.8-flash-tts` | TTS model |
| `AGY_PATH` | auto | Path to the `agy` binary |
| `BRIDGE_URL` | unset | Opt-in local bridge |
| `GMP_AGY_UNSAFE` | unset | `1` lets `agy` auto-approve everything. Not recommended |
| `GMP_TIMEOUT_SECONDS` | 180 | Per Gemini call |
| `GMP_FLOW_MAX_CREDITS` | 40 | Credit cap per Flow call |
| `GMP_FLOW_TIMEOUT_SECONDS` | 900 | Per Flow render |
| `GMP_EDGE_VOICE` | unset | Any edge-tts voice, for example `en-US-AndrewNeural` |
| `GMP_FFMPEG_TIMEOUT_SECONDS` | 600 | Per ffmpeg cut or join |
| `GMP_GFLOW_KEYCHAIN` | unset | macOS: Flow tools skip gflow's "Chrome Safe Storage" Keychain read, which prompts on every call. `1` runs gflow unchanged |

## Development

```bash
git clone https://github.com/fullvaluedan/gemini-media-pass.git
cd gemini-media-pass
pip install -e ".[dev]"
pytest -q
```

Tests never touch the network, `agy` or `gflow`.

## ⚖️ Disclaimer & Terms of Service

* **Official Gemini API (Option 1):** Operates under the official [Google APIs Terms of Service](https://developers.google.com/terms) and [Google Generative AI Additional Terms of Service](https://ai.google.dev/terms). Fully supported, intended, and compliant.
* **Google Flow & Studio Connectors (Option 2):** Connects to personal browser sessions for local interoperability and workflow automation. It is an independent, unofficial client and is not affiliated with, maintained by, or endorsed by Google LLC.
* **Trademarks:** Google, Gemini, Veo, Stitch, and Imagen are registered trademarks of Google LLC.

## License

MIT. See [LICENSE](LICENSE).
