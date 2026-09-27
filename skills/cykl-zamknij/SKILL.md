---
name: cykl-zamknij
description: Domknięcie sesji projektu wielosesyjnego — zbierz co się wydarzyło, zaktualizuj dokumenty stanu (w tym pozycję w roadmapie), złap lekcje i przygotuj commit. Użyj na końcu sesji gdy użytkownik pisze "/zamknij", "domknijmy sesję", "zamykamy wątek", "kończymy na dziś", "zapisz postęp i zakończ". Uruchom zanim użytkownik zamknie czat po realnej pracy. NIE używaj gdy "zamknij" dotyczy pliku, okna, nawiasu, połączenia, zasobu, issue lub PR w kodzie — skill domyka SESJĘ pracy, nie obiekt w programie.
---
<!-- cykl-lifecycle v2.8.0 -->

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

2. **Zweryfikuj na żywym repo.** Odczyt plików + **wyłącznie te komendy gita**:
   `git rev-parse --short HEAD` · `git rev-list --left-right --count <remote>...HEAD` ·
   `git log --oneline -n` · `git show` · `git diff --stat HEAD`.
   **ZAKAZANE:** `git status`, `git add --dry-run`, `git stash` — tworzą `.git/index.lock`,
   którego mosty zdalne (Cowork/device bridge) nie potrafią usunąć, i blokują repo na kolejne dni.
   - Data z systemu do nagłówków — nie kopiuj z pamięci ani z plików.
   - Co realnie jest w HANDOFF/ROADMAP/CONFIG.
   - Test idempotencji: data ostatniego wpisu changelogu HANDOFF = dziś? To poprawka po wcześniejszym /zamknij: edytuj istniejący wpis, bump tylko patch wersji.
   - **Pomiar ma datę ważności.** „Dziś zero zmian" zmierzone o 18:00 bywa nieprawdą o 21:00 — zamknięcie
     dnia przed jego końcem to pomiar przedwczesny. Dlatego znacznik zawiera godzinę, nie samą datę.

3. **Zaktualizuj dokumenty stanu.** Przy KAŻDEJ edycji ciała dokumentu zsynchronizuj nagłówek
   (Wersja + Ostatnia aktualizacja) i dopisz wiersz changelogu w tym samym ruchu.

   **Pola dziennikowe vs stanowe.** Dziennikowe (changelog, nagłówek, sprint) są przyrostowe. Stanowe
   (stan repo, następna decyzja, URL, hash artefaktu) mają JEDNĄ wartość — **NADPISZ po pomiarze**;
   dopisanie obok starej daje pole ze sprzecznymi stanami, gdzie czytający bierze pierwszy = najstarszy.
   Siedzi tam też trwała wiedza (obejścia, ograniczenia)? **Rozszczep**: stan + notatki.

   **Bramka spójności — po KAŻDEJ edycji, zanim pójdziesz dalej.** Data i wersja w nagłówku = te
   z ostatniego wiersza changelogu. Rozjazd = STOP, popraw teraz. Nagłówek i treść to dwa osobne
   ruchy edycyjne; sprawdzenie kosztuje dwa odczyty, więc rób je przy zapisie, nie zostawiaj `/start`.

   **Porządek i próg rozmiaru robi skrypt.** Po edycjach uruchom
   `python3 <katalog skilla cykl-start>/scripts/porzadek.py --wykonaj <katalog projektu>` (leży obok
   `/start`, skille są sąsiadami). Przenosi historię do `docs/archive/`, zostawia 5 wierszy changelogu
   i drukuje tabelę. FAIL rozmiaru po skrypcie = proza w jednej sekcji (skrypt ją wskazuje) — przenieś
   ją do archiwum ręcznie, ZANIM przejdziesz dalej. Dokumentu, którego nie przeglądasz w całości,
   nie da się aktualizować kompletnie — to źródło driftu, nie objaw.

   - docs/HANDOFF.md — nadpisz snapshot: data · gdzie jesteśmy (1 zdanie) · ostatnio zamknięte · następny ruch + dlaczego.
   - docs/ROADMAP.md — zmień statusy domkniętych kroków (TYLKO status, nie usuwaj treści), przesuń Pozycję. Etap flipuj na DONE **tylko przy spełnionej Bramce wyjścia** — pokaż, czym została spełniona; komplet kroków DONE to warunek konieczny, nie wystarczający. Dopiero wtedy rozbij NASTĘPNY etap na kroki (F6) i ustaw Pozycję na jego pierwszy krok.
   - PROJECT_CONFIG.md — Current Sprint (status, następna decyzja, ryzyka) + CURRENT_MILESTONE/CURRENT_SPRINT = nowa Pozycja. Bump nagłówka (Wersja + data; CONFIG nie ma changelogu).
     Pole stanowe kończ znacznikiem `[zmierzone RRRR-MM-DD HH:MM UTC]`. Pole mierzone przez `STATE_PROBE`
     zastąp **odwołaniem** (`<mierzone przez STATE_PROBE>`), nie kopią: wartość zapisana wewnątrz commitu
     opisuje stan sprzed samej siebie, odwołanie mierzy się przy odczycie.
     „Następna decyzja" = numer **bieżącej** sesji; bez zmian → „przeniesione bez zmian z sesji N".

4. **Lekcje** — zastosuj logikę /lekcja (projektowa) lub /lekcja-g (globalna).
   Globalnej nigdy nie zapisuj sam — pokaż i zapytaj.

5. **Pokaż diff** — co zmieniłeś w których plikach.

6. **Przygotuj komendę commit z bramką MECHANICZNĄ.** Warunek egzekwuje składnia powłoki, nigdy komentarz —
   człowiek wkleja cały blok naraz, więc `# nie commituj, jeśli…` nie zatrzyma niczego.

   set -euo pipefail
   python3 <katalog skilla cykl-start>/scripts/porzadek.py . \
     && grep -n "Ostatnia aktualizacja" docs/HANDOFF.md docs/ROADMAP.md PROJECT_CONFIG.md \
     | grep -q "$(date +%Y-%m-%d)" \
     && git add docs/HANDOFF.md docs/ROADMAP.md PROJECT_CONFIG.md docs/LESSONS_CANON.md docs/archive/ \
     && git commit -m "..."

   Pierwszy człon to bramka porządku (kod wyjścia 1 = FAIL w tabeli): jeden nagłówek wersji, jeden blok
   bieżący na sekcję, changelog ≤ 5 wierszy, rozmiar ≤ 40 kB, data nagłówka = 1. wiersz changelogu.

   `pipefail` jest obowiązkowe: `cmd | tail` zwraca kod wyjścia `tail`, nie `cmd`, więc bramka
   przepuściłaby błąd. Pomiar stanu repo zrób w kroku 2 i wpisz do pola PRZED tym blokiem.
   Nie wykonuj git mutującego — blok podaj; wykonuje go użytkownik w terminalu.
   **Tryb orkiestratora:** jeśli reguły projektu jawnie dają Ci mandat do commitowania dokumentów stanu
   (prowadzący wielu wykonawców), wykonaj DOKŁADNIE ten blok, nie jego skróconą wersję — bramka
   obowiązuje tak samo, a przy równoległych sesjach dodaj tylko własne linie (`git add -p` / `hash-object`),
   nigdy cały plik z cudzymi zmianami.

## Zasady

- Fałszywy stan gorszy niż brak. Nie wiesz? [DO UZUPEŁNIENIA], nie zgaduj.
- Krok DONE = weryfikacja spełniona. Nie flipuj statusu na wrażeniu.
- Nie deklaruj "zapisane na dysku". Bramka z kroku 6 sprawdza to tam, gdzie jest prawda.
- Pole stanowe bez pomiaru = `[DO SPRAWDZENIA]`, **nigdy** stara wartość przepisana z pliku.
- Nie dopisuj do pola stanowego. Jeśli ma już kilka wartości z różnych dat — to jest drift do naprawy
  w tym samym ruchu, nie tło, na którym dokładasz kolejną.
- **Fakt ma JEDNO miejsce.** Ta sama wartość w dwóch dokumentach = drugi ma zawierać odwołanie, nie kopię.
  Kopii nie da się pilnować tanio — koszt rośnie z każdą kopią i z każdą sesją.
- Korekta twierdzenia musi dotknąć KAŻDEGO jego powtórzenia — dopóki kopie istnieją.
  Po poprawce `grep` starego brzmienia = 0 wystąpień poza changelogiem.
- Nie wykonuj git mutującego (add/commit/push/stash) — komendy pomiarowe z białej listy w kroku 2
  wykonujesz sam.

## Output (co użytkownik widzi)

1. Podsumowanie sesji (3-5 zdań) + nowa Pozycja (Etap X/N · krok Y/M).
2. Lista zaktualizowanych dokumentów z nowymi wersjami.
3. Lekcje zapisane / globalne do akceptacji.
4. Blok komend: bramka mechaniczna + git add/commit.

## Powiązane

- /migawka — lżejsza wersja (snapshot bez commita), do środka sesji.
- /start — następna sesja czyta to, co /zamknij zapisał.
- /lekcja, /lekcja-g — klasyfikacja i zapis wniosków.
