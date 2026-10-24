---
description: Check live Flow balance and account credit activity
---

Use `skills/gemini-usage/SKILL.md` if available. This command must check actual
account data, not stop at a missing local ledger.

With browser control, open https://flow.google.com, read Account details → Flow
credits and refresh wording, then follow the credit link to
https://one.google.com/ai/activity. Verify both pages use the same account. Read
balances and the transaction table, including pagination/date coverage. Report
charged credits, refunds, net usage, last activity and when checked. Do not infer
30-day coverage, reset timezone or spend from the balance alone. No media generation.

Without browser control, call the `gemini_usage` MCP tool or installed
`gemini-usage` CLI. If live access fails, report it explicitly and ask for browser
access; local spending alone is not actual account usage. Never extract cookies.
