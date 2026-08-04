# PROJECT_CONFIG — {PROJECT_NAME}

**Wersja:** 1.0.0 · **Ostatnia aktualizacja:** {YYYY-MM-DD HH:MM CEST}
<!-- Plik parametrów: bump tylko tych dwóch pól przy edycji (/handoff, /zamknij). Bez changelogu. -->

## Identity
OWNER_NAME={owner}
PROJECT_NAME={pełna nazwa}
PROJECT_CODENAME={codename}
PROJECT_SLUG={slug}

## Paths
PROJECT_ROOT={ścieżka}

## Privacy
{granice prywatności — co NIGDY nie idzie do chmury, jeśli dotyczy}

## Assumptions (uzupełnij gdy nieznane na starcie)
{pola UNKNOWN z ownerem i terminem — zamiast zgadywać}

## State probe (czym mierzyć stan POZA dokumentami — czyta /start)
<!-- Jedna komenda read-only. Bez niej drift-check porównuje dokumenty wyłącznie ze sobą,
     a dokumenty zgodne ze sobą bywają zgodnie nieaktualne. Zakaz: git status, git add --dry-run, git stash. -->
STATE_PROBE={np. git rev-parse --short HEAD; git rev-list --left-right --count origin/main...HEAD}

## Current Sprint (live state)
<!-- CURRENT_MILESTONE/CURRENT_SPRINT = identyfikatory zgodne z Pozycją w docs/ROADMAP.md (etap/krok).
     Rozbicie i statusy żyją TYLKO w ROADMAP — tu same wskaźniki. Sync robi /zamknij i /handoff.
     Pola STANOWE (jedna prawdziwa wartość) NADPISUJ w całości po pomiarze i znakuj
     [zmierzone RRRR-MM-DD HH:MM UTC]. Pola dziennikowe są przyrostowe. -->
CURRENT_MILESTONE={etap z ROADMAP, np. Etap 2: nazwa}
CURRENT_SPRINT={krok z ROADMAP, np. 2.3: nazwa}
CURRENT_SPRINT_STATUS={...}
CURRENT_SPRINT_BRANCH={sama nazwa brancha — nic więcej}
REPO_STATE={STANOWE — wynik STATE_PROBE + [zmierzone …]; opisuje stan PRZED commitem tej sesji}
REPO_NOTES={przyrostowe — trwała wiedza o repo: obejścia, ograniczenia narzędzi. Tu wiedzy NIE kasujemy}
CURRENT_SPRINT_NEXT_DECISION={decyzja + numer BIEŻĄCEJ sesji; bez zmian → "przeniesione bez zmian z sesji N"}
CURRENT_SPRINT_OPEN_RISKS={...}

## Last Completed Sprint
LAST_SPRINT={...}

## Global lessons baseline (które GL-NNN obowiązują w tym projekcie)
<!-- Aktualizuje CCT po faktycznym zapisie GL-NNN (krok 4 /lekcja-g). /start porównuje przy wejściu. -->
GLOBAL_LESSONS_BASELINE={...}
