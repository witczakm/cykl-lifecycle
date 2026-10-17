---
name: cykl-lekcja
description: "Record a project lesson with evidence; /lekcja; English alias: /lesson."
---
<!-- cykl-lifecycle v3.0.2 -->

# cykl-lekcja

Read `context --root "$PROJECT" --skill cykl-lekcja`. Form one rule, its precedent
and operational test. Assign a stable L-* ID in DECISIONS, with explicit scope and status.
Prepare only the new row as JSON with id, kind="lesson", status, scope, supersedes="-",
and text (rule, precedent and test). Run
`decisions add --root "$PROJECT" --input "$ROW" --expected "$HASH"`.
The locked writer retains the existing index internally and returns only the new index
line and checkpoint card. No whole-index read or replacement is needed. Add a NOW
reference through checkpoint only when applicable, using the returned hash. Never
reuse IDs. Say saved only after acknowledgement. Use archived scope for historical lessons.

Resolve LIFECYCLE to the installed sibling `cykl-start/scripts/lifecycle.py`; PROJECT
is the selected project root. Install all seven skills together. Execute the script;
do not load its source into context. Python 3.9+ is required.

Read only `context` output (16,384 UTF-8 bytes total). Additional named files use
`context --file PATH`, inside that same cap. Index/history retrieval uses bounded
helper commands; no whole-index/history reads or recursive reference expansion.
All lifecycle writes use checkpoint, decisions add or migrate; never direct edits or v2 cleanup.
Use exact expected hashes, and keep returned acknowledgement cards before compaction.
Offline continues only an already-dispatched packet in this shared worktree; no new
assignment, scope change, acceptance or publication. Mirroring is disabled by default.
