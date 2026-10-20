"""Clip QA for a downloaded Flow clip: hidden cuts, dialogue heard vs requested, lyrics in music.

Cuts come from ffmpeg's scene score (the difference between neighbouring frames). Speech comes from faster-whisper
when it is installed (`pip install faster-whisper`, the model downloads once on first use).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from typing import Dict, List, Optional

CUT_THRESHOLD = 0.35
WHISPER_MODEL = os.environ.get("GMP_WHISPER_MODEL", "base")
PTS = re.compile(r"pts_time:([0-9.]+)")


def parse_cut_times(ffmpeg_stderr: str, min_gap: float = 0.1) -> List[float]:
    """Cut times from ffmpeg showinfo output. A change in the first 0.1 s is the clip starting, not a cut."""
    times = [round(float(t), 2) for t in PTS.findall(ffmpeg_stderr)]
    return [t for t in times if t >= min_gap]


def find_cuts(path: str, threshold: float = CUT_THRESHOLD) -> List[float]:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise FileNotFoundError("ffmpeg is not installed or not on PATH")
    res = subprocess.run([ffmpeg, "-hide_banner", "-i", path, "-vf", f"select='gt(scene,{threshold})',showinfo",
                          "-an", "-f", "null", "-"], capture_output=True, text=True, timeout=300,
                         encoding="utf-8", errors="replace")
    return parse_cut_times(res.stderr)


def words(text: str) -> List[str]:
    return re.findall(r"[a-z0-9']+", text.lower().replace("’", "'"))


def compare_dialogue(expected: str, heard: str) -> Dict[str, object]:
    """Which requested words were not heard, and which heard words were never requested."""
    want, got = words(expected), words(heard)
    pool = list(got)
    missing = []
    for w in want:
        if w in pool:
            pool.remove(w)
        else:
            missing.append(w)
    ratio = (len(want) - len(missing)) / len(want) if want else 1.0
    return {"match": round(ratio, 2), "missing": missing, "extra": pool,
            "ok": ratio >= 0.8 and len(pool) <= 2}


def sung_words(segments: List[Dict[str, float]]) -> List[str]:
    """Words whisper is fairly sure it heard. Whisper invents words on pure music, so weak guesses are dropped."""
    out: List[str] = []
    for s in segments:
        if s.get("no_speech_prob", 1) < 0.6 and s.get("avg_logprob", -9) > -1.0:
            out += words(str(s.get("text", "")))
    return out


def transcribe(path: str) -> List[Dict[str, float]]:
    from faster_whisper import WhisperModel  # optional dependency
    model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(path, vad_filter=True)
    return [{"text": s.text, "no_speech_prob": s.no_speech_prob, "avg_logprob": s.avg_logprob} for s in segments]


def run_qa(path: str, kind: str = "video", expected_words: Optional[str] = None,
           cut_threshold: float = CUT_THRESHOLD) -> str:
    if not os.path.isfile(path):
        return f"Error: no file at `{path}`"
    lines = [f"### Clip QA: `{os.path.basename(path)}`", ""]
    problems = 0

    if kind != "music":
        try:
            cuts = find_cuts(path, cut_threshold)
            if cuts:
                problems += 1
                lines.append(f"- **Cuts:** {len(cuts)} inside the clip at {', '.join(f'{t:.2f} s' for t in cuts)}. "
                             "Trim to one shot, or regenerate with guardrails=True.")
            else:
                lines.append("- **Cuts:** none, one continuous shot.")
        except Exception as e:
            lines.append(f"- **Cuts:** not checked ({e}).")

    if kind == "music" or expected_words:
        try:
            segs = transcribe(path)
        except ImportError:
            segs = None
            lines.append("- **Speech:** not checked. Install faster-whisper: `pip install faster-whisper`.")
        except Exception as e:
            segs = None
            lines.append(f"- **Speech:** not checked ({type(e).__name__}: {e}).")
        if segs is not None and kind == "music":
            sung = sung_words(segs)
            if len(sung) >= 4:
                problems += 1
                lines.append(f"- **Lyrics:** heard words: \"{' '.join(sung[:30])}\". Flow Music ignored "
                             "'instrumental only'. Use another take.")
            else:
                lines.append("- **Lyrics:** none heard, instrumental.")
        elif segs is not None:
            heard = " ".join(str(s["text"]).strip() for s in segs)
            cmp = compare_dialogue(expected_words or "", heard)
            if not cmp["ok"]:
                problems += 1
            lines.append(f"- **Dialogue:** heard \"{heard.strip()}\" ({int(cmp['match'] * 100)}% of the requested words).")
            if cmp["missing"]:
                lines.append(f"  - Missing: {' '.join(cmp['missing'])}")
            if cmp["extra"]:
                lines.append(f"  - Not requested: {' '.join(cmp['extra'])}")

    lines += ["", "**Verdict:** " + ("usable." if problems == 0 else f"{problems} problem(s), see above.")]
    return "\n".join(lines)
