# cykl-lifecycle

**Wersja 2.8.2** · [pełna dokumentacja i changelog](https://github.com/witczakm/cykl-lifecycle)

Pamięć projektu dla agentów AI. 7 komend, które dają projektowi pamięć między sesjami — stan żyje w plikach (`HANDOFF`, `ROADMAP`, `LESSONS`), nie w przewijaniu czatu. Zamiast tłumaczyć kontekst od nowa, wpisujesz `/start` i w pół minuty wiesz, gdzie skończyłeś i co dalej.

## 7 komend

- `/kickoff` — raz, na start projektu (zakłada strukturę, pyta o etapy)
- `/start` — na początku każdej sesji (wczytuje stan: gdzie jesteś + jeden następny krok)
- `/zamknij` — na koniec sesji (zapisuje postęp, szykuje commit)
- `/migawka` — lekki zapis stanu po ważnej decyzji w środku sesji
- `/roadmap` — podgląd postępu (etapy + kroki)
- `/lekcja` — zapisz wniosek do tego projektu
- `/lekcja-g` — zapisz wniosek globalnie (za Twoją zgodą)

## Pierwsza sesja

Wpisz `/kickoff` i odpowiedz na kilka pytań (nazwa, cel, główne etapy, katalog projektu). Agent założy strukturę dokumentów i od razu powie, jaki jest pierwszy krok. Każdą kolejną sesję zaczynaj od `/start`, kończ przez `/zamknij`.

## Co nowego w 2.8.0

Wydanie zamienia **reguły, których nikt nie wykonywał, na skrypt, który je wykonuje**. Diagnoza na żywym projekcie po 2.7.0: próg 40 kB i „nadpisuj, nie dopisuj" stały w tekście, a HANDOFF urósł do 418 kB, PROJECT_CONFIG miał 23 nagłówki wersji, a drift był zgłaszany przez cztery kolejne sesje i nie naprawiany przez żadną.

| Zmiana | Dlaczego |
|---|---|
| **`scripts/porzadek.py`** (w `cykl-start`): `/start` uruchamia go z `--wykonaj` przy pierwszym poleceniu w sesji; `/zamknij`, `/migawka`, `/lekcja` używają go jako bramki. Przenosi historię do `docs/archive/`, zostawia jeden blok bieżący i 5 wierszy changelogu, wraca lekcje zabłąkane za changelog, drukuje tabelę PASS/FAIL. Nic nie kasuje, jest idempotentny. | Reguła bez egzekucji maszynowej gnije — sprawdzone na czterech sesjach. Skrypt na tym samym projekcie: HANDOFF 418 → 6,5 kB, CONFIG 49 → 8,7 kB w jednym przebiegu. |
| **Bramka commita w `/zamknij` zaczyna się od `porzadek.py`** (kod wyjścia 1 = STOP). | Dotąd bramka sprawdzała tylko datę; przepuszczała plik z 23 nagłówkami. |
| **`/lekcja` ma stałe miejsce wstawki** — koniec Części II, przed `## Changelog`. | 32 lekcje trafiły za changelog, gdzie `/start` ich nie czyta. |
| **Tryb orkiestratora w `/zamknij`.** | Skill zakładał człowieka wklejającego blok; w praktyce commituje prowadzący wielu wykonawców — bez bramki. |

Aktualizujesz ze starszej wersji? Pierwszy `/start` po instalacji sam uporządkuje dokumenty; przejrzyj `docs/archive/` i dodaj go do commita.

## Co nowego w 2.6.0

- **Bramka commita jest mechaniczna** — warunek egzekwuje składnia powłoki (`set -euo pipefail` + `&&`), nie komentarz. Wcześniej `git commit` wykonywał się mimo niespełnionego sprawdzenia, bo blok wkleja się w całości.
- **`/start` mierzy stan poza dokumentami** — nowe, opcjonalne pole `STATE_PROBE` w `PROJECT_CONFIG`. Drift-check porównywał dokumenty wyłącznie ze sobą, a trzy dokumenty potrafią zgodnie powtarzać tę samą nieprawdę.
- **Pola stanowe są nadpisywane po pomiarze**, nie dopisywane — inaczej pole niesie kilka sprzecznych stanów, a czytający bierze pierwszy, czyli najstarszy.
- **Bramka wyjścia etapu jest sprawdzana** przy flipie na DONE.
- **Biała lista komend gita**; zakaz `git status`, `git add --dry-run`, `git stash` — tworzą `.git/index.lock`, którego mosty zdalne nie usuwają.

Aktualizujesz ze starszej wersji? Nic nie musisz migrować — `STATE_PROBE` jest opcjonalne, a istniejące dokumenty stanu czytają się bez zmian.

## Ważna zasada

Nie prowadź całego projektu w jednym, gigantycznym wątku — to pali tokeny i obniża jakość. Nowa rozmowa na każdą sesję, a pamięć i tak zostaje w plikach.

---

Pełna dokumentacja, wersje dla Claude Code i Codex: https://github.com/witczakm/cykl-lifecycle
