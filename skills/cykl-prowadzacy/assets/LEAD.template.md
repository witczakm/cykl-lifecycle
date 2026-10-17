# LEAD (Owner-edited configuration; no release needed to change it)

Model names are examples only. Replace them with what your harness offers.

## Routing

| Tier | Example models | Use for |
|---|---|---|
| mechanical | small/cheap model | test runs, counts, copies, release scripts |
| moderate code | mid model | ordinary implementation, refactors |
| hard code / judgement | strongest model | design, difficult bugs, review of risky changes |
| independent review | a different model family | review before merge |
| local models | only if the Owner allows (e.g. daytime) | bulk, low-risk work |

## Budget thresholds (plan usage in the current window)

- below 75 %: continue; start new work only if the forecast stays under 80 %
- 85 % or more: pause lowest-priority work
- 95 % or more: only the item closest to done
- never use paid overage

## Conventions

- Build language: English
- Decision language: English
- Holding directory for deletions: docs/lead/hold/
- Long-report directory: docs/lead/reports/
