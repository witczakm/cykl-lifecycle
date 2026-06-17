# Changelog

All notable changes to cykl-lifecycle are documented here.

---

## [2.4.0] — 2026-06-17

### Added
- **Wsparcie OpenAI Codex (dual-compatible).** Ten sam `SKILL.md` działa teraz w Claude i w Codeksie.
- `agents/openai.yaml` w każdym z 7 skilli — metadane UI + polityka wywołania dla Codeksa (Claude ignoruje plik). `cykl-kickoff` ma `allow_implicit_invocation: false` (tylko jawne `$cykl-kickoff`).
- Pakiet jako **Codex plugin**: `.codex-plugin/plugin.json` + `marketplace.json`.
- `docs/INSTALL-codex.md` — instalacja na Codeksie (skille albo plugin) + sekcja bezpieczeństwa (tryb zatwierdzania).
- `CONTRIBUTING.md` oraz README przepisany pod dwie platformy (Claude + Codex), przyjazny początkującym w AI.
- `/lekcja-g` na Codeksie zapisuje do `~/.codex/AGENTS.md` (globalne instrukcje czytane na starcie każdej sesji).

### Changed
- Uogólniono fragmenty platform-coupled w skillach: „CCT" → „terminal (Claude Code / Codex)"; `cykl-kickoff` adnotuje plik instrukcji projektu jako CLAUDE.md (Claude) / AGENTS.md (Codex); `cykl-lekcja-globalna` ma tri-platform tabelę celu zapisu.
- `docs/INSTRUKCJA-INSTALACJI.md` → `docs/INSTALL-claude.md`; instalacja rozdzielona per platforma.
- README: bump wersji 2.3.0 → 2.4.0.

### Verified
- Wszystkie 7 skilli przetestowane na żywo: Claude (Cowork) oraz Codex v0.140.0 / gpt-5.5 (2026-06-17) — triggery explicit, implicit i negatywne oraz poprawność zapisów dokumentów stanu. Komplet PASS.

---

## [2.3.0] — 2026-06-17

### Fixed
- LESSONS_CANON.template: F1–F6 uogólnione (usunięto referencje BidSentinel)
- README: instalacja CCT — jedna komenda `cp -r skills/cykl-*` zamiast 7 osobnych
- README: badge URL Skills — poprawny link do docs.anthropic.com
- README: Cowork UI reference — usunięto hardkodowaną lokalizację ikony

### Added
- README: sekcja "Pierwsze 15 minut — quickstart" z literalnym transkryptem
- README: tabela porównawcza profili lite/standard/regulated
- README: minimum viable workflow dla małych projektów
- README: nota dla użytkowników Cowork bez CCT przy /lekcja-g
- Wszystkie SKILL.md: wersja `<!-- cykl-lifecycle v2.3.0 -->`
- cykl-roadmap: rozszerzony negatywny trigger
- HANDOFF.template: komentarz HTML oznaczający sekcję instrukcji dla modelu AI (P3.1)
- README: zasada „nie prowadź całego projektu w jednym wątku" (uzasadnienie token/jakość + context rot) oraz wpis FAQ

### Changed
- cykl-zaloz → cykl-kickoff — nazwa folderu, pole `name:` w SKILL.md oraz referencje w README i docs/INSTRUKCJA-INSTALACJI.md (P3.2)
- README: badge wersji 2.2.0 → 2.3.0

## [2.2.0] — 2026-06-17

### Changed
- Rename `nsos-*` → `cykl-*` (universal prefix, neutral to code context)
- Rename `nsos-handoff` → `cykl-migawka` (avoids collision with test/VM snapshots)
- Added **negative triggers** to every skill description ("NIE używaj gdy…")
- Added public GitHub release with professional README, installation guide, command guide

### Added
- `INSTRUKCJA-INSTALACJI.md` — 3-option installation guide (CCT global / Claude.ai Settings / local)
- `PRZEWODNIK-KOMEND.md` — per-command reference with examples, diffs, Q&A

---

## [2.1.0] — 2026-06-10

### Fixed (CRITICAL)
- Mandatory changelog row on every header bump (`/handoff`, `/zamknij`) — without it `/start` drift-check produced false alarms on every correctly-executed session

### Added
- **Two-level position awareness** (Stage X/N · step Y/M) in ROADMAP template and all skills
- `/start` step 0: guard for non-lifecycle directories (no `PROJECT_CONFIG.md` → propose `/kickoff`)
- `/start` drift-check: scans `LESSONS_CANON.md` for `[CANDIDATE GLOBAL]` markers and surfaces them with CCT command
- ROADMAP: `Verification` column — step only flips to DONE when verifiable criterion is met
- ROADMAP: `Exit gate` column on stage table — stage only DONE when gate is satisfied
- `GLOBAL_LESSONS_BASELINE` loop closed: CCT writes GL-NNN to field after confirmed global save
- Conflict resolver for HANDOFF ↔ ROADMAP in `struktura-projektu.md` and `README.template`
- Pre-flight `grep` in `/zamknij` commit block (verifies files actually wrote to disk)
- Idempotency test in `/zamknij` (today's changelog date = patch-only bump, no duplicate rows)
- `/kickoff` interview limit (max 5-7 questions/turn, rest → `UNKNOWN`)
- Project-local F-lessons numbered from F10 (F1-F6 = universal baseline, F7-F9 = visual buffer)

### Fixed
- `/handoff` snapshot model: overwrite-only (was append; accumulation → log, then `/zamknij` overwrote it losing interim decisions)
- `PROJECT_CONFIG.template`: added minimal version header (skills said "bump CONFIG header" but template had no header)
- `README.template`: profile-aware pruning instruction (lite profile must not reference non-existent `docs/adr/`, `CLAUDE.md`)

---

## [2.0.0] — 2026-06-09

### Changed
- Full de-escalation from Faza 1 (11 commands, Python scripts, transactional rollback, JSON manifests) to Faza 2: **prose-only skills**, zero code, zero automation without human approval
- Aligned with Anthropic Agent Skills best practices format

### Added
- 7 skills: `/start`, `/zamknij`, `/handoff`, `/roadmap`, `/lekcja`, `/lekcja-g`, `/kickoff`
- 5 document templates (HANDOFF, ROADMAP, LESSONS_CANON, PROJECT_CONFIG, README)
- `struktura-projektu.md` reference (source-of-truth hierarchy, profiles)
- IoC pattern for global lessons (Cowork → CCT handoff, no hanging markers)
- Common principles from BidSentinel lessons F1-F6 (pre-loaded in every new project)
