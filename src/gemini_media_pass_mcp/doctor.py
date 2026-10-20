"""First-try helpers: flow_doctor (one readable health report), flow_clip_qa and flow_spend_ledger."""
from __future__ import annotations

import asyncio
import importlib.util
import json
import shutil
from typing import Any, Dict, Optional

from . import clipqa, flow, ledger, runner

WORKS_CLASSIC = "text to video, image to video, extend, text to image, image to image, download"
WORKS_MIGRATED = "text to video (count 1, no explicit resolution), text to image"
WEB_UI_ONLY = "image to image, image to video with a start frame, extend, avatars, ingredients, character references"


async def _gflow(*args: str, timeout: int = 90) -> tuple:
    rc, out, err = await flow._run(flow._find_gflow() + list(args), timeout=timeout)
    return rc, out.decode("utf-8", errors="replace").strip(), err.decode("utf-8", errors="replace").strip()


def _migrated_seen() -> Optional[str]:
    """When a request last failed because the account moved to the new frontend, from the spend ledger."""
    for e in reversed(ledger.read_entries(days=30)):
        if "new frontend" in e.get("note", ""):
            return f"{e['time'][:16].replace('T', ' ')} ({e['tool']})"
    return None


async def gather_facts() -> Dict[str, Any]:
    runner._last_ping_ok = 0.0        # the doctor always pings for real
    version, profiles, credits, agy = await asyncio.gather(
        _gflow("--version", timeout=30), _gflow("auth", "list", "--json", timeout=30),
        flow._fetch_credits_raw(), runner.ping_agy(), return_exceptions=True)
    facts: Dict[str, Any] = {
        "gflow_version": version[1] if isinstance(version, tuple) and version[0] == 0 else None,
        "account": None, "profile": None, "tier": None, "credits": None,
        "signed_in": isinstance(credits, dict) and credits.get("authenticated", False),
        "balance_unknown": isinstance(credits, dict) and credits.get("balance_unknown", False),
        "agy_problem": agy if isinstance(agy, str) else f"{type(agy).__name__}: {agy}",
        "ffmpeg": bool(shutil.which("ffmpeg")), "ffprobe": bool(shutil.which("ffprobe")),
        "whisper": importlib.util.find_spec("faster_whisper") is not None,
        "migrated_seen": _migrated_seen(),
    }
    if isinstance(profiles, tuple) and profiles[0] == 0:
        try:
            rows = json.loads(profiles[1])
            row = next((r for r in rows if r.get("is_default")), rows[0] if rows else {})
            facts["account"], facts["profile"] = row.get("google_account"), row.get("name")
        except (ValueError, IndexError):
            pass
    if isinstance(credits, dict) and credits.get("authenticated") and not credits.get("balance_unknown"):
        facts["credits"] = credits.get("credits")
        facts["tier"] = credits.get("sku") or credits.get("user_paygate_tier")
        facts["account"] = facts["account"] or credits.get("email")
    return facts


def format_report(f: Dict[str, Any]) -> str:
    ok, bad, warn = "OK", "PROBLEM", "NOTE"
    out = ["### Gemini Media Pass doctor", ""]
    fixes = []
    if f["gflow_version"]:
        out.append(f"- {ok} gflow installed: {f['gflow_version']}")
    else:
        out.append(f"- {bad} gflow not found")
        fixes.append("Install gflow: `pip install gflow-cli`")
    if f["signed_in"]:
        who = f["account"] or "unknown account"
        out.append(f"- {ok} Flow signed in as {who}" + (f" (profile {f['profile']})" if f["profile"] else ""))
    else:
        out.append(f"- {bad} Flow not signed in")
        fixes.append("Sign in: `gflow auth login` (or `gemini-media-pass-login`)")
    if f["credits"] is not None:
        out.append(f"- {ok} Plan: {f['tier'] or 'unknown'}, {f['credits']} credits")
    elif f["signed_in"]:
        out.append(f"- {warn} Balance unreadable (gflow issue #795). Check it in Flow. `flow_spend_ledger` logs "
                   "what this server spends")
    migrated = f["balance_unknown"] or f["migrated_seen"]
    if migrated:
        out.append(f"- {warn} Frontend: new flow.google.com (migrated account)"
                   + (f", last refusal {f['migrated_seen']}" if f["migrated_seen"] else ""))
        out.append(f"  - Works here: {WORKS_MIGRATED}")
        out.append(f"  - Use the Flow web UI for: {WEB_UI_ONLY}")
    elif f["signed_in"]:
        out.append(f"- {ok} Frontend: classic labs.google. Works here: {WORKS_CLASSIC}")
    if f["agy_problem"]:
        out.append(f"- {bad} agy: {f['agy_problem']}")
        fixes.append("Open `agy` once, sign in, and check the model list. Or set GEMINI_API_KEY")
    else:
        out.append(f"- {ok} agy answered a {runner.PING_SECONDS} s ping")
    if f["ffmpeg"] and f["ffprobe"]:
        out.append(f"- {ok} ffmpeg and ffprobe found")
    else:
        out.append(f"- {bad} ffmpeg missing (needed for clip QA cut checks and mp3 speech)")
        fixes.append("Install ffmpeg and put it on PATH (`winget install Gyan.FFmpeg` on Windows)")
    out.append(f"- {ok if f['whisper'] else warn} faster-whisper "
               + ("installed (clip QA checks dialogue and lyrics)" if f["whisper"]
                  else "not installed, clip QA skips speech: `pip install faster-whisper`"))
    out += ["", "**Fix first:**" if fixes else "**Ready.**"] + [f"{i}. {x}" for i, x in enumerate(fixes, 1)]
    return "\n".join(out)


def register_doctor_tools(mcp):
    @mcp.tool(name="flow_doctor",
              description="One readable health check: gflow sign-in, Google account and plan, classic or migrated "
                          "Flow frontend and what works on it, an agy ping, ffmpeg and faster-whisper. Spends nothing.")
    async def flow_doctor() -> str:
        return format_report(await gather_facts())

    @mcp.tool(name="flow_clip_qa",
              description="Check a downloaded clip before you edit with it: cuts inside the clip, the words actually "
                          "spoken vs expected_words, and lyrics in music (kind='music'). Needs ffmpeg; speech checks "
                          "need faster-whisper.")
    async def flow_clip_qa(path: str, kind: str = "video", expected_words: Optional[str] = None,
                           cut_threshold: float = clipqa.CUT_THRESHOLD) -> str:
        return await asyncio.to_thread(clipqa.run_qa, path.replace("\\", "/"), kind, expected_words, cut_threshold)

    @mcp.tool(name="flow_spend_ledger",
              description="What this server spent on Flow, per request, from its local ledger. Useful because the "
                          "Flow balance often cannot be read.")
    async def flow_spend_ledger(days: int = 1) -> str:
        return ledger.summary(days)
