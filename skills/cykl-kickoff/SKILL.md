---
name: cykl-kickoff
description: Załóż nowy projekt wielosesyjny od zera — stwórz strukturę folderów, skopiuj template'y dokumentów stanu, przeprowadź wywiad założeń (w tym etapy roadmapy) i zostaw projekt gotowy do pierwszej sesji. Użyj gdy użytkownik pisze "/kickoff", "/zaloz", "załóż projekt", "nowy projekt wielosesyjny", "zacznij projekt od zera", "rozpocznij nowy projekt który będzie trwał wiele sesji". To komenda jednorazowa na projekt — w istniejącym projekcie użyj /start. NIE używaj gdy "nowy projekt" oznacza scaffold frameworka (npx create-react-app, cargo new, django-admin startproject) bez intencji wielosesyjnego prowadzenia — wtedy po prostu pomóż w kodzie.
---
<!-- cykl-lifecycle v2.3.0 -->

# /kickoff — założenie nowego projektu

## Cel

Każdy nowy projekt startuje z identycznej, sprawdzonej struktury. Zero ad-hoc. Powód: spójna
struktura od dnia pierwszego znaczy, że pozostałe skille (cykl-start, cykl-zamknij…) działają
od razu, a projekt jest "świadomy", do czego każdy element służy. Odpalasz to RAZ.

## Najpierw: czy to faktycznie nowy projekt?

Sprawdź katalog docelowy. Jeśli istnieją PROJECT_CONFIG.md lub docs/HANDOFF.md:
- adopt — dołóż tylko brakujące elementy (nie nadpisuj istniejących plików),
- abort — przerwij.

Nigdy nie nadpisuj istniejących dokumentów na ślepo.

## Kroki

1. **Wywiad założeń** (maks 5-7 pytań w jednej turze, reszta → UNKNOWN z ownerem):
   - Wymagane do założenia: nazwa, codename/slug, katalog docelowy.
   - Wymagane przed pracą: cel projektu (1-2 zdania), lista etapów projektu (3-7 haseł "co po kolei" — zasila ROADMAP poziom 1), granice prywatności.
   - Opcjonalne: repo git, licencja.
   - Pole nieznane → UNKNOWN z ownerem i terminem. Wywiad-przesłuchanie zostanie porzucony; lepiej UNKNOWN niż elegancka halucynacja (F4).

2. **Wybierz profil struktury** (patrz references/struktura-projektu.md):
   - lite — README + PROJECT_CONFIG + docs/{HANDOFF,ROADMAP,LESSONS_CANON}. Mały projekt/PoC.
   - standard — lite + plik instrukcji projektu (Claude: CLAUDE.md · Codex: AGENTS.md) + docs/{adr,specs,runbooks,reports} + skills/. Typowy projekt.
   - regulated — standard + _ai_ops/ + runtime/audit/ + AGENTS.md. Produkcja/audyt.
   Reszta katalogów powstaje lazy — gdy realnie potrzebna (F6).

3. **Stwórz katalogi** wg wybranego profilu.

4. **Skopiuj i wypełnij template'y** z assets/:
   - Podstaw {PROJECT_NAME}, {owner}, datę z systemu.
   - ROADMAP: wpisz etapy z wywiadu do tabeli poziomu 1 (z bramkami wyjścia), rozbij TYLKO etap 1 na kroki (poziom 2). Ustaw Pozycję na etap 1, krok 1.
   - LESSONS_CANON startuje z F1-F6 + pustą sekcją W. Projektowe F numeruj od F10.
   - README: przytnij tabelę i hierarchię do wybranego profilu — usuń wiersze nieistniejące w tym profilu.

5. **Pokaż użytkownikowi** strukturę + co trafiło do każdego pliku.

6. **Przygotuj komendę commit** "initial scaffold" (explicit ścieżki, nie -A). Nie wykonuj git.

7. **Pierwszy /start** — zreferuj: "projekt założony, Pozycja: etap 1/N · krok 1/M, następny ruch = ...".

## Zasady

- Nie nadpisuj istniejącego projektu. Krok "czy nowy" jest obowiązkowy.
- Data z systemu, nie z pamięci.
- Nie zgaduj — UNKNOWN z ownerem.
- Nie wykonuj git.

## Materiały skilla

- references/struktura-projektu.md — mapa struktury + hierarchia + profile.
- assets/*.template.md — 5 template'ów dokumentów.

## Powiązane

- /start — pierwsze wejście po kickoffie i każda kolejna sesja.
- /zamknij, /migawka, /lekcja, /lekcja-g, /roadmap — pętla prowadzenia.
