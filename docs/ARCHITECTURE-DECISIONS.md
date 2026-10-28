# Architecture decisions — cykl-lifecycle
**English** · [Polski](ARCHITECTURE-DECISIONS.pl.md)

> **Historical (v2, 2.6.0).** This explains why v2 was built this way. Version 3 is a breaking redesign: for current behaviour see the [README](../README.md) and the [command guide](COMMAND-GUIDE.md). Do not run v2 cleanup/writers on schema 3.

**Version:** 2.6.0 · **Last updated:** 2026-08-04

This document explains **why** the system looks the way it does. Every decision has a precedent: a failure or a measurement that forced it. If you want to know **how to use it**, go to [COMMAND-GUIDE.md](COMMAND-GUIDE.md); if you want to know **what changed**, see [CHANGELOG.md](../CHANGELOG.md).

---

## D1 — State lives in files, not in the thread

**Decision.** Project memory is `PROJECT_CONFIG.md`, `docs/HANDOFF.md`, `docs/ROADMAP.md` and `docs/LESSONS_CANON.md`. The chat is a workbench for a single session.

**Why.** The model is stateless: with every message it receives the whole conversation again, so the cost of a turn grows roughly quadratically with the length of the thread. Quality drops regardless of cost: in a long context the model is worse at retrieving information from the middle and gets lost in the noise.

**Consequence.** A new conversation for every session. `/start` on the way in, `/zamknij` (/close) on the way out.

---

## D2 — Two kinds of fields: log fields and state fields

**Decision.** A **log** field (changelog, document header, current sprint) is append-only. A **state** field (repo state, next open decision, public URL, hash of the deployed artifact) has one true value and is overwritten in full after a measurement, with the marker `[measured YYYY-MM-DD HH:MM UTC]` (original: `[zmierzone RRRR-MM-DD HH:MM UTC]`).

**Precedent.** In a project run with this toolkit, the field describing repository state grew over six consecutive sessions until it reached **1369 characters** and held **three contradictory states from three different dates**. The last session appended the current measurement to the end of the line without removing the two previous ones. The reader — a human or `/start` — took the first value, i.e. the oldest, and got a picture from five days earlier. The newest value **was in the file**, just behind two stale ones.

**Consequence.** The skills treated every field as a log field. Since 2.5.0 they distinguish the two explicitly, and `/start` reports as drift any field carrying more than one state — even if the newest value is in it.

**Edge case.** When a state field also holds durable operational knowledge (workarounds, tool limitations), split it in two: `REPO_STATE` (overwritten) and `REPO_NOTES` (append-only). We don't delete knowledge — we move it.

---

## D3 — The field describing the last commit is one commit behind

**Decision.** The field describing repository state is labelled `stan PRZED commitem tej sesji` (state BEFORE this session's commit).

**Why.** You write the value *inside* the commit that persists it, so by definition it describes the state before itself. This is not a bug to fix but a structural property — yet unlabelled it looks like a bug and invites "fixing".

---

## D4 — The session number on an open decision comes from the current session

**Decision.** The "next decision" field carries the number of the **current** session. If the decision carries over unchanged, write it out explicitly: "carried over unchanged from session N".

**Precedent.** A commit covering sessions 62 and 63 rewrote this field from `[SESJA 61]` to `[SESJA 62]` — one short. The field was not skipped; it was rewritten from what the session **found**, instead of from what the session itself established.

---

## D5 — Git is read-only, from a closed allowlist

**Decision.** The skills run only: `git rev-parse --short HEAD`, `git rev-list --left-right --count <remote>...HEAD`, `git log --oneline -n`, `git show`, `git diff --stat HEAD`. Forbidden: **`git status`**, **`git add --dry-run`**, **`git stash`**.

**Precedent.** A check of whether writing to the repo through a remote bridge worked was done with `git add --dry-run` — and that very call created `.git/index.lock`, which the bridge cannot remove (`unable to unlink: Operation not permitted`). The diagnostic produced exactly the failure it was diagnosing. A plain `git status` does the same, because it refreshes the index. The repository was locked for four days.

**Consequence.** For the question "does git write through this bridge at all" **there is no safe command**. The answer is: a human checks it in their own terminal.

---

## D6 — A gate is shell syntax, not a comment

**Decision.** Every "do Y only if X" condition in a command block is written as `set -euo pipefail` + `&&`. Never as an annotation like `# dopiero gdy zielone` (only when green).

**Precedent.** A runbook whose condition was expressed as a comment pushed changes despite three failing tests — the human pasted the whole block at once, and the comment did not stop `git push`. The same class of problem recurred in another session in a pipeline variant: `npm run build | tail` reported success despite a compilation error, because a pipeline returns the exit code of its last element.

**Consequence.** `pipefail` is mandatory wherever a gate contains a pipeline. Up to 2.5.0 the pre-flight block in `/zamknij` was itself this anti-pattern — the condition "date = today? if not, do NOT commit" sat in a comment above `git add`.

---

## D7 — `/start` measures state outside the documents

**Decision.** `PROJECT_CONFIG` declares `STATE_PROBE` — a single read-only command that measures live state. `/start` runs it **before** comparing the documents with each other. At most three attempts; no answer means `[DO SPRAWDZENIA]` (to be checked), never a block on entering the session.

**Precedent.** The drift check compared only documents with each other: the header with the changelog, `PROJECT_CONFIG` with `HANDOFF`, the Position with step statuses. In a real project `HANDOFF` and `ROADMAP` **agreed** that no work had happened on a given day — while the deployment system showed five changes and a different artifact hash. The drift check would have passed cleanly, because every document repeated the same falsehood. **Internal consistency is not truth.**

**Why this, and not "recon at startup".** Building a full pre-task reconnaissance into `/start` was considered. Rejected: reconnaissance is **per task** and happens before an irreversible move; `/start` is **per session** and read-only. At entry you don't yet know what the task will be, so reconnaissance has nothing to measure — it would measure "something general", i.e. nothing, and `/start` would stop being cheap and fall out of use. The probe costs about a fifth of that idea and fixes a defect that actually occurred.

**The skill stays generic.** It knows nothing about git, databases or builds — it runs whatever the project declared. The project brings the measuring gear, not the plugin.

---

## D8 — A stage exit gate is a condition, not a description

**Decision.** A stage moves to `DONE` only when its **Exit gate** from the stage table is met and it has been shown what met it. All steps being `DONE` is a necessary condition, not a sufficient one.

**Why.** The "Exit gate" column had existed in the `ROADMAP` template since version 2.0, but **no skill read it** — flipping a stage relied solely on step statuses. The column was decoration: it described a condition nobody checked. This is the same class as D6, only in a document instead of the shell.

---

## D9 — Measurement rules

A reconnaissance that measures wrongly is **more dangerous than none** — it produces confidence that nobody verifies anymore. Four rules derived from documented failures:

| Rule | Precedent |
|---|---|
| **Measurement contradicts the document? First check you are measuring the right object** — the one the current step uses, not one with a similar name | the report mentioned a table with 107 rows; the screen rendered a function returning 9. Had the measurement followed the name from the report text, the scope of work would have targeted list virtualization, i.e. nothing. The same class of error occurred three times in two days |
| **A truncated read is not proof of absence** — a listing cut off by a limit says "I don't see it", not "it isn't there" | an analysis after reading 65 files reported one number and **explicitly flagged the gap** (48 files unread); measuring the complete artifact gave a different one. A partial read gives a lower bound, not a total |
| **A measurement has an expiry date** — hence the time in the marker, not just the date | "zero changes today" measured at 18:00 was untrue at 21:00; work started 74 minutes after the measurement. The entry was not a lie when written, but the document was saying something false by the next day |
| **Correcting a claim must touch every repetition of it** — after the fix, `grep` for the old wording = 0 outside the changelog | the same facts live in `HANDOFF`, `ROADMAP` and `PROJECT_CONFIG` at once. A fix in one place leaves two sources of falsehood that later sessions read as fact |

---

## D10 — Automatic push: deliberately NO

**Decision.** `/zamknij` does not run `git push` or `git commit`. The order for rolling out automation: first the mechanical gate (D6), then measurement on entry (D7), and auto-push only as a per-project opt-in — and only after the first two have run for several sessions.

**Why.**

1. **Automation on top of a broken gate multiplies the error.** As long as the condition was a comment, auto-push would have guaranteed pushing a state that had not passed the check.
2. **`git add` and `git commit` also create `.git/index.lock`** — the same failure mechanism that forced the ban in D5, only triggered more often.
3. **A push is practically irreversible** in a public repository. The cost of a false positive is asymmetric to the convenience gained.
4. **Divergence from the remote needs a human.** Auto-push assumes a fast-forward; on divergence, a conflict in the state documents would have to be resolved unsupervised.

**What actually hurt, and how it was solved without pushing.** The symptom was "work uncommitted for several days, nobody noticed". The cause was not missing automation but that `/start` read only files — and uncommitted work looks identical in files to committed work. `STATE_PROBE` from D7 closes this without a single write to the repository.

**What would reverse this decision.** A private, single-person repository with no CI — then the cost of a bad push drops enough that enabling it by default becomes reasonable.

---

## D11 — State document size is the cause of drift, not its effect

**Decision.** State documents have a threshold (~40 kB for HANDOFF). Once it is exceeded, `/zamknij` moves historical entries to `docs/archive/<name>-YYYY-Qn.md` and keeps the last 5 plus a pointer. `/start` reports the overrun as debt.

**Precedent.** In a project run with this toolkit, state documents grew to **153 / 179 / 294 / 316 kB**. The template the last of these came from weighs ~2 kB and has said since its first version: *"This is a **thin** snapshot"*. A hundred and sixty times larger, and no mechanism noticed.

**Why it is the cause, not a contributing factor.** A diagnosis after four consecutive sessions with the same type of drift identified three separate mechanisms: a field referring to itself, a fact duplicated across three files, and the header diverging from the content. All three are consequences of size:

- a duplicated fact only hurts when you can't see all the copies at once;
- the header diverges from the content because whoever appends at the bottom of the file doesn't go back to the top;
- whoever closes the session *"updates the places they remember — and the number of places grows with every session"*.

With a file you can review in full, none of these three has a way to happen.

**Consequence for the order of fixes.** Removing copies in a file that keeps growing buys one session of peace. The size threshold goes first.

**What would reverse this decision.** If the state documents deliberately served as an audit archive and trimming meant losing the trail. Checkable with one question: has anyone ever looked at a HANDOFF older than five sessions?

---

## D12 — A fact has one home; everything else refers to it

**Decision.** A value that lives in one document is entered in others as a **reference**, never as a copy. This also applies to fields measured by `STATE_PROBE`: `REPO_STATE=<mierzone przez STATE_PROBE>` (measured by STATE_PROBE) instead of a copied hash.

**Precedent.** `CURRENT_MILESTONE` carried the plan's version number, which also lived in the plan document. A session updated the plan and the current sprint but missed the third place. Separately: the field describing the last commit was **always** one behind, because it is written by the very commit that persists it.

**Why this replaces the earlier rule rather than supplementing it.** The 2.6.0 rule — *"correcting a claim must touch every repetition of it"* — polices copies. The cost of policing grows with the number of copies and with every session, and verification requires reviewing everything, which is infeasible for a large file (D11). Removing copies is the only version that can be checked cheaply: there is nothing to compare. The 2.6.0 rule stays, but only to handle the transition period — while copies still exist.

**Edge case.** A reference must not be a void. When `STATE_PROBE` cannot run (Cowork without a bridge, Claude.ai), the reader must know the value exists elsewhere — not that it is missing. Hence the explicit `<mierzone przez STATE_PROBE>` entry instead of removing the field.

**Side effect that is the main gain.** Self-reference disappears without needing to be labelled: measurement moves from write time to read time.
