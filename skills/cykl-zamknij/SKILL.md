---
name: cykl-zamknij
description: "Close a project session durably; /zamknij; English alias: /close."
---
<!-- cykl-lifecycle v3.0.2 -->

# cykl-zamknij

Read `context --root "$PROJECT" --skill cykl-zamknij`. Collect verified outcomes,
remaining obligations, approvals, constraints, failed approaches and one next action.
Prepare the same JSON draft as cykl-migawka, retaining unresolved IDs. Run:
`python3 "$LIFECYCLE" checkpoint --root "$PROJECT" --input "$DRAFT" --expected "$HASH"`.
Only a successful UUID/hash and compaction card authorize saying the session is saved.
Then run `check --root "$PROJECT"`. Include the card in compaction/close output.
Failure stops close. Report checks honestly; commit/publish only if separately authorized.

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
