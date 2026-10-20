"""The first-try fixes: gflow flags, plain error messages, agy failures, guardrails, clip QA and the ledger.
No network, no agy, no gflow: every external call is replaced."""
import asyncio
import json
import shutil
import subprocess

import pytest

from gemini_media_pass_mcp import clipqa, doctor, flow, guardrails, ledger, runner


class FakeMCP:
    """Collects the tool functions register_flow_tools defines, so tests can call them."""
    def __init__(self):
        self.tools = {}

    def tool(self, name, description=""):
        def wrap(fn):
            self.tools[name] = fn
            return fn
        return wrap


@pytest.fixture
def tools(monkeypatch, tmp_path):
    monkeypatch.setenv("GMP_FLOW_LEDGER", str(tmp_path / "spend.jsonl"))
    monkeypatch.setattr(flow, "TRACKER_FILE", tmp_path / "tracker.json")
    monkeypatch.setattr(flow, "_find_gflow", lambda: ["gflow"])
    mcp = FakeMCP()
    flow.register_flow_tools(mcp)
    return mcp.tools


def fake_gflow(monkeypatch, rc=0, out=b"", err=b"", seen=None):
    async def run(cmd, timeout=120):
        if seen is not None:
            seen.append(cmd)
        if cmd[1:3] == ["credits", "user"]:
            return 0, b'{"credits": 1000, "email": "me@example.com"}', b""
        return rc, out, err
    monkeypatch.setattr(flow, "_run", run)


# 1. music
def test_music_command_uses_only_flags_gflow_accepts(monkeypatch):
    monkeypatch.setattr(flow, "_find_gflow", lambda: ["gflow"])
    cmd = flow.music_command("lofi beat", 30)
    assert cmd[:4] == ["gflow", "tools", "run", "music"]
    assert "--duration" not in cmd and "-o" not in cmd
    assert "30 seconds" in cmd[4]


def test_music_without_a_music_tool_says_where_to_go(tools, monkeypatch, tmp_path):
    fake_gflow(monkeypatch, rc=1, err=b"ConfigurationError: unknown tool 'music'. Available: creative-director")
    out = asyncio.run(tools["flow_generate_music"]("calm piano", 20, str(tmp_path / "m.mp3")))
    assert "not generated" in out and "flowmusic.app" in out


# 2. download
def test_download_uses_out_folder_not_dash_o(monkeypatch, tmp_path):
    monkeypatch.setattr(flow, "_find_gflow", lambda: ["gflow"])
    cmd, target = flow.download_command("abc", str(tmp_path / "clips" / "shot1.mp4"))
    assert "-o" not in cmd and cmd[cmd.index("--out") + 1] == (tmp_path / "clips").as_posix()
    assert target.endswith("clips/shot1.mp4")
    cmd, target = flow.download_command("abc", str(tmp_path / "clips"))
    assert target is None and "--out" in cmd


def test_download_of_web_ui_media_explains_why(tools, monkeypatch):
    body = json.dumps({"status": "fail", "error": {"detail": "No local media record found: abc"}}).encode()
    fake_gflow(monkeypatch, rc=16, out=body)
    out = asyncio.run(tools["flow_download_media"]("abc"))
    assert "not downloaded" in out and "Flow web UI" in out


def test_download_renames_to_the_requested_file(tools, monkeypatch, tmp_path):
    made = tmp_path / "clips" / "flow_123.mp4"
    made.parent.mkdir()
    made.write_bytes(b"x")
    fake_gflow(monkeypatch, out=json.dumps({"status": "ok", "path": str(made)}).encode())
    out = asyncio.run(tools["flow_download_media"]("abc", str(tmp_path / "clips" / "shot1.mp4")))
    assert (tmp_path / "clips" / "shot1.mp4").exists() and "shot1.mp4" in out


def test_sync_passes_the_required_names_flag(tools, monkeypatch):
    seen = []
    fake_gflow(monkeypatch, out=b"{}", seen=seen)
    asyncio.run(tools["flow_sync_catalog"]())
    assert "--names" in seen[-1]


# 3. agy
def test_agy_empty_answer_is_named(monkeypatch):
    monkeypatch.delenv("BRIDGE_URL", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(runner, "find_agy_binary", lambda: "agy")

    async def empty(*a, **k):
        raise runner.AgyEmpty("agy answered with nothing")

    monkeypatch.setattr(runner, "_agy", empty)
    runner._last_ping_ok = 0.0
    out = asyncio.run(runner.execute_query("m", "hi"))
    assert "agy answered with nothing" in out and "no backend is configured" not in out


def test_agy_hang_fails_fast_on_the_ping(monkeypatch):
    monkeypatch.delenv("BRIDGE_URL", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(runner, "find_agy_binary", lambda: "agy")
    calls = []

    async def hang(model, content, writes, timeout=999):
        calls.append(timeout)
        raise TimeoutError("agy timed out")

    monkeypatch.setattr(runner, "_agy", hang)
    runner._last_ping_ok = 0.0
    out = asyncio.run(runner.execute_query("m", "a long job"))
    assert calls == [runner.PING_SECONDS]            # the long call never started
    assert "agy timed out on a 20 s ping" in out


def test_real_agy_process_with_no_output_is_empty_not_unconfigured(monkeypatch):
    # a stand-in agy that exits at once with nothing on stdout
    monkeypatch.setattr(runner, "find_agy_binary", lambda: "python")
    monkeypatch.setattr(runner, "agy_command", lambda *a, **k: ["python", "-c", "import sys; sys.stdin.read()"])
    with pytest.raises(runner.AgyEmpty, match="answered with nothing"):
        asyncio.run(runner._agy("m", "hi", False, timeout=30))


def test_good_ping_is_cached(monkeypatch):
    monkeypatch.setattr(runner, "find_agy_binary", lambda: "agy")
    calls = []

    async def ok(*a, **k):
        calls.append(1)
        return "OK"

    monkeypatch.setattr(runner, "_agy", ok)
    runner._last_ping_ok = 0.0
    assert asyncio.run(runner.ping_agy()) == "" and asyncio.run(runner.ping_agy()) == ""
    assert len(calls) == 1


# 4. migrated frontend
MIGRATED = json.dumps({"status": "fail", "error": {"type": "https://gflow-cli.dev/errors/flow-host-migrated",
                                                   "class": "FlowHostMigratedError", "exit_code": 36}}).encode()


def test_migrated_frontend_gets_plain_guidance(tools, monkeypatch, tmp_path):
    frame = tmp_path / "f.png"
    frame.write_bytes(b"png")
    fake_gflow(monkeypatch, rc=36, out=MIGRATED)
    out = asyncio.run(tools["flow_generate_video"]("a cat walks", mode="i2v", initial_frame=str(frame),
                                                   output_dir=str(tmp_path)))
    assert "new frontend" in out and "text to video" in out and "Flow web UI" in out
    assert ledger.read_entries()[-1]["credits"] == 0


def test_agent_only_composer_message_is_recognised():
    msg = "this account is served Flow's agent-only composer, where gflow drives text-to-image (#799)"
    assert "new frontend" in guardrails.explain_flow_error(msg)


def test_unknown_error_is_not_dressed_up():
    assert guardrails.explain_flow_error("socket closed") is None


# 6. guardrails
def test_guardrail_text_and_exact_words():
    p = guardrails.apply_guardrails("A chef tastes soup.", "Needs more salt.")
    assert "no cuts" in p and "No on-screen text or captions" in p
    assert '"Needs more salt."' in p and "stays silent after" in p


@pytest.mark.parametrize("prompt,flagged", [
    ("A Jack Sparrow-like pirate on a ship", True),
    ("Taylor Swift singing on stage", True),
    ("Darth Vader walks in", True),
    ("A weathered pirate in a red bandana", False),
    ("Something like a cat sleeping", False),
    ("A man on a thorny path", False),
])
def test_third_party_names(prompt, flagged):
    assert bool(guardrails.third_party_names(prompt)) is flagged


def test_named_prompt_is_stopped_before_spending(tools, monkeypatch):
    seen = []
    fake_gflow(monkeypatch, seen=seen)
    out = asyncio.run(tools["flow_generate_video"]("A Jack Sparrow-like pirate laughs"))
    assert out.startswith("Not sent, nothing spent") and seen == []


def test_guardrails_reach_gflow(tools, monkeypatch, tmp_path):
    seen = []
    fake_gflow(monkeypatch, out=b'{"files": []}', seen=seen)
    asyncio.run(tools["flow_generate_video"]("A chef tastes soup", spoken_line="Needs salt.",
                                             output_dir=str(tmp_path)))
    gen = [c for c in seen if c[1] == "video"][0]
    assert "stays silent after" in gen[3]


def test_third_party_block_is_explained():
    out = guardrails.explain_flow_error("Blocked in the interests of third-party content providers")
    assert "refunds" in out


# 7. clip QA
def test_parse_cut_times_skips_the_first_frame():
    err = "[Parsed_showinfo_1] n:0 pts:0 pts_time:0.0 \n[Parsed_showinfo_1] n:1 pts:3 pts_time:2.5 "
    assert clipqa.parse_cut_times(err) == [2.5]


def test_dialogue_compare():
    good = clipqa.compare_dialogue("Needs more salt.", "needs more salt")
    assert good["ok"] and good["match"] == 1.0
    bad = clipqa.compare_dialogue("Needs more salt.", "needs more pepper and also garlic and lemon")
    assert not bad["ok"] and bad["missing"] == ["salt"] and "pepper" in bad["extra"]


def test_lyrics_ignore_weak_whisper_guesses():
    segs = [{"text": "thank you", "no_speech_prob": 0.9, "avg_logprob": -1.5},
            {"text": "dancing in the moonlight tonight", "no_speech_prob": 0.1, "avg_logprob": -0.4}]
    assert clipqa.sung_words(segs) == ["dancing", "in", "the", "moonlight", "tonight"]
    assert clipqa.sung_words(segs[:1]) == []


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")
def test_real_clip_with_a_hard_cut(tmp_path):
    clip = tmp_path / "cut.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=red:s=160x120:d=1:r=10",
                    "-f", "lavfi", "-i", "color=blue:s=160x120:d=1:r=10",
                    "-filter_complex", "[0][1]concat=n=2:v=1", "-y", str(clip)], check=True)
    cuts = clipqa.find_cuts(str(clip))
    assert len(cuts) == 1 and 0.9 <= cuts[0] <= 1.1
    assert "1 inside the clip" in clipqa.run_qa(str(clip))


def test_qa_without_whisper_says_how_to_install(monkeypatch, tmp_path):
    f = tmp_path / "song.mp3"
    f.write_bytes(b"x")

    def no_whisper(path):
        raise ImportError

    monkeypatch.setattr(clipqa, "transcribe", no_whisper)
    assert "pip install faster-whisper" in clipqa.run_qa(str(f), kind="music")


# 8. ledger
def test_ledger_logs_real_cost_when_gflow_reports_it(monkeypatch, tmp_path):
    monkeypatch.setenv("GMP_FLOW_LEDGER", str(tmp_path / "l.jsonl"))
    ledger.log_request("flow_generate_video", "veo-fast", "a", 20, "ok", '{"credits_spent": 10}')
    ledger.log_request("flow_generate_video", "veo-fast", "b", 20, "ok", "not json")
    ledger.log_request("flow_generate_video", "veo-fast", "c", 20, "blocked")
    e = ledger.read_entries()
    assert [x["credits"] for x in e] == [10, 20, 0] and [x["estimated"] for x in e] == [False, True, False]
    assert "30 credits (some estimated)" in ledger.summary()


def test_successful_render_is_logged(tools, monkeypatch, tmp_path):
    fake_gflow(monkeypatch, out=b'{"files": [], "credits_spent": 10}')
    asyncio.run(tools["flow_generate_video"]("a quiet beach at dawn", output_dir=str(tmp_path)))
    assert ledger.read_entries()[-1]["credits"] == 10


# 5. doctor
FACTS = {"gflow_version": "gflow, version 0.86.0", "account": "me@example.com", "profile": "me", "tier": None,
         "credits": None, "signed_in": True, "balance_unknown": True, "agy_problem": "", "ffmpeg": True,
         "ffprobe": True, "whisper": False, "migrated_seen": None}


def test_doctor_report_for_a_migrated_account():
    out = doctor.format_report(FACTS)
    assert "me@example.com" in out and "migrated" in out and "Flow web UI" in out
    assert "faster-whisper" in out and "**Ready.**" in out


def test_doctor_lists_fixes_in_order():
    out = doctor.format_report({**FACTS, "signed_in": False, "agy_problem": "agy timed out on a 20 s ping",
                                "ffmpeg": False})
    assert "1. Sign in" in out and "2. Open `agy`" in out and "3. Install ffmpeg" in out


def test_doctor_reads_migration_from_the_ledger(monkeypatch, tmp_path):
    monkeypatch.setenv("GMP_FLOW_LEDGER", str(tmp_path / "l.jsonl"))
    ledger.log_request("flow_generate_video", "veo-fast", "x", 20, "failed",
                       note=guardrails.explain_flow_error("FlowHostMigratedError")[:120])
    assert "flow_generate_video" in doctor._migrated_seen()
