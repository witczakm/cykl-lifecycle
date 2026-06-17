# Wkład w cykl-lifecycle

Dzięki, że chcesz pomóc. Najbardziej przydatne:

- **Raporty błędnych triggerów** — kiedy skill odpalił się, choć nie powinien (false positive), albo nie odpalił, choć powinien (false negative). Podaj: co wpisałeś, w jakim środowisku (Claude Code / Cowork / web / Codex) i co się stało.
- **Tłumaczenia** na inne języki (angielski, czeski, ukraiński…). Skille to pliki tekstowe — przetłumacz `SKILL.md` i triggery w `description`.
- **Doświadczenia z różnych środowisk** — zwłaszcza Codex (różne wersje) i Cowork.

## Zasady

- Jeden skill = jedno zadanie. Trzymaj `description` zwięzłe (Codex skraca opisy przy budżecie ~2%; ważne triggery i negatywy dawaj na początek).
- Każda zmiana treści dokumentu stanu = bump wersji + wiersz changelogu w tym samym ruchu.
- Skille **nie wykonują `git`** automatycznie — dają gotowy blok poleceń do wklejenia.
- `agents/openai.yaml` to metadane wyłącznie dla Codeksa; Claude je ignoruje. Nie wstawiaj tam logiki — logika żyje w `SKILL.md`.

## Testowanie skilli

Negatywne triggery testuj **pytaniami kontrolnymi**, nie rozkazami — w Codeksie (agent) prompt-rozkaz typu „zrób X" zostanie naprawdę wykonany. Trzymaj rozsądny tryb zatwierdzania i pracuj na jednorazowej, gitowanej kopii projektu.

## Przed PR

Przeczytaj [CHANGELOG.md](CHANGELOG.md), żeby zrozumieć ewolucję systemu (Faza 1 → Faza 2 → wsparcie Codeksa). Zgłaszając PR zgadzasz się na licencję [MIT](LICENSE).
