# Changelog

All notable changes to cykl-lifecycle are documented here.

---

## [2.7.0] — 2026-08-05

Wydanie atakuje **przyczynę powracającego driftu**, nie kolejny jego objaw. 2.5.0 naprawiła jeden mechanizm (pola dopisywane zamiast nadpisywanych) — drift wrócił, bo to była przyczyna wtórna. Diagnoza na żywym projekcie po czterech kolejnych sesjach wskazała trzy odrębne źródła i jeden czynnik, który je wszystkie mnoży.

### Added
- **Próg rozmiaru dokumentów stanu z rotacją.** `/zamknij` mierzy `wc -c` każdego dokumentu; powyżej ~40 kB przenosi historyczne wpisy do `docs/archive/<nazwa>-RRRR-Qn.md` i zostawia ostatnie 5 + odsyłacz. `/start` zgłasza przekroczenie progu jako dług.
  **Powód:** w projekcie prowadzonym tym zestawem dokumenty stanu urosły do 153 / 179 / 294 / **316 kB** — przy szablonie HANDOFF ważącym ~2 kB. Domykający sesję fizycznie nie przegląda takiego pliku w całości, więc aktualizuje miejsca, które pamięta, a ich liczba rośnie z każdą sesją. Pozostałe przyczyny driftu są konsekwencjami rozmiaru: duplikat faktu boli dopiero wtedy, gdy nie widać wszystkich kopii naraz. Szablon od zawsze mówił „**cienki** snapshot" — bez liczby było to życzenie, nie regułą.
- **Bramka spójności nagłówek ↔ changelog** w `/zamknij` (krok 3) i `/migawka` (krok 3). Po każdej edycji: data i wersja w nagłówku muszą równać się tym z ostatniego wiersza changelogu; rozjazd zatrzymuje pracę.
  **Powód:** nagłówek i treść to dwa osobne ruchy edycyjne i drugi bywa pominięty — kto dopisał pozycję na dole pliku, nie wrócił na górę. Do 2.6.0 wykrywał to dopiero `/start`, czyli po fakcie. Sprawdzenie kosztuje dwa odczyty i nie zależy od rozmiaru pliku, więc należy do momentu zapisu.
- **Zasada „fakt ma JEDNO miejsce"** w Zasadach `/zamknij` oraz w `PROJECT_CONFIG.template`: wartość żyjąca w innym dokumencie wpisywana jest jako odwołanie, nigdy jako kopia.
  **Powód:** dotychczasowa reguła „korekta dotyka każdego powtórzenia" pilnuje kopii — koszt rośnie liniowo z ich liczbą i z każdą sesją. Likwidacja kopii zdejmuje problem zamiast go administrować, i jest jedyną wersją weryfikowalną tanio: nie ma czego porównywać.

### Changed
- **Pole stanowe mierzone sondą zawiera odwołanie, nie wartość.** `REPO_STATE` w szablonie to teraz `<mierzone przez STATE_PROBE>`. Znika samoodniesienie: wartość zapisywana wewnątrz commitu opisuje stan sprzed samej siebie i **zawsze** jest o jeden commit do tyłu. 2.6.0 to oznaczała (`stan PRZED commitem tej sesji`); 2.7.0 usuwa źródło, przenosząc pomiar z czasu zapisu na czas odczytu.
- `CURRENT_MILESTONE` w szablonie to sam identyfikator etapu — bez wersji planu i budżetu, które żyją we własnych dokumentach.
- `HANDOFF.template` — próg 40 kB wpisany wprost do noty „po co ten plik".
- **`cykl-zamknij` skondensowany**, żeby zmieścić trzy nowe reguły bez przekroczenia progu lekkości: 100 → 106 linii przy limicie 110. Uzasadnienia przeniesione do `docs/ARCHITEKTURA-DECYZJE.md`, w skillu zostały same reguły. Ten sam mechanizm, który wydanie wprowadza dla dokumentów stanu, zastosowany do samego skilla.

---

## [2.6.0] — 2026-08-04

Wydanie naprawia **mechanizmy**, nie opisy. Trzy defekty klasy „reguła istnieje, ale nic jej nie egzekwuje" oraz zestaw reguł pomiaru wyprowadzonych z analizy praktyki reconu w projekcie prowadzonym tym zestawem.

### Fixed
- **Bramka pre-flight była komentarzem, nie mechanizmem.** Blok w kroku 6 `/zamknij` (i analogicznie w `/kickoff`) miał postać `grep …` / `# jeśli nie — NIE commituj` / `git add` / `git commit`. Człowiek wkleja cały blok naraz, więc commit wykonywał się niezależnie od wyniku grepa. Warunek egzekwuje teraz **składnia powłoki** (`set -euo pipefail` + `&&`). Precedens z projektu prowadzonego tym zestawem: push wystrzelił mimo trzech nieprzechodzących testów.
- **`pipefail` obowiązkowe w bramkach** — `cmd | tail` zwraca kod wyjścia `tail`, nie `cmd`, więc bramka bez `pipefail` przepuszcza błąd.
- **`skills/cykl-zamknij/agents/openai.yaml`** deklarował „nie wykonuje git" — nieprawda od 2.5.0, która dopuściła białą listę komend pomiarowych. Szóste miejsce, w którym żył ten kontrakt.
- **Nazwa „pre-flight grep" w Zasadach `/zamknij`** wskazywała na blok, który przestał istnieć pod tą nazwą.

### Added
- **`STATE_PROBE` — pomiar zewnętrzny na wejściu w sesję.** Drift-check w `/start` porównywał dokumenty **wyłącznie ze sobą nawzajem**: nagłówek z changelogiem, CONFIG z HANDOFF, Pozycję ze statusami. Trzy dokumenty potrafią zgodnie powtarzać tę samą nieprawdę — spójność wewnętrzna to nie prawdziwość. `PROJECT_CONFIG` deklaruje teraz jedną komendę read-only mierzącą stan poza dokumentami; `/start` wykonuje ją i porównuje z polem stanowym. Maks. 3 próby, brak odpowiedzi = `[DO SPRAWDZENIA]`, nigdy blokada wejścia w sesję. Skill pozostaje generyczny — osprzęt pomiarowy wnosi projekt.
- `/kickoff` pyta o remote i `STATE_PROBE`, jeśli projekt ma repo. Wcześniej repo git było „opcjonalne", a krok 6 i tak zakładał, że istnieje.
- `/migawka` wykonuje sondę, gdy migawka dotyka pola stanowego — zamiast przepisywać starą wartość.
- **Bramka wyjścia etapu jest egzekwowana.** Kolumna „Bramka wyjścia" istniała w szablonie ROADMAP od 2.0, ale żaden skill jej nie sprawdzał — flip etapu na DONE opierał się na kompletności kroków. `/zamknij` i `/roadmap` wymagają teraz pokazania, czym bramka została spełniona; komplet kroków DONE to warunek konieczny, nie wystarczający.
- **Reguły pomiaru** (z analizy 15 udokumentowanych trybów, w których pomiar kłamie):
  - `/start`: **pomiar przeczy dokumentowi → najpierw sprawdź, czy mierzysz właściwy obiekt** — ten, którego używa bieżący krok, nie ten o podobnej nazwie. Najczęstszy tryb porażki w materiale źródłowym.
  - `/start`: **ucięty odczyt nie jest dowodem nieobecności** — listing obcięty limitem mówi „nie widzę", nie „nie ma".
  - `/zamknij`: **pomiar ma datę ważności** — „dziś zero zmian" zmierzone o 18:00 bywa nieprawdą o 21:00; zamknięcie dnia przed jego końcem to pomiar przedwczesny. Stąd godzina w znaczniku `[zmierzone …]`, nie sama data.
  - `/zamknij`: **korekta twierdzenia musi dotknąć KAŻDEGO jego powtórzenia** — te same fakty żyją w kilku dokumentach; po poprawce `grep` starego brzmienia = 0 poza changelogiem.
  - `/lekcja`: precedens w „Dlaczego" podawany liczbą z pomiaru, nie przymiotnikiem.

### Packaging
- **`build-plugin.sh`** — buduje `cykl-lifecycle.plugin` ze źródeł i **weryfikuje wynik**: integralność archiwum, zgodność `skills/` w paczce z repozytorium oraz jednolitość markera wersji. Kończy się błędem, gdy cokolwiek się nie zgadza. Powód: paczka jest binarnym duplikatem `skills/`, a zapomniana przebudowa daje wydanie, w którym zmiana nie dociera do nikogo instalującego przez Cowork — zdarzyło się raz, paczka wiozła skille o dwie wersje starsze niż repo.
- **`packaging/plugin-README.md`** — README widoczne po instalacji z paczki jest teraz **wersjonowane w repo**. Wcześniej istniało wyłącznie wewnątrz archiwum, więc nikt go nie utrzymywał: nie miało numeru wersji ani informacji o zmianach. Teraz zawiera jedno i drugie.

### Documentation
- **Instrukcje aktualizacji per środowisko** — `docs/INSTALL-codex.md` **nie miał sekcji aktualizacji w ogóle**, a `docs/INSTALL-claude.md` miał dwie linijki bez restartu agenta i bez ścieżki dla Cowork. Obie sekcje opisują teraz: sprawdzenie zainstalowanej wersji markerem (`grep -h "cykl-lifecycle v" …/cykl-*/SKILL.md | sort -u`), wykrycie wymieszanych wersji, aktualizację jedną komendą i ręczną, wariant pluginowy, wymóg restartu agenta oraz jawne stwierdzenie, że wydanie nie łamie kompatybilności.
- `README` — nowa sekcja „Masz już starszą wersję?" z komendą sprawdzającą dla obu środowisk.
- **`docs/ARCHITEKTURA-DECYZJE.md`** — nowy dokument: dziesięć decyzji projektowych (D1–D10), każda z precedensem, który ją wymusił, i z warunkiem, który by ją odwrócił. Osobno od przewodnika, bo odpowiada na „dlaczego", nie na „jak używać".
- `README` — sekcja „Co nowego w 2.6.0"; opis dwóch typów pól i `STATE_PROBE`; ostrzeżenie, że `cykl-lifecycle.plugin` jest binarnym duplikatem `skills/` i wymaga przebudowy przy każdej zmianie; struktura repozytorium uzupełniona o `install.sh`, `.claude-plugin/` i paczkę.
- `README` — **poprawiona nieprawda**: „skille nigdy nie wykonują git" nie obowiązuje od 2.5.0, która dopuściła białą listę komend pomiarowych.
- `docs/PRZEWODNIK-KOMEND.md` — przykładowy blok commita w `/zamknij` **pokazywał antywzorzec** naprawiony w tym wydaniu (warunek jako komentarz); zastąpiony bramką mechaniczną z wyjaśnieniem. Nowe reguły 5–7 (pola dziennikowe vs stanowe, bramka jako składnia, data ważności pomiaru). Zaktualizowana odpowiedź na „co jeśli nie commituję przez kilka sesji" — od 2.6.0 `/start` to zauważy.
- `CONTRIBUTING.md` — bramki przed PR (wersja w pięciu miejscach, kontrakt gita w ośmiu, frontmatter nietykalny, paczka identyczna z `skills/`) oraz wymóg mierzenia przyrostu linii: skille mają zostać lekkie.

### Changed
- **`PROJECT_CONFIG.template`** — nowa sekcja `STATE_PROBE` oraz rozszczepienie worka na stan repo na dwa pola: `REPO_STATE` (stanowe, nadpisywane po pomiarze, ze znacznikiem) i `REPO_NOTES` (przyrostowe, trwała wiedza operacyjna). `CURRENT_SPRINT_BRANCH` zostaje, ale wyłącznie na nazwę brancha. W projekcie źródłowym jedno pole zlepiające obie role spuchło przez sześć sesji do 1369 znaków i zawierało trzy sprzeczne stany z trzech dat.
- **`HANDOFF.template`** — „Następny ruch" wymaga teraz wykonawcy, modelu i decyzji TEN SAM / NOWY wątek, oraz musi być wykonywalny bez otwierania innych plików (zero placeholderów). Wcześniej mówił CO i DLACZEGO, nigdy KTO i CZYM.
- **`ROADMAP.template`** — nota przy rozbiciu etapu opisuje warunek flipu etapu, nie tylko kroku.

---

## [2.5.0] — 2026-08-04

### Added
- **Rozróżnienie pól dziennikowych i stanowych w dokumentach stanu.** Pole dziennikowe (changelog, nagłówek, bieżący sprint) jest przyrostowe; pole stanowe (np. stan repo, następna otwarta decyzja, publiczny URL, hash wdrożonego artefaktu) ma jedną prawdziwą wartość i musi być NADPISANE po pomiarze. Diagnoza: w projekcie prowadzonym tym zestawem pole stanowe urosło przez 6 sesji do 1369 znaków i zawierało trzy sprzeczne stany z trzech dat — czytający brał pierwszy, czyli najstarszy.
- `cykl-zamknij` krok 3: akapit „Pola dziennikowe vs stanowe" + reguła rozszczepienia pola stanowego na stan (nadpisywany) i notatki (przyrostowe), gdy siedzi w nim trwała wiedza operacyjna.
- `cykl-zamknij` krok 3: znacznik `[zmierzone RRRR-MM-DD HH:MM UTC]` przy każdym polu stanowym; pole opisujące ostatni commit dodatkowo oznaczane jako „stan PRZED commitem tej sesji" (jest o jeden commit do tyłu z definicji, bo zapisywane jest wewnątrz commitu, który je utrwala); pole „następna decyzja" opatrywane numerem BIEŻĄCEJ sesji.
- `cykl-zamknij` krok 6: pre-flight mierzy teraz stan repo (`git rev-parse --short HEAD`, `git rev-list --left-right --count`), a nie tylko `grep "Ostatnia aktualizacja"` — czyli jedyne pole, które nie mogło być nieaktualne, bo właśnie zostało wpisane.
- `cykl-zamknij` Zasady: pole stanowe bez pomiaru = `[DO SPRAWDZENIA]`, nigdy stara wartość przepisana z pliku; kilka wartości z różnych dat w jednym polu = drift do naprawy w tym samym ruchu.
- `cykl-start` krok 2 (drift-check): czytaj CAŁE pole stanowe, nie jego początek (pola >1000 znaków — obcięcie pokazuje najstarszą wartość jako bieżącą); kilka stanów w jednym polu = drift, nawet jeśli najnowsza wartość w nim jest.
- `.claude-plugin/plugin.json` — manifest Claude w repozytorium. Wcześniej istniał wyłącznie wewnątrz artefaktu `cykl-lifecycle.plugin`, przez co repo nie było poprawnym rootem pluginu Claude.

### Changed
- `cykl-zamknij` krok 2: „odczyt plików, nie git" → biała lista komend read-only (`git rev-parse --short HEAD`, `git rev-list --left-right --count`, `git log --oneline -n`, `git show`, `git diff --stat HEAD`). Jawny ZAKAZ `git status`, `git add --dry-run`, `git stash` — tworzą `.git/index.lock`, którego mosty zdalne (Cowork / device bridge) nie potrafią usunąć, i blokują repo na kolejne dni.
- `cykl-zamknij` krok 6 i Zasady: „Nie wykonuj git" doprecyzowane na „nie wykonuj git mutującego (add/commit/push/stash)" — komendy pomiarowe z białej listy model wykonuje sam. Bez tego krok 2 i Zasady dawały sprzeczną instrukcję.
- `cykl-migawka` krok 2: reguła NADPISZ rozciągnięta z sekcji Snapshot w HANDOFF na pola stanowe w PROJECT_CONFIG. Historia idzie do changelogu, nie do wnętrza pola.

### Fixed
- **Drift wersji w samym pluginie — ta sama klasa błędu, którą to wydanie naprawia.** Repozytorium deklarowało cztery różne wersje naraz: `.codex-plugin/plugin.json` 2.3.0, markery w 7 × `SKILL.md` 2.3.0, badge README 2.4.0, `docs/PRZEWODNIK-KOMEND.md` 2.2.0, a manifest wewnątrz `cykl-lifecycle.plugin` 2.4.0. Wszystko zsynchronizowane do 2.5.0.
- `cykl-lifecycle.plugin` przebudowany z bieżącej treści skilli. Artefakt wiózł bajt-w-bajt kopie `SKILL.md` sprzed zmiany, więc instalacja jednym plikiem dostarczała starą wersję niezależnie od stanu repozytorium.

---

## [2.4.0] — 2026-06-17

### Added
- **Wsparcie OpenAI Codex (dual-compatible).** Ten sam `SKILL.md` działa teraz w Claude i w Codeksie.
- `agents/openai.yaml` w każdym z 7 skilli — metadane UI + polityka wywołania dla Codeksa (Claude ignoruje plik). `cykl-kickoff` ma `allow_implicit_invocation: false` (tylko jawne `$cykl-kickoff`).
- Pakiet jako **Codex plugin**: `.codex-plugin/plugin.json` + `marketplace.json`.
- `docs/INSTALL-codex.md` — instalacja na Codeksie (skille albo plugin) + sekcja bezpieczeństwa (tryb zatwierdzania).
- `CONTRIBUTING.md` oraz README przepisany pod dwie platformy (Claude + Codex), przyjazny początkującym w AI.
- `/lekcja-g` na Codeksie zapisuje do `~/.codex/AGENTS.md` (globalne instrukcje czytane na starcie każdej sesji).

### Changed
- Uogólniono fragmenty platform-coupled w skillach: „CCT" → „terminal (Claude Code / Codex)"; `cykl-kickoff` adnotuje plik instrukcji projektu jako CLAUDE.md (Claude) / AGENTS.md (Codex); `cykl-lekcja-globalna` ma tri-platform tabelę celu zapisu.
- `docs/INSTRUKCJA-INSTALACJI.md` → `docs/INSTALL-claude.md`; instalacja rozdzielona per platforma.
- README: bump wersji 2.3.0 → 2.4.0.

### Verified
- Wszystkie 7 skilli przetestowane na żywo: Claude (Cowork) oraz Codex v0.140.0 / gpt-5.5 (2026-06-17) — triggery explicit, implicit i negatywne oraz poprawność zapisów dokumentów stanu. Komplet PASS.

---

## [2.3.0] — 2026-06-17

### Fixed
- LESSONS_CANON.template: F1–F6 uogólnione (usunięto referencje BidSentinel)
- README: instalacja CCT — jedna komenda `cp -r skills/cykl-*` zamiast 7 osobnych
- README: badge URL Skills — poprawny link do docs.anthropic.com
- README: Cowork UI reference — usunięto hardkodowaną lokalizację ikony

### Added
- README: sekcja "Pierwsze 15 minut — quickstart" z literalnym transkryptem
- README: tabela porównawcza profili lite/standard/regulated
- README: minimum viable workflow dla małych projektów
- README: nota dla użytkowników Cowork bez CCT przy /lekcja-g
- Wszystkie SKILL.md: wersja `<!-- cykl-lifecycle v2.3.0 -->`
- cykl-roadmap: rozszerzony negatywny trigger
- HANDOFF.template: komentarz HTML oznaczający sekcję instrukcji dla modelu AI (P3.1)
- README: zasada „nie prowadź całego projektu w jednym wątku" (uzasadnienie token/jakość + context rot) oraz wpis FAQ

### Changed
- cykl-zaloz → cykl-kickoff — nazwa folderu, pole `name:` w SKILL.md oraz referencje w README i docs/INSTRUKCJA-INSTALACJI.md (P3.2)
- README: badge wersji 2.2.0 → 2.3.0

## [2.2.0] — 2026-06-17

### Changed
- Rename `nsos-*` → `cykl-*` (universal prefix, neutral to code context)
- Rename `nsos-handoff` → `cykl-migawka` (avoids collision with test/VM snapshots)
- Added **negative triggers** to every skill description ("NIE używaj gdy…")
- Added public GitHub release with professional README, installation guide, command guide

### Added
- `INSTRUKCJA-INSTALACJI.md` — 3-option installation guide (CCT global / Claude.ai Settings / local)
- `PRZEWODNIK-KOMEND.md` — per-command reference with examples, diffs, Q&A

---

## [2.1.0] — 2026-06-10

### Fixed (CRITICAL)
- Mandatory changelog row on every header bump (`/handoff`, `/zamknij`) — without it `/start` drift-check produced false alarms on every correctly-executed session

### Added
- **Two-level position awareness** (Stage X/N · step Y/M) in ROADMAP template and all skills
- `/start` step 0: guard for non-lifecycle directories (no `PROJECT_CONFIG.md` → propose `/kickoff`)
- `/start` drift-check: scans `LESSONS_CANON.md` for `[CANDIDATE GLOBAL]` markers and surfaces them with CCT command
- ROADMAP: `Verification` column — step only flips to DONE when verifiable criterion is met
- ROADMAP: `Exit gate` column on stage table — stage only DONE when gate is satisfied
- `GLOBAL_LESSONS_BASELINE` loop closed: CCT writes GL-NNN to field after confirmed global save
- Conflict resolver for HANDOFF ↔ ROADMAP in `struktura-projektu.md` and `README.template`
- Pre-flight `grep` in `/zamknij` commit block (verifies files actually wrote to disk)
- Idempotency test in `/zamknij` (today's changelog date = patch-only bump, no duplicate rows)
- `/kickoff` interview limit (max 5-7 questions/turn, rest → `UNKNOWN`)
- Project-local F-lessons numbered from F10 (F1-F6 = universal baseline, F7-F9 = visual buffer)

### Fixed
- `/handoff` snapshot model: overwrite-only (was append; accumulation → log, then `/zamknij` overwrote it losing interim decisions)
- `PROJECT_CONFIG.template`: added minimal version header (skills said "bump CONFIG header" but template had no header)
- `README.template`: profile-aware pruning instruction (lite profile must not reference non-existent `docs/adr/`, `CLAUDE.md`)

---

## [2.0.0] — 2026-06-09

### Changed
- Full de-escalation from Faza 1 (11 commands, Python scripts, transactional rollback, JSON manifests) to Faza 2: **prose-only skills**, zero code, zero automation without human approval
- Aligned with Anthropic Agent Skills best practices format

### Added
- 7 skills: `/start`, `/zamknij`, `/handoff`, `/roadmap`, `/lekcja`, `/lekcja-g`, `/kickoff`
- 5 document templates (HANDOFF, ROADMAP, LESSONS_CANON, PROJECT_CONFIG, README)
- `struktura-projektu.md` reference (source-of-truth hierarchy, profiles)
- IoC pattern for global lessons (Cowork → CCT handoff, no hanging markers)
- Common principles from BidSentinel lessons F1-F6 (pre-loaded in every new project)
