# Decyzje architektoniczne — cykl-lifecycle

**Wersja:** 2.6.0 · **Ostatnia aktualizacja:** 2026-08-04

Ten dokument tłumaczy **dlaczego** system wygląda tak, a nie inaczej. Każda decyzja ma precedens — awarię albo pomiar, który ją wymusił. Jeśli szukasz **jak używać**, idź do [PRZEWODNIK-KOMEND.md](PRZEWODNIK-KOMEND.md); jeśli szukasz **co się zmieniło**, do [CHANGELOG.md](../CHANGELOG.md).

---

## D1 — Stan żyje w plikach, nie w wątku

**Decyzja.** Pamięć projektu to `PROJECT_CONFIG.md`, `docs/HANDOFF.md`, `docs/ROADMAP.md`, `docs/LESSONS_CANON.md`. Czat jest warsztatem na jedną sesję.

**Dlaczego.** Model jest bezstanowy — przy każdej wiadomości dostaje całą rozmowę od nowa, więc koszt tury rośnie mniej więcej kwadratowo z długością wątku. Niezależnie od kosztu spada jakość: w długim kontekście model słabiej sięga po informacje ze środka i gubi się w szumie.

**Konsekwencja.** Nowa rozmowa na każdą sesję. `/start` na wejściu, `/zamknij` na wyjściu.

---

## D2 — Dwa typy pól: dziennikowe i stanowe

**Decyzja.** Pole **dziennikowe** (changelog, nagłówek dokumentu, bieżący sprint) jest przyrostowe. Pole **stanowe** (stan repo, następna otwarta decyzja, publiczny URL, hash wdrożonego artefaktu) ma jedną prawdziwą wartość i jest nadpisywane w całości po pomiarze, ze znacznikiem `[zmierzone RRRR-MM-DD HH:MM UTC]`.

**Precedens.** W projekcie prowadzonym tym zestawem pole opisujące stan repozytorium rosło przez sześć kolejnych sesji, aż osiągnęło **1369 znaków** i zawierało **trzy sprzeczne stany z trzech różnych dat**. Ostatnia sesja dopisała aktualny pomiar na końcu linii, nie usuwając dwóch poprzednich. Czytający — człowiek albo `/start` — brał wartość pierwszą, czyli najstarszą, i dostawał obraz sprzed pięciu dni. Najnowsza wartość **była w pliku**, tylko za dwiema nieaktualnymi.

**Konsekwencja.** Skille traktowały wszystkie pola jak dziennikowe. Od 2.5.0 rozróżniają je jawnie, a `/start` zgłasza jako drift każde pole niosące więcej niż jeden stan — nawet jeśli najnowsza wartość w nim jest.

**Wariant brzegowy.** Gdy w polu stanowym siedzi też trwała wiedza operacyjna (obejścia, ograniczenia narzędzi), rozszczep je na dwa: `REPO_STATE` (nadpisywane) i `REPO_NOTES` (przyrostowe). Wiedzy nie kasujemy — przenosimy.

---

## D3 — Pole opisujące ostatni commit jest o jeden commit do tyłu

**Decyzja.** Pole opisujące stan repozytorium oznaczamy dopiskiem `stan PRZED commitem tej sesji`.

**Dlaczego.** Wartość zapisujesz *wewnątrz* commitu, który ją utrwala, więc z definicji opisuje stan sprzed samej siebie. To nie jest błąd do naprawienia, tylko strukturalna właściwość — ale nieoznaczona wygląda jak błąd i zaprasza do „poprawiania".

---

## D4 — Numer sesji przy otwartej decyzji pochodzi z sesji bieżącej

**Decyzja.** Pole „następna decyzja" opatrujemy numerem **bieżącej** sesji. Jeśli decyzja przechodzi bez zmian, piszemy wprost „przeniesione bez zmian z sesji N".

**Precedens.** Commit obejmujący sesje 62 i 63 przepisał to pole z `[SESJA 61]` na `[SESJA 62]` — o jedną za mało. Pole nie zostało pominięte; zostało przepisane z tego, co sesja **zastała**, zamiast z tego, co sama ustaliła.

---

## D5 — Git tylko do odczytu, z zamkniętej białej listy

**Decyzja.** Skille wykonują wyłącznie: `git rev-parse --short HEAD`, `git rev-list --left-right --count <remote>...HEAD`, `git log --oneline -n`, `git show`, `git diff --stat HEAD`. Zakazane: **`git status`**, **`git add --dry-run`**, **`git stash`**.

**Precedens.** Sprawdzenie, czy zapis do repo przez most zdalny działa, wykonano komendą `git add --dry-run` — i tym samym wywołaniem założono `.git/index.lock`, którego most nie potrafi usunąć (`unable to unlink: Operation not permitted`). Diagnostyka wyprodukowała dokładnie tę awarię, którą diagnozowała. Zwykły `git status` robi to samo, bo odświeża indeks. Repozytorium było zablokowane cztery dni.

**Konsekwencja.** Na pytanie „czy git w ogóle pisze przez ten most" **nie ma bezpiecznej komendy**. Odpowiedź brzmi: sprawdzi to człowiek w swoim terminalu.

---

## D6 — Bramka jest składnią powłoki, nie komentarzem

**Decyzja.** Każdy warunek „zrób Y tylko gdy X" w bloku komend zapisujemy jako `set -euo pipefail` + `&&`. Nigdy jako adnotację `# dopiero gdy zielone`.

**Precedens.** Runbook z warunkiem wyrażonym komentarzem wypchnął zmiany mimo trzech nieprzechodzących testów — człowiek wkleił cały blok naraz, a komentarz nie zatrzymał `git push`. Klasa problemu powtórzyła się w innej sesji w wariancie potokowym: `npm run build | tail` zaraportowało sukces mimo błędu kompilacji, bo potok zwraca kod wyjścia ostatniego elementu.

**Konsekwencja.** `pipefail` jest obowiązkowe wszędzie, gdzie bramka zawiera potok. Do 2.5.0 blok pre-flight w `/zamknij` sam był tym antywzorcem — warunek „data = dziś? jeśli nie, NIE commituj" stał w komentarzu nad `git add`.

---

## D7 — `/start` mierzy stan poza dokumentami

**Decyzja.** `PROJECT_CONFIG` deklaruje `STATE_PROBE` — jedną komendę read-only mierzącą żywy stan. `/start` wykonuje ją **przed** porównaniem dokumentów między sobą. Maksymalnie trzy próby; brak odpowiedzi to `[DO SPRAWDZENIA]`, nigdy blokada wejścia w sesję.

**Precedens.** Drift-check porównywał wyłącznie dokumenty ze sobą: nagłówek z changelogiem, `PROJECT_CONFIG` z `HANDOFF`, Pozycję ze statusami kroków. W realnym projekcie `HANDOFF` i `ROADMAP` **zgodnie** twierdziły, że danego dnia nie było żadnej pracy — a system wdrożeniowy pokazywał pięć zmian i inny hash artefaktu. Drift-check przeszedłby czysto, bo wszystkie dokumenty powtarzały tę samą nieprawdę. **Spójność wewnętrzna to nie prawdziwość.**

**Dlaczego akurat tak, a nie „recon na starcie".** Rozważano wbudowanie w `/start` pełnego rozpoznania przed zadaniem. Odrzucone: rozpoznanie jest **per zadanie** i przed nieodwracalnym ruchem, `/start` jest **per sesja** i read-only. Na wejściu nie wiadomo jeszcze, jakie będzie zadanie, więc rozpoznanie nie ma czego zmierzyć — zmierzyłoby „coś ogólnego", czyli nic, a `/start` przestałby być tani i wyszedłby z użycia. Sonda bierze około jednej piątej kosztu tamtego pomysłu i naprawia defekt, który realnie wystąpił.

**Skill zostaje generyczny.** Nie wie nic o gicie, bazie ani buildzie — wykonuje to, co zadeklarował projekt. Osprzęt pomiarowy wnosi projekt, nie plugin.

---

## D8 — Bramka wyjścia etapu jest warunkiem, nie opisem

**Decyzja.** Etap przechodzi na `DONE` dopiero, gdy spełniona jest jego **Bramka wyjścia** z tabeli etapów i pokazano, czym została spełniona. Komplet kroków `DONE` to warunek konieczny, nie wystarczający.

**Dlaczego.** Kolumna „Bramka wyjścia" istniała w szablonie `ROADMAP` od wersji 2.0, ale **żaden skill jej nie czytał** — flip etapu opierał się wyłącznie na statusach kroków. Kolumna była dekoracją: opisywała warunek, którego nikt nie sprawdzał. To ta sama klasa co D6, tylko w dokumencie zamiast w powłoce.

---

## D9 — Reguły pomiaru

Rozpoznanie, które mierzy źle, jest **groźniejsze niż jego brak** — produkuje pewność, której nikt już nie weryfikuje. Cztery reguły wyprowadzone z udokumentowanych awarii:

| Reguła | Precedens |
|---|---|
| **Pomiar przeczy dokumentowi? Najpierw sprawdź, czy mierzysz właściwy obiekt** — ten, którego używa bieżący krok, nie ten o podobnej nazwie | zgłoszenie mówiło o tabeli ze 107 wierszami; ekran renderował funkcję zwracającą 9. Gdyby pomiar poszedł za nazwą z tekstu zgłoszenia, zakres prac trafiłby w wirtualizację listy, czyli w nic. Ta sama klasa błędu wystąpiła trzy razy w ciągu dwóch dni |
| **Ucięty odczyt nie jest dowodem nieobecności** — listing obcięty limitem mówi „nie widzę", nie „nie ma" | analiza po odczycie 65 plików raportowała jedną liczbę i **jawnie zgłosiła lukę** (48 plików nieprzeczytanych); pomiar na kompletnym artefakcie dał inną. Odczyt częściowy daje dolną granicę, nie sumę |
| **Pomiar ma datę ważności** — stąd godzina w znaczniku, nie sama data | „dziś zero zmian" zmierzone o 18:00 było nieprawdą o 21:00; praca zaczęła się 74 minuty po pomiarze. Wpis nie był kłamstwem w chwili zapisu, ale dokument mówił nieprawdę już następnego dnia |
| **Korekta twierdzenia musi dotknąć każdego jego powtórzenia** — po poprawce `grep` starego brzmienia = 0 poza changelogiem | te same fakty żyją w `HANDOFF`, `ROADMAP` i `PROJECT_CONFIG` naraz. Poprawka w jednym miejscu zostawia dwa źródła nieprawdy, które kolejne sesje czytają jako fakt |

---

## D10 — Automatyczny push: świadomie NIE

**Decyzja.** `/zamknij` nie wykonuje `git push` ani `git commit`. Kolejność wdrażania automatyzacji: najpierw bramka mechaniczna (D6), potem pomiar na wejściu (D7), a auto-push dopiero jako opcja włączana per projekt — i dopiero gdy dwa pierwsze przepracują kilka sesji.

**Dlaczego.**

1. **Automatyzacja nad zepsutą bramką mnoży błąd.** Dopóki warunek był komentarzem, auto-push gwarantowałby wypchnięcie stanu, który nie przeszedł sprawdzenia.
2. **`git add` i `git commit` też tworzą `.git/index.lock`** — ten sam mechanizm awarii, który wymusił zakaz z D5, tylko uruchamiany częściej.
3. **Push jest praktycznie nieodwracalny** w repozytorium publicznym. Koszt fałszywego pozytywu jest asymetryczny wobec zysku z wygody.
4. **Rozjazd z remote wymaga człowieka.** Auto-push zakłada fast-forward; przy rozjeździe trzeba rozstrzygać konflikt w dokumentach stanu bez nadzoru.

**Co realnie bolało i jak zostało rozwiązane bez pushowania.** Objaw brzmiał „praca niezacommitowana od kilku dni, nikt tego nie zauważył". Przyczyna nie leżała w braku automatyzacji, tylko w tym, że `/start` czytał wyłącznie pliki — a praca niezacommitowana wygląda w plikach identycznie jak zacommitowana. `STATE_PROBE` z D7 zamyka to bez jednego zapisu do repozytorium.

**Co odwróci tę decyzję.** Repozytorium prywatne, jednoosobowe, bez CI — wtedy koszt złego pusha spada na tyle, że domyślne włączenie staje się rozsądne.
