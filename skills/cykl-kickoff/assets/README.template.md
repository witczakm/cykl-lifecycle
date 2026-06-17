# {PROJECT_NAME}

{1-2 zdania: czym jest projekt i po co.}

## Jak prowadzimy ten projekt (świadomość struktury)

Projekt jest prowadzony wielosesyjnie zestawem skilli lifecycle. Każdy element ma swoje miejsce:
<!-- /kickoff: usuń z tabeli i z hierarchii pozycje nieistniejące w wybranym profilu (lite: bez CLAUDE.md, adr, specs). -->

| Dokument | Do czego | Kiedy aktualizowany |
|---|---|---|
| `PROJECT_CONFIG.md` | parametry + live-state sprintu (twarde liczby) | `/zamknij`, `/handoff` |
| `docs/HANDOFF.md` | snapshot „gdzie jesteśmy + następny ruch" (cienki) | `/handoff`, `/zamknij` |
| `docs/ROADMAP.md` | sekwencja prac „co po kolei" (SSOT kolejności) | `/roadmap`, `/zamknij` |
| `docs/LESSONS_CANON.md` | kanon lekcji (F fundamentalne + W wykonawcze) | `/lekcja` |
| `docs/adr/` | wiążące decyzje architektoniczne (1 plik = 1 decyzja) | przy decyzji |
| `docs/specs/` | specyfikacje i plany sprintów | przy sprincie |

**Hierarchia źródeł prawdy** (kto wygrywa konflikt): `CLAUDE.md` → `PROJECT_CONFIG.md` → `docs/adr/` →
`docs/specs/` → `docs/runbooks/` → kod (pozycje istniejące w tym profilu). Pamięć AI nie jest źródłem
prawdy — trzyma tylko wskaźniki. Konflikt HANDOFF↔ROADMAP = drift do zgłoszenia, nie do cichego
rozstrzygnięcia (doraźnie: HANDOFF rozstrzyga „następny ruch", ROADMAP — kolejność i pozycję).

## Pętla sesji

```
/start  →  praca (+/handoff +/lekcja gdy trzeba)  →  /zamknij
```

Pełna mapa struktury i lekcje fundamentalne: patrz `docs/LESSONS_CANON.md` (F1-F6).

## Status

{aktualny etap — patrz ROADMAP + PROJECT_CONFIG}
