---
name: cykl-kickoff
description: "Initialize lifecycle memory for a new project; /kickoff. Existing v2 projects require reviewed migration, not overwrite."
---
<!-- cykl-lifecycle v3.0.2 -->

# cykl-kickoff

Check for existing lifecycle files without loading their bodies. Existing legacy state
routes to `migrate --root "$PROJECT"` (external plan file plus bounded summary); never overwrite it as a new project.
For a new project, establish goal, repo, branch and next action. Prepare a JSON draft
with repo, branch, goal, position, next, preserve=[], work={}, risks=[], references=[].
Use the generic NOW and DECISIONS templates only through the bounded helper:
`context --file` for existing projects; templates are packaged and capped at 4,096 bytes.
Run `python3 "$LIFECYCLE" checkpoint --root "$PROJECT" --input "$DRAFT" --expected absent`.
Then run context. Install the hook/Action and configure the required lifecycle-integrity
check per repository. Until a blocked canary proves it, report merge protection unverified.
This release does not create GitHub issues, milestones or releases.

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
