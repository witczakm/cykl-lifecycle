# Instalacja — OpenAI Codex

Wszystkie 7 skilli zweryfikowane na żywo na Codex v0.140.0 / gpt-5.5 (2026-06-17).

## 0. Masz Codeksa?

```bash
npm install -g @openai/codex   # pakiet @openai/codex (nie "codex")
codex --version
codex                          # pierwsze uruchomienie: zaloguj się kontem ChatGPT
```

## Wariant A — same skille (najprostszy, zalecany na start)

**Z gotowej paczki ZIP** (bez klonowania repo) — pobierz [`cykl-lifecycle-skills.zip`](https://github.com/witczakm/cykl-lifecycle/releases/latest/download/cykl-lifecycle-skills.zip) z najnowszego wydania. Archiwum ma 7 folderów `cykl-*` w korzeniu, więc rozpakowujesz je wprost:

```bash
mkdir -p ~/.agents/skills
unzip -o ~/Downloads/cykl-lifecycle-skills.zip -d ~/.agents/skills/
```

`-o` nadpisuje istniejące pliki — ta sama komenda instaluje i aktualizuje.

**Albo z klonu repo:**

```bash
mkdir -p ~/.agents/skills
cp -r skills/cykl-* ~/.agents/skills/
```

Zrestartuj Codex, wpisz `/skills` (ma być widocznych 7), potem `$cykl-kickoff`.

## Wariant B — jako plugin Codeksa

Repo zawiera manifest (`.codex-plugin/plugin.json`) i przykładowy marketplace (`marketplace.json`).

```bash
mkdir -p ~/.agents/plugins/cykl-lifecycle
cp -r .codex-plugin skills  ~/.agents/plugins/cykl-lifecycle/
cp marketplace.json         ~/.agents/plugins/marketplace.json
```

Potem w Codeksie podłącz plugin: wpisz `$plugin-creator` i poproś o podłączenie pluginu z `~/.agents/plugins/cykl-lifecycle` do marketplace, albo otwórz katalog pluginów i zainstaluj z marketplace „Michał — personal plugins". Zrestartuj Codex.

## Aktualizacja do nowszej wersji

**Najpierw sprawdź, co masz zainstalowane:**

```bash
grep -h "cykl-lifecycle v" ~/.agents/skills/cykl-*/SKILL.md | sort -u
# oczekiwane po aktualizacji: <!-- cykl-lifecycle v2.6.0 -->
```

Marker siedzi w każdym `SKILL.md` tuż pod frontmatterem. Jeśli komenda zwróci **więcej niż jedną linię**, masz wymieszane wersje — usuń wszystko i wgraj od nowa.

**Aktualizacja z paczki ZIP** — pobierz [`cykl-lifecycle-skills.zip`](https://github.com/witczakm/cykl-lifecycle/releases/latest/download/cykl-lifecycle-skills.zip) i rozpakuj z `-o`:

```bash
rm -rf ~/.agents/skills/cykl-*     # usuń stare, żeby nie zostały pliki spoza nowej wersji
unzip -o ~/Downloads/cykl-lifecycle-skills.zip -d ~/.agents/skills/
```

**Aktualizacja jedną komendą** (pobiera skille wprost z GitHuba, nadpisuje istniejące):

```bash
curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash -s -- codex
```

**Albo ręcznie**, z pobranego repo:

```bash
cd cykl-lifecycle && git pull          # jeśli masz klon
rm -rf ~/.agents/skills/cykl-*         # usuń stare — inaczej zostaną pliki, których nowa wersja już nie ma
cp -r skills/cykl-* ~/.agents/skills/
```

**Jeśli instalowałeś wariantem B (jako plugin)** — podmień też zawartość katalogu pluginu:

```bash
rm -rf ~/.agents/plugins/cykl-lifecycle/skills
cp -r .codex-plugin skills ~/.agents/plugins/cykl-lifecycle/
```

**Na koniec zrestartuj Codeksa** i sprawdź `/skills` — ma być widocznych 7. Skille ładują się na starcie sesji, więc bez restartu nadal działa stara wersja.

> **Czy aktualizacja zepsuje istniejące projekty?** Nie. 2.6.0 nie łamie kompatybilności: nowe pole `STATE_PROBE` w `PROJECT_CONFIG` jest opcjonalne — jego brak daje zachowanie sprzed zmiany, a `/start` po prostu pominie pomiar zewnętrzny. Dokumenty stanu założone starszą wersją czytają się bez migracji.

## Jak wołać skille

| Sposób | Jak |
|---|---|
| jawnie | `$cykl-start`, `$cykl-kickoff`, … |
| z menu | `/skills` → wybierz |
| zdaniem | „gdzie jesteśmy w projekcie?" |

`/start` jako slash to **Claude-izm** — w Codeksie użyj `$cykl-start`. `cykl-kickoff` odpala się **tylko** jawnie (`allow_implicit_invocation: false`), bo scaffolduje strukturę.

## ⚠ Bezpieczeństwo — tryb zatwierdzania

Codex to **agent**: wykonuje realne komendy i potrafi sięgnąć **poza** katalog projektu.

- Ustaw rozsądny tryb zatwierdzania: `/approvals` w sesji (lub `--sandbox` / `approval_policy` w `~/.codex/config.toml`).
- **Czytaj, co zatwierdzasz** — odrzucaj akcje poza bieżącym projektem albo komendy systemowe (`pg_dump`, `npx`, `rm`, `docker`…), których świadomie nie zleciłeś.
- Skille cykla zapisują tylko dokumenty stanu w katalogu projektu i **nigdy nie wykonują git mutującego** (`add`, `commit`, `push`, `stash`) — dostajesz gotowy blok do wklejenia. Od 2.5.0 wykonują komendy **pomiarowe z białej listy** (`rev-parse`, `rev-list`, `log`, `show`, `diff --stat`) — wyłącznie odczyt.

**Higiena (opcjonalna).** Przy wielu zainstalowanych skillach Codex skraca opisy (budżet ~2%) i chętnie odpala inne skille. Na czysto-cyklowe sesje możesz wyłączyć nieużywane w `~/.codex/config.toml`:
```toml
[[skills.config]]
path = "/ścieżka/do/SKILL.md"
enabled = false
```

## /lekcja-g na Codeksie

Lekcja globalna ląduje w **`~/.codex/AGENTS.md`** (sekcja „cykl-lifecycle — global lessons", numeracja GL-NNN) — to plik globalnych instrukcji czytany na starcie każdej sesji w każdym projekcie. Zawsze za Twoją zgodą; sandbox może poprosić o zatwierdzenie zapisu poza katalogiem projektu (to oczekiwane).
