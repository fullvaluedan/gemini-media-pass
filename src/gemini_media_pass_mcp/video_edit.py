"""
Local video editing with ffmpeg: grab frames, trim clips to exact lengths, scale and join them.

ffmpeg comes from PATH, or from the imageio-ffmpeg package (installed with this server), so nothing extra is needed.
"""

from __future__ import annotations

import asyncio
import os
import re
import shutil
from typing import List, Optional, Sequence, Tuple

TIMEOUT = int(os.environ.get("GMP_FFMPEG_TIMEOUT_SECONDS", "600"))

# (width, height) for each aspect and resolution
SIZES = {
    ("9:16", "720p"): (720, 1280),
    ("9:16", "1080p"): (1080, 1920),
    ("16:9", "720p"): (1280, 720),
    ("16:9", "1080p"): (1920, 1080),
}


def find_ffmpeg() -> Optional[str]:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


async def _ffmpeg(args: Sequence[str], timeout: int = TIMEOUT) -> Tuple[int, str]:
    """Run ffmpeg. Returns (returncode, stderr text)."""
    exe = find_ffmpeg()
    if not exe:
        return 127, "ffmpeg not found. Install it (brew install ffmpeg) or pip install imageio-ffmpeg."
    proc = await asyncio.create_subprocess_exec(exe, "-hide_banner", *args,
                                                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    try:
        _, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return 124, f"ffmpeg did not finish within {timeout} s and was stopped"
    return proc.returncode, err.decode("utf-8", errors="replace")


def parse_duration(ffmpeg_stderr: str) -> Optional[float]:
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", ffmpeg_stderr)
    if not m:
        return None
    h, mnt, s = m.groups()
    return int(h) * 3600 + int(mnt) * 60 + float(s)


async def probe(path: str) -> Tuple[Optional[float], bool]:
    """(duration in seconds or None, has an audio stream)."""
    _, err = await _ffmpeg(["-i", path], timeout=60)   # exits non-zero with no output file; stderr has the info
    return parse_duration(err), bool(re.search(r"Stream #.*Audio:", err))


async def extract_frame(video: str, out_png: str, at: Optional[float] = None, last: bool = False) -> Optional[str]:
    """Save one frame as PNG: at `at` seconds, or the last frame. Returns an error message, or None on success."""
    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)
    if last and at is None:
        args = ["-y", "-sseof", "-0.25", "-i", video, "-update", "1", "-frames:v", "1", out_png]
    else:
        args = ["-y", "-ss", f"{at or 0:.3f}", "-i", video, "-frames:v", "1", out_png]
    rc, err = await _ffmpeg(args, timeout=120)
    if rc != 0 or not os.path.isfile(out_png):
        return err.strip()[-800:] or f"ffmpeg exit {rc}"
    return None


async def cut(src: str, start: float, length: float, out_path: str) -> Optional[str]:
    """Copy `length` seconds of src from `start` into out_path (re-encoded so cuts are frame exact).
    Returns an error message, or None on success."""
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    args = ["-y", "-ss", f"{start:.3f}", "-i", src, "-t", f"{length:.3f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out_path]
    rc, err = await _ffmpeg(args)
    if rc != 0 or not os.path.isfile(out_path):
        return err.strip()[-800:] or f"ffmpeg exit {rc}"
    return None


def concat_filter(lengths: Sequence[float], has_audio: Sequence[bool], width: int, height: int,
                  fps: int = 24) -> Tuple[str, List[str]]:
    """filter_complex that trims clip i to lengths[i] seconds, fits it to width x height and joins all clips.
    Clips without audio get silence so the join never fails. Returns (filter, extra input args for silence)."""
    parts, extra_inputs, labels = [], [], []
    silence_index = len(lengths)
    for i, (sec, audio) in enumerate(zip(lengths, has_audio)):
        parts.append(
            f"[{i}:v]trim=0:{sec:.3f},setpts=PTS-STARTPTS,"
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}[v{i}]"
        )
        if audio:
            parts.append(f"[{i}:a]atrim=0:{sec:.3f},asetpts=PTS-STARTPTS,aresample=48000[a{i}]")
        else:
            extra_inputs += ["-f", "lavfi", "-t", f"{sec:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
            parts.append(f"[{silence_index}:a]asetpts=PTS-STARTPTS[a{i}]")
            silence_index += 1
        labels.append(f"[v{i}][a{i}]")
    parts.append(f"{''.join(labels)}concat=n={len(lengths)}:v=1:a=1[v][a]")
    return ";".join(parts), extra_inputs


async def trim_scale_join(clips: Sequence[str], lengths: Sequence[float], out_path: str,
                          aspect: str = "9:16", resolution: str = "1080p") -> Optional[str]:
    """Trim each clip to its length, fit to the target size, and join into out_path.
    Returns an error message, or None on success."""
    width, height = SIZES.get((aspect, resolution), SIZES[("9:16", "1080p")])
    has_audio = []
    for c in clips:
        _, audio = await probe(c)
        has_audio.append(audio)
    graph, extra = concat_filter(lengths, has_audio, width, height)
    args = ["-y"]
    for c in clips:
        args += ["-i", c]
    args += extra + ["-filter_complex", graph, "-map", "[v]", "-map", "[a]",
                     "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out_path]
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    rc, err = await _ffmpeg(args)
    if rc != 0 or not os.path.isfile(out_path):
        return err.strip()[-1200:] or f"ffmpeg exit {rc}"
    return None
