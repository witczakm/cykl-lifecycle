# Struktura projektu wielosesyjnego — co do czego służy

**Wersja:** 1.1.0
**Utworzono:** 2026-06-09 20:22 CEST
**Ostatnia aktualizacja:** 2026-06-10
**Źródło:** wyekstrahowane z żywego `northstar-os` (struktura sprawdzona w praktyce) + lekcje F1-F6 (BidSentinel, w `LESSONS_CANON.md`).
**Po co:** żeby `/kickoff` zakładał projekt wg sprawdzonego wzorca, a nowy projekt był świadomy, do czego każdy element służy (nie zgadywał).

---

## Hierarchia źródeł prawdy (kto wygrywa konflikt)

To jest najważniejsza zasada — gdy dwa dokumenty mówią co innego, wygrywa wyżej:

```
1. CLAUDE.md      — jak BUDUJEMY (aktorzy, proces, zasady). Wygrywa ze wszystkim.
   AGENTS.md      — jak system DZIAŁA w produkcji (opcjonalny, gdy projekt ma runtime).
2. PROJECT_CONFIG.md — parametry, ścieżki, live-state sprintu (SSOT liczb).
3. docs/adr/      — zaakceptowane decyzje („co i dlaczego zdecydowaliśmy").
4. docs/specs/    — specyfikacje, standardy („jak ma działać").
5. docs/runbooks/ — egzekucja („jak to wykonać krok po kroku").
6. kod + testy    — po starcie implementacji.
```

Pamięć globalna AI **nie jest** źródłem prawdy projektu — trzyma tylko wskaźniki do plików w repo.

**Dokumenty stanu (HANDOFF/ROADMAP/CONFIG) stoją obok tej hierarchii** — opisują „gdzie jesteśmy",
nie „co jest prawdą o architekturze". Gdy są ze sobą sprzeczne, to **drift do zgłoszenia** (robi to
`/start`), nie konflikt do cichego rozstrzygnięcia. Doraźny rozjemca, zanim drift zostanie naprawiony:
**HANDOFF** rozstrzyga „następny atomowy ruch", **ROADMAP** rozstrzyga kolejność etapów i Pozycję,
**CONFIG** rozstrzyga twarde liczby live-state (branch, status, ryzyka).

---

## Dokumenty stanu (żywe — aktualizowane co sesję)

| Plik | Do czego | Kto aktualizuje | Zasada |
|---|---|---|---|
| **`docs/HANDOFF.md`** | snapshot „gdzie jesteśmy + następny ruch". Cienki — NIE powiela liczb z CONFIG. | `/handoff`, `/zamknij` | jedyne źródło „następnego atomowego ruchu" |
| **`docs/ROADMAP.md`** | sekwencja + postęp dwupoziomowy: etapy projektu (poziom 1) i kroki bieżącego etapu (poziom 2, ze statusami i weryfikacją) + linia `Pozycja` (etap X/N · krok Y/M). SSOT kolejności i pozycji. | `/roadmap`, `/handoff` (flip statusu kroku), `/zamknij` | statusy zmieniaj swobodnie; treści kroków nie usuwaj/nie przeredagowuj bez jawnej decyzji — usunięty krok znika bezgłośnie. Linkuje do CONFIG, nie kopiuje liczb |
| **`PROJECT_CONFIG.md`** | parametry + `§Current Sprint` (twarde liczby: branch, commity, status, ryzyka). | `/zamknij`, `/handoff` | jedyne źródło live-state (`CURRENT_SPRINT`) |
| **`docs/LESSONS_CANON.md`** | kanon lekcji projektu (F=fundamentalne, W=wykonawcze). | `/lekcja` | każda lekcja: Reguła + Dlaczego + Test operacyjny |

---

## Dokumenty decyzji i wiedzy (rosną w miarę projektu)

| Katalog | Do czego | Format |
|---|---|---|
| **`docs/adr/`** | Architecture Decision Records — 1 plik = 1 wiążąca decyzja. | `ADR-NNN-<temat>.md` |
| **`docs/specs/`** | specyfikacje, plany sprintów, rejestry, standardy. | `YYYY-MM-DD-<temat>-{design,plan}.md` |
| **`docs/runbooks/`** | procedury krok-po-kroku (instalacja, smoke-testy). | `YYYY-MM-DD-<temat>.md` |
| **`docs/reports/`** | closeout sprintów — ślad audytowy zamknięć. | `YYYY-MM-DD-<temat>-closeout.md` |
| **`docs/reviews/`** | wyniki cross-AI review (GPT/Gemini/Codex). | per runda |
| **`docs/backlog/`** | follow-upy odłożone świadomie. | per temat |
| **`docs/vision/`** | „dlaczego docelowo" — wizja produktu (opcjonalne). | per dokument |

---

## Katalogi pracy

| Katalog | Do czego |
|---|---|
| **`skills/`** | skille projektowe (komendy `/start`, `/zamknij`…). Źródło w repo (git trail), instalacja globalna do `~/.claude/skills/`. |
| **`runtime/audit/`** | paczki cross-AI (ZIP per runda) + ślady syntez. |
| **`src/`, `tests/`, `migrations/`** | kod, testy, migracje DB (gdy projekt ma kod). |
| **`legacy_reference/`** | historyczne pliki — TYLKO referencja, NIE źródło wykonania. |

---

## Lekcje F1-F6 (fundament — czego pilnować, z BidSentinel)

Te lekcje są w `LESSONS_CANON.md` każdego projektu — to destylat błędów, które kosztowały czas:

- **F1 Buy-before-build** — sprawdź, czy istnieje gotowiec, zanim zbudujesz.
- **F2 Brief przed modułem** — CO + PO CO + STOP na akceptację, zanim kod.
- **F3 Fundament first** — buduj od fundamentu; mierz zmienną, która naprawdę decyduje.
- **F4 Fakty nie założenia** — weryfikuj w kodzie/danych, nie z pamięci; oddzielaj fakty|założenia|ryzyka|rekomendacje.
- **F5 Wzorce korporacyjne** — bierz sprawdzone nazwane wzorce, nie wymyślaj nowych.
- **F6 Anti-overengineering** — nie buduj ciężkich komponentów przedwcześnie; sloty na przyszłość, nie implementacja.

---

## Minimalny vs pełny projekt (profile)

Nie każdy projekt potrzebuje wszystkiego. `/kickoff` proponuje profil:

- **lite** — `README + PROJECT_CONFIG + docs/{HANDOFF,ROADMAP,LESSONS_CANON}`. Mały projekt/PoC.
- **standard** — lite + `CLAUDE.md + docs/{adr,specs,runbooks,reports} + skills/`. Typowy projekt z procesem.
- **regulated** — standard + `_ai_ops/ (audit trail) + runtime/audit/ + AGENTS.md`. Projekt z autonomią/produkcją/wymogami audytu.

Reszta katalogów powstaje lazy — gdy realnie potrzebna (F6).
