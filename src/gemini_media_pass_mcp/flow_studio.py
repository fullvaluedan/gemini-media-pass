"""
Google Flow production tools: shot lists that spend as few generations as possible, 1080p upscale,
avatar (Flow Character) tools, and remaking a movie scene from its first and last frames.

Shot lists deliver separate, trimmed clips plus a shotlist.json/csv so the footage can be cut in an editor
(for example DaVinci Resolve). Joining them into one file is optional.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from . import video_edit
from .flow import (
    COST_CATALOG, DEFAULT_OUTPUT_DIR, GEN_TIMEOUT, CreditTracker, _find_gflow, _format_not_authenticated_msg,
    _run, balance_line, parse_video_json, reference_args, spend_check,
)

VEO_LENGTHS = [4, 6, 8]
OMNI_LENGTHS = [4, 6, 8, 10]
SHORT_SHOT_SECONDS = 4          # shots this short default to the cheapest model
STATE_FILE = ".flow_shots_state.json"
MODELS = {"veo-fast", "veo-lite", "veo-quality", "veo-lite-lp", "omni-flash"}


def allowed_lengths(model: str) -> List[int]:
    return OMNI_LENGTHS if model == "omni-flash" else VEO_LENGTHS


def render_length(seconds: float, model: str) -> Optional[int]:
    """Shortest clip Flow can render that still covers `seconds`, or None if it is too long."""
    for n in allowed_lengths(model):
        if seconds <= n:
            return n
    return None


def pick_model(seconds: float, requested: Optional[str], default: str) -> str:
    m = (requested or default or "auto").lower().strip().replace("_", "-")
    if m == "auto":
        return "veo-lite" if seconds <= SHORT_SHOT_SECONDS else "veo-fast"
    return m if m in MODELS else "veo-fast"


def aspect_of(orientation: str) -> str:
    o = (orientation or "").lower().strip()
    return "16:9" if o in {"horizontal", "landscape", "16:9", "widescreen", "cinematic", "youtube"} else "9:16"


def slug(text: str, limit: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return (s[:limit].strip("-")) or "shot"


@dataclass
class Shot:
    index: int
    name: str
    prompt: str
    seconds: float
    model: str
    group: Optional[str] = None
    initial_frame: Optional[str] = None
    end_frame: Optional[str] = None
    avatar: bool = False
    takes: int = 1


@dataclass
class Unit:
    """One Flow generation. It holds one shot, or several short shots packed as timed beats."""
    shots: List[Shot]
    model: str
    length: int
    prompt: str
    offsets: List[float] = field(default_factory=list)
    takes: int = 1
    initial_frame: Optional[str] = None
    end_frame: Optional[str] = None
    avatar: bool = False

    @property
    def cost(self) -> int:
        return COST_CATALOG.get(self.model, 20) * self.takes

    def key(self, aspect: str, entity: Optional[str]) -> str:
        raw = json.dumps([self.prompt, self.model, self.length, aspect, self.takes, self.initial_frame,
                          self.end_frame, entity if self.avatar else None], sort_keys=True)
        return hashlib.sha1(raw.encode()).hexdigest()[:16]


def parse_shots(shots: List[Dict[str, Any]], default_model: str = "auto") -> List[Shot]:
    out: List[Shot] = []
    for i, raw in enumerate(shots, 1):
        if isinstance(raw, str):
            raw = {"prompt": raw}
        prompt = str(raw.get("prompt", "")).strip()
        if not prompt:
            raise ValueError(f"shot {i} has no prompt")
        seconds = float(raw.get("seconds", raw.get("duration", SHORT_SHOT_SECONDS)))
        if seconds <= 0:
            raise ValueError(f"shot {i}: seconds must be above 0")
        model = pick_model(seconds, raw.get("model"), default_model)
        out.append(Shot(
            index=i, name=slug(raw.get("name") or prompt), prompt=prompt, seconds=seconds, model=model,
            group=(str(raw["group"]).strip() or None) if raw.get("group") else None,
            initial_frame=raw.get("initial_frame"), end_frame=raw.get("end_frame"),
            avatar=bool(raw.get("avatar", False)), takes=max(1, min(int(raw.get("takes", 1)), 4)),
        ))
    return out


def packed_prompt(shots: List[Shot]) -> str:
    beats, t = [], 0.0
    for s in shots:
        beats.append(f"[{t:g}s-{t + s.seconds:g}s] {s.prompt}")
        t += s.seconds
    return ("Same subject, setting, lighting and camera framing throughout. Hard cut at each timestamp, "
            "each beat is a separate moment: " + " ".join(beats))


def plan_units(shots: List[Shot], pack: bool = True) -> List[Unit]:
    """Group shots into as few generations as possible.

    Shots that share a `group`, model, take count and avatar setting, and have no start/end frames, are
    packed into one clip as timed beats, up to the longest clip the model allows. Every other shot is its
    own generation at the shortest length that covers it."""
    units: List[Unit] = []
    open_packs: Dict[tuple, Unit] = {}
    for s in shots:
        length = render_length(s.seconds, s.model)
        if length is None:
            raise ValueError(f"shot {s.index} ({s.name}) is {s.seconds:g}s; {s.model} renders at most "
                             f"{max(allowed_lengths(s.model))}s. Split it into shorter shots.")
        packable = pack and s.group and not s.initial_frame and not s.end_frame
        if packable:
            k = (s.group, s.model, s.takes, s.avatar)
            u = open_packs.get(k)
            limit = max(allowed_lengths(s.model))
            used = sum(x.seconds for x in u.shots) if u else 0.0
            if u and used + s.seconds <= limit:
                u.offsets.append(used)
                u.shots.append(s)
                u.length = render_length(used + s.seconds, s.model) or limit
                u.prompt = packed_prompt(u.shots)
                continue
            u = Unit(shots=[s], model=s.model, length=length, prompt=s.prompt, offsets=[0.0], takes=s.takes,
                     avatar=s.avatar)
            open_packs[k] = u
            units.append(u)
            continue
        units.append(Unit(shots=[s], model=s.model, length=length, prompt=s.prompt, offsets=[0.0],
                          takes=s.takes, initial_frame=s.initial_frame, end_frame=s.end_frame, avatar=s.avatar))
    for u in units:
        if len(u.shots) == 1:
            u.prompt = u.shots[0].prompt   # a group of one is just a normal shot
    return units


def naive_cost(shots: List[Shot]) -> int:
    """What the same shots would cost as one default (veo-fast, 8 s) generation each."""
    return sum(COST_CATALOG["veo-fast"] * s.takes for s in shots)


def plan_text(units: List[Unit], shots: List[Shot], aspect: str) -> str:
    total = sum(u.cost for u in units)
    rows = []
    for n, u in enumerate(units, 1):
        names = ", ".join(f"{s.index:02d} {s.name} ({s.seconds:g}s)" for s in u.shots)
        how = "packed beats" if len(u.shots) > 1 else ("i2v" if u.initial_frame else "t2v")
        rows.append(f"| {n} | {names} | {u.model} | {u.length}s | {how} | {u.takes} | ~{u.cost} |")
    return (
        f"### Shot plan: {len(shots)} shots in {len(units)} generations, ~{total} credits ({aspect})\n\n"
        f"| Gen | Shots | Model | Renders | How | Takes | Credits |\n|---|---|---|---|---|---|---|\n"
        + "\n".join(rows)
        + f"\n\nOne veo-fast generation per shot would be ~{naive_cost(shots)} credits.\n"
        "Nothing has been generated. To render, call again with confirm=true and max_credits of at least "
        f"{total}. Shots already rendered in this output folder are reused, not paid for again."
    )


def _load_state(out_dir: str) -> Dict[str, Any]:
    try:
        with open(os.path.join(out_dir, STATE_FILE), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_state(out_dir: str, state: Dict[str, Any]) -> None:
    with open(os.path.join(out_dir, STATE_FILE), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _rendered(rec: Optional[Dict[str, Any]]) -> bool:
    return bool(rec and rec.get("files") and all(os.path.isfile(f) for f in rec["files"]))


def _newest_mp4(folder: str, after: float = 0.0) -> Optional[str]:
    try:
        mp4s = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(".mp4")]
    except OSError:
        return None
    mp4s = [p for p in mp4s if os.path.getmtime(p) >= after]
    return max(mp4s, key=os.path.getmtime) if mp4s else None


async def generate_unit(u: Unit, aspect: str, raw_dir: str, entity: Optional[str], entity_name: Optional[str],
                        project_id: Optional[str]) -> Dict[str, Any]:
    """Run one Flow generation. Returns {files, media_ids, error}."""
    cmd = _find_gflow() + ["video"]
    if u.initial_frame:
        cmd += ["i2v", "--initial-frame", os.path.abspath(u.initial_frame)]
        if u.end_frame:
            cmd += ["--end-frame", os.path.abspath(u.end_frame)]
        cmd += [u.prompt]
    else:
        cmd += ["t2v", u.prompt]
    cmd += ["--aspect", aspect, "--model", u.model, "--duration", str(u.length), "--count", str(u.takes),
            "--out-dir", raw_dir, "--json"]
    if u.avatar:
        cmd += reference_args(entity, entity_name)
    if project_id:
        cmd += ["--project", project_id]
    rc, out, err = await _run(cmd, timeout=GEN_TIMEOUT)
    text = out.decode("utf-8", errors="replace")
    parsed = parse_video_json(text)
    if rc != 0 or parsed["errors"] or not parsed["files"]:
        return {"files": parsed["files"], "media_ids": parsed["media_ids"],
                "error": failure_reason(rc, parsed["errors"], text, err.decode("utf-8", errors="replace"))}
    return {"files": parsed["files"], "media_ids": parsed["media_ids"], "error": None}


def failure_reason(rc: int, errors: List[str], out_text: str, err_text: str) -> str:
    """Why a gflow run failed, from its JSON error fields and stderr, never just 'generation failed'."""
    detail: List[str] = [e for e in errors if e and e != "generation failed"]
    for block in [out_text] + out_text.splitlines():
        try:
            obj = json.loads(block)
        except Exception:
            continue
        if isinstance(obj, dict):
            for k in ("detail", "error_detail", "title", "error"):
                v = obj.get(k)
                if isinstance(v, str) and v and v not in detail:
                    detail.append(v)
    tail = [ln for ln in err_text.strip().splitlines() if ln.strip() and not ln.lstrip().startswith("{")][-3:]
    detail += [ln.strip() for ln in tail if ln.strip() not in detail]
    reason = "; ".join(detail) or f"gflow exit {rc} with no error text"
    if "no finished video within" in reason:
        reason += (" (Flow may have rejected the clip on its side, for example 'Audio generation failed'; "
                   "Flow refunds failed generations. Check the project at flow.google.com.)")
    return reason[:1200]


async def upscale(media_id: str, out_dir: str, scale: str = "1080p", project_id: Optional[str] = None) -> Dict[str, Any]:
    """Flow's own upscale (credit-free per gflow's measurements). Returns {file, error}."""
    os.makedirs(out_dir, exist_ok=True)
    started = time.time()
    cmd = _find_gflow() + ["video", "upscale", media_id, "--scale", scale, "--out", out_dir]
    if project_id:
        cmd += ["--project", project_id]
    rc, out, err = await _run(cmd, timeout=GEN_TIMEOUT)
    found = _newest_mp4(out_dir, after=started - 1)
    if rc != 0 or not found:
        return {"file": None, "error": (err or out).decode("utf-8", errors="replace").strip()[-800:] or f"gflow exit {rc}"}
    return {"file": found, "error": None}


def write_manifest(out_dir: str, rows: List[Dict[str, Any]]) -> str:
    path_json = os.path.join(out_dir, "shotlist.json")
    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    with open(os.path.join(out_dir, "shotlist.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["shot", "name", "take", "seconds", "file", "prompt", "media_id", "source_clip", "source_start"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in w.fieldnames})
    return path_json


async def describe_frame(path: str, question: str) -> str:
    from .runner import execute_query
    instruction = f"Please inspect the image file at `{path}` using view_file.\nUser question / instruction: {question}"
    try:
        return (await execute_query("gemini-3.8-flash-high", instruction)).strip()
    except Exception as e:  # analysis is optional; the frames are still useful without it
        return f"(could not describe this frame: {e})"


FRAME_QUESTION = (
    "Describe this movie frame for recreating it with an AI video model: subjects and their positions, wardrobe, "
    "expressions, setting, props, lighting, colour palette, lens and camera angle, framing. Be concrete and brief."
)


def register_studio_tools(mcp):
    """Registers shot list, upscale, avatar and scene-remake tools."""

    @mcp.tool(
        name="flow_shoot_shot_list",
        description=(
            "Generate footage for several shots (reactions, B-roll, cutaways, avatar shots) with as few Google Flow "
            "generations as possible, delivered as separate trimmed clips plus shotlist.json/csv for editing in "
            "DaVinci Resolve or similar. Each shot: {name, prompt, seconds (any length up to 8, or 10 on omni-flash), "
            "model?, group?, avatar?, takes?, initial_frame?, end_frame?}. Saves credits by: rendering the shortest "
            "clip that covers each shot and trimming locally (a 2s reaction renders as 4s, not 8s); using veo-lite "
            "for shots of 4s or less when model is 'auto'; packing shots that share a `group` (same subject and "
            "setting, e.g. several reactions) into one generation as timed beats and cutting them apart; and "
            "reusing shots already rendered in the same output folder. With confirm=false (default) it only "
            "returns the plan and credit estimate; nothing is spent. resolution '1080p' uses Flow's own upscale "
            "(credit-free). join=true also writes one joined preview mp4. avatar=true on a shot adds the Flow "
            "Character given by reference_entity (see flow_list_characters)."
        ),
    )
    async def flow_shoot_shot_list(
        shots: List[Dict[str, Any]],
        orientation: str = "vertical",
        model: str = "auto",
        resolution: str = "720p",
        output_dir: Optional[str] = None,
        pack_groups: bool = True,
        confirm: bool = False,
        max_credits: Optional[int] = None,
        reference_entity: Optional[str] = None,
        reference_entity_name: Optional[str] = None,
        project_id: Optional[str] = None,
        join: bool = False,
    ) -> str:
        try:
            parsed = parse_shots(shots, model)
            units = plan_units(parsed, pack=pack_groups)
        except (ValueError, TypeError) as e:
            return f"Shot list problem: {e}"
        aspect = aspect_of(orientation)
        if any(s.avatar for s in parsed) and not reference_entity:
            return "Some shots have avatar=true but no reference_entity was given. Find one with flow_list_characters."
        for s in parsed:
            for frame in (s.initial_frame, s.end_frame):
                if frame and not os.path.isfile(frame):
                    return f"Shot {s.index} ({s.name}): frame file not found: {frame}"
        if not confirm:
            return plan_text(units, parsed, aspect)

        out_dir = os.path.abspath(output_dir or os.path.join(DEFAULT_OUTPUT_DIR, "shots"))
        raw_dir = os.path.join(out_dir, "raw")
        os.makedirs(raw_dir, exist_ok=True)
        state = _load_state(out_dir)
        todo_keys: Dict[str, Unit] = {}
        for u in units:
            k = u.key(aspect, reference_entity)
            if not _rendered(state.get(k)):
                todo_keys.setdefault(k, u)          # identical shots render once
        cost = sum(u.cost for u in todo_keys.values())
        refusal = spend_check(cost, max_credits)
        if refusal:
            return refusal + f"\n\n{len(todo_keys)} of {len(units)} generations still need rendering."
        if todo_keys:
            ledger = await CreditTracker.get_or_sync()
            if not ledger.get("authenticated"):
                return _format_not_authenticated_msg()

        rows: List[Dict[str, Any]] = []
        problems: List[str] = []
        spent = ran = failed = 0
        spend_info: Dict[str, Any] = {}
        for u in units:
            k = u.key(aspect, reference_entity)
            rec = state.get(k)
            if not _rendered(rec):
                res = await generate_unit(u, aspect, raw_dir, reference_entity, reference_entity_name, project_id)
                if res["error"]:
                    failed += 1
                    problems.append(f"Shots {', '.join(s.name for s in u.shots)}: {res['error']}")
                    continue
                ran += 1
                spent += u.cost
                spend_info = await CreditTracker.record_real_spend(u.cost)
                rec = {"files": [os.path.abspath(f) for f in res["files"]], "media_ids": res["media_ids"]}
                state[k] = rec
                _save_state(out_dir, state)
            for take, src in enumerate(rec["files"], 1):
                media_id = rec["media_ids"][take - 1] if take - 1 < len(rec["media_ids"]) else None
                if resolution == "1080p" and media_id:
                    up = rec.setdefault("upscaled", {})
                    if not (up.get(media_id) and os.path.isfile(up[media_id])):
                        r = await upscale(media_id, os.path.join(out_dir, "raw_1080p"), "1080p", project_id)
                        if r["file"]:
                            up[media_id] = r["file"]
                            _save_state(out_dir, state)
                        else:
                            problems.append(f"Upscale of {os.path.basename(src)} failed, kept 720p: {r['error']}")
                    src = up.get(media_id) or src
                for s, start in zip(u.shots, u.offsets):
                    suffix = f"_take{take}" if len(rec["files"]) > 1 else ""
                    dest = os.path.join(out_dir, f"{s.index:02d}_{s.name}{suffix}.mp4")
                    err = await video_edit.cut(src, start, s.seconds, dest)
                    if err:
                        problems.append(f"Cutting {os.path.basename(dest)} failed: {err}")
                        continue
                    rows.append({"shot": s.index, "name": s.name, "take": take, "seconds": s.seconds, "file": dest,
                                 "prompt": s.prompt, "media_id": media_id, "source_clip": src, "source_start": start})
        rows.sort(key=lambda r: (r["shot"], r["take"]))
        manifest = write_manifest(out_dir, rows) if rows else None

        joined = ""
        if join and rows:
            firsts = [r for r in rows if r["take"] == 1]
            jpath = os.path.join(out_dir, "joined_preview.mp4")
            err = await video_edit.trim_scale_join([r["file"] for r in firsts], [r["seconds"] for r in firsts],
                                                   jpath, aspect, resolution if resolution in ("720p", "1080p") else "720p")
            joined = f"\n- Joined preview: `{jpath}`" if not err else f"\n- Joining failed: {err}"

        lines = [f"- `{os.path.basename(r['file'])}` ({r['seconds']:g}s)" for r in rows]
        reused = len(units) - ran - failed
        return (
            f"### Shot list rendered: {len(rows)} clips in `{out_dir}`\n\n"
            + "\n".join(lines)
            + f"\n\n- Generations run: {ran}, failed: {failed}, reused from earlier runs: {reused}"
            + f"\n- Credits spent (estimate): {spent}. Balance: {balance_line(spend_info) if spend_info else 'unchanged'}"
            + (f"\n- Manifest for the editor: `{manifest}` (and shotlist.csv)" if manifest else "")
            + joined
            + ("\n\n**Problems:**\n" + "\n".join(f"- {p}" for p in problems) if problems else "")
        )

    @mcp.tool(
        name="flow_upscale_video",
        description="Upscale a Flow-generated video to 1080p (or download 720p / a 270p GIF) by its media id, using Flow's own upscaler. gflow measured this as credit-free.",
    )
    async def flow_upscale_video(media_id: str, scale: str = "1080p", output_dir: Optional[str] = None,
                                 project_id: Optional[str] = None) -> str:
        if scale not in ("1080p", "720p", "270p"):
            return "scale must be 1080p, 720p or 270p."
        r = await upscale(media_id, os.path.abspath(output_dir or DEFAULT_OUTPUT_DIR), scale, project_id)
        return f"Saved `{r['file']}` ({scale})." if r["file"] else f"Upscale failed:\n```\n{r['error']}\n```"

    @mcp.tool(
        name="flow_list_characters",
        description="List the Flow Characters (avatars) saved in a Flow project, with the entity ids to pass as reference_entity for consistent avatar shots.",
    )
    async def flow_list_characters(project_id: str) -> str:
        rc, out, err = await _run(_find_gflow() + ["character", "list", "--project", project_id, "--json"], timeout=180)
        text = out.decode("utf-8", errors="replace").strip()
        if rc != 0:
            return f"Could not list characters:\n```\n{err.decode('utf-8', errors='replace').strip() or text}\n```"
        try:
            data = json.loads(text)
        except Exception:
            return f"```\n{text}\n```"
        items = data if isinstance(data, list) else data.get("characters", [])
        if not items:
            return f"No characters in project `{project_id}`. Create one with flow_create_character."
        rows = "\n".join(f"| {c.get('display_name') or c.get('name', '?')} | `{c.get('entity_id') or c.get('id')}` |" for c in items)
        return f"| Character | reference_entity |\n|---|---|\n{rows}"

    @mcp.tool(
        name="flow_create_character",
        description=(
            "Create a Flow Character (avatar) in a project from a face description (and optional body/clothing "
            "description and preset voice), for consistent avatar shots. Generates reference images, so it spends "
            "image credits (estimated 10)."
        ),
    )
    async def flow_create_character(project_id: str, name: str, face_prompt: str, body_prompt: Optional[str] = None,
                                    voice: Optional[str] = None, max_credits: Optional[int] = None) -> str:
        refusal = spend_check(2 * COST_CATALOG["image"], max_credits)
        if refusal:
            return refusal
        cmd = _find_gflow() + ["character", "create", "--project", project_id, "--name", name,
                               "--face-prompt", face_prompt, "--json"]
        if body_prompt:
            cmd += ["--body-prompt", body_prompt]
        if voice:
            cmd += ["--voice", voice]
        rc, out, err = await _run(cmd, timeout=GEN_TIMEOUT)
        text = out.decode("utf-8", errors="replace").strip()
        if rc != 0:
            return f"Character was not created:\n```\n{err.decode('utf-8', errors='replace').strip()[-800:] or text}\n```"
        try:
            data = json.loads(text)
            eid = (data.get("character") or data).get("entity_id")
        except Exception:
            eid = None
        return f"Created character **{name}**" + (f", reference_entity `{eid}`." if eid else f".\n```\n{text}\n```")

    @mcp.tool(
        name="flow_remake_scene",
        description=(
            "Recreate a scene from a local video file (for example a movie clip) with changes. Grabs the first and "
            "last frame of the scene (or of start_seconds..end_seconds), describes both with Gemini, and returns the "
            "frame paths and descriptions. Nothing is spent until confirm=true: then it renders image-to-video "
            "from the first frame to the last frame with your changes applied. To change how the frames look "
            "(new character, new setting), edit the saved frames first, for example with gemini_generate_image, "
            "and pass them as first_frame / last_frame."
        ),
    )
    async def flow_remake_scene(
        video_path: str,
        changes: str,
        start_seconds: Optional[float] = None,
        end_seconds: Optional[float] = None,
        orientation: str = "vertical",
        model: str = "veo-fast",
        describe: bool = True,
        first_frame: Optional[str] = None,
        last_frame: Optional[str] = None,
        confirm: bool = False,
        max_credits: Optional[int] = None,
        output_dir: Optional[str] = None,
        reference_entity: Optional[str] = None,
        reference_entity_name: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> str:
        src = os.path.abspath(video_path)
        if not os.path.isfile(src):
            return f"Video not found: {src}"
        length, _ = await video_edit.probe(src)
        start = start_seconds or 0.0
        end = end_seconds if end_seconds is not None else length
        if end is None:
            return "Could not read the video's length. Pass end_seconds."
        scene_len = max(0.1, end - start)

        out_dir = os.path.abspath(output_dir or os.path.join(DEFAULT_OUTPUT_DIR, "remakes", slug(os.path.basename(src))))
        os.makedirs(out_dir, exist_ok=True)
        f1 = first_frame or os.path.join(out_dir, "first_frame.png")
        f2 = last_frame or os.path.join(out_dir, "last_frame.png")
        if not first_frame:
            err = await video_edit.extract_frame(src, f1, at=start)
            if err:
                return f"Could not grab the first frame: {err}"
        if not last_frame:
            err = await (video_edit.extract_frame(src, f2, last=True) if end_seconds is None
                         else video_edit.extract_frame(src, f2, at=max(start, end - 0.05)))
            if err:
                return f"Could not grab the last frame: {err}"
        for f in (f1, f2):
            if not os.path.isfile(f):
                return f"Frame not found: {f}"

        chosen = pick_model(scene_len, model, "veo-fast")
        clip_len = render_length(scene_len, chosen) or max(allowed_lengths(chosen))
        note = ("" if scene_len <= max(allowed_lengths(chosen)) else
                f"\n\nThe scene is {scene_len:.1f}s but one clip is at most {clip_len}s, so the action is compressed. "
                "For a faithful remake, split it into shots with flow_shoot_shot_list.")

        d1 = d2 = ""
        if describe:
            d1 = await describe_frame(f1, FRAME_QUESTION)
            d2 = await describe_frame(f2, FRAME_QUESTION)
        prompt = (f"Recreate this scene with these changes: {changes}. "
                  + (f"It opens on: {d1} " if d1 else "")
                  + (f"It ends on: {d2}" if d2 else "")).strip()

        report = (
            f"### Scene remake: `{os.path.basename(src)}` {start:g}s to {end:g}s ({scene_len:.1f}s)\n\n"
            f"- First frame: `{f1}`\n- Last frame: `{f2}`\n"
            + (f"\n**First frame:** {d1}\n\n**Last frame:** {d2}\n" if describe else "")
            + f"\n**Prompt to render:** {prompt}\n\n- Model `{chosen}`, {clip_len}s clip, ~{COST_CATALOG.get(chosen, 20)} credits"
            + note
        )
        if not confirm:
            return report + ("\n\nNothing has been generated. Edit the frames or the changes if needed, then call again "
                             "with confirm=true (and first_frame / last_frame if you edited them).")

        u = Unit(shots=[Shot(1, "remake", prompt, min(scene_len, clip_len), chosen)], model=chosen, length=clip_len,
                 prompt=prompt, offsets=[0.0], initial_frame=f1, end_frame=f2, avatar=bool(reference_entity))
        refusal = spend_check(u.cost, max_credits)
        if refusal:
            return report + "\n\n" + refusal
        ledger = await CreditTracker.get_or_sync()
        if not ledger.get("authenticated"):
            return _format_not_authenticated_msg()
        res = await generate_unit(u, aspect_of(orientation), out_dir, reference_entity, reference_entity_name, project_id)
        if res["error"]:
            return report + f"\n\n**Render failed:** {res['error']}"
        spend_info = await CreditTracker.record_real_spend(u.cost)
        files = "\n".join(f"- `{f}`" for f in res["files"])
        ids = ", ".join(f"`{m}`" for m in res["media_ids"]) or "not reported"
        return report + f"\n\n### Rendered\n{files}\n- Media ids: {ids}\n- Balance: {balance_line(spend_info)}"
