# Workflow: Release-readiness check

Run before saying a milestone or game is complete. Every line needs evidence (a command and its
result) or an explicit "not verified" with the reason.

| # | Gate | Evidence required |
| --- | --- | --- |
| 1 | Game starts and quits cleanly | Smoke/headless run output, or "no engine available" |
| 2 | Build/export succeeds (if in scope) | Build command output and artifact path |
| 3 | Automated tests pass | Test command, pass/fail counts |
| 4 | Data contract valid | `validate_game_project.py` with 0 errors |
| 5 | Essential acceptance criteria met | Each criterion in `ACCEPTANCE_CRITERIA.md` mapped to a test or a manual step |
| 6 | Save/load round trip | Test that saves, reloads, and compares state; corrupted-save handling |
| 7 | No open Critical or High defects | `KNOWN_ISSUES.md` reviewed |
| 8 | Assets validated | Meta checks pass; preview reviewed or flagged for human review |
| 9 | User-requested deliverables present | Checklist against the original request |
| 10 | Limitations disclosed | Manual playtest needs, unverified platforms, missing tools |

Verdict:

- **Ready**: gates 1, 3, 4, 5, 6, 7, 9 pass; others pass or are explicitly out of scope.
- **Ready with known issues**: only Medium/Low/Enhancement issues remain, all documented.
- **Not ready**: any Critical/High open, the game does not start, or an essential criterion fails.

Never round "Not ready" up. Report the verdict with the table.
