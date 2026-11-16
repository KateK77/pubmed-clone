# Final Evaluation — 100 AI-Generated Tests + Native CUA

You are conducting the final evaluation of this software after three rounds of AI-assisted development.

The goal is to measure how accurately the final website implements the requirements in the **latest and final Description (Round 3 / V3)**.

This is a final evaluation, not another development round.

## Step 1 — Identify the Final Description

1. Locate the final Description used in Round 3.
2. Verify that it is the latest approved version.
3. Treat this Description as the authoritative requirements specification.
4. Extract all required features, user roles, workflows, validations, and expected behaviors.
5. Do not use earlier descriptions or the current implementation to determine test expectations.
6. If the final Description cannot be located or identified confidently, stop and ask me to provide it.

Do not modify the Description or application during evaluation.

## Step 2 — Generate 100 AI Test Cases

Design exactly **100 unique, specification-based end-to-end tests** derived from the final Description.

Use the following difficulty distribution:

| Difficulty | Tests | Description |
|---|---:|---|
| Easy | 30 | Basic functions, navigation, simple interactions |
| Medium | 40 | Multi-step workflows, forms, search, validation |
| Hard | 20 | Complex workflows, permissions, edge cases |
| Expert | 10 | Long end-to-end scenarios, cross-module interactions, error recovery |

Distribute the tests across all major functional areas described in V3.

Include positive tests, negative tests, boundary conditions, and realistic user scenarios where supported by the requirements.

Each test must include:

- Test ID (T001–T100)
- Difficulty level
- Functional category
- Related requirement ID(s)
- Natural-language test task
- Preconditions and required test data
- Step-by-step expected user workflow
- Expected result
- Objective pass/fail criteria

**Important rules:**

- Generate tests from the final Description, NOT from the features currently implemented.
- Missing required features must remain testable and count as failures.
- Do not invent requirements not supported by V3.
- Do not make tests artificially easy.
- Do not modify tests after seeing the execution results.
- Freeze and save all 100 tests before starting execution.

Save the complete test suite to:

`evaluation/final_test_cases_100.json`

Also generate a readable Markdown version:

`evaluation/FINAL_TEST_CASES.md`

## Step 3 — Prepare Native CUA Execution

Inspect the existing project and determine how to run the website locally.

Set up a safe, isolated test environment using synthetic data.

Use **native OpenAI Computer-Using Agent (CUA)** to perform the actual browser interactions.

The CUA agent must:

1. Observe the website using screenshots.
2. Decide where to click and what to type.
3. Interact through native computer-use actions.
4. Navigate the actual website.
5. Attempt to complete each test task.
6. Verify the final application state.

Do NOT replace native CUA with scripted Playwright tests.

Playwright may be used for browser infrastructure, screenshots, test isolation, or independent verification, but not as a substitute for native CUA task execution.

If the project already has a native CUA harness, reuse it.

If no native CUA harness exists, implement a compatible evaluation harness without changing application functionality.

Use an available model that actually supports native computer-use actions.

## Step 4 — Execute All 100 Tests

Run the frozen 100-test suite against the final application version.

For each test:

1. Reset the test environment to the required initial state.
2. Give the CUA agent the natural-language test instruction.
3. Allow the agent to interact with the website.
4. Record screenshots and action logs.
5. Independently verify the final outcome against the frozen acceptance criteria.
6. Record the result as PASS, FAIL, BLOCKED, ERROR, or NOT_RUN.
7. Record execution time, action count, model requests, and token usage where available.
8. Document the reason for every failure.

Use clear classifications:

- PASS: The required behavior was successfully demonstrated.
- FAIL: The application failed the specified requirement.
- BLOCKED: A prerequisite prevented a valid assessment.
- ERROR: The testing infrastructure or CUA execution failed.
- NOT_RUN: The test was not executed.

Do not automatically count CUA navigation mistakes as application failures.

Do not silently retry failed tests.

Do not modify the website to make tests pass.

Do not change expected results after execution.

## Step 5 — Calculate Final Pass Rates

Calculate the following:

**Primary Overall Pass Rate**

PASS / 100 × 100%

Also report:

- Number of passed tests
- Number of failed tests
- Number of blocked tests
- Number of execution errors
- Number of tests not run
- Validly evaluated pass rate: PASS / (PASS + FAIL) × 100%
- Pass rate for Easy tests
- Pass rate for Medium tests
- Pass rate for Hard tests
- Pass rate for Expert tests
- Pass rate by functional category

Clearly disclose incomplete evaluations.

If fewer than 100 tests are successfully evaluated, do not present the result as a complete 100-test evaluation.

## Step 6 — Generate Final Evaluation Reports

Create the following files:

- `evaluation/final_test_cases_100.json`
- `evaluation/FINAL_TEST_CASES.md`
- `evaluation/final_results_100.json`
- `evaluation/FINAL_EVALUATION_REPORT.md`
- `evaluation/summary.csv`
- `evaluation/screenshots/`
- `evaluation/logs/`

The Markdown test document must list all 100 tests, grouped by difficulty and functional category.

The final evaluation report must include:

### A. Overall Results

Total: 100 tests

PASS: X

FAIL: X

BLOCKED: X

ERROR: X

NOT_RUN: X

Overall Pass Rate: X%

### B. Difficulty-Based Results

| Difficulty | Total | Passed | Failed | Pass Rate |
|---|---:|---:|---:|---:|
| Easy | 30 | | | |
| Medium | 40 | | | |
| Hard | 20 | | | |
| Expert | 10 | | | |
| Total | 100 | | | |

### C. Detailed Test Results

For all 100 tests, provide:

- Test ID
- Test description
- Difficulty
- Expected outcome
- Actual outcome
- PASS/FAIL/BLOCKED/ERROR/NOT_RUN
- Failure reason, if applicable
- Evidence references

### D. Failure Analysis

Identify:

- Missing required features
- Incorrect functionality
- UI/UX problems
- Permission and validation failures
- CUA agent execution failures
- Infrastructure failures

### E. Evaluation Metadata

Record:

- Final Description version
- Git commit hash of the evaluated application
- CUA model used
- Number of model requests
- Total CUA actions
- Total execution time
- API token usage
- Actual or estimated API cost

Do not invent results or usage figures.

## Step 7 — GitHub

Save the complete evaluation artifacts in the existing project repository.

Create a dedicated evaluation branch.

Commit the test cases, reports, and non-sensitive evidence.

Do not modify the application code during evaluation.

Do not merge into main without approval.

Do not commit API keys, credentials, or sensitive data.

## API Cost and Approval

Before starting paid native CUA execution:

1. Verify that a compatible model and API configuration are available.
2. Estimate the total cost of 100 CUA tests.
3. Set per-test limits for model requests, actions, tokens, and runtime.
4. Define a total execution budget.
5. Present the plan and estimated cost to me.

**Stop and wait for my explicit approval before making paid API calls.**

After approval, execute the evaluation and generate all final reports.

## Final Deliverables

I need two main outputs:

**1. The complete set of 100 AI-generated test cases**, based strictly on the final Round 3 Description.

**2. The actual CUA evaluation results**, including the final overall pass rate, pass rates by difficulty, detailed results for all 100 tests, and failure analysis.

Do not report simulated or predicted pass rates.

Only report results obtained from actual native CUA execution.