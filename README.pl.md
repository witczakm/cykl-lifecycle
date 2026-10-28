# cykl-lifecycle 3.1.0
[English](README.md) · **Polski**

**Pamięć projektu dla agentów AI.** Agent AI zapomina wszystko, gdy kończy się rozmowa.
cykl-lifecycle daje mu krótką, wiarygodną pamięć, która mieszka w folderze projektu:
każdą sesję zaczynasz od `/start` („gdzie jesteśmy, co dalej?”), a kończysz `/close`
(„zapisz, gdzie skończyliśmy”). Następna sesja, w dowolnej rozmowie, rusza od tego miejsca.

**Dla kogo:** dla każdego, kto prowadzi projekt z Claude Code, Claude Cowork albo OpenAI Codex
przez wiele sesji — od jednoosobowego projektu po agenta-prowadzącego, który koordynuje kilka
modeli. Nie musisz czytać kodu; agent uruchamia go za Ciebie.

**Wypróbuj w minutę** (potrzebny Python 3.9+):

```sh
curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash -s -- claude
```

Zrestartuj agenta, otwórz projekt i wpisz `/kickoff`. Od tej pory: `/start` na początek pracy,
`/close` na koniec.

**Dlaczego można temu ufać.** *Stan projektu* (kilka małych plików mówiących, gdzie projekt
jest, co jest otwarte i jaki jest jeden następny krok) zapisuje wyłącznie jeden prosty skrypt
w Pythonie — nigdy ręcznie ani bezpośrednio agent. Każdy odczyt ma limit rozmiaru, więc start
sesji jest szybki i tani. Zapis liczy się dopiero wtedy, gdy skrypt zwróci potwierdzenie
(identyfikator i hash punktu kontrolnego).

Dokumentacja: [Przewodnik po komendach](docs/COMMAND-GUIDE.pl.md) ·
[Instalacja w Claude](docs/INSTALL-claude.pl.md) · [Instalacja w Codex](docs/INSTALL-codex.pl.md) ·
[Ochrona scalania](docs/MERGE-PROTECTION.pl.md) ·
[Dlaczego tak to zbudowano (v2)](docs/ARCHITECTURE-DECISIONS.pl.md)

## Wybierz edycję

Wszystkie edycje to ta sama paczka. Edycję wybierasz dla każdego projektu przy `/kickoff`
(jedna linia konfiguracji), a pracę wieloagentową — instalując jeden dodatkowy skill.

| | Lokalna | GitHub | GitHub + wielu agentów |
|---|---|---|---|
| Dla kogo | jedna osoba, jeden agent, bez GitHuba | projekty prowadzone w zgłoszeniach (issues) GitHuba | jeden agent-prowadzący koordynuje kilku agentów/modeli wykonawczych |
| Wymaga | Python 3.9+ | Python 3.9+, repozytorium na GitHubie | jak GitHub, plus dostęp do modeli wykonawczych, którym zlecasz pracę |
| Gdzie są zadania | `docs/ROADMAP.md` + `docs/issues/` | zgłoszenia i kamienie milowe GitHuba | zgłoszenia i kamienie milowe GitHuba |
| Stan sesji | `docs/NOW.md`, `docs/DECISIONS.md` | to samo | to samo + `docs/lead/` (rejestr wątków, dziennik, routing) |
| Komendy | 7 podstawowych | 7 podstawowych | 7 podstawowych + `/lead` |
| Działa offline | wszystko | wszystko poza nowymi przydziałami i odbiorem prac | jak GitHub |
| Ochrona scalania | lokalny hook pre-commit | hook + wymagana kontrola CI | hook + wymagana kontrola CI |

- **Lokalna** — gdy projekt nie ma repozytorium na GitHubie albo musi zostać na jednym komputerze.
- **GitHub** — gdy zgłoszenia i wydania już żyją na GitHubie; to zachowanie z wersji 3.0.x.
- **Wielu agentów** — gdy jeden wątek ma planować i decydować, a inne modele implementować,
  testować i recenzować.

Projekt możesz później przenieść z edycji Lokalnej do GitHub: zmieniasz jedną linię konfiguracji
i zakładasz zgłoszenia; nic więcej się nie zmienia. Prowadzący wieloagentowy działa też na
edycji Lokalnej.

## Instalacja

Skille instaluje się razem; pozostałe skille wywołują `cykl-start/scripts/lifecycle.py`.
Ponowne uruchomienie instalatora podmienia wszystkie skille `cykl-*`, więc wersje się nie mieszają.

```sh
# Edycje Lokalna i GitHub (7 podstawowych skilli)
curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash -s -- claude

# Edycja GitHub + wielu agentów (7 podstawowych skilli + cykl-prowadzacy)
curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash -s -- claude --edition multi

# Offline: rozpakuj pobrany wcześniej ZIP ze skillami (zawiera wszystkie 8;
# usuń potem cykl-prowadzacy, jeśli chcesz edycję z 7 skillami)
unzip cykl-lifecycle-skills.zip -d ~/.claude/skills/      # Codex: ~/.agents/skills/
```

Dla OpenAI Codex użyj `codex` albo `both` zamiast `claude`. Claude Cowork: przeciągnij
`cykl-lifecycle.plugin` do rozmowy. Po instalacji zrestartuj agenta.

Potem w projekcie: `/kickoff` i na pytanie, gdzie mają być zadania, odpowiedz „local” albo „github”.
Szczegóły: [Claude](docs/INSTALL-claude.pl.md), [Codex](docs/INSTALL-codex.pl.md).

## Pętla sesji

```
/kickoff (raz) -> /start -> praca -> /snapshot (opcjonalnie) -> /close -> następna sesja /start
```

`/close` kończy się sukcesem tylko wtedy, gdy skrypt zwróci kartę punktu kontrolnego (UUID + hash).
Dowodem zapisu stanu jest ta karta, nie rozmowa.

## Komendy

Nazwy kanoniczne to `cykl-*`; aliasy są podane w opisach skilli i nie tworzą duplikatów.
Polskie nazwy (`/zamknij`, `/migawka`, `/lekcja`, `/lekcja-g`, `/prowadz`) działają tak samo jak angielskie.

| Skill | Komenda | Do czego |
|---|---|---|
| cykl-kickoff | /kickoff | Założenie nowego projektu i wybór edycji |
| cykl-start | /start | Sprawdzenie stanu, raport pozycji i następnego kroku |
| cykl-migawka | /snapshot, /handoff (/migawka) | Zapis punktu kontrolnego w trakcie pracy |
| cykl-zamknij | /close (/zamknij) | Zapis przed zamknięciem sesji albo kompakcją |
| cykl-roadmap | /roadmap | Pozycja zadań i wydań |
| cykl-lekcja | /lesson (/lekcja) | Zapis lekcji projektu wraz z dowodem |
| cykl-lekcja-globalna | /lesson-global (/lekcja-g) | Propozycja lekcji dla wszystkich projektów |
| cykl-prowadzacy | /lead (/prowadz) | Tylko edycja wieloagentowa: protokół wątku prowadzącego |

Opis każdej komendy z przykładami: [przewodnik po komendach](docs/COMMAND-GUIDE.pl.md).

## Edycje w szczegółach

**Lokalna.** `PROJECT_CONFIG.md` zawiera `TASKS=local`. `docs/ROADMAP.md` to spis zadań
(`- T-12 open Tytuł`; statusy open, doing, done, dropped), każde otwarte lub trwające zadanie
ma plik `docs/issues/T-12.md`, a `check` sprawdza oba. Wydania zapisuje się w `CHANGELOG.md`
i tagach gita. Żaden serwer niczego nie wymusza; jedyną ochroną jest hook pre-commit.
Limit 4 KB dla ROADMAP mieści mniej więcej 60–80 linii zadań; usuwaj linie done i dropped
(historia zostaje w gicie) albo przejdź na edycję GitHub.

**GitHub.** `TASKS=github` albo brak linii `TASKS` (domyślne zachowanie 3.0.x). Zakresem,
przydziałem i odbiorem zadań rządzą zgłoszenia GitHuba; wydaniami — kamienie milowe i Releases.
Lokalny ROADMAP to tylko ograniczony podgląd. Offline agent może kontynuować już przydzielone
zadanie, ale nie może zaczynać ani odbierać nowych. Skrypt nigdy nie łączy się z API GitHuba;
operacje na zgłoszeniach robisz ręcznie albo własnymi narzędziami.

**GitHub + wielu agentów.** Dodaje protokół wątku prowadzącego `cykl-prowadzacy`:
- jeden wątek prowadzący na projekt planuje, zleca pracę wykonawcom, czyta krótkie raporty,
  zapisuje decyzje i prowadzi dziennik; sam nie implementuje, nie testuje i nie wydaje;
- każde zlecenie to samodzielny brief (zadanie, pliki, czego nie wolno, wymagany dowód, format
  raportu) ze wskazaniem modelu i powodu wyboru, z tabeli routingu, którą edytujesz w
  `docs/lead/LEAD.md`; przed scaleniem — niezależna recenzja przez model z innej rodziny;
- wykonawcy zwracają blok `=== SHORT ===` o długości najwyżej 8 linii; długie raporty trafiają do plików;
- po trzech rundach poprawek tej samej klasy błędu bez postępu prowadzący zatrzymuje się i prosi
  o świeże spojrzenie na sam krok zamiast czwartej rundy;
- decyzje Właściciela są numerowane i zapisywane z dosłownym cytatem jego słów, razem z
  rekomendacją i tym, co by ją zmieniło;
- wątki prowadzące przekazują sobie pracę przez `docs/lead/THREADS.md`; nowy prowadzący najpierw się tam rejestruje;
- progi zużycia budżetu wstrzymują pracę o niskim priorytecie; sposób pomiaru zależy od Twojego środowiska.

To zasady pracy dla agentów, egzekwowane treścią skilla i kilkoma kontrolami plików (kształt
briefu i raportu, limit rejestru wątków), a nie przez osobny system orkiestracji. Routing modeli
to Twoja konfiguracja. Szablony są w `skills/cykl-prowadzacy/assets/`.

## Aktualizacja

Z 3.0.x: zainstaluj 3.1.0 na wszystkie skille. Migracja nie jest potrzebna; projekty bez `TASKS=`
działają jak edycja GitHub. Z v2: zobacz [docs/MIGRATION-v2.md](docs/MIGRATION-v2.md) (po angielsku).
Nie mieszaj wersji skilli.

## Ochrona scalania (edycje GitHub)

Hook pre-commit i wymagana kontrola CI (`lifecycle-integrity` — *bramka wyniku scalenia*:
sprawdza, jak będzie wyglądał kod po scaleniu, względem obu gałęzi, zanim GitHub pozwoli scalić)
nie pozwalają, żeby scalenie po cichu zgubiło otwartą pracę albo decyzje.
Zobacz [docs/MERGE-PROTECTION.pl.md](docs/MERGE-PROTECTION.pl.md). Dopóki w Twoim repozytorium
nie zostanie pokazany zablokowany próbny PR (canary), raportuj „ochrona scalania niezweryfikowana”.

## Skrypt — dokumentacja techniczna

Wymaga Pythona 3.9+. Nie potrzeba żadnych pakietów Pythona, pobierania tokenizerów ani dostępu do sieci.

```sh
LIFECYCLE=/path/to/skills/cykl-start/scripts/lifecycle.py
python3 "$LIFECYCLE" check --root /path/to/project
python3 "$LIFECYCLE" context --root /path/to/project --skill cykl-start
python3 "$LIFECYCLE" decisions --root /path/to/project
```

Skille uruchamiają te komendy za Ciebie. Dla nowego projektu przygotuj szkic na podstawie JSON-a
z [NOW.template.md](skills/cykl-kickoff/assets/NOW.template.md), a potem:

```sh
python3 "$LIFECYCLE" checkpoint --root /path/to/project --input /tmp/draft.json --expected absent
```

Kolejne zapisy podają bieżący `content_sha256` zamiast `absent`. Szkic może zawierać `decisions`
(pełny tekst indeksu) i `files` (zarządzana ścieżka → tekst). Pliki stanu zapisuje tylko skrypt.
Nierozstrzygniętych identyfikatorów nie usuwaj. Zamknięcie lub zastąpienie wymaga identyfikatora
i powodu, a przy zastąpieniu — istniejącego następcy. Zwrócona karta UUID/hash potwierdza, że
fakty są zapisane; dołącz ją przed kompakcją. Błąd odczytu zatrzymuje pracę.

Żeby dopisać decyzję albo lekcję, podaj jako JSON tylko nowy wiersz; skrypt (z blokadą zapisu)
sam zachowa istniejący indeks i zwróci nową linię indeksu oraz kartę punktu kontrolnego:

```json
{"id":"L-example","kind":"lesson","status":"accepted","scope":"project","supersedes":"-","text":"Rule; precedent; operational test"}
```

```sh
python3 "$LIFECYCLE" decisions add --root /path/to/project --input /path/to/row.json --expected HASH
```

Zduplikowane albo wcześniej zamknięte identyfikatory są odrzucane. W razie potrzeby dodaj
odwołanie w NOW kolejnym punktem kontrolnym. Do dopisania wiersza agent nigdy nie musi czytać
ani podmieniać całego indeksu.

NOW ma limit 4096 bajtów UTF-8. Wszystkie odpowiedzi skryptu mają wspólny limit 16 384 bajtów;
dodatkowe pliki czyta się przez `context --file PATH`. Decyzje mieszkają w *indeksie decyzji*
`docs/DECISIONS.md` (jedna linia na decyzję albo lekcję); skille widzą tylko jego przycięty
wycinek, nigdy cały plik. Nie ma gwarancji liczby tokenów. Niezapisane myśli i dowolne odczyty
wykonywane przez środowisko agenta są poza zakresem tej kontroli.

## Offline i prywatność

Przy `TASKS=github` offline kontynuowana jest tylko praca już zlecona, w jednym wspólnym katalogu
roboczym (worktree). Bieżący status dają pliki prób; NOW przechowuje ich identyfikatory. Nowe
przydziały, zmiany zakresu, odbiór i publikacja czekają na uzgodnienie online. Przy `TASKS=local`
źródłem prawdy są ROADMAP i `docs/issues`, zmieniane przez punkt kontrolny. Synchronizacja i import
z API GitHuba są ręczne. Przygotowane treści zgłoszeń, łącznie z przypiętym blokiem, mają limit
8192 bajtów. Lustrzane kopiowanie (mirroring) jest wyłączone; ewentualne przyszłe lustro (tylko
po włączeniu) musi wybierać sprawdzone, bezpieczne do publikacji: tożsamość, cel, pozycję, następny
krok i identyfikatory. Sekcje Preserve/Risks i treści decyzji nie trafiają do lustra.

## Weryfikacja i budowanie

```sh
python3 -B -m unittest discover -s tests -v
python3 -B skills/cykl-start/scripts/lifecycle.py check --package
bash build-plugin.sh
```

Budowanie tworzy plugin, zbiorczy ZIP ze skillami i osiem osobnych ZIP-ów (po jednym na skill).
Zmiany: [CHANGELOG](CHANGELOG.md); limity i kontrakty: [R2](docs/design/v3.0.md) i
[zmiany w 3.1](docs/design/v3.1.md) (po angielsku).

## Wersje

- **Aktualna: 3.1.0** — [wydanie v3.1.0](https://github.com/witczakm/cykl-lifecycle/releases/tag/v3.1.0).
- **Nieaktualne:** 2.x i 3.0.x; historia w [CHANGELOG.md](CHANGELOG.md).
- **Nieaktualne:** osobne, anglojęzyczne repozytorium [witczakm/cycle-lifecycle](https://github.com/witczakm/cycle-lifecycle) (2.4.0) — zastąpione przez to repozytorium.

## Licencja

MIT
