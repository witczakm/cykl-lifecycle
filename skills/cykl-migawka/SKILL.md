---
name: cykl-migawka
description: Lekki snapshot stanu w środku sesji projektu wielosesyjnego — nadpisz HANDOFF, odśwież PROJECT_CONFIG i status kroku w roadmapie po istotnej decyzji, bez lekcji i bez commita. Użyj gdy użytkownik pisze "/migawka", "/handoff", "zapisz stan", "zrób snapshot", "utrwal tę decyzję", albo gdy w trakcie długiej sesji domknął się krok roadmapy lub zapadła ważna decyzja. To nie jest koniec sesji (to /zamknij) — to migawka w trakcie. NIE używaj przy snapshotach testów (Jest/Vitest), maszyn wirtualnych, baz danych ani containerów — skill dotyczy wyłącznie dokumentów stanu projektu lifecycle.
---
<!-- cykl-lifecycle v2.7.0 -->

# /migawka — snapshot w środku sesji

## Cel

Utrwalić stan natychmiast po ważnej decyzji lub domknięciu kroku, zamiast czekać do końca sesji.
Roadmapa powinna być aktualna W TRAKCIE pracy, nie dopiero po niej — /migawka to mechanizm
bieżącej aktualizacji między /start a /zamknij.

## Kroki

1. **Sprawdź na żywym repo** aktualny stan HANDOFF + PROJECT_CONFIG + ROADMAP + datę z systemu.
   Jeśli migawka dotyka pola stanowego, a PROJECT_CONFIG ma `STATE_PROBE=` — wykonaj sondę zamiast
   przepisywać starą wartość.

2. **Zaktualizuj stan:**
   - docs/HANDOFF.md — NADPISZ sekcję "Snapshot" (data · gdzie jesteśmy · ostatnio zamknięte · następny ruch + dlaczego). Zawsze nadpisuj — snapshot opisuje stan "teraz". Ślad pośrednich decyzji zostaje w changelogu.
   - docs/ROADMAP.md — TYLKO jeśli decyzja domknęła krok lub zmieniła bieżący krok: flipnij status i przesuń Pozycję. Nie zmieniaj treści kroków ani sekwencji etapów — to robi /roadmap update na jawne polecenie.
   - PROJECT_CONFIG.md — Current Sprint, jeśli decyzja zmieniła live-state. **Pola stanowe NADPISUJ
     w całości** (tak jak Snapshot w HANDOFF) i opatrz znacznikiem `[zmierzone …]`. Historia idzie do
     changelogu, nie do wnętrza pola.

3. **Zsynchronizuj nagłówek + changelog** — przy każdym edytowanym dokumencie z changelogiem (HANDOFF, ROADMAP):
   bump Wersja + Ostatnia aktualizacja i dopisz wiersz changelogu w tym samym ruchu.
   CONFIG: bump tylko nagłówka (Wersja + data — bez changelogu).
   **Bramka spójności:** po edycji sprawdź, że data i wersja w nagłówku = te z ostatniego wiersza
   changelogu. Rozjazd = popraw teraz; to dwa osobne ruchy edycyjne i drugi bywa pominięty.

4. **Pokaż** krótko: co zmieniłeś + nowa Pozycja (jeśli się przesunęła).

## Zasady

- Tylko snapshot. Bez lekcji, bez komendy commit — to należy do /zamknij.
- Status kroku flipuj tylko przy spełnionej weryfikacji (kolumna "Weryfikacja" w ROADMAP). DONE bez dowodu = fałszywy postęp.
- Nie wykonuj git mutującego — `STATE_PROBE` musi być read-only. Commit zbiorczo przy /zamknij.

## Powiązane

- /zamknij — pełne domknięcie sesji (migawka + lekcje + commit).
- /start — czyta snapshot przy następnym wejściu.
