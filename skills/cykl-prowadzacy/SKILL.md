---
name: cykl-prowadzacy
description: "Lead a multi-agent project: brief executors, read SHORT reports, record Owner decisions, hand over between lead threads; /prowadz; English alias: /lead."
---
<!-- cykl-lifecycle v3.1.0 -->

# cykl-prowadzacy (lead thread)

Working rules for one lead agent coordinating executor agents or models. They are
enforced by this text and a few file checks, not by an orchestration runtime.
Resolve LIFECYCLE to the sibling `cykl-start/scripts/lifecycle.py`; PROJECT is the root.

1. **Start.** Run cykl-start, then `context --root "$PROJECT" --file docs/lead/LEAD.md`.
   THREADS is already in the projection. Register this thread in THREADS through
   checkpoint (`files` map, expected hash). If another thread is active and not handed
   over, stop and ask the Owner. Templates: `assets/` (copy to docs/lead/ at first use).
2. **The lead does not implement, test or release.** It briefs, reads SHORT blocks,
   decides within delegated authority, records decisions and journal lines. Read a long
   report only when a decision needs it.
3. **Every delegation** is a packet from BRIEF.template.json plus an A-* attempt in NOW.
   Choose `model` from the LEAD.md routing table and give a one-sentence `model_reason`.
   Independent review before merge comes from a different model family than the implementer.
4. **Briefs are self-contained.** Executors do not mutate git unless the brief says so;
   then only `git -C <path>`, only listed files, never reset, rebase, amend, stash, clean
   or add -A. Deletion means moving to the holding directory named in LEAD.md.
5. **Reports.** Executors write `=== SHORT ===` plus at most 8 lines to
   docs/queue/results/<A-id>.md; long reports go to the directory named in LEAD.md.
6. **Step back.** After 3 fix rounds in one failure class where findings do not fall, or
   each round adds a new blocker, do not brief round 4. Brief a fresh-context review of
   the step itself (different model, no prior transcript): what does it really produce,
   who decides, can it be removed. Journal the trigger.
7. **Owner decisions.** Give one recommendation plus what would change it, not a menu.
   After the answer run `decisions add` with text
   `Owner: "<exact words>" | Decision: ... | Would change: ...` in the LEAD.md language.
   A pending question is an O-* entry in NOW ("awaiting Owner: ...").
8. **Budget.** Before each wave, measure plan usage if the harness exposes it and apply
   the LEAD.md thresholds, lowest priority first. Never use paid overage. If usage cannot
   be measured, journal "unmeasured"; do not guess.
9. **Done** means committed, pushed (if there is a remote), verification named
   (command and result) and one journal line in docs/lead/JOURNAL.md (append only;
   retrieve with grep by ID, never load whole).
10. **Handover.** Run cykl-zamknij. In the same checkpoint set this thread's THREADS row
    to `handed-over` with the NOW checkpoint UUID. The next lead reads NOW and THREADS.

Read only `context` output (16,384 UTF-8 bytes total). All lifecycle writes use
checkpoint or decisions add, except docs/lead/JOURNAL.md (append only, outside the writer;
the writer rejects it). BRIEF issue_url: local = docs/issues/T-n.md, github = issue URL; keep returned acknowledgement cards before compaction.
