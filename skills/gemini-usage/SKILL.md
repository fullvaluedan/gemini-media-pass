---
name: gemini-usage
description: Check actual Flow credits remaining and Google One credit activity on demand or once after a batch of generations.
---

Use live account data, not just the local ledger. With browser control available:

Honor the user's chosen account or configured `GMP_FLOW_ACCOUNT` (which may be in
`~/.gemini_media_pass.env`). Read only that setting, without exposing other config
values. When an expected account is set, prefer `gemini_usage` / the CLI with its
account check for the balance. Only use browser activity from the same account;
do not substitute whichever account happens to be open.

1. Open or reuse https://flow.google.com in the user's signed-in browser. Read
   Account details and confirm the selected account. If multiple accounts make
   selection ambiguous, ask which one. Read the displayed Flow credit balance
   and refresh text; do not assume an allowance or reset timezone.
2. Follow the credits link to Google One's activity page, or open
   https://one.google.com/ai/activity. Confirm it is the same account. Read the
   Flow and AI balances and the credit transaction history table. Include
   pagination and the displayed date range when describing coverage.
3. Sum debit magnitudes as charged, positive refund entries as refunded, and
   charged minus refunded as net usage. Do not count refunds as new allowance.
   Do not call recent rows a complete 30-day history unless coverage proves it.
   Only calculate rolling-window totals if row timestamps and timezone are known.
4. Return balance, refresh wording, charges/refunds/net, activity dates, source
   links and when checked. Missing history is unknown, not zero. Stop at login
   or account-verification blockers and explain the required user action.

Without browser control, call `gemini_usage` (the MCP tool), or run the installed
`gemini-usage` CLI / `python -m gemini_media_pass_mcp.receipts`. This queries gflow's
selected signed-in profile for a live balance and separately labels partial local
spend. Include the reported account identity. Pass `account_email` to the tool
or `--account` to the CLI when the intended account is known, so a mismatch
withholds the balance. Browser and CLI sessions may use different accounts;
never merge their numbers. If the provider query fails, report that limitation and offer the browser
path above; a local-only receipt does not fulfill a live-usage request. Do not
install packages just to display a report. Do not inspect or export cookies.

After a batch, leave individual receipts disabled and request one report after
all requested generations/extensions finish, including failures. Batch boundaries
are an agent/user convention, not an automatic server event. Never generate media
to test usage. Only use a personal budget if the user supplies one. Gemini/image
quotas and chat token usage are separate and must not be inferred from Flow credits.
