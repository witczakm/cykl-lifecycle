# Migration from v2 (breaking)

**Do not run 3.0.0 `migrate --apply` on a project with regular documentation.**
Upgrade to 3.0.1 or later and generate a new plan. The 3.0.0 inventory included ordinary docs.

Migration is **keep-by-default**. The closed default source list is `PROJECT_CONFIG.md`,
`docs/HANDOFF.md`, `docs/ROADMAP.md`, and `docs/LESSONS_CANON.md`, when present.
[Exact v2 provenance](migration-scope-v301.md) explains each entry and why ADRs,
registers, journals, reports, specs, runbooks and existing archives are excluded.
All other documentation and root `AGENTS.md` / `CLAUDE.md` stay byte-identical: no stub,
no archive copy, no required source entry. The plan's `keep` list is informational;
new or changed ordinary docs do not invalidate the source inventory.

In CONFIG, only `## Current Sprint ...` through the next level-1/2 heading is replaced;
static sections and `REPO_NOTES=` lines are preserved. The v3 schema fields are appended.
The complete original CONFIG is reconstructable. An unrecognized section stays intact.
If preservation exceeds the existing 2,048-byte CONFIG cap, migration refuses to apply;
review `replacements["PROJECT_CONFIG.md"]` explicitly, including `CYKL_SCHEMA=3`.

Upgrade **every** installed writer first. `porzadek.py` now always exits 2 without writes.
There is no automatic cleanup on startup and no automatic “newest Snapshot” guess.
Work on a reviewed copy; never migrate private project data into this public skills repo.

```sh
python3 "$LIFECYCLE" migrate --root /path/to/project --output /path/outside/project/migration-plan.json
# Review and edit the plan outside the project, then validate without applying:
python3 "$LIFECYCLE" migrate --root /path/to/project --plan /path/outside/project/migration-plan.json
python3 "$LIFECYCLE" migrate --root /path/to/project --plan /path/outside/project/migration-plan.json --apply
```

Inventory writes the full plan to that new file, never into the project, and prints only
its path, SHA-256, source count and change/keep counts with bounded path previews.
Each preview includes a `truncated` flag; full kept paths and source entries are in the plan. Without `--output`, it creates a unique plan in the
system temporary directory. Existing outputs and symlink paths are refused. Plan files
are not subject to the helper stdout cap. A reviewed `--plan` without `--apply` is read-only.

To migrate an additional file, opt in by exact project-relative path during inventory:

```sh
python3 "$LIFECYCLE" migrate --root /path/to/project --output /path/outside/project/plan.json --extra-source docs/journal.txt
```

Repeat `--extra-source` for each file. It populates `extra_sources` and creates the
required `sources[PATH]` hash/range entry for review. When editing a plan manually,
both entries are required; listing an ordinary file in `sources` alone is rejected.
An explicit `replacements[PATH]` also opts in that reviewed source. To withdraw an opt-in,
remove its `extra_sources`, `sources` and replacement entries; it returns to keep.
Instruction files require a nonempty bounded replacement even with `extra_sources`.
Generated v3 files that collide with unselected documents block apply until explicitly
selected and reviewed; `draft.files` cannot bypass this protection.

The initial plan has unresolved source ranges and checklist entries. For each source,
partition every line exactly once. Each range needs `start`, `end`, `disposition` and
`reason`. Active ranges also need an ID; decisions/lessons may specify scope:

```json
{"start":1,"end":2,"disposition":"active","id":"O-constraint","reason":"Still required"}
```

O-* obligations and A-* attempts go into NOW; D-* decisions and L-* lessons go into
DECISIONS. A-* also require matching attempt/packet files in draft.files. Historical
ranges use `disposition: "archived"`. D/L scope defaults to `archived`; promote a binding
rule explicitly to `project`. Set repo/branch/goal in draft. Fill all review checklist
entries with evidence: active facts, ambiguous snapshots, issue URLs, readers, writers,
privacy. Only selected AGENTS/CLAUDE files require explicit bounded `replacements` preserving
applicable instructions; otherwise they remain untouched. Known secret hits need `acknowledgements: {"line": "ACK-review-id"}`;
review hashes and privacy manually too. The scanner cannot prove publication safety.

Apply verifies all hashes and extraction before replacing sources. Only remaining history
becomes plain UTF-8 chunks; the manifest records paths, lines, hashes, extracted facts and
review evidence. Original bytes, including CRLF and missing final newline, reconstruct
exactly. Source drift, gaps, duplicates, ambiguity and cap overflow block apply.
A fact incorrectly classified as historical remains a human review failure.

```sh
python3 "$LIFECYCLE" archive show --root /path/to/project --source docs/HANDOFF.md --lines 1-20
```

Archives stay grep-able. Use bounded line ranges for agent retrieval. For rollback,
run the executable reconstruction command:

```sh
python3 "$LIFECYCLE" migrate --root /path/to/project --rollback --dest /path/to/new-recovery-directory
```

It verifies and reconstructs every original migration source, including files larger
than the stdout cap. It restores migration sources, not an entire historical checkout.
The destination must be new, outside the live tree, with an existing parent and no
symlink components. Existing, nested and ancestor destinations are refused. Live v3
files and merge protection remain in place. A process killed during export may leave
a partial recovery directory; use a new destination for retry.
Repeated apply with the same plan is a no-op. If promotion is interrupted, all readers
stop at the lock; `recover --root PATH` verifies candidate and destination hashes before
finishing. Never steal a live lock. Before promotion there may be no descriptor: inspect
and remove only the stale local stage/lock after proving that no live writer remains.
