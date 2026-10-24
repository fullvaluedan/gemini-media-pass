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

For image/reset questions, also report the separate daily Flow bucket when the
activity page exposes it. Inspect an existing project's image model settings for
provider quota or reset notices without submitting a generation or saving settings.
State "not exposed" for remaining images or exact reset times that are absent.
Do not infer an hourly image quota from daily credits or Gemini/Search limits.
Google's Flow help says the daily 50-credit refresh is triggered by the first
generation; monthly subscription credits refresh on the billing cycle:
https://support.google.com/flow/answer/16526234?hl=en
Preserve the account's exact reset wording. For a clock time without a timezone,
say "as displayed; timezone unverified". Only convert a reset to the user's
timezone or show a countdown if a dated, timezone-aware timestamp is provided.
Do not assume local midnight, UTC midnight, or a fresh 24h window after every job.

The CLI also reports distinct image assets recorded in the selected gflow profile
over rolling 1h/24h, using catalog timestamps. This may include uploads/imports,
exclude other devices, and be capped at 1000 rows. It is not a provider quota or
verified count of successful generation calls. Never subtract it from an assumed
image allowance to manufacture an "images left" estimate.

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
