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


## Usage after a batch (recommended)

Call `flow_credit_receipt()` for a compact local spend summary without fetching a
provider balance. `flow_credit_receipt(daily_budget=50)` also shows the remainder
of **your own rolling-24h budget**, not Google's allowance or reset schedule.
Use `flow_get_credits(force_refresh=True)` when you need a provider balance
(which may be unavailable on migrated accounts).

To attach a receipt to a successful `flow_generate_video` or `flow_extend_video`
call, pass `include_credit_receipt=True`. Set `GMP_CREDIT_RECEIPTS=on` to opt in
by default; `include_credit_receipt=False` overrides it for one call. The default
is off. Early refusals and failed jobs retain their existing error responses.
The original generation result is preserved; receipts are appended after it.

Optionally set `GMP_FLOW_DAILY_BUDGET` to a positive integer. Example:

```text
[Flow local only | Job: ~20 cr | 24h spent: ~20 cr | 30d spent: ~60 cr | 24h budget left: ~30/50 cr]
```

`~` marks an estimate. Windows are rolling 24 hours and 30 days, not calendar
periods. Totals cover this server's Flow ledger (`GMP_FLOW_LEDGER` or
`~/.gemini_media_pass/flow_spend.jsonl`) only; web UI spending and other machines
are excluded. Missing history reports usage unknown, never a verified zero.
Unreadable history produces an unavailable notice; malformed records are skipped
with a notice. Image calls, image quota limits, and the host chat model's tokens
are not tracked by this ledger and are deliberately omitted. No prompts or paths
are included in the compact receipt.

Receipt formatting is local Python with no extra LLM or Flow API call. Its text
still consumes context tokens when returned to an AI client. Prefer an on-demand
receipt at the end of a batch or before a costly render; enable every-call
receipts when you are actively budgeting. A 10% alert requires an explicit budget
and persistent threshold tracking; this feature does not infer that threshold
from chat tokens or implement automatic alerts. Major code updates alone do not
change the Flow budget. Existing detailed generation output remains unchanged,
so enabling receipts adds text rather than reducing it.


### On-demand command: gemini-usage

After installing the updated package, run:

```sh
gemini-usage
# Equivalent:
python -m gemini_media_pass_mcp.receipts
# Optional personal budget:
gemini-usage --daily-budget 50
```

**Claude Code:** this checkout includes `.claude/commands/gemini-usage.md`, so
`/gemini-usage` is available when working here. For other projects, copy that
command file into the project's `.claude/commands/` directory (or your personal
`~/.claude/commands/`). An MCP server connection alone does not install it.
See [Claude Code custom commands](https://code.claude.com/docs/en/skills).

**Codex:** install the bundled `skills/gemini-usage` folder into your user skills
location, or a project's `.agents/skills/`, then invoke `$gemini-usage` or choose
it from `/skills`. This is the Codex skill equivalent; `/gemini-usage` is not a
universal MCP slash command. See [Codex skills](https://learn.chatgpt.com/docs/build-skills).

The bundled workflow recommends `include_credit_receipt=False` during the batch,
then one `flow_credit_receipt()` call after all requested generations finish.
You can also say: "Generate these clips, then show Gemini usage once at the end."
Batch completion is determined by the agent/user; the server has no automatic
batch-boundary event. No background hook, timer, or extra report runs per job.
The command and skill report local Flow credits only, not Gemini quota or chat
tokens. They use the server's ledger when called through MCP and the current
machine's ledger when run as a CLI; those may differ for remote MCP servers.
