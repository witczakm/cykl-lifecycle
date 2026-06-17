# cykl-lifecycle

> **Pamięć projektu dla agentów AI.** Prowadź jeden projekt przez dziesiątki sesji z Claude lub Codex — model na starcie każdej sesji wie, gdzie skończyłeś i co jest następne.
>
> *Multi-session memory for AI coding agents. Works with Claude Code, OpenAI Codex & Claude Cowork. Polish-language skills.*

[![Version](https://img.shields.io/badge/version-2.4.0-blue)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platformy](https://img.shields.io/badge/platformy-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Cowork-orange)](#instalacja--wybierz-narz%C4%99dzie)
[![Format](https://img.shields.io/badge/format-Agent%20Skills-blueviolet)](https://agentskills.io)
[![Język](https://img.shields.io/badge/j%C4%99zyk-polski-red)](#)

---

## Po co to jest

Agenci AI (Claude Code, OpenAI Codex) nie pamiętają poprzednich rozmów. Przy projekcie, który trwa tygodnie, każdą sesję zaczynasz od tłumaczenia od nowa: *„gdzie skończyliśmy, co już zrobione, co dalej…"*. Tracisz na to czas — a często i jakość, bo prowadzenie całego projektu w jednym, gigantycznym wątku psuje odpowiedzi i pali tokeny.

**cykl-lifecycle** to 7 komend, które dają projektowi pamięć. Stan zapisujesz do plików po każdej sesji i wczytujesz na starcie następnej. Zamiast tłumaczyć kontekst, wpisujesz `/start` i w pół minuty masz pełny obraz: na którym jesteś etapie, co ostatnio zamknięte i jaki jest **jeden** następny ruch.

## Jak to działa — pętla

```
   /kickoff   (raz — zakłada projekt)
      │
      ▼
   /start  ──►   praca   ──►  /zamknij        ◄── tak wygląda każda sesja
 (wczytaj stan)            (zapisz stan)
      ▲                          │
      └──────────────────────────┘
        następna sesja czyta to, co poprzednia zapisała
```

Stan żyje w **plikach** projektu (`HANDOFF`, `ROADMAP`, `LESSONS`), nie w przewijaniu czatu. Dlatego możesz zamknąć rozmowę, wrócić za tydzień, wpisać `/start` i kontynuować bez gubienia kontekstu.

## Czy to dla Ciebie?

✅ **Tak**, jeśli:
- projekt potrwa dłużej niż 2–3 sesje,
- pracujesz nad czymś złożonym (aplikacja, dokumentacja, badania, analiza),
- chcesz mieć pewność, że postęp jest zapisany i nic nie ginie.

❌ **Raczej nie**, jeśli:
- to jednorazowe zadanie na jeden raz,
- projekt jest prosty i dobrze go pamiętasz.

---

## Dopiero zaczynasz z AI? Minuta teorii

Jeśli te narzędzia są dla Ciebie nowe — oto wszystko, czego potrzebujesz, żeby zrozumieć resztę:

- **Agent AI w terminalu** — program, który rozmawia z Tobą i edytuje pliki na Twoim komputerze. Dwa popularne: **Claude Code** (Anthropic) i **OpenAI Codex**. **Claude Cowork** to wersja na pulpit, bez terminala.
- **Skill** — plik z instrukcją (`SKILL.md`), który uczy agenta jednej powtarzalnej rzeczy. Agent sam go uruchamia, gdy pasuje do tego, co piszesz. To otwarty standard ([agentskills.io](https://agentskills.io)) — ten sam format działa w Claude i w Codeksie.
- **cykl-lifecycle** = 7 takich skilli, które razem dają projektowi pamięć między sesjami.

Komendy (`/start`, `/zamknij`…) wpisujesz po prostu w rozmowie z agentem.

---

## 7 komend

| Komenda | Kiedy | Co robi |
|---|---|---|
| `/kickoff` | raz, na start projektu | zakłada strukturę i pyta o etapy |
| `/start` | na początku **każdej** sesji | wczytuje stan, mówi gdzie jesteś |
| `/zamknij` | na koniec każdej sesji | zapisuje postęp, szykuje commit |
| `/migawka` | po ważnej decyzji w środku sesji | lekki zapis stanu |
| `/roadmap` | gdy chcesz zobaczyć postęp | pokazuje etapy i kroki |
| `/lekcja` | gdy wyciągniesz wniosek z pracy | zapisuje naukę do projektu |
| `/lekcja-g` | gdy wniosek dotyczy wszystkich projektów | zapisuje globalnie (za zgodą) |

> **Claude:** wpisujesz `/start` albo po prostu opisujesz, czego chcesz.
> **Codex:** wołasz przez `$nazwa` (np. `$cykl-start`) albo zdaniem („gdzie jesteśmy w projekcie?"). Komenda `/start` w Codeksie nie działa jako slash — użyj `$cykl-start`.

---

## Instalacja

### ⚡ Jedną komendą — wprost z GitHuba (Claude Code / Codex)

**Codex + Claude (oba naraz):**

```bash
curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash
```

**Tylko Codex:**

```bash
curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash -s -- codex
```

**Tylko Claude:**

```bash
curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash -s -- claude
```

Skrypt pobiera 7 skilli **wprost z repo** i kopiuje do `~/.claude/skills` i/lub `~/.agents/skills` — nic nie ściągasz ręcznie. Potem zrestartuj agenta i wpisz `/kickoff` (Claude) albo `$cykl-kickoff` (Codex). Nie masz Codeksa? `npm install -g @openai/codex`.

> Chcesz zobaczyć, co odpalasz? Otwórz [`install.sh`](install.sh) — kilkanaście linii. (`curl … | bash` uruchamia kod z sieci; rób to tylko z zaufanych repo — np. swojego.)

### ▶ Claude Cowork (desktop) — najprościej, jeden plik

Pobierz **[`cykl-lifecycle.plugin`](cykl-lifecycle.plugin)** (na stronie pliku kliknij **Download**) i **otwórz go w Cowork** — przeciągnij plik do rozmowy; pokaże się przycisk **Zainstaluj**, który wgra **wszystkie 7 skilli naraz**. Potem wpisz `/kickoff`. Bez pobierania repo, bez dodawania folderów po kolei.

Wariant zapasowy (ręcznie): **Settings → Capabilities → Skills → Add skill** → dodaj 7 folderów `skills/cykl-*` osobno.

### ▶ Claude.ai (web / mobile)

**Settings → Capabilities → Skills → Add skill** (7 folderów osobno). Wersja web nie ma dostępu do plików — pomoże w planowaniu, ale zapis do plików projektu wymaga Cowork, Claude Code lub Codeksa.

### ▶ Instalacja ręczna (bez skryptu)

Pobierz repo (**Code → Download ZIP** albo `git clone`), wejdź do folderu `cykl-lifecycle` i wgraj skille.

**Claude Code:**

```bash
mkdir -p ~/.claude/skills && cp -r skills/cykl-* ~/.claude/skills/
```

**Codex:**

```bash
mkdir -p ~/.agents/skills && cp -r skills/cykl-* ~/.agents/skills/
```

> Szczegóły i troubleshooting: **[docs/INSTALL-claude.md](docs/INSTALL-claude.md)** · **[docs/INSTALL-codex.md](docs/INSTALL-codex.md)**.

---

## Pierwsze 15 minut

**Sesja 1 — założenie projektu (~5 min).** Wpisz `/kickoff` (lub `$cykl-kickoff` w Codeksie). Agent zapyta o kilka rzeczy:

```
1. Nazwa projektu? (np. "Moja Aplikacja" / "moja-app")
2. Cel? (1–2 zdania — co budujesz i dla kogo)
3. Główne etapy? (3–7 haseł "co po kolei", np.:
   Planowanie → Baza danych → Backend → Frontend → Testy → Deploy)
4. Gdzie tworzyć pliki? (ścieżka do katalogu projektu)
5. Profil? (lite = 3 pliki / standard = pełna struktura / regulated = z audytem)
```

Czegoś nie wiesz? Wpisz „nie wiem" — agent zapisze jako UNKNOWN do uzupełnienia później. Po odpowiedziach tworzy strukturę, wypełnia ROADMAP Twoimi etapami i od razu mówi, jaki jest pierwszy krok.

**Każda kolejna sesja (~30 sekund na wejście).** Otwórz nową rozmowę i wpisz `/start`:

```
Pozycja: Etap 1/4 "Planowanie" · krok 1/3 "Zebranie wymagań"
Ostatnio zamknięte: projekt założony — struktura gotowa ✓
Następny ruch: zdefiniuj wymagania funkcjonalne (krok 1.1)
Drift: brak.
```

Pracujesz normalnie. Na koniec wpisz `/zamknij` — dostajesz podsumowanie i gotowy blok `git add + commit` do skopiowania.

---

## Najważniejsza zasada: nie prowadź całego projektu w jednym wątku

Najczęstszy błąd początkujących: cały, wielotygodniowy projekt w jednej, nieskończonej rozmowie. Płacisz za to **jakością i tokenami**:

- Model jest bezstanowy — przy każdej wiadomości dostaje **całą** rozmowę od nowa. Im dłuższy wątek, tym drożej każda kolejna tura (koszt rośnie ~kwadratowo).
- W długim kontekście jakość spada („context rot"): model słabiej sięga po informacje ze środka wątku i gubi się w szumie.

**Dobry nawyk:** nowa rozmowa na każdą sesję — `/start` na wejściu, `/zamknij` na wyjściu. Stan żyje w plikach, więc świeży wątek niczego nie gubi. Czat to „warsztat" na jedną sesję; pamięć projektu jest w plikach.

---

## Bezpieczeństwo (zwłaszcza w Codeksie)

Codex to **agent** — wykonuje realne komendy i potrafi sięgnąć poza bieżący katalog. Zanim ruszysz na realnym projekcie:

- ustaw rozsądny tryb zatwierdzania (`/approvals` w sesji),
- **czytaj, co zatwierdzasz** — odrzucaj akcje poza projektem albo komendy systemowe (`pg_dump`, `npx`, `rm`…), których świadomie nie zleciłeś.

Same skille cykla są bezpieczne: zapisują wyłącznie dokumenty stanu w katalogu projektu i **nigdy nie wykonują git** — dają tylko gotowy blok poleceń do wklejenia.

---

## Co powstaje w Twoim projekcie

Po `/kickoff`:

```
projekt/
├── PROJECT_CONFIG.md      ← parametry + live-state (co jest teraz w toku)
└── docs/
    ├── HANDOFF.md         ← snapshot "gdzie jesteśmy + następny krok"
    ├── ROADMAP.md         ← postęp: etapy + kroki + Pozycja
    └── LESSONS_CANON.md   ← kanon lekcji (F1–F6 + Twoje)
```

| Plik | Aktualizuje | Zasada |
|---|---|---|
| `PROJECT_CONFIG.md` | `/migawka`, `/zamknij` | live-state: branch, status, decyzje |
| `docs/HANDOFF.md` | `/migawka`, `/zamknij` | zawsze nadpisywany (stan „teraz") |
| `docs/ROADMAP.md` | `/migawka`, `/roadmap`, `/zamknij` | statusy kroków, Pozycja |
| `docs/LESSONS_CANON.md` | `/lekcja` | dopisywany, nigdy nadpisywany |

---

## FAQ

**Muszę wpisywać `/start` ręcznie?**
Nie. Agent zwykle odpala go sam, gdy wykryje powrót do projektu. Ale wpisanie `/start` zawsze jest bezpieczne.

**Działa bez terminala?**
Tak — w Claude Cowork (desktop) i Claude.ai (web) przez Settings → Capabilities. W web bez zapisu do plików.

**Mogę używać z innymi skillami?**
Tak. Prefiks `cykl-` i polskie triggery są projektowane pod współistnienie z anglojęzycznymi skillami technicznymi.

**Mogę przetłumaczyć komendy na angielski?**
Tak. Skille to pliki tekstowe — zmień triggery w `SKILL.md` i używaj własnych komend.

**Gdzie ląduje `/lekcja-g` (lekcja globalna)?**
Claude Code → `~/.claude/context/lessons.md`. Codex → `~/.codex/AGENTS.md`. Cowork → marker + gotowa komenda dla terminala. Zawsze za Twoją zgodą.

---

## Struktura repozytorium

```
cykl-lifecycle/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── CONTRIBUTING.md
├── .codex-plugin/
│   └── plugin.json              # manifest pluginu Codeksa
├── marketplace.json             # osobisty marketplace Codeksa (instalacja jako plugin)
├── skills/                      # 7 skilli (dual-compatible: Claude + Codex)
│   ├── cykl-start/  · cykl-zamknij/  · cykl-migawka/  · cykl-roadmap/
│   ├── cykl-lekcja/ · cykl-lekcja-globalna/
│   └── cykl-kickoff/            # + assets/ (5 template'ów) + references/
│       └── agents/openai.yaml   # każdy skill ma metadane Codeksa (Claude je ignoruje)
└── docs/
    ├── INSTALL-claude.md        # instalacja: Claude Code / Cowork / web
    ├── INSTALL-codex.md         # instalacja: Codex (skille albo plugin) + bezpieczeństwo
    └── PRZEWODNIK-KOMEND.md     # przewodnik po komendach z przykładami
```

---

## Jak to działa technicznie

Skille to pliki `SKILL.md` zgodne z [otwartym standardem Agent Skills](https://agentskills.io). Agent ładuje na starcie tylko ich nazwę + opis (progressive disclosure), a pełną treść dopiero gdy komenda lub kontekst pasują do triggera. Każdy skill ma klauzulę „NIE używaj gdy…", która chroni przed odpaleniem w złym momencie.

Architektura odpowiada wzorcom dla długo działających agentów: lista kroków ze statusami (edytuje się tylko status), jeden krok na sesję, protokół „wczytaj stan" na wejściu (`/start`), czysty zapis + commit na końcu (`/zamknij`). **Zero automatyzacji bez Twojej zgody** — każda zmiana pokazywana jest jako diff, a `git commit` wykonujesz sam.

Wariant dual-compatible: ten sam `SKILL.md` działa w Claude i Codeksie. Dodatkowy `agents/openai.yaml` (metadane + polityka wywołania) czyta tylko Codex — Claude go ignoruje. Status walidacji: wszystkie 7 skilli przetestowane na żywo na Claude i na Codex (gpt-5.5) — patrz [CHANGELOG](CHANGELOG.md).

---

## Wkład

Issues i PR-y mile widziane — zwłaszcza raporty błędnych triggerów (false positive / negative), tłumaczenia na inne języki i doświadczenia z różnych środowisk. Szczegóły: [CONTRIBUTING.md](CONTRIBUTING.md).

## Licencja

[MIT](LICENSE) © 2026 Michał Witczak
