"""How every Gemini call is made.

Order of backends, first one that answers wins:
1. The Google Antigravity CLI (`agy`), sandboxed. Read-only tools run in plan mode. The CLI never gets
   --dangerously-skip-permissions unless the user opts in with GMP_AGY_UNSAFE=1, because text inside an
   analyzed file could otherwise make the agent run commands on this machine.
2. A local OpenAI-compatible bridge, ONLY when BRIDGE_URL is set.
3. The Gemini API with GEMINI_API_KEY, sent in the x-goog-api-key header (never in the URL).
Video/audio tools disable steps 2 and 3 unless allow_paid_api=True was explicitly passed.

Every backend has a timeout, and every failure is reported back instead of being swallowed.
"""
from __future__ import annotations

import asyncio
import base64
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import wave

from .config import find_agy_binary, get_bridge_url

API = "https://generativelanguage.googleapis.com/v1beta/models"
API_FLASH = os.environ.get("GEMINI_API_MODEL_FLASH", "gemini-3.5-flash")
API_PRO = os.environ.get("GEMINI_API_MODEL_PRO", "")
AGY_FLASH = os.environ.get("GMP_AGY_MODEL_FLASH", "gemini-3.8-flash-high")
AGY_PRO = os.environ.get("GMP_AGY_MODEL_PRO", "gemini-3.1-pro-high")
TTS_MODEL = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
TIMEOUT = int(os.environ.get("GMP_TIMEOUT_SECONDS", "180"))
INLINE_LIMIT = 20 * 1024 * 1024
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
        ".mp3": "audio/mp3", ".wav": "audio/wav", ".m4a": "audio/m4a", ".pdf": "application/pdf",
        ".mp4": "video/mp4", ".mov": "video/quicktime", ".webm": "video/webm"}
TTS_VOICES = ("Puck", "Charon", "Kore", "Fenrir", "Aoede")


def agy_command(agy_path: str, model: str, writes: bool = False) -> list[str]:
    """The agy command line. writes=False (every analysis tool) runs read-only in plan mode."""
    cmd = [agy_path, "--input-format", "stream-json", "--output-format", "stream-json", "--model", model,
           "--sandbox", "--print-timeout", f"{TIMEOUT}s"]
    if not writes:
        cmd += ["--mode", "plan"]
    if os.environ.get("GMP_AGY_UNSAFE") == "1":
        cmd.append("--dangerously-skip-permissions")
    return cmd


def _post(url: str, body: dict, api_key: str, timeout: int = TIMEOUT) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json", "x-goog-api-key": api_key})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _bridge(model: str, content: str) -> str:
    url = get_bridge_url()
    if not url:
        return ""
    body = {"model": model, "messages": [{"role": "user", "content": content}], "stream": False}
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()


class AgyEmpty(Exception):
    """agy ran and finished but returned no answer."""


PING_SECONDS = int(os.environ.get("GMP_AGY_PING_SECONDS", "20"))
PING_OK_FOR = 600          # a good ping is trusted for 10 minutes
_last_ping_ok = 0.0


async def _agy(model: str, content: str, writes: bool, timeout: int = TIMEOUT + 15) -> str:
    """The answer from agy, "" when agy is not installed. Raises TimeoutError or AgyEmpty when agy fails."""
    agy_path = find_agy_binary()
    if not agy_path:
        return ""
    proc = await asyncio.create_subprocess_exec(*agy_command(agy_path, model, writes), stdin=asyncio.subprocess.PIPE,
                                                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    payload = json.dumps({"event": "user", "message": {"content": content}}) + "\n"
    try:
        out, err = await asyncio.wait_for(proc.communicate(payload.encode("utf-8")), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise TimeoutError(f"agy timed out, no answer within {timeout} s")
    for line in out.decode("utf-8", errors="replace").splitlines():
        try:
            evt = json.loads(line)
        except ValueError:
            continue
        if evt.get("event") == "result":
            answer = (evt.get("result", {}).get("response") or "").strip()
            if answer:
                return answer
    why = err.decode("utf-8", errors="replace").strip()[-200:]
    raise AgyEmpty("agy answered with nothing" + (f" ({why})" if why else "") +
                   ". Open agy once and check it is signed in and the model is available.")


async def ping_agy(model: str = "gemini-3.8-flash-high") -> str:
    """"" when agy answers a tiny prompt within PING_SECONDS, else why not. Passing pings are cached."""
    global _last_ping_ok
    if PING_SECONDS <= 0 or time.monotonic() - _last_ping_ok < PING_OK_FOR:
        return ""
    if not find_agy_binary():
        return "agy is not installed (or set AGY_PATH)"
    try:
        await _agy(model, "Reply with the single word OK.", False, timeout=PING_SECONDS)
    except TimeoutError:
        return f"agy timed out on a {PING_SECONDS} s ping"
    except AgyEmpty as e:
        return f"{e}"
    except Exception as e:
        return f"agy failed a ping: {type(e).__name__}: {e}"[:300]
    _last_ping_ok = time.monotonic()
    return ""


async def _agy_checked(model: str, content: str, writes: bool) -> str:
    """Fail fast: a short ping before a long call, so a dead agy costs 20 s, not minutes."""
    problem = await ping_agy()
    if problem:
        raise AgyEmpty(problem)
    return await _agy(model, content, writes)


def _api(model: str, content: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return ""
    parts, notes = [], []
    for p in re.findall(r"`([A-Za-z]:/[^`\r\n]+|/[^`\r\n]+)`", content):
        ext = os.path.splitext(p)[1].lower()
        if os.path.isfile(p) and ext in MIME:
            if os.path.getsize(p) > INLINE_LIMIT:
                notes.append(f"{p} is over 20 MB, too big to send inline through the API")
                continue
            with open(p, "rb") as f:
                parts.append({"inlineData": {"mimeType": MIME[ext], "data": base64.b64encode(f.read()).decode()}})
    if notes and not parts:
        raise ValueError("; ".join(notes))
    api_model = API_PRO if "pro" in model else API_FLASH
    if not api_model:
        raise ValueError("Set GEMINI_API_MODEL_PRO to an available Pro model; refusing silent Flash substitution")
    res = _post(f"{API}/{api_model}:generateContent", {"contents": [{"parts": parts + [{"text": content}]}]}, api_key)
    out = res.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    return "\n".join(p.get("text", "") for p in out).strip()


async def execute_query(model: str, content: str, writes: bool = False, *,
                        allow_paid_fallback: bool = True, api_model_tier: str | None = None) -> str:
    """Ask Gemini. writes=True only for tools that must create files (image generation)."""
    errors = []
    backends = [("agy", lambda: _agy_checked(model, content, writes))]
    if allow_paid_fallback:
        backends.extend([("bridge", lambda: asyncio.to_thread(_bridge, model, content)),
                         ("api", lambda: asyncio.to_thread(_api, api_model_tier or model, content))])
    for name, call in backends:
        try:
            answer = await call()
            if answer:
                return answer
        except Exception as e:  # report, then try the next backend
            label = "" if isinstance(e, (AgyEmpty, TimeoutError)) else f"{type(e).__name__}: "
            errors.append(f"{name}: {label}{e}"[:300])
    if not find_agy_binary():
        errors.append("agy: not installed (or set AGY_PATH)")
    if not allow_paid_fallback:
        return ("Error: subscription analysis did not complete.\n" +
                "\n".join(f"- {e}" for e in errors) +
                "\nPaid API and bridge fallback are disabled. Fix agy/sign-in or, only with user "
                "authorization, retry with allow_paid_api=True. No paid fallback was attempted.")
    if not os.environ.get("GEMINI_API_KEY"):
        errors.append("api: GEMINI_API_KEY is not set")
    tried = "\n".join(f"- {e}" for e in errors)
    return ("Error: Gemini did not answer.\n" + tried + "\n\nFix one of: install and sign in to the Antigravity CLI "
            "(`agy`), set AGY_PATH, or set GEMINI_API_KEY. Run `flow_doctor` for a full check.")


async def execute_media_query(content: str, model_tier: str = "flash", allow_paid_api: bool = False) -> str:
    """Flash by default; explicit Pro and external fallback are independent choices."""
    if model_tier not in {"flash", "pro"}:
        return "Error: model_tier must be 'flash' or 'pro'."
    model = AGY_PRO if model_tier == "pro" else AGY_FLASH
    return await execute_query(model, content, allow_paid_fallback=allow_paid_api, api_model_tier=model_tier)


def pcm_to_wav(pcm: bytes, rate: int = 24000) -> bytes:
    """Gemini TTS returns raw 16-bit mono PCM; wrap it in a WAV header."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)
    return buf.getvalue()


def save_audio(wav_bytes: bytes, path: str) -> str:
    """Write WAV bytes to `path`. A non-.wav path is converted with ffmpeg; without ffmpeg it is saved as .wav."""
    if path.lower().endswith(".wav"):
        with open(path, "wb") as f:
            f.write(wav_bytes)
        return path
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        path = os.path.splitext(path)[0] + ".wav"
        with open(path, "wb") as f:
            f.write(wav_bytes)
        return path
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(wav_bytes)
    try:
        subprocess.run([ffmpeg, "-y", "-v", "error", "-i", tmp.name, path], check=True, timeout=120)
    finally:
        os.unlink(tmp.name)
    return path


def _gemini_tts(text: str, voice: str, style: str, api_key: str) -> bytes:
    body = {"contents": [{"parts": [{"text": f"{style}\n\n{text}" if style else text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {
                "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice if voice in TTS_VOICES else "Puck"}}}}}
    res = _post(f"{API}/{TTS_MODEL}:generateContent", body, api_key, timeout=120)
    inline = res["candidates"][0]["content"]["parts"][0]["inlineData"]
    raw, mime = base64.b64decode(inline["data"]), inline.get("mimeType", "")
    if raw[:4] == b"RIFF":
        return raw
    rate = int(mime.split("rate=")[1].split(";")[0]) if "rate=" in mime else 24000
    return pcm_to_wav(raw, rate)


async def execute_tts(text: str, voice: str = "Puck", output_path: str = "generated_speech.wav",
                      style_instruction: str = "") -> str:
    """Speech from text: Gemini TTS when GEMINI_API_KEY is set, else free edge-tts neural voices."""
    clean_path = os.path.abspath(output_path).replace("\\", "/")
    os.makedirs(os.path.dirname(clean_path) or ".", exist_ok=True)
    errors = []
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            wav_bytes = await asyncio.to_thread(_gemini_tts, text, voice, style_instruction, api_key)
            saved = save_audio(wav_bytes, clean_path)
            return f"Speech saved with Gemini TTS ({TTS_MODEL}, voice {voice}): `{saved}`"
        except Exception as e:
            errors.append(f"gemini tts: {type(e).__name__}: {e}"[:300])
    try:
        import edge_tts
        edge_voice = os.environ.get("GMP_EDGE_VOICE") or {
            "Puck": "en-US-GuyNeural", "Charon": "en-US-ChristopherNeural", "Kore": "en-US-JennyNeural",
            "Fenrir": "en-US-EricNeural", "Aoede": "en-US-AriaNeural"}.get(voice, voice if "Neural" in voice else "en-US-JennyNeural")
        mp3_path = clean_path if clean_path.lower().endswith(".mp3") else os.path.splitext(clean_path)[0] + ".mp3"
        await asyncio.wait_for(edge_tts.Communicate(text, edge_voice).save(mp3_path), timeout=120)
        return f"Speech saved with edge-tts (voice {edge_voice}): `{mp3_path}`"
    except ImportError:
        errors.append("edge-tts is not installed (pip install edge-tts)")
    except Exception as e:
        errors.append(f"edge-tts: {type(e).__name__}: {e}"[:300])
    return "Error: no speech was generated.\n" + "\n".join(f"- {e}" for e in errors)
