---
name: cykl-zamknij
description: Domknięcie sesji projektu wielosesyjnego — zbierz co się wydarzyło, zaktualizuj dokumenty stanu (w tym pozycję w roadmapie), złap lekcje i przygotuj commit. Użyj na końcu sesji gdy użytkownik pisze "/zamknij", "domknijmy sesję", "zamykamy wątek", "kończymy na dziś", "zapisz postęp i zakończ". Uruchom zanim użytkownik zamknie czat po realnej pracy. NIE używaj gdy "zamknij" dotyczy pliku, okna, nawiasu, połączenia, zasobu, issue lub PR w kodzie — skill domyka SESJĘ pracy, nie obiekt w programie.
---
<!-- cykl-lifecycle v2.3.0 -->

# /zamknij — domknięcie sesji

## Cel

Zostawić projekt w czystym stanie, z którego następna sesja wejdzie bez gubienia kontekstu:
dokumenty zgodne z rzeczywistością, pozycja w roadmapie aktualna, kod nadający się do podjęcia
pracy bez sprzątania po poprzedniku.

## Kiedy NIE uruchamiać

Pusta sesja (sama dyskusja, bez decyzji/zmian) — podsumuj słownie. Nie bumpuj wersji dokumentów
ani nie generuj commita dla niczego — to zaśmieca historię.

## Kroki

1. **Zbierz fakty z sesji** (notatki, jeszcze nie do plików):
   - Jakie decyzje zapadły, co zrobiono/zmergowano, co zweryfikowano.
   - Które kroki roadmapy się domknęły (kryterium: kolumna "Weryfikacja" spełniona — nie "wydaje się gotowe").
   - Jakie wnioski/lekcje. Jaki jest następny ruch i dlaczego.

2. **Zweryfikuj na żywym repo** (odczyt plików, nie git):
   - Data z systemu do nagłówków — nie kopiuj z pamięci ani z plików.
   - Co realnie jest w HANDOFF/ROADMAP/CONFIG.
   - Test idempotencji: data ostatniego wpisu changelogu HANDOFF = dziś? To poprawka po wcześniejszym /zamknij: edytuj istniejący wpis, bump tylko patch wersji.

3. **Zaktualizuj dokumenty stanu.** Przy KAŻDEJ edycji ciała dokumentu zsynchronizuj nagłówek
   (Wersja + Ostatnia aktualizacja) i dopisz wiersz changelogu w tym samym ruchu:
   - docs/HANDOFF.md — nadpisz snapshot: data · gdzie jesteśmy (1 zdanie) · ostatnio zamknięte · następny ruch + dlaczego.
   - docs/ROADMAP.md — zmień statusy domkniętych kroków (TYLKO status, nie usuwaj treści), przesuń Pozycję. Jeśli etap DONE: rozbij NASTĘPNY etap na kroki (dopiero teraz — F6) i ustaw Pozycję na jego pierwszy krok.
   - PROJECT_CONFIG.md — Current Sprint (status, branch, next decision, ryzyka) + CURRENT_MILESTONE/CURRENT_SPRINT = nowa Pozycja. Bump nagłówka (Wersja + data; CONFIG nie ma changelogu).

4. **Lekcje** — zastosuj logikę /lekcja (projektowa) lub /lekcja-g (globalna).
   Globalnej nigdy nie zapisuj sam — pokaż i zapytaj.

5. **Pokaż diff** — co zmieniłeś w których plikach.

6. **Przygotuj komendę commit** z wbudowanym pre-flightem:

   grep -n "Ostatnia aktualizacja" docs/HANDOFF.md docs/ROADMAP.md PROJECT_CONFIG.md
   # data = dziś? jeśli nie — pliki nie zeszły na dysk, NIE commituj
   git add docs/HANDOFF.md docs/ROADMAP.md PROJECT_CONFIG.md
   git commit -m "..."

   Nie wykonuj git — podaj komendy; użytkownik wykonuje je w terminalu (Claude Code lub Codex).

## Zasady

- Fałszywy stan gorszy niż brak. Nie wiesz? [DO UZUPEŁNIENIA], nie zgaduj.
- Krok DONE = weryfikacja spełniona. Nie flipuj statusu na wrażeniu.
- Nie deklaruj "zapisane na dysku". Pre-flight grep sprawdza to tam, gdzie jest prawda.
- Nie wykonuj git.

## Output (co użytkownik widzi)

1. Podsumowanie sesji (3-5 zdań) + nowa Pozycja (Etap X/N · krok Y/M).
2. Lista zaktualizowanych dokumentów z nowymi wersjami.
3. Lekcje zapisane / globalne do akceptacji.
4. Blok komend: pre-flight grep + git add/commit.

## Powiązane

- /migawka — lżejsza wersja (snapshot bez commita), do środka sesji.
- /start — następna sesja czyta to, co /zamknij zapisał.
- /lekcja, /lekcja-g — klasyfikacja i zapis wniosków.
