# Native GPT-5.4 CUA harness

This is evaluation infrastructure, not application behavior or test results. See [the reviewed plan](../BUDGET_ANALYSIS.md) and [machine-readable forecast](../BUDGET_ESTIMATE.json).

- Native Responses `computer` tool, screenshot-only actor, structured `computer_call.actions` and matching `computer_call_output` screenshots. No scripted Playwright task replacement.
- GPT-5.4 / Standard / reasoning none / store false. Complete frozen task retained each turn. Latest native turn and screenshot plus complete text action/observation ledger; older images remain evidence, not repeated model input. Unexpected reasoning items stop for compatibility review.
- Frozen desktop 1440x900 and mobile 390x844, device scale factor 1, CSS screenshots, original image detail. Screenshot hashes deduplicate files; each action retains an evidence reference. Final action capture reused for the native output.
- Fresh isolated cases. Preserved application cookie names. Loopback app8124, mail8125, optional trusted navigation8126, SMTP8127. Native model must operate navigation/mail tabs itself. DOM/database are independent-review-only.
- Only reviewed external publication destinations allowed. Top-level boundary violations stop; blocked third-party resources are recorded separately. No hidden external scripts or OS actions.
- Proposed target/active stop $4; absolute configurable ceiling $5. Each request reserves counted input at $2.50/M and maximum output at $15/M. Cache-adjusted estimates use $0.25/M cached input, but conservative budget does not spend the discount. No bill/invoice guarantee; unknown usage retains reserve and stops. No automatic paid retries.
- Explicit approval file must match suite hash, config hash, model and amount. Check-only never loads a key, creates an approval or contacts OpenAI. This documentation does not authorize execution.
- All formal results remain NOT_RUN. Native self-report is pending independent review, never automatically PASS. Raw typed values are redacted; API keys, cookies, credentials and approval files remain private. Review screenshots before publication.

From repository root, offline commands:

```powershell
node evaluation/harness/native-cua.mjs --config evaluation/run-config.json
node evaluation/harness/adapter-selftest.mjs
node evaluation/harness/optimization-selftest.mjs
node evaluation/harness/browser-adapter-selftest.mjs frontend/node_modules/playwright/index.mjs
node evaluation/harness/offline-preflight.mjs
```

The offline preflight requires the pinned source snapshot prepared by environment.py. It starts only local owned children, strips OpenAI variables, blocks external backend networking and checks actual browser rendering, local database persistence and mail transport. It is not a rehearsal of the 100 task workflows. Original preflight failures and fixes are documented in the budget analysis.

Paid use is deliberately omitted here until a fresh explicit approval. Native API compatibility still requires the first approved actual request; no fallback to a function-tool imitation or another model is permitted.
