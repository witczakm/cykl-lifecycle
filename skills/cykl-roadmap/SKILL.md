---
name: cykl-roadmap
description: Pokaż pozycję i sekwencję prac z ROADMAP projektu — na którym etapie projektu jesteśmy i w którym kroku tego etapu — opcjonalnie zaktualizuj na wyraźne polecenie. Użyj gdy użytkownik pisze "/roadmap", "co po kolei w projekcie", "pokaż plan projektu", "pokaż postęp", "na którym etapie jesteśmy", "jaka jest kolejność prac". Domyślnie tylko pokazuje (read-only). NIE używaj gdy mowa o roadmapie produktu klienta, firmy zewnętrznej lub ogólnej strategii biznesowej — skill czyta wyłącznie docs/ROADMAP.md bieżącego projektu lifecycle. NIE używaj gdy pytanie dotyczy kolejności kroków w konkretnym bieżącym zadaniu — ten skill czyta docs/ROADMAP.md projektu lifecycle, nie odpowiada na ogólne pytania "co robić dalej".
---
<!-- cykl-lifecycle v2.3.0 -->

# /roadmap — pozycja i sekwencja prac

## Cel

Pokazać dwie rzeczy naraz: gdzie jesteśmy w całym projekcie (etap X z N) i gdzie jesteśmy
w bieżącym etapie (krok Y z M). ROADMAP to jedyne źródło prawdy o kolejności i postępie.
Domyślnie read-only — przypadkowa zmiana roadmapy to drift.

## Kroki

1. **Jeśli to początek sesji** (nie było /start w tej rozmowie) — zaproponuj najpierw /start:
   sama roadmapa bez HANDOFF i CONFIG da niepełny obraz.

2. **Pokaż** zwięźle:
   - Linia Pozycja: Etap X/N "nazwa" · krok Y/M "nazwa".
   - Statusy kroków bieżącego etapu — co DONE, co IN_PROGRESS, co TODO.
   - Sekwencja pozostałych etapów (poziom 1) — jednym wierszem na etap.

3. **Aktualizuj TYLKO na wyraźne polecenie** ("/roadmap update <powód>" lub "zaktualizuj roadmap"):
   - Zmiana statusów / Pozycji / rozbicia etapu — według polecenia.
   - Treści etapów i kroków nie usuwaj i nie przeredagowuj przy zmianie statusu. Usunięty krok znika bezgłośnie — nikt nie zauważy braku. Zmiana zakresu wymaga powodu od użytkownika + wpisu w changelogu.
   - Następny etap rozbijaj na kroki dopiero gdy bieżący się domyka (F6). Rozbicie z wyprzedzeniem zdezaktualizuje się zanim do niego dojdziesz.
   - Zsynchronizuj nagłówek (Wersja + Ostatnia aktualizacja) + wiersz changelogu w tym samym ruchu.
   - Nie kopiuj tu live-state (commity/testy/daty) — to żyje w PROJECT_CONFIG.

## Zasady

- Read-only domyślnie. Mutuj tylko na jawne polecenie.
- Status — swobodnie (na polecenie); treść kroków — tylko świadomie. To dwie różne operacje o różnym ryzyku.
- ROADMAP nie powiela liczb z CONFIG.
- Nie wykonuj git.

## Powiązane

- /start — czyta ROADMAP (Pozycję) jako część wejścia w sesję.
- /migawka — flipuje status kroku w trakcie sesji.
- /zamknij — aktualizuje statusy, Pozycję i rozbicie następnego etapu.
