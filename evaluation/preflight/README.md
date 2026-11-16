# Offline infrastructure evidence only

These are not native CUA task results. No OpenAI inference was made.

- The initial browser adapter launch was blocked by local sandbox permissions; the permitted local rerun passed 7/7 synthetic browser checks.
- Attempt 01 used a nonexistent /register direct route; the preflight was corrected to /profile.
- Attempt 02 exposed missing static assets in the isolated runserver. The configuration now selects the existing pinned medresearch.wsgi.application wrapper; application code was not edited.
- Final offline preflight passed 15 checks; see ../OFFLINE_PREFLIGHT.json. Original failed attempt records are retained here.
- Screenshots are empty synthetic sign-in pages at the frozen 1440x900 / 390x844 dimensions, visually inspected for readability. They prove infrastructure rendering only.
- Unit checks and hashes are separate from the frozen 100-task pass rate.
