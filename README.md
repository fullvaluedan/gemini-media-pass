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

## Tools (28)

### Understanding & Help
| Tool | Parameters | What it does |
|---|---|---|
| gemini_media_pass_guide | 	opic ('overview', 'models', 'billing', 'settings', 'workflows', 'all') | **Interactive help & settings guide**. Explains Flash vs Pro, subscription vs API billing, and video workflows. |
| gemini_video | ideo_path, question, model_tier ('flash' or 'pro') | Watch and analyze a video file. Defaults to lash for 97% savings; set model_tier='pro' for deep critique. |
| gemini_vision | image_path, question, model_tier | Inspect an image, diagram or screenshot. |
| gemini_audio | udio_path, question, model_tier | Transcribe and analyze audio (dialogue, tone, background sounds). |
| gemini_read_document | ile_path, question, model_tier | Read a large document, log or codebase file using the 2M token window. |
| gemini_multimodal_inspect | ile_path, question, model_tier | Universal inspector for any media file type. |
| sk_gemini_pro | prompt | Deep reasoning or a second opinion. |
| sk_gemini_flash | prompt | Fast extraction, summarization, and batch work. |

## ⚡ Flash vs. Pro: Cost & Quality Optimization (Save ~97%)

Google Gemini models process video by natively tokenizing frames (~258 tokens per frame at ~1 fps) with audio synchronization.

### Market Cost Comparison (5-Minute Video / ~300 Frames)

| Provider | Model | Video Ingestion Method | Input Token / Min Cost | Approx. 5-Min Video Cost | Best For |
|---|---|---|---|---|---|
| **Google** | **Gemini 1.5 Flash** | **Native video upload** | **.075 / 1M tokens** | **~.007 (< 1 cent)** | **Timestamp indexing, scene retrieval, B-roll sourcing (97% cheaper)** |
| **Google** | **Gemini 1.5 Pro** | **Native video upload** | **.50 - .00 / 1M tokens** | **~.35 - .70** | Deep thematic critique, narrative subtext, subtle animation comparisons |
| **Meta** | **SAM 2 (Segment Anything)**| Video Object Tracker | Free (self-hosted) | **.00** | Pixel-level object segmentation, rotoscoping, tracking moving subjects |
| **Meta** | **Llama 3.2 Vision (11B/90B)** | Open-Weights Vision LLM | Free self-hosted / ~.10/1M | **~.01 - .03** | Local private document/image reading on your GPU |
| **Alibaba**| **Qwen2-VL (7B/72B)** | Open-Weights Vision-Language | Free self-hosted / ~.20/1M | **~.02 - .05** | High-resolution open-source video comprehension |
| **OpenAI** | **GPT-4o mini** | Sampled base64 frames | .15 / 1M tokens | **~.015 - .02** | Cheap conversational vision; lower spatial detail on small text |
| **OpenAI** | **GPT-4o** | Sampled base64 frames | .50 / 1M tokens | **~.25 - .30** | High-precision visual reasoning and diagrams |
| **Anthropic**| **Claude 3.5 Sonnet** | Sampled base64 frames | .00 / 1M tokens | **~.50 - .90** | UI-to-code, technical diagrams, deep text/chart reasoning |
| **Twelve Labs** | **Marengo 2.6 / Pegasus** | Specialized Video Model | .05 / video minute | **~.25** | Dedicated natural language video timestamp search |

### How to Select Models & Change Settings

You have 3 easy ways to control model tiers:

1. **Per Tool Call (On the Fly)**:
   Pass model_tier='flash' or model_tier='pro' directly:
   gemini_video('D:/videos/simpsons_s04e12.mp4', 'Find the timestamp where the monorail arrives', model_tier='flash')

2. **Global Environment Configuration (.env)**:
   In your .env or ~/.gemini_media_pass.env file:
   GMP_DEFAULT_TIER=flash
   GMP_VIDEO_TIER=flash

3. **Interactive Help & Options Guide**:
   Call the built-in MCP tool anytime:
   gemini_media_pass_guide(topic='all')
   *(Specific topics: 'overview', 'models', 'billing', 'settings', 'workflows')*

### Subscription Credits vs. Google Cloud API Credits

- **Antigravity CLI (gy)**: When gy is installed and authenticated, analysis calls route through your Google AI subscription flat fee and cost **.00 in Google Cloud API credits**.
- **Google Flow (Veo)**: Connects to your Google AI Pro/Ultra subscription pool via python -m gemini_media_pass_mcp.auth.
- **Google Cloud API Key (GEMINI_API_KEY)**: Only acts as a pay-as-you-go fallback if gy is not present or times out. To strictly prevent any surprise API billing on your Google Cloud invoice, remove or comment out GEMINI_API_KEY in ~/.gemini_media_pass.env.

---

### Generation
| Tool | Parameters | What it does |
|---|---|---|
| `gemini_text_to_speech` | `text`, `voice`, `output_path`, `style_instruction` | Speech to `.wav` (or `.mp3` with ffmpeg). Voices `Puck`, `Charon`, `Kore`, `Fenrir`, `Aoede`; edge-tts fallback (`GMP_EDGE_VOICE` picks any edge voice) |
| `gemini_generate_image` | `prompt`, `aspect_ratio`, `image_name` | Image generation through `agy`; returns the saved path only if the file exists |
| `flow_generate_music` | `prompt`, `duration`, `output_path` | Music through gflow, only if your gflow version has a music tool (0.86 has none). Otherwise it tells you to use flowmusic.app |

### Google Flow (Veo)
| Tool | Parameters | What it does |
|---|---|---|
| `flow_generate_video` | `prompt`, `orientation`, `duration`, `model`, `mode`, `initial_frame`, `end_frame`, `count`, `max_credits`, `guardrails`, `spoken_line`, `allow_names` | Text to video or image to video, 9:16 or 16:9. Refuses calls over the credit cap. `guardrails=True` adds "one continuous shot, no cuts, no on-screen text or captions". `spoken_line` pins the exact words and keeps the speaker silent after. Stops before spending when the prompt names a real person or famous character, unless `allow_names=True` |
| `flow_extend_video` | `media_id`, `prompt`, `project_id`, `orientation` | Extend a clip by about 8 seconds |
| `flow_list_projects` | `limit` | Your Flow projects |
| `flow_download_media` | `media_id`, `output_path` | Download a video gflow made (`output_path` is a folder or a file name). Clips made in the Flow web UI are not in gflow's catalog: download those from flow.google.com |
| `flow_sync_catalog` | none | Refresh names of media already in gflow's catalog |
| `flow_get_credits` | `force_refresh` | Live credit balance |
| `flow_list_models` | none | Video and image models with estimated costs |
| `flow_auth_status` | none | Session health |
| `flow_doctor` | none | One report: sign-in, Google account and plan, classic or migrated Flow frontend and what works on it, an `agy` ping, ffmpeg, faster-whisper. Run it first |
| `flow_clip_qa` | `path`, `kind`, `expected_words`, `cut_threshold` | Checks a downloaded clip: cuts inside it, the words actually spoken vs `expected_words`, lyrics in music (`kind='music'`). Speech checks need `pip install faster-whisper` |
| `flow_spend_ledger` | `days` | What this server spent on Flow, per request, from `~/.gemini_media_pass/flow_spend.jsonl` |

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

## Your first 20-second short

A short that works on the first try is several short clips cut together, not one long generation.

1. **Check your setup.** Run `flow_doctor`. Fix anything marked PROBLEM. If it says your account is on the new
   flow.google.com frontend, only text to video and text to image work from here (see below).
2. **Split the idea into a setup and a reveal.** Generate them as separate clips. The setup builds the question,
   the reveal answers it. Plan for the reveal to land on the punch word of the line.
3. **Generate each clip with guardrails.** For example:
   `flow_generate_video(prompt="A chef in a white apron tastes soup in a busy kitchen, close-up",
   guardrails=True, spoken_line="Needs more salt.", duration=6)`.
   This adds "one continuous shot, no cuts, no on-screen text or captions" and keeps the speaker silent after
   the line. Describe generic looks. Real people and famous characters get blocked (a Jack Sparrow-like pirate
   failed 5 of 5 times), while your own Flow avatar in a generic costume passes.
4. **QA every clip before editing.** `flow_clip_qa(path, expected_words="Needs more salt.")` flags hidden cuts
   and wrong or extra dialogue. Regenerate the bad ones instead of fixing them in the edit.
5. **Cut it in 2 to 4 second shots.** Trim each clip to its best 2 to 4 seconds. Use J cuts (the next shot's
   sound starts before its picture) and L cuts (the sound carries over the next picture) so the cuts feel smooth.
   Put the reveal cut exactly on the punch word.
6. **Add music without lyrics.** Make the track at flowmusic.app (gflow cannot make music yet), download it, and
   run `flow_clip_qa(path, kind="music")`. Flow Music ignored "instrumental only" on 1 of 2 takes, so check.
   Keep music well under the dialogue.
7. **Check what you spent.** `flow_spend_ledger` lists every request and its cost, because the Flow balance often
   cannot be read from here.

### Migrated accounts: avatars and ingredients

Google is moving accounts from labs.google to a new Flow frontend at flow.google.com. On a migrated account,
gflow (and this server) can only do text to video and text to image. The Flow web UI is the only path for
avatars, ingredients, character references, image to image and image to video with a start frame. Make those
clips in the web UI, download them from there, and use `flow_clip_qa` on them like any other clip.

## Troubleshooting

| Message | What it means | What to do |
|---|---|---|
| `Your Google account was moved to Flow's new frontend` | The account is on flow.google.com and gflow cannot drive that request there (gflow `FlowHostMigratedError`). Nothing was spent | Use text to video or text to image here. Do image to image, image to video, avatars and ingredients in the Flow web UI. Retrying does not help |
| `Not sent, nothing spent. The prompt names ...` | The prompt names a real person or famous character, which Flow blocks | Describe a generic look, or pass `allow_names=True` to send it anyway |
| `Flow blocked this prompt to protect third-party content` | Flow refused the render ("interests of third-party content providers") and refunded it | Remove the name or look-alike wording |
| `Media ... was not downloaded. gflow only downloads media it made itself` | The clip was made in the Flow web UI, so gflow has no record of it | Download it from flow.google.com |
| `Music was not generated ... no music generator` | gflow 0.86 has no music tool | Make the track at flowmusic.app, then run `flow_clip_qa` with `kind='music'` |
| `agy answered with nothing` | `agy` ran but returned no text | Open `agy` once, check you are signed in and the model is available. Or set `GEMINI_API_KEY` |
| `agy timed out on a 20 s ping` | `agy` hangs. The server checks before long calls so you wait 20 seconds, not minutes | Same as above. `GMP_AGY_PING_SECONDS` changes the wait, `0` turns the ping off |
| `api: GEMINI_API_KEY is not set` | There is no API fallback | Optional: add a free key from Google AI Studio |
| `Balance unreadable (gflow issue #795)` | Signed in and generation works, but gflow cannot read credits on this account | Check the balance in Flow. `flow_spend_ledger` shows what this server spent |
| `Refused: this would spend N credits, over the cap` | The call costs more than `GMP_FLOW_MAX_CREDITS` | Pass `max_credits=N` or raise the setting |
| `Cuts: N inside the clip` (clip QA) | Veo cut to another angle inside one generation | Trim to one shot, or regenerate with `guardrails=True` |
| `Lyrics: heard words` (clip QA) | The track has singing | Use another take |

## Setup

1. Install the [Antigravity CLI](https://antigravity.google) and sign in, or create a Gemini API key.
2. For Flow: `pip install gflow-cli`, then `gflow auth login` (or `gemini-media-pass-login`).
   For clip QA: install ffmpeg, and optionally `pip install faster-whisper` for the speech checks.
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
| `GMP_AGY_PING_SECONDS` | 20 | Quick `agy` check before long calls. `0` turns it off |
| `GMP_FLOW_LEDGER` | `~/.gemini_media_pass/flow_spend.jsonl` | Where Flow spend is logged |
| `GMP_WHISPER_MODEL` | `base` | faster-whisper model for clip QA |

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
