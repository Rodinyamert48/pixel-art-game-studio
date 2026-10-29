# Workflow C: Automated QA and bug fixing

Example request: "Inspect this game, run all available tests, and fix reproducible bugs."

## Procedure

1. **Discover tooling.** Engine CLI, test frameworks, documented commands in `PROJECT_CONVENTIONS.md`,
   CI files, `package.json` scripts, `*.csproj` test projects. Note what is missing.
2. **Baseline.** Run the full suite and the smoke check once. Save the output summary.
3. **Static data check.** `python "${CLAUDE_SKILL_DIR}/scripts/validate_game_project.py" <project>`.
4. **QA Tester** (delegate for anything larger than a handful of tests): converts acceptance criteria
   into tests, runs them, and returns defect reports in the format from
   [../references/quality-standards.md](../references/quality-standards.md).
5. **Triage** (Director): sort by severity and confidence. Only confirmed, reproducible defects go to the
   Bug Fixer. Suspected defects get a reproduction attempt first.
6. **Bug Fixer**: one defect per brief (or a group sharing a root cause). Files touched by different
   fixes must not overlap when fixes run in parallel; otherwise run them sequentially.
7. **Focused verification** after each fix: the regression test for that defect plus tests of the
   touched subsystem.
8. **Full regression** once all fixes in the batch are accepted, plus the startup/build check.
9. **Record** remaining issues in `KNOWN_ISSUES.md` with evidence and what is needed to resolve them.
10. **Report** only evidence-backed results.

## Retry bounds

- Max three fix attempts per defect. After that, mark it blocked with the evidence collected.
- Max two full QA → fix → regression cycles per request unless the user asks for more.
- If the same test flips between pass and fail without code changes, report it as flaky; do not
  "fix" it by adding sleeps or retries without understanding the cause.

## Forbidden shortcuts

Deleting or skipping tests, weakening assertions, catching and ignoring exceptions, disabling the
feature under test, editing expected outputs to match wrong behavior, or claiming a fix without a run.
