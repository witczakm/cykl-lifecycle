# cykl-lifecycle 3.0.2

Seven English skills for project memory across sessions. Canonical names stay `cykl-*`.
One stdlib Python script writes bounded checkpoints; GitHub remains task/release authority.

| Skill | Purpose | Descriptive English alias |
|---|---|---|
| cykl-kickoff | Initialize a new project | /kickoff |
| cykl-start | Validate and resume | /start |
| cykl-migawka | Save during work | /snapshot |
| cykl-zamknij | Save before close/compaction | /close |
| cykl-roadmap | Show observed task/release position | /roadmap |
| cykl-lekcja | Record a project lesson | /lesson |
| cykl-lekcja-globalna | Propose a global lesson | /lesson-global |

Aliases appear in descriptions; they do not create duplicate skills. Install all seven
skills together: the other six use `cykl-start/scripts/lifecycle.py`.

## Install and use

Requires Python 3.9+. No Python packages, tokenizer downloads or network access are needed.
The existing `install.sh` downloads from GitHub; for offline installation unpack the skills ZIP
into your tool's skills directory. The `.plugin` artifact is for Claude Cowork; `.codex-plugin`
contains Codex metadata. A terminal-capable harness is required; no Python means stop.
Older installation/architecture guides describe v2 and are historical; use this README
and [R2 spec](docs/design/v3.0.md) for v3 behavior.

```sh
LIFECYCLE=/path/to/skills/cykl-start/scripts/lifecycle.py
python3 "$LIFECYCLE" check --root /path/to/project
python3 "$LIFECYCLE" context --root /path/to/project --skill cykl-start
python3 "$LIFECYCLE" decisions --root /path/to/project
```

For a new project, create a draft using the JSON in
[NOW.template.md](skills/cykl-kickoff/assets/NOW.template.md), then:

```sh
python3 "$LIFECYCLE" checkpoint --root /path/to/project --input /tmp/draft.json --expected absent
```

Subsequent writes pass the current `content_sha256` instead of `absent`. Drafts may include
`decisions` (complete index text) and `files` (managed path → text). Only the script writes
lifecycle files. Preserve unresolved IDs. Close/supersede needs an ID and a reason and,
for supersession, a surviving successor. The returned UUID/hash card is the
acknowledgement that facts are saved; include it before compaction. Read failures stop work.

To append a decision or lesson, submit only its new row as JSON; the locked writer retains
the existing index internally and returns the new index line plus a checkpoint card:

```json
{"id":"L-example","kind":"lesson","status":"accepted","scope":"project","supersedes":"-","text":"Rule; precedent; operational test"}
```

```sh
python3 "$LIFECYCLE" decisions add --root /path/to/project --input /path/to/row.json --expected HASH
```

Duplicate or previously closed IDs are refused. Add a NOW reference with a subsequent
checkpoint when needed. Agents never need a whole-index read or replacement for an append.

NOW is capped at 4,096 UTF-8 bytes. All helper responses share a 16,384-byte cap; extra
files use `context --file PATH`. Decisions are projected, never loaded whole by skills.
There is no token-count guarantee. Unwritten thoughts and arbitrary harness reads are
outside this enforcement boundary.

## Migration from v2 (breaking)

**Do not run 3.0.0 `migrate --apply` on a project with regular documentation.**
Upgrade to 3.0.2 and generate a new plan. The 3.0.0 inventory included ordinary docs.

Migration is **keep-by-default**. The closed default source list is `PROJECT_CONFIG.md`,
`docs/HANDOFF.md`, `docs/ROADMAP.md`, and `docs/LESSONS_CANON.md`, when present.
[Exact v2 provenance](docs/migration-scope-v301.md) explains each entry and why ADRs,
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

## Required merge protection

[Hook sample](hooks/pre-commit.sample) checks the complete staged tree, not the worktree.
It can be bypassed and does not replace [lifecycle-integrity](.github/workflows/lifecycle-integrity.yml).
The Action uses a trusted validator and checks the test merge against **both parents and
merge-base**, including decisions, obligations, explicit closures and immutable archives.
The Action uses `--merge-result`: it validates the union of both parents and merge-base
without requiring NOW to name GitHub's synthetic commit parents. Every O/A/D/L ID in
either parent or merge-base must remain in work/DECISIONS or have an explicit closing
line in merged NOW (ID, close/supersede action and reason). Record text, metadata,
ordering, timestamps, settled rows and historical source hashes are not compared.
One-sided changes and changes on both sides pass when the ID union is retained or closed,
as does a later PR after a settled update. Silently dropping another side's obligation fails.
Without `--merge-result`, explicit parent/base UUID checks remain available for a
separately authored reconciliation checkpoint against its source snapshots.

For each adopting repository: install the validator at the same path, bootstrap a reviewed
trusted revision (optionally `LIFECYCLE_VALIDATOR_REF` repository variable), require the
`lifecycle-integrity` check, prohibit ordinary bypass/direct pushes, require up-to-date PRs
or merge queue. `--trusted-root` compares the candidate workflow's SHA-256 with the
trusted checkout and rejects replacement or deletion in project and package checks.
Bootstrap workflow and validator together; a workflow upgrade requires an authorized
update of the trusted version, not a PR-provided expected hash.

**External enforcement is required:** configure a required workflow whose definition
and revision are controlled outside the PR. If that policy is unavailable, require
CODEOWNERS approval for `.github/workflows/**`, `.github/CODEOWNERS`, and the trusted
validator path, dismiss stale approvals after new commits, and disallow ordinary bypass.
Protect changes to `LIFECYCLE_VALIDATOR_REF` as well. A same-name no-op job can remove
its own hash check; the hash comparison alone cannot prevent that attack.
Test canaries that replace/delete the workflow and restore HANDOFF over 512 bytes;
verify a non-admin cannot merge them. Record ruleset ID and canary evidence in
PROJECT_CONFIG. Until then report **merge protection unverified**. This offline release
has not configured any remote repository or tested GitHub event execution.

Local tree checks need no git inside Python:

```sh
python3 "$LIFECYCLE" check --merge-result --root result --parent left --parent right --base merge-base
```

To prepare parent/base identity and closure entries for missing IDs, replace
`--merge-result` with `--reconcile-template`. Merge its JSON into a checkpoint draft;
restore each missing ID or replace its REVIEW REQUIRED reason with the reason for closure.
No source hashes are needed. Existing hash lists are accepted without comparison.
Terminal attempts may leave NOW only after integrated/abandoned status and explicit closure.

The caller must export the real tested trees; arbitrary directories are not proof of ancestry.

## Offline and privacy

Only already-dispatched work continues offline, in one shared worktree. Attempt files
supply current status; NOW holds their IDs. New assignments, scope changes, acceptance and
publication wait for online reconciliation. GitHub API synchronization/import is manual
in this minimal release. Prepared issue bodies, including the pin, cap at 8,192 bytes.
Mirroring is disabled; any future opt-in mirror must select reviewed public-safe identity,
goal, position, next action and IDs. Preserve/Risks/decision bodies stay out of the mirror.

## Verify and build

```sh
python3 -B -m unittest discover -s tests -v
python3 -B skills/cykl-start/scripts/lifecycle.py check --package
bash build-plugin.sh
```

Build produces the plugin, combined skills ZIP and seven individual skill ZIPs.
See [CHANGELOG](CHANGELOG.md) for breaking changes and [R2](docs/design/v3.0.md) for caps/contracts.
