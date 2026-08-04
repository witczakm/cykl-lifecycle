# Wkład w cykl-lifecycle

Dzięki, że chcesz pomóc. Najbardziej przydatne:

- **Raporty błędnych triggerów** — kiedy skill odpalił się, choć nie powinien (false positive), albo nie odpalił, choć powinien (false negative). Podaj: co wpisałeś, w jakim środowisku (Claude Code / Cowork / web / Codex) i co się stało.
- **Tłumaczenia** na inne języki (angielski, czeski, ukraiński…). Skille to pliki tekstowe — przetłumacz `SKILL.md` i triggery w `description`.
- **Doświadczenia z różnych środowisk** — zwłaszcza Codex (różne wersje) i Cowork.

## Zasady

- Jeden skill = jedno zadanie. Trzymaj `description` zwięzłe (Codex skraca opisy przy budżecie ~2%; ważne triggery i negatywy dawaj na początek).
- **Skille mają zostać lekkie.** Przy każdej zmianie zmierz przyrost linii per plik i pokaż go w PR. Punkt odniesienia 2.6.0: 433 linie w siedmiu `SKILL.md`, najdłuższy ma 100. Dodawaj mechanizmy i reguły w jednym zdaniu, nie akapity uzasadniające — uzasadnienie idzie do CHANGELOG i do `docs/`.
- Każda zmiana treści dokumentu stanu = bump wersji + wiersz changelogu w tym samym ruchu.
- Skille **nie wykonują `git` mutującego** (`add`, `commit`, `push`, `stash`) — dają gotowy blok do wklejenia. Wykonują natomiast komendy **pomiarowe z białej listy** (`rev-parse`, `rev-list`, `log`, `show`, `diff --stat`). `git status`, `git add --dry-run` i `git stash` są zakazane w każdym skillu — jedynym dozwolonym wystąpieniem tych fraz jest zdanie ich zakazujące.
- **Warunek egzekwuj składnią, nie komentarzem.** Każde „zrób Y tylko gdy X" w bloku komend zapisuj jako `set -euo pipefail` + `&&`. Komentarz nie zatrzyma wklejonego bloku.
- `agents/openai.yaml` to metadane wyłącznie dla Codeksa; Claude je ignoruje. Nie wstawiaj tam logiki — logika żyje w `SKILL.md`. **Pilnuj, żeby `short_description` nie kłamało** o tym, co skill robi; to szóste miejsce, w którym żyje kontrakt „nie wykonuj git".

## Wydanie — bramki przed PR

Kontrakty w tym repo żyją w wielu plikach naraz. Zmiana jednego wystąpienia bez pozostałych to najczęstszy defekt tego projektu — dwa razy trafił do wydania.

| Sprawdzenie | Oczekiwane |
|---|---|
| `grep -rc "cykl-lifecycle vX.Y.Z" skills --include=SKILL.md \| grep -c ":1$"` | `7` |
| `grep -r "vSTARA" skills .claude-plugin .codex-plugin \| wc -l` | `0` |
| `grep -rn "Nie wykonuj git" skills --include=SKILL.md` | skille, które **mierzą**, mówią „git mutującego"; pozostałe pełny zakaz |
| `git diff -U0 <baza> -- skills \| grep -E "^[+-](name\|description):" \| wc -l` | `0` — frontmatter steruje wyzwalaniem, nie ruszamy |
| `diff -r <rozpakowany .plugin>/skills skills` | identyczne — **paczka to binarny duplikat `skills/`** |

Wersja żyje w pięciu miejscach: `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, marker w siedmiu `SKILL.md`, badge w `README.md`, nagłówek `docs/PRZEWODNIK-KOMEND.md` — plus manifest wewnątrz `cykl-lifecycle.plugin`.

Przebudowa paczki jest **obowiązkowa przy każdej zmianie w `skills/`** i sprowadza się do jednej komendy:

```bash
./build-plugin.sh
```

Skrypt składa paczkę ze źródeł (`packaging/plugin-README.md` → `README.md` w roocie paczki, `.claude-plugin/plugin.json`, całe `skills/`) i **weryfikuje wynik**: `unzip -t`, `diff -r` zawartości `skills/` wobec repo oraz jednolitość markera wersji. Kończy się błędem, jeśli cokolwiek się nie zgadza. Nie pakuj ręcznie — README paczki to inny plik niż README repozytorium i łatwo je pomylić.

## Testowanie skilli

Negatywne triggery testuj **pytaniami kontrolnymi**, nie rozkazami — w Codeksie (agent) prompt-rozkaz typu „zrób X" zostanie naprawdę wykonany. Trzymaj rozsądny tryb zatwierdzania i pracuj na jednorazowej, gitowanej kopii projektu.

## Przed PR

Przeczytaj [CHANGELOG.md](CHANGELOG.md), żeby zrozumieć ewolucję systemu (Faza 1 → Faza 2 → wsparcie Codeksa). Zgłaszając PR zgadzasz się na licencję [MIT](LICENSE).
