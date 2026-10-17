---
name: cykl-start
description: "Resume a project session; /start. Read a validated bounded projection and report the next action."
---
<!-- cykl-lifecycle v3.0.3 -->

# cykl-start

Run `python3 "$LIFECYCLE" context --root "$PROJECT" --skill cykl-start`.
A failure stops startup; do not fall back to raw files or chat memory. Report current
position, next action, unresolved IDs and stale/offline status. Resume attempts by ID.
For legacy projects, run `migrate --root "$PROJECT"`; review the external plan file
reported in its bounded path/hash/count summary before any apply.
A stale writer lock requires inspection, then `recover --root "$PROJECT"` only when
the writer is no longer running. Never steal a live lock or discard recovery evidence.
For named historical evidence use `archive show --root "$PROJECT" --source PATH --lines A-B`;
keep the requested range within the helper output cap.

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
