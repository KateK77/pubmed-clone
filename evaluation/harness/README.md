# Native CUA evaluation harness

This is infrastructure for the frozen V3 evaluation, not an application test suite and not evaluation results. No paid call has been made by preparing or self-testing these files.

## Native protocol

The actor uses `gpt-6.1-sol` with the Responses API's native `tools: [{"type":"computer"}]`. It sees screenshots and decides coordinate actions. Ordered `computer_call.actions` are mapped to browser mouse/keyboard controls; matching `computer_call_output` items contain `computer_screenshot` images at `detail: "original"`. No functions masquerade as computer use. There is no model-generated JavaScript, locator, DOM query, or scripted user workflow.

Playwright only provides fresh browser contexts, screenshots, native action translation, download evidence, and a network allowlist. Lifecycle hooks establish isolated synthetic preconditions and may independently verify outcomes. They must never perform the workflow under test. A model final answer is logged as an observation and defaults to `BLOCKED` / `completed_pending_independent_review`, never PASS. An independent reviewer may resolve it using frozen criteria and evidence.

## Before any execution

1. Freeze exactly T001–T100 and record the suite SHA-256. Do not rewrite tests after outcomes.
2. Create a reviewed config from `config.example.json`, set paths and local URL, and implement `lifecycle.mjs` against the isolated test database. Every test requires a `prepare` result with `ready: true`. The default hook blocks execution.
3. Run `node native-cua.mjs --config <config.json>` for a no-network configuration/hash check. This does not establish account model access. No API-key lookup occurs in check-only mode.
4. Obtain the user's explicit cost approval. Only then create a private approval JSON containing `approved: true`, their `user_statement`, `approved_at`, `model`, `max_usd`, `suite_sha256`, and the printed `config_sha256`. Never fill approval automatically.
5. Set `OPENAI_API_KEY` through the process environment. Do not commit it. Run with `--execute` only after approval. Use an OpenAI project-level spend control as a second layer.

The harness creates a run lock using exclusive creation. Reusing the same output directory is rejected; it does not silently resume/retry. A retry must have a new explicitly recorded run and reviewed budget, and must not overwrite first-attempt evidence. All network/API failures are recorded without automatic retry.

## Limits and cost accounting

The following are **proposed, not approved** limits. Each frozen difficulty selects an overlay; effective limits are recorded in the result.

| Difficulty | Model requests | Actions | Cumulative input tokens | Output tokens | Runtime |
|---|---:|---:|---:|---:|---:|
| Easy | 20 | 60 | 150,000 | 20,000 | 600 s |
| Medium | 30 | 100 | 300,000 | 30,000 | 900 s |
| Hard | 45 | 160 | 600,000 | 45,000 | 1,200 s |
| Expert | 60 | 220 | 900,000 | 60,000 | 1,800 s |

Global ceilings: 3,000 model requests, 10,000 actions, 30M input tokens, 3M output tokens, eight hours, and $100. The dollar budget can stop the run well before the other ceilings. These are caps, not a claim that $100 guarantees all 100 tests complete. Increasing the proposed cap does not grant paid approval; an approval artifact matching the new config hash and sufficient approved amount is still required.

The planning scenario of 1,450 inference requests, 16.14M total input tokens and 0.725M output tokens estimates $39.53 at the quoted standard token rates, versus $95.20 in conservative reserve accounting. This is an unbenchmarked planning scenario, not actual usage. The proposed actual-price range is $20–60; neither estimate guarantees completion. A user may instead approve a reviewed $50 config for a potentially partial evaluation. No approval is implied by either config example.

Before each inference request, `/responses/input_tokens` counts the exact input, including previous response state and screenshots. Counts are logged separately from inference requests. Its body is selected from the count endpoint's documented fields; `reasoning`, `tools`, `instructions`, `input`, `model`, and `previous_response_id` are accepted. Inference-only `store`, `service_tier`, and `max_output_tokens` are not sent to token counting. The harness reserves input cost plus the maximum permitted output before sending inference. It uses conservative accounting rates of $5/M input and $20/M output; these are safety reserve rates, **not official quoted prices**. The fetched model page lists standard short-context pricing of $2/M input and $10/M output. No caching discount is assumed. Unknown/failed inference retains its full reserve and stops the entire run. If returned usage exceeds token reservations, execution stops for billing review. Report usage-derived estimates as estimates, not invoices. Confirm current pricing/account tier before paid use.

The $100 hard cap is enforced in approval validation. API HTTP failures, missing usage, native safety approvals, unsupported actions and budget/deadline limits are classified as infrastructure errors or blocked prerequisites, not automatically application failures. The harness stops when native safety approval is requested; it never auto-acknowledges it.

Observed token usage also produces a separate `standard_rate_token_estimate_usd` using $2/M input and $10/M output. It is not the `charged_upper_usd` budget counter and not an invoice; cache read/write adjustments are not applied. `actual_invoice_cost_usd` remains null. Requests above 272,000 input tokens are blocked before inference because long-context pricing has not been separately approved. This single-request limit is distinct from cumulative per-test token allowances.

## Evidence and privacy

Each native action and each response gets a timestamp; screenshots are saved after actions, and downloads are kept for independent review. Every typed text action is redacted from logs. Lifecycle-provided secret strings are removed from model final text/error logs. Password fields should remain masked. Screenshots can still contain synthetic identifiers or content; review all evidence before committing. Raw request payloads, API credentials, cookies, storage states, and model response bodies are never saved.

The loop uses `previous_response_id` with `store: true` for coherent native conversation state; screenshots and synthetic test instructions are sent to OpenAI. This does not claim zero retention. Do not use real user accounts, patient information, or production data. Evidence output should remain private until reviewed. Allowed browser requests are the exact local application origin, exact loopback origins listed in `allowed_local_origins` (for example `http://127.0.0.1:8125` for the synthetic mailbox), and configured HTTPS NCBI/DOI hosts. The extra local origins must not contain paths, query strings, credentials or non-loopback hosts. Publisher redirects beyond that allowlist stop as blocked; add only explicitly reviewed destinations before a run, never silently during one.

The driver does not expose browser developer tools, OS shortcuts, arbitrary URL navigation, external JavaScript execution or file upload. The initial URL is fixture infrastructure. A reviewed lifecycle `prepare` may return `extra_pages` on approved local origins; these are opened as preconditions while the application remains the initially selected tab. The model must itself request tab switching and visually read any verification code. Set `mailbox_navigation_supported: true` only with this driver implementation. A `viewport` precondition can establish a mobile window without performing the test workflow.

Blocked top-level navigation stops as BLOCKED. Blocked third-party subresources are aborted and logged by origin/resource type without automatically stopping the test; missing essential rendering remains an infrastructure limitation for independent review. The resource-only allowlist permits NCBI static asset hosts but does not grant top-level navigation to them. The frozen PUBLISHER fixture's published destination is `www.acpjournals.org`; FREE also exposes `europepmc.org` and `academic.oup.com`. These are required destination-review candidates, not implicitly permitted by this example config. Actual redirects may require further explicit review before a paid run. Do not mistake an allowlist block for an application defect.

Native `keypress` actions for Alt+Left/Right map to `goBack`/`goForward`, Ctrl+R/F5 map to `reload`, and Ctrl+Tab/Ctrl+Shift+Tab map to selecting actual existing browser tabs. These execute only when explicitly requested by the native model. Screenshots then use the selected tab. They are browser infrastructure translations, not scripted task steps. Ctrl+L remains blocked: browser chrome is not shown in page screenshots, and arbitrary address-bar typing is not emulated. Tasks requiring unsupported browser chrome must be recorded as driver limitations rather than application failures.

The reviewed local navigation/clipboard fixture may run at `http://127.0.0.1:8126`. The native actor must switch to its tab, type a destination and click its normal form; the harness never automatically fills or submits it. When `prepare.navigation_state_file` is provided, the harness writes only the last observed application URL and timestamp under the lifecycle module's `.runtime` directory. Credential-like query parameters and fragments are stripped/redacted. It does not expose DOM, cookies or hidden application state. Clipboard permissions are restricted to the approved local origins; the actor uses ordinary native copy/paste, and any acceptance decision still needs independent clipboard verification.

## Local adapter checks

`node adapter-selftest.mjs` exercises native-shape action translation, allowlists, redaction and budget guards with an in-memory fake page. It performs zero API calls and zero website evaluation tests. Passing these checks cannot be included in the 100-test pass rate. Actual model/project access and end-to-end API compatibility remain unverified until an approved native request succeeds.

`node browser-adapter-selftest.mjs <path-to-playwright/index.mjs>` checks back/forward/reload and tab switching against two temporary synthetic local HTML pages in a real browser. It also checks that the captured screenshot follows the selected tab. It does not contact MedResearch or OpenAI, and is not one of the 100 formal tests. Its fixture HTTP server and browser close after the check.

## Official documentation consulted

- [Computer use](https://developers.openai.com/api/docs/guides/tools-computer-use)
- [Native action integration recipes](https://developers.openai.com/api/docs/guides/tools-computer-use-integration)
- [GPT-6.1 Sol model and pricing](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
- [Counting tokens](https://developers.openai.com/api/docs/guides/token-counting)
- [Input token count API](https://developers.openai.com/api/reference/resources/responses/subresources/input_tokens/methods/count)

Consulted November 15, 2026 America/Chicago. API schema may evolve; stop on incompatibility rather than falling back to scripted Playwright or a function-tool imitation.
