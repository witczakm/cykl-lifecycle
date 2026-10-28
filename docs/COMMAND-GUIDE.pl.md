# Przewodnik po komendach — cykl-lifecycle 3.1
[English](COMMAND-GUIDE.md) · **Polski**

**Dla kogo:** dla każdego, kto prowadzi projekt z cykl-lifecycle przez wiele sesji z AI.
Ty wpisujesz komendy; skrypt, który za nimi stoi, uruchamia agent.

## Idea w jednym akapicie

Projekt trwający wiele sesji ma jeden główny problem: każda nowa rozmowa zaczyna się bez pamięci
o poprzednich. cykl-lifecycle rozwiązuje to pętlą: **start → praca → zapis → zamknięcie → start
następnym razem**. To, co agent musi pamiętać, mieszka w kilku małych plikach w Twoim projekcie
— to *stan projektu*:

| Plik | Co zawiera |
|---|---|
| `docs/NOW.md` | gdzie jest projekt, otwarte prace i jeden następny krok (maks. 4 KB) |
| `docs/DECISIONS.md` | *indeks decyzji*: jedna linia na decyzję albo lekcję, ze stałym identyfikatorem |
| `PROJECT_CONFIG.md` | kilka ustawień, np. `TASKS=local` albo `TASKS=github` |
| `docs/ROADMAP.md`, `docs/issues/` | zadania — tylko w edycji Lokalnej |

Te pliki zapisuje wyłącznie skrypt `cykl-start/scripts/lifecycle.py`. Każdy zapis zwraca
**kartę punktu kontrolnego** (identyfikator i hash). Nie ma karty = nic nie zapisano, niezależnie
od tego, co mówi rozmowa.

## Pętla

```
Pierwsza sesja:
  /kickoff  ->  kilka pytań, pierwszy zapis, potem /start

Każda kolejna sesja:
  /start  ->  praca  ->  (opcjonalnie: /migawka, /lekcja po drodze)  ->  /zamknij

Sprawdzenie postępu:          /roadmap
Zapamiętanie wniosku:         /lekcja (ten projekt) albo /lekcja-g (wszystkie projekty)
Edycja wieloagentowa:         /prowadz
```

Angielskie nazwy działają tak samo: `/snapshot` = `/migawka`, `/close` = `/zamknij`,
`/lesson` = `/lekcja`, `/lesson-global` = `/lekcja-g`, `/lead` = `/prowadz`. W Codeksie skille
wołasz jako `$cykl-start`, `$cykl-kickoff` itd.

## Identyfikatory, które zobaczysz

| Przedrostek | Znaczenie |
|---|---|
| `O-…` | zobowiązanie: coś, co wciąż jest do zrobienia (obietnica, oczekująca zgoda) |
| `A-…` | próba: praca w toku |
| `D-…` | decyzja |
| `L-…` | lekcja |
| `T-…` | zadanie (edycja Lokalna) |

Otwarte identyfikatory nigdy nie znikają po cichu. Zamknięcie wymaga identyfikatora i powodu.

---

## /kickoff — założenie projektu

**Kiedy:** raz, na samym początku projektu.

**Co robi:**
1. Sprawdza, czy projekt ma już pliki stanu. Jeśli ma pliki z v2, zatrzymuje się i kieruje do
   migracji ([MIGRATION-v2.md](MIGRATION-v2.md), po angielsku); nigdy ich nie nadpisuje.
2. Pyta o cel, repozytorium, gałąź i pierwszy następny krok.
3. Pyta, gdzie mają być zadania: **github** (domyślnie) albo **local** (bez GitHuba).
4. Zapisuje pierwszy stan (`checkpoint --expected absent`) i pokazuje kartę punktu kontrolnego.
5. Instaluje hook pre-commit; w projektach na GitHubie także kontrolę `lifecycle-integrity`
   (zobacz [Ochrona scalania](MERGE-PROTECTION.pl.md)).

Nie zakłada zgłoszeń, kamieni milowych ani wydań na GitHubie.

## /start — wejście w sesję

**Kiedy:** na początku każdej sesji, jako pierwsza komenda.

**Co robi:** uruchamia `lifecycle.py context`, który sprawdza stan i zwraca krótkie podsumowanie
z limitem rozmiaru. Agent raportuje:
- bieżącą pozycję i jeden następny krok,
- otwarte identyfikatory (zobowiązania, próby),
- czy coś jest nieaktualne albo czy pracujesz offline.

Jeśli sprawdzenie się nie powiedzie, sesja na tym się zatrzymuje: agent nie wraca do starej
pamięci rozmowy ani do ręcznego czytania plików. Przykład:

```
Pozycja: etap API, endpoint logowania w toku (A-login).
Następny krok: dokończyć /auth/login i uruchomić jego testy.
Otwarte: O-review-auth (czeka na recenzję). Offline: nie.
```

## /migawka (/snapshot, /handoff) — zapis w trakcie sesji

**Kiedy:** po ważnej decyzji albo domkniętym kroku, gdy nie chcesz czekać do końca sesji.

**Co robi:** zapisuje nowy punkt kontrolny z pozycją, następnym krokiem, otwartą pracą i ryzykami,
podając hash bieżącego stanu (dzięki temu dwa zapisy nie nadpiszą się nawzajem). Zwraca kartę
punktu kontrolnego. Nigdy nie robi commita w gicie.

## /zamknij (/close) — koniec sesji

**Kiedy:** na końcu każdej sesji, w której była realna praca, i zanim długa rozmowa zostanie
skompaktowana.

**Co robi:**
1. Zbiera sprawdzone wyniki, to, co zostaje otwarte, zgody, nieudane podejścia i jeden następny krok.
2. Zapisuje punkt kontrolny, potem uruchamia `check`.
3. Pokazuje kartę punktu kontrolnego. Dopiero ona pozwala powiedzieć „sesja zapisana”.

Commit albo publikację robi tylko wtedy, gdy osobno o to poprosisz.

## /roadmap — przegląd postępu

**Kiedy:** chcesz zobaczyć zadania i wydania „z lotu ptaka”.

**Co robi:** pokazuje bieżący kamień milowy, identyfikatory zadań, następny krok i to, jak świeży
jest ten widok.
- Edycja Lokalna: linie w `docs/ROADMAP.md` (`- T-1 open Tytuł`) są listą zadań.
- Edycja GitHub: prawdą są zgłoszenia i kamienie milowe GitHuba; lokalny ROADMAP to tylko podgląd.

`/roadmap update …` zmienia go wyłącznie na Twoją prośbę i tylko przy sprawdzonym uprawnieniu;
offline zmiana jest zapisywana jako oczekująca pozycja `O-…`.

## /lekcja (/lesson) — zapis lekcji projektu

**Kiedy:** coś poszło źle (albo dobrze) i nie chcesz tego powtarzać w tym projekcie.

**Co robi:** dopisuje jeden wiersz do indeksu decyzji: regułę, precedens, który jej nauczył,
i test operacyjny. Przykład:

```
/lekcja
Straciłem godzinę, bo przed testami integracyjnymi Redis nie był uruchomiony.
```

zamienia się w wiersz w rodzaju `L-redis-przed-testami lesson accepted: Sprawdź, czy Redis działa,
przed testami integracyjnymi; precedens: stracona 1 h; test: docker ps | grep redis przed npm test`.
Identyfikatorów nigdy nie używa się ponownie.

## /lekcja-g (/lesson-global) — propozycja lekcji dla wszystkich projektów

**Kiedy:** wniosek jest na tyle ogólny, że przyda się w każdym projekcie.

**Co robi:** zapisuje go w tym projekcie jako lekcję **proponowaną** i trzyma zobowiązanie `O-…`,
dopóki jej nie zatwierdzisz. Sam nigdy nie zmienia instrukcji innego projektu ani Twoich
instrukcji globalnych: dostajesz zatwierdzony tekst do wstawienia tam, gdzie należy.

## /prowadz (/lead) — prowadzenie projektu wieloagentowego

**Edycja:** tylko GitHub + wielu agentów (`install.sh … --edition multi`).

**Co robi:** jeden wątek prowadzący planuje i decyduje; inni agenci albo modele implementują,
testują i recenzują. Prowadzący pisze samodzielne briefy, czyta raporty `=== SHORT ===` (najwyżej
8 linii), zapisuje decyzje Właściciela z jego dosłownymi słowami i przekazuje pracę kolejnemu
wątkowi prowadzącemu przez `docs/lead/THREADS.md`. Po trzech rundach poprawek bez postępu
zatrzymuje się i prosi o świeże spojrzenie na sam krok. Szczegóły: sekcja o edycji wieloagentowej
w [README](../README.pl.md).

---

## Reguły, które warto znać

1. **Jeden następny krok.** `/start` zawsze podaje dokładnie jeden następny krok.
2. **Zapisane znaczy: jest karta.** Fakt jest zapisany dopiero wtedy, gdy skrypt zwróci kartę punktu kontrolnego.
3. **„Zrobione” wymaga dowodu.** Zadanie jest zrobione, gdy spełniony jest jego warunek (test przeszedł,
   plik istnieje), a nie gdy „wydaje się działać”.
4. **Nie musisz nic pamiętać między sesjami.** O to chodzi: `/zamknij` i zapominasz do `/start`.
5. **Agent nigdy nie edytuje plików stanu bezpośrednio.** Wszystkie zapisy idą przez skrypt.

## Pytania

**Czy muszę wpisywać /start?** To najpewniejszy sposób. Skill może też zadziałać, gdy powiesz
„gdzie skończyliśmy?”.

**A jeśli ostatnio pominąłem /zamknij?** `/start` i tak ruszy od ostatniego zapisanego punktu
kontrolnego; wszystko, czego od tamtej pory nie zapisano, przepada. W długich sesjach używaj `/migawka`.

**Czy potrzebny jest internet?** Nie. Skrypt wymaga tylko Pythona 3.9+. Przy `TASKS=github` praca
offline ogranicza się do zadań już przydzielonych.

**Używałem v2.** Wersja 3 nie jest zgodna wstecz; postępuj według [MIGRATION-v2.md](MIGRATION-v2.md).
Wersja tego przewodnika dla v2 jest w historii gita (tag `v2.8.2`, plik `docs/PRZEWODNIK-KOMEND.md`).
