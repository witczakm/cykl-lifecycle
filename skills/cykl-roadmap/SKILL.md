---
name: cykl-roadmap
description: "Show observed GitHub release/task position; /roadmap. Update only on explicit request."
---
<!-- cykl-lifecycle v3.1.0 -->

# cykl-roadmap

Run `context --root "$PROJECT" --skill cykl-roadmap`. Show the current milestone,
issue IDs, next action and observation freshness. With TASKS=local, the ROADMAP task
lines are the authority (`- T-1 open Title`; bodies in docs/issues). With TASKS=github, GitHub issues/milestones own scope
and status. The local ROADMAP is a bounded observation, never a second queue.
An explicit update needs verified online authority; offline, record an O-* pending
change through checkpoint. In this minimal release GitHub operations are manual.
Persist a reviewed projection using checkpoint's files map, with the expected NOW hash.

Resolve LIFECYCLE to the installed sibling `cykl-start/scripts/lifecycle.py`; PROJECT
is the selected project root. Install all seven skills together. Execute the script;
do not load its source into context. Python 3.9+ is required.

Read only `context` output (16,384 UTF-8 bytes total). Additional named files use
`context --file PATH`, inside that same cap. Index/history retrieval uses bounded
helper commands; no whole-index/history reads or recursive reference expansion.
All lifecycle writes use checkpoint, decisions add or migrate; never direct edits or v2 cleanup.
Use exact expected hashes, and keep returned acknowledgement cards before compaction.
With TASKS=github (default) offline continues only an already-dispatched packet in this
shared worktree: no new assignment, scope change, acceptance or publication. With TASKS=local,
docs/ROADMAP.md and docs/issues are the task authority and change only through checkpoint.
Mirroring is disabled by default.
