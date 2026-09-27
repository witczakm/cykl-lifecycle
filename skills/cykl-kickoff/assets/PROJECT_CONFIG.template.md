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
     [zmierzone RRRR-MM-DD HH:MM UTC]. Pola dziennikowe są przyrostowe.
     FAKT MA JEDNO MIEJSCE: jeśli wartość żyje już w innym dokumencie (wersja planu, budżet,
     zakres etapu), wpisz tu ODWOŁANIE do tamtego pliku, nigdy kopię. Kopie się rozjeżdżają. -->
CURRENT_MILESTONE={etap z ROADMAP — sam identyfikator, np. "Etap 2: nazwa". Bez wersji planu i budżetu}
CURRENT_SPRINT={krok z ROADMAP, np. 2.3: nazwa}
CURRENT_SPRINT_STATUS={...} [zmierzone {YYYY-MM-DD HH:MM}]
CURRENT_SPRINT_BRANCH={sama nazwa brancha — nic więcej} [zmierzone {YYYY-MM-DD HH:MM}]
REPO_STATE=<mierzone przez STATE_PROBE — NIE kopiuj tu wartości; kopia zapisana wewnątrz commitu opisuje stan sprzed samej siebie>
REPO_NOTES={przyrostowe — trwała wiedza o repo: obejścia, ograniczenia narzędzi. Tu wiedzy NIE kasujemy}
CURRENT_SPRINT_NEXT_DECISION={decyzja + numer BIEŻĄCEJ sesji; bez zmian → "przeniesione bez zmian z sesji N"} [zmierzone {YYYY-MM-DD HH:MM}]
CURRENT_SPRINT_OPEN_RISKS={...} [zmierzone {YYYY-MM-DD HH:MM}]

## Last Completed Sprint
LAST_SPRINT={...}

## Global lessons baseline (które GL-NNN obowiązują w tym projekcie)
<!-- Aktualizuje CCT po faktycznym zapisie GL-NNN (krok 4 /lekcja-g). /start porównuje przy wejściu. -->
GLOBAL_LESSONS_BASELINE={...}
