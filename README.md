# cykl-lifecycle 3.1.0

Project memory for AI coding agents across sessions. A session starts with `/start`,
ends with `/close`, and the next session knows where the last one stopped, what is
open and what the one next action is. Works with Claude Code, Claude Cowork and
OpenAI Codex (Agent Skills format). One stdlib Python script is the only writer of
lifecycle state; every read is size-capped so startup stays small.

## Choose your edition

All editions are the same package. The edition is chosen per project at `/kickoff`
(one config line) and, for multi-agent work, by installing one extra skill.

| | Local | GitHub | GitHub + multi-agent |
|---|---|---|---|
| For | one person, one agent, no GitHub | projects tracked in GitHub issues | one lead agent coordinating several executor agents/models |
| Needs | Python 3.9+ | Python 3.9+, a GitHub repository | as GitHub, plus access to the executor models you route to |
| Tasks live in | `docs/ROADMAP.md` + `docs/issues/` | GitHub issues and milestones | GitHub issues and milestones |
| Session state | `docs/NOW.md`, `docs/DECISIONS.md` | same | same + `docs/lead/` (thread registry, journal, routing) |
| Commands | 7 core | 7 core | 7 core + `/lead` |
| Works offline | everything | everything except new assignments and acceptance | as GitHub |
| Merge protection | local pre-commit hook | hook + required CI check | hook + required CI check |

- **Local** if the project has no GitHub repository or must stay on one machine.
- **GitHub** if issues and releases already live in GitHub; this is the 3.0.x behaviour.
- **Multi-agent** if one thread should plan and decide while other models implement,
  test and review.

You can move a project from Local to GitHub later by changing one config line and
creating the issues; nothing else changes. The multi-agent lead also works on top of
the Local edition.

## Install

Skills are installed together; the other skills call `cykl-start/scripts/lifecycle.py`.
Re-running the installer replaces all `cykl-*` skills, so versions never mix.

```sh
# Local and GitHub editions (7 core skills)
curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash -s -- claude

# GitHub + multi-agent edition (7 core skills + cykl-prowadzacy)
curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash -s -- claude --edition multi

# Offline: unpack the skills ZIP once downloaded (it holds all 8 skills;
# delete cykl-prowadzacy afterwards if you want the 7-skill editions)
unzip cykl-lifecycle-skills.zip -d ~/.claude/skills/      # Codex: ~/.agents/skills/
```

Use `codex` or `both` instead of `claude` for OpenAI Codex. Claude Cowork: drag
`cykl-lifecycle.plugin` into a conversation. Restart the agent after installing.

Then, in the project: `/kickoff` and answer "local" or "github" when asked where tasks live.

## The session loop

```
/kickoff (once) -> /start -> work -> /snapshot (optional) -> /close -> next session /start
```

`/close` succeeds only when the script returns a checkpoint card (UUID + hash). That
card, not the chat, is the proof that state was saved.

## Commands

Canonical names stay `cykl-*`; aliases appear in the skill descriptions and create no
duplicate skills.

| Skill | Command | Purpose |
|---|---|---|
| cykl-kickoff | /kickoff | Set up a new project and choose the edition |
| cykl-start | /start | Validate state and report position and next action |
| cykl-migawka | /snapshot, /handoff | Save a checkpoint during work |
| cykl-zamknij | /close | Save before closing or compaction |
| cykl-roadmap | /roadmap | Show task and release position |
| cykl-lekcja | /lesson | Record a project lesson with evidence |
| cykl-lekcja-globalna | /lesson-global | Propose a cross-project lesson |
| cykl-prowadzacy | /lead | Multi-agent edition only: lead-thread protocol |

## Editions in detail

**Local.** `PROJECT_CONFIG.md` contains `TASKS=local`. `docs/ROADMAP.md` is the task
index (`- T-12 open Title`; statuses open, doing, done, dropped), each open or doing task
has `docs/issues/T-12.md`, and `check` validates both. Releases are recorded in
`CHANGELOG.md` and git tags. No server enforces anything; the pre-commit hook is the only
guard. The 4 KB ROADMAP cap fits roughly 60-80 task lines; prune done and dropped lines
(history is in git) or move to the GitHub edition.

**GitHub.** `TASKS=github`, or no `TASKS` line (the 3.0.x default). GitHub issues own
scope, assignment and acceptance; milestones and Releases own releases. The local ROADMAP
is a bounded observation. Offline, an agent may continue an already-assigned task but not
start or accept new ones. The script never calls the GitHub API; issue operations are
manual or via your own tooling.

**GitHub + multi-agent.** Adds the `cykl-prowadzacy` lead-thread protocol:
- one lead thread per project plans, briefs executors, reads short reports, records
  decisions and keeps a journal; it does not implement, test or release itself;
- each delegation is a self-contained brief (task, files, forbidden actions, required
  proof, report format) naming the model and why, chosen from a routing table you edit
  in `docs/lead/LEAD.md`; independent review by a different model family before merge;
- executors return a `=== SHORT ===` block of at most 8 lines; long reports go to files;
- after three fix rounds in the same failure class without convergence, the lead stops and
  asks for a fresh-context review of the step itself instead of a fourth round;
- Owner decisions are numbered and stored with the Owner's words quoted, together with
  the recommendation and what would change it;
- lead threads hand over through `docs/lead/THREADS.md`; a new lead registers there first;
- usage-budget thresholds pause low-priority work; measurement depends on your harness.

These are working rules for agents, enforced by the skill text and a few file checks
(brief and report shape, thread registry cap), not by an orchestration runtime. Model
routing is your configuration. Templates live in `skills/cykl-prowadzacy/assets/`.

## Upgrading

From 3.0.x: install 3.1.0 over all skills. No migration; projects without `TASKS=`
behave as the GitHub edition. From v2: see [docs/MIGRATION-v2.md](docs/MIGRATION-v2.md).
Do not mix versions of the skills.

## Merge protection (GitHub editions)

See [docs/MERGE-PROTECTION.md](docs/MERGE-PROTECTION.md). Until a blocked canary PR has
been demonstrated in your repository, report "merge protection unverified".

## Script reference

Requires Python 3.9+. No Python packages, tokenizer downloads or network access are needed.

```sh
LIFECYCLE=/path/to/skills/cykl-start/scripts/lifecycle.py
python3 "$LIFECYCLE" check --root /path/to/project
python3 "$LIFECYCLE" context --root /path/to/project --skill cykl-start
python3 "$LIFECYCLE" decisions --root /path/to/project
```

The skills run these commands for you. For a new project, create a draft using the JSON in
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

## Offline and privacy

With `TASKS=github`, only already-dispatched work continues offline, in one shared
worktree. Attempt files supply current status; NOW holds their IDs. New assignments, scope
changes, acceptance and publication wait for online reconciliation. With `TASKS=local`,
ROADMAP and `docs/issues` are the authority and change through checkpoint. GitHub API
synchronization/import is manual. Prepared issue bodies, including the pin, cap at 8,192
bytes. Mirroring is disabled; any future opt-in mirror must select reviewed public-safe
identity, goal, position, next action and IDs. Preserve/Risks/decision bodies stay out of
the mirror.

## Verify and build

```sh
python3 -B -m unittest discover -s tests -v
python3 -B skills/cykl-start/scripts/lifecycle.py check --package
bash build-plugin.sh
```

Build produces the plugin, the combined skills ZIP and eight individual skill ZIPs.
See [CHANGELOG](CHANGELOG.md) for changes, [R2](docs/design/v3.0.md) and
[the 3.1 delta](docs/design/v3.1.md) for caps and contracts.

## License

MIT
