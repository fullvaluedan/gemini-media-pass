# Gemini Media Pass client instructions

You have access to the Gemini Media Pass MCP server.

1. For help, settings or tool options, call `gemini_media_pass_guide` with
   `topic="all"` (or `models`, `billing`, `settings`, `workflows`).
2. When searching or indexing video (scenes, timestamps, B-roll, character actions
   or transcription), ALWAYS use `gemini_video(model_tier="flash")`.
3. Only select `model_tier="pro"` for explicitly requested deep artistic critique,
   nuanced subtext analysis or subtle directorial/thematic comparisons.
4. Prefer the local Antigravity CLI (`agy`) under the Google AI subscription for
   video/audio analysis. Leave `allow_paid_api=False`; do not send heavy batch
   media to paid API keys or a configured bridge unless the user instructs you to.
   If agy fails, report the failure rather than changing tier or spending route.
5. For Veo generation use `flow_*` tools, which consume Flow credits. Check
   `flow_doctor` or `flow_get_credits` first. After a batch, show `gemini_usage`
   once and verify the account identity.

Native video support and context capacity depend on the selected model/backend;
this wrapper does not guarantee the full advertised model context through agy.
Subscription processing makes no direct API-key charge through this server, but
subscription limits still apply. Do not promise a fixed 97% cost reduction or a
fixed cloud cost per clip. Verify current model/pricing information at
[Google's video guide](https://ai.google.dev/gemini-api/docs/video-understanding)
and [pricing](https://ai.google.dev/gemini-api/docs/pricing).
