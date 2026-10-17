---
name: cykl-migawka
description: "Save an in-session checkpoint; /migawka, /handoff; English alias: /snapshot."
---
<!-- cykl-lifecycle v3.0.1 -->

# cykl-migawka

Read `context --root "$PROJECT" --skill cykl-migawka`. Prepare a JSON draft with
repo, branch, goal, position, next, preserve, work, risks and references. Use stable
O-* obligation IDs and A-* attempt IDs; retain unresolved work. Use the current hash:
`python3 "$LIFECYCLE" checkpoint --root "$PROJECT" --input "$DRAFT" --expected "$HASH"`.
The returned card is the compaction handoff. A failed checkpoint stops dependent work;
never claim a fact saved before the returned checkpoint UUID/hash. No commit.

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
