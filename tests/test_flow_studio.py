"""Shot planning, result parsing and local ffmpeg editing. No network, no gflow: generation is faked."""
import asyncio
import json
import os

import pytest

from gemini_media_pass_mcp import flow, flow_studio, video_edit


def shots(*items):
    return flow_studio.parse_shots(list(items))


def test_render_length_picks_shortest_clip():
    assert flow_studio.render_length(2, "veo-lite") == 4
    assert flow_studio.render_length(5, "veo-fast") == 6
    assert flow_studio.render_length(9, "omni-flash") == 10
    assert flow_studio.render_length(9, "veo-fast") is None


def test_auto_model_uses_cheapest_for_short_shots():
    s = shots({"prompt": "nod", "seconds": 2}, {"prompt": "walk", "seconds": 7})
    assert [x.model for x in s] == ["veo-lite", "veo-fast"]


def test_grouped_reactions_pack_into_one_generation():
    s = shots(*[{"prompt": f"reaction {i}", "seconds": 2, "group": "dan"} for i in range(4)],
              {"prompt": "city b-roll", "seconds": 5})
    units = flow_studio.plan_units(s)
    assert len(units) == 2
    packed = units[0]
    assert [x.prompt for x in packed.shots] == [f"reaction {i}" for i in range(4)]
    assert packed.offsets == [0, 2, 4, 6] and packed.length == 8
    assert "[2s-4s] reaction 1" in packed.prompt
    assert sum(u.cost for u in units) < flow_studio.naive_cost(s)


def test_packing_respects_clip_limit_and_frames(tmp_path):
    frame = tmp_path / "f.png"
    frame.write_bytes(b"x")
    s = shots(*[{"prompt": f"r{i}", "seconds": 3, "group": "g"} for i in range(4)],
              {"prompt": "framed", "seconds": 2, "group": "g", "initial_frame": str(frame)})
    units = flow_studio.plan_units(s)
    assert [len(u.shots) for u in units] == [2, 2, 1]       # 3+3 fits in 8, a third would not
    assert units[2].initial_frame == str(frame)
    assert len(flow_studio.plan_units(s, pack=False)) == 5


def test_too_long_shot_is_refused():
    with pytest.raises(ValueError):
        flow_studio.plan_units(shots({"prompt": "long", "seconds": 9, "model": "veo-fast"}))


def test_parse_video_json_reads_gflow_result():
    out = json.dumps({"status": "ok", "media_id": "m1", "local_path": "/tmp/a.mp4", "succeeded": True})
    assert flow.parse_video_json(out) == {"files": ["/tmp/a.mp4"], "media_ids": ["m1"], "errors": []}
    two = "\n".join(json.dumps({"media_id": m, "local_path": f"/t/{m}.mp4"}) for m in ("a", "b"))
    assert flow.parse_video_json(two)["media_ids"] == ["a", "b"]
    bad = json.dumps({"status": "fail", "succeeded": False, "failure_reasons": ["policy"]})
    assert flow.parse_video_json(bad)["errors"] == ["policy"]


def test_reference_args_pairs_ids_and_names():
    assert flow.reference_args("e1, e2", "Dan") == ["--reference-entity", "e1", "--reference-entity-name", "Dan",
                                                    "--reference-entity", "e2"]
    assert flow.reference_args(None) == []


def test_unreadable_balance_still_counts_as_signed_in(monkeypatch):
    async def fake_run(cmd, timeout=120):
        return 1, b"", b"aisandbox-pa authentication failed: the labs.google session returned no access token"
    monkeypatch.setattr(flow, "_run", fake_run)
    data = asyncio.run(flow._fetch_credits_raw())
    assert data == {"authenticated": True, "balance_unknown": True}
    assert "unknown" in flow.balance_line({"current": None})


def test_concat_filter_adds_silence_for_clips_without_audio():
    graph, extra = video_edit.concat_filter([2, 3], [True, False], 720, 1280)
    assert "trim=0:2.000" in graph and "atrim=0:2.000" in graph
    assert "anullsrc" in " ".join(extra) and "concat=n=2:v=1:a=1" in graph


class FakeMCP:
    def __init__(self):
        self.tools = {}

    def tool(self, name, description=""):
        def deco(fn):
            self.tools[name] = fn
            return fn
        return deco


async def make_clip_async(path, seconds=8):
    rc, err = await video_edit._ffmpeg([
        "-y", "-f", "lavfi", "-i", f"testsrc=size=360x640:rate=24:duration={seconds}",
        "-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(path)])
    assert rc == 0, err


def make_clip(path, seconds=8):
    asyncio.run(make_clip_async(path, seconds))


needs_ffmpeg = pytest.mark.skipif(video_edit.find_ffmpeg() is None, reason="ffmpeg not available")


def test_plan_only_spends_nothing(monkeypatch):
    async def boom(*a, **k):
        raise AssertionError("gflow must not run for a plan")
    monkeypatch.setattr(flow_studio, "_run", boom)
    mcp = FakeMCP()
    flow_studio.register_studio_tools(mcp)
    out = asyncio.run(mcp.tools["flow_shoot_shot_list"](
        [{"prompt": "laugh", "seconds": 2, "group": "r"}, {"prompt": "gasp", "seconds": 2, "group": "r"}]))
    assert "2 shots in 1 generations" in out and "Nothing has been generated" in out


@needs_ffmpeg
def test_shot_list_cuts_clips_writes_manifest_and_reuses(monkeypatch, tmp_path):
    calls = []

    async def fake_generate(u, aspect, raw_dir, *a):
        calls.append(u.prompt)
        dest = os.path.join(raw_dir, f"gen{len(calls)}.mp4")
        await make_clip_async(dest, u.length)
        return {"files": [dest], "media_ids": [f"m{len(calls)}"], "error": None}

    async def signed_in(*a, **k):
        return {"authenticated": True, "balance_unknown": True}

    async def spend(cost):
        return {"current": None}

    monkeypatch.setattr(flow_studio, "generate_unit", fake_generate)
    monkeypatch.setattr(flow_studio.CreditTracker, "get_or_sync", signed_in)
    monkeypatch.setattr(flow_studio.CreditTracker, "record_real_spend", spend)
    mcp = FakeMCP()
    flow_studio.register_studio_tools(mcp)
    shot_list = [{"name": "laugh", "prompt": "laughs", "seconds": 2, "group": "r"},
                 {"name": "gasp", "prompt": "gasps", "seconds": 3, "group": "r"},
                 {"name": "street", "prompt": "street b-roll", "seconds": 5}]
    run = lambda: asyncio.run(mcp.tools["flow_shoot_shot_list"](
        shot_list, output_dir=str(tmp_path), confirm=True, max_credits=100, join=True))

    out = run()
    assert len(calls) == 2, out
    rows = json.loads((tmp_path / "shotlist.json").read_text())
    assert [r["name"] for r in rows] == ["laugh", "gasp", "street"]
    assert [r["source_start"] for r in rows][:2] == [0.0, 2.0]
    for r in rows:
        length, _ = asyncio.run(video_edit.probe(r["file"]))
        assert abs(length - r["seconds"]) < 0.25
    assert (tmp_path / "joined_preview.mp4").is_file()

    out2 = run()                                  # same list again: nothing new is generated
    assert len(calls) == 2 and "reused from earlier runs: 2" in out2


@needs_ffmpeg
def test_remake_grabs_frames_and_waits_for_confirm(monkeypatch, tmp_path):
    clip = tmp_path / "scene.mp4"
    make_clip(clip, 5)

    async def describe(path, q):
        return f"desc of {os.path.basename(path)}"

    async def boom(*a, **k):
        raise AssertionError("must not generate before confirm")
    monkeypatch.setattr(flow_studio, "describe_frame", describe)
    monkeypatch.setattr(flow_studio, "generate_unit", boom)
    mcp = FakeMCP()
    flow_studio.register_studio_tools(mcp)
    out = asyncio.run(mcp.tools["flow_remake_scene"](str(clip), "make it snow", output_dir=str(tmp_path / "o")))
    assert (tmp_path / "o" / "first_frame.png").is_file() and (tmp_path / "o" / "last_frame.png").is_file()
    assert "desc of first_frame.png" in out and "make it snow" in out and "Nothing has been generated" in out


def test_character_tools_read_gflow_json(monkeypatch):
    async def fake_run(cmd, timeout=120):
        if "list" in cmd:
            return 0, json.dumps({"status": "ok", "characters": [{"entity_id": "e1", "display_name": "Dan"}]}).encode(), b""
        return 0, json.dumps({"status": "ok", "character": {"entity_id": "e2", "name": "Dan 2"}}).encode(), b""
    monkeypatch.setattr(flow_studio, "_run", fake_run)
    mcp = FakeMCP()
    flow_studio.register_studio_tools(mcp)
    assert "| Dan | `e1` |" in asyncio.run(mcp.tools["flow_list_characters"]("p1"))
    assert "`e2`" in asyncio.run(mcp.tools["flow_create_character"]("p1", "Dan 2", "face"))


def test_failure_reason_keeps_gflow_detail():
    out = json.dumps({"status": "fail", "detail": "agent-only composer: no finished video within 600s of submit"})
    why = flow_studio.failure_reason(9, ["generation failed"], out, "")
    assert "no finished video within 600s" in why and "refunds failed generations" in why
    assert flow_studio.failure_reason(2, [], "", "Error: bad flag\n") == "Error: bad flag"
