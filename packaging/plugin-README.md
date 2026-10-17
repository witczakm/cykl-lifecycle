# cykl-lifecycle 3.0.2

Seven English project lifecycle skills, retaining the canonical cykl-* names.
Install all seven together; Python 3.9+ is required. State is written only through
cykl-start/scripts/lifecycle.py. Use cykl-start to resume and cykl-migawka/cykl-zamknij
to checkpoint before compaction or close. Only a returned UUID/hash means saved.

Breaking upgrade: porzadek.py no longer writes. Existing v2 projects need reviewed
`lifecycle.py migrate` (dry-run default), then explicit --apply. Migration extracts active
facts into NOW/DECISIONS and preserves remaining history as searchable UTF-8 chunks.
Migration keeps ordinary documentation and AGENTS/CLAUDE files unchanged by default.
Only CONFIG (Current Sprint), HANDOFF, ROADMAP and LESSONS_CANON are default sources.
Use `--extra-source PATH` during inventory for per-file opt-in; review its ranges.
Instruction changes also require explicit `replacements`. Inspect change/keep summaries.
Do not run 3.0.0 `migrate --apply` on projects with regular documentation.
Never let old installed v2 writers continue after migration.

Offline work is limited to already-dispatched tasks in one shared worktree. GitHub task
and release authority remains online; this release has no API synchronization client.
Mirroring is disabled by default. Configure lifecycle-integrity as a required check in
each repository and verify a blocked canary before claiming merge protection.

Full instructions, migration guide, hooks and workflow:
https://github.com/witczakm/cykl-lifecycle
