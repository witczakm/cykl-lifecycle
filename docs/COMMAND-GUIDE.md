# Command guide — cykl-lifecycle 3.1
**English** · [Polski](COMMAND-GUIDE.pl.md)

**Who it's for:** anyone using cykl-lifecycle to run a project over many AI sessions.
You type the commands; the agent runs the script behind them.

## The idea in one paragraph

A project that spans many sessions has one core problem: every new chat starts with no
memory of the previous ones. cykl-lifecycle solves it with a loop: **start → work → save →
close → start again next time**. What the agent must remember lives in a few small files in
your project, the *lifecycle state*:

| File | What it holds |
|---|---|
| `docs/NOW.md` | where the project stands, open work and the one next action (max 4 KB) |
| `docs/DECISIONS.md` | the *decision index*: one line per decision or lesson, with a stable ID |
| `PROJECT_CONFIG.md` | a few settings, e.g. `TASKS=local` or `TASKS=github` |
| `docs/ROADMAP.md`, `docs/issues/` | tasks, in the Local edition only |

Only the script `cykl-start/scripts/lifecycle.py` writes these files. Every save returns a
**checkpoint card** (an ID and a hash). No card = nothing was saved, whatever the chat says.

## The loop

```
First session:
  /kickoff  ->  a few questions, the first save, then /start

Every session after that:
  /start  ->  work  ->  (optional: /snapshot, /lesson along the way)  ->  /close

Check progress:            /roadmap
Keep something you learned: /lesson (this project) or /lesson-global (all projects)
Multi-agent edition:        /lead
```

Polish names work too: `/migawka` = `/snapshot`, `/zamknij` = `/close`, `/lekcja` = `/lesson`,
`/lekcja-g` = `/lesson-global`, `/prowadz` = `/lead`. In Codex, call skills as `$cykl-start`,
`$cykl-kickoff` and so on.

## IDs you will see

| Prefix | Meaning |
|---|---|
| `O-…` | obligation: something still owed (a promise, a pending approval) |
| `A-…` | attempt: a piece of work in progress |
| `D-…` | decision |
| `L-…` | lesson |
| `T-…` | task (Local edition) |

Open IDs are never dropped silently. Closing one needs the ID and a reason.

---

## /kickoff — set up a project

**When:** once, at the very start of a project.

**What it does:**
1. Checks whether the project already has lifecycle files. If it has v2 files, it stops and
   routes you to migration ([MIGRATION-v2.md](MIGRATION-v2.md)); it never overwrites them.
2. Asks for the goal, repository, branch and the first next action.
3. Asks where tasks live: **github** (default) or **local** (no GitHub needed).
4. Saves the first state (`checkpoint --expected absent`) and shows the checkpoint card.
5. Installs the pre-commit hook; for GitHub projects also the `lifecycle-integrity` check
   (see [Merge protection](MERGE-PROTECTION.md)).

It does not create GitHub issues, milestones or releases.

## /start — begin a session

**When:** at the start of every session, as the first command.

**What it does:** runs `lifecycle.py context`, which validates the state and returns a short,
size-capped summary. The agent reports:
- current position and the one next action,
- open IDs (obligations, attempts),
- whether anything is stale or offline.

If validation fails, the session stops there: the agent does not fall back to old chat memory
or to reading files by hand. Example:

```
Position: API stage, login endpoint in progress (A-login).
Next: finish /auth/login and run its tests.
Open: O-review-auth (waiting for review). Offline: no.
```

## /snapshot (/migawka, /handoff) — save during a session

**When:** after an important decision or a finished step, when you don't want to wait for the end.

**What it does:** writes a new checkpoint with the position, next action, open work and risks,
using the hash of the current state (so two writers cannot overwrite each other). Returns a
checkpoint card. It never commits to git.

## /close (/zamknij) — end a session

**When:** at the end of every session with real work, and before a long chat is compacted.

**What it does:**
1. Collects verified outcomes, what is still open, approvals, failed approaches and one next action.
2. Saves a checkpoint, then runs `check`.
3. Shows the checkpoint card. Only that card allows saying "the session is saved".

It commits or publishes only if you separately ask for it.

## /roadmap — see progress

**When:** you want a bird's-eye view of tasks and releases.

**What it does:** shows the current milestone, task IDs, the next action and how fresh the view is.
- Local edition: the lines in `docs/ROADMAP.md` (`- T-1 open Title`) are the task list.
- GitHub edition: GitHub issues and milestones are the truth; the local ROADMAP is only a view.

`/roadmap update …` changes it only when you ask, and only with verified authority; offline,
the change is recorded as a pending `O-…` item.

## /lesson (/lekcja) — record a project lesson

**When:** something went wrong (or right) and you don't want to repeat it in this project.

**What it does:** writes one row to the decision index: a rule, the precedent that taught it,
and an operational test. Example:

```
/lesson
I lost an hour because Redis wasn't running before the integration tests.
```

becomes a row like `L-redis-before-tests lesson accepted: Check that Redis is up before
integration tests; precedent: 1 h lost; test: docker ps | grep redis before npm test`.
IDs are never reused.

## /lesson-global (/lekcja-g) — propose a lesson for all projects

**When:** the lesson is general enough to matter in every project.

**What it does:** records it as a **proposed** lesson in this project and keeps an `O-…`
obligation until you approve it. It never changes another project's or your global
instructions on its own: you get the approved text to apply where it belongs.

## /lead (/prowadz) — lead a multi-agent project

**Edition:** GitHub + multi-agent only (`install.sh … --edition multi`).

**What it does:** one lead thread plans and decides; other agents or models implement, test
and review. The lead writes self-contained briefs, reads `=== SHORT ===` reports of at most
8 lines, records Owner decisions with the Owner's exact words, and hands over to the next lead
thread through `docs/lead/THREADS.md`. After three fix rounds without progress it stops and asks
for a fresh review of the step itself. Details: the multi-agent section of the [README](../README.md).

---

## Rules worth knowing

1. **One next action.** `/start` always gives exactly one next step.
2. **Saved means a card.** A fact counts as saved only after the script returns a checkpoint card.
3. **Done needs proof.** A task is done when its check is met (test passed, file exists), not
   when it "seems to work".
4. **Nothing to remember between sessions.** That is the point: `/close`, and forget until `/start`.
5. **The agent never edits lifecycle files directly.** All writes go through the script.

## Questions

**Do I have to type /start?** It is the safest way. The skill can also trigger when you say
"where were we?".

**What if I skipped /close last time?** `/start` still works from the last saved checkpoint;
anything not saved since then is lost. Use `/snapshot` during long sessions.

**Does it need the internet?** No. The script needs only Python 3.9+. With `TASKS=github`,
offline work is limited to tasks already assigned.

**I used v2.** Version 3 is a breaking change; follow [MIGRATION-v2.md](MIGRATION-v2.md).
The v2 version of this guide is in the git history (tag `v2.8.2`).
