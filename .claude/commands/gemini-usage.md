---
description: Show local Gemini Media Pass Flow usage
---

Use the gemini-usage workflow in `skills/gemini-usage/SKILL.md` to show current
local usage. Prefer `flow_credit_receipt`; otherwise use the installed
`gemini-usage` CLI. If this command was copied outside this repository, the
workflow is: read the local receipt once, report unknown if history is missing,
preserve estimate markers, and do not generate media or infer provider balances.
