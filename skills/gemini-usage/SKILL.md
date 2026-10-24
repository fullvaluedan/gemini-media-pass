---
name: gemini-usage
description: Show Gemini Media Pass local Flow credit usage on request or once after a batch of Flow generations.
---

Call Gemini Media Pass's `flow_credit_receipt` tool once and show its compact result.
If that tool is unavailable, run `gemini-usage` in the environment where Gemini
Media Pass is installed. The equivalent is
`python -m gemini_media_pass_mcp.receipts`. Do not install or fetch packages just
to display a receipt. If neither is available, explain that the updated server
or package must be installed first.

After a batch, leave individual call receipts disabled and request one summary
when all requested generations/extensions have finished, including failures.
Do not report after each intermediate call. This is an agent workflow convention;
the server cannot infer a batch boundary. Do not run generations to test usage.

Only pass a daily budget when the user specifies one; never assume 50 credits.
Keep estimates marked `~`. Local history excludes other machines and web UI
spending, and does not measure Gemini/image quotas or chat token usage. Missing
history means usage unknown. A local report is not the provider balance.
