---
name: cykl-lekcja-globalna
description: "Propose a cross-project lesson; /lekcja-g; English alias: /lesson-global. Global installation needs explicit approval."
---
<!-- cykl-lifecycle v3.0.3 -->

# cykl-lekcja-globalna

Read `context --root "$PROJECT" --skill cykl-lekcja-globalna`. Record an L-* proposed
lesson using `decisions add --root "$PROJECT" --input "$ROW" --expected "$HASH"`.
Supply one JSON row: id, kind="lesson", status="proposed", scope, supersedes="-",
and text containing rule, precedent and test. Keep the returned index line and card;
the writer preserves the old index without a whole-index read by the agent.
Keep an O-* obligation for any pending global approval/installation. Ask for explicit
approval before changing another project's or global instructions. This release does
not install global rules: provide the approved text for the target's authorized writer.
Do not mark applied without verified evidence; preserve the pending ID until then.

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
