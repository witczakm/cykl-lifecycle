# Instalacja — Claude (Code / Cowork / web)
[English](INSTALL-claude.md) · **Polski**

cykl-lifecycle 3.1 to 7 podstawowych skilli plus opcjonalny `cykl-prowadzacy` (prowadzący
wieloagentowy). Instaluj je razem: pozostałe skille wywołują `cykl-start/scripts/lifecycle.py`.
Wymagany jest Python 3.9+.

## Claude Code (terminal) — zalecane

```bash
# Edycje Lokalna i GitHub (7 skilli)
curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash -s -- claude

# Edycja GitHub + wielu agentów (8 skilli)
curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash -s -- claude --edition multi
```

Instalator podmienia wszystkie skille `cykl-*` w `~/.claude/skills/`, więc wersje się nie mieszają.
Zrestartuj Claude Code, otwórz projekt i wpisz `/kickoff`.

**Bez curl | bash** — pobierz [`cykl-lifecycle-skills.zip`](https://github.com/witczakm/cykl-lifecycle/releases/latest/download/cykl-lifecycle-skills.zip)
(wszystkie 8 folderów skilli w korzeniu archiwum):

```bash
mkdir -p ~/.claude/skills
rm -rf ~/.claude/skills/cykl-*
unzip ~/Downloads/cykl-lifecycle-skills.zip -d ~/.claude/skills/
rm -rf ~/.claude/skills/cykl-prowadzacy   # tylko jeśli chcesz edycję z 7 skillami
```

**Z klonu repozytorium:**

```bash
git clone https://github.com/witczakm/cykl-lifecycle.git
CYKL_SKILLS_DIR="$PWD/cykl-lifecycle/skills" bash cykl-lifecycle/install.sh claude
```

## Claude Cowork (desktop)

Przeciągnij [`cykl-lifecycle.plugin`](https://github.com/witczakm/cykl-lifecycle/releases/latest/download/cykl-lifecycle.plugin)
do rozmowy. Albo: **Settings → Capabilities → Skills → Add skill** i wgraj osobno każdy plik
`cykl-*.zip` z [najnowszego wydania](https://github.com/witczakm/cykl-lifecycle/releases/latest)
(jeden zip = jeden skill; zbiorczego ZIP-a ze skillami aplikacja nie przyjmie). Zrestartuj Cowork i wpisz `/kickoff`.

## Claude.ai (web / telefon)

**Settings → Capabilities → Skills → Add skill**, po jednym skillu. Ograniczenie: aplikacja webowa
nie uruchamia skryptu i nie zapisuje plików projektu, więc pomoże tylko w planowaniu. Do zapisu
stanu potrzebny jest Claude Code albo Cowork.

## Aktualizacja

Sprawdź, co masz zainstalowane:

```bash
grep -h "cykl-lifecycle v" ~/.claude/skills/cykl-*/SKILL.md | sort -u
# po aktualizacji powinno być: <!-- cykl-lifecycle v3.1.0 -->
```

Więcej niż jedna linia oznacza wymieszane wersje: uruchom instalator ponownie. Potem
**zrestartuj agenta** — skille ładują się na starcie sesji.

- Z 3.0.x: po prostu zainstaluj 3.1.0; migracja nie jest potrzebna.
- Z v2: wersja 3 nie jest zgodna wstecz. Zanim użyjesz jej w istniejącym projekcie, przejdź
  [MIGRATION-v2.md](MIGRATION-v2.md) (po angielsku).
- Plik `.plugin` ma własną kopię skilli: jeśli używasz i pluginu, i instalacji folderów, zaktualizuj oba.

## Rozwiązywanie problemów

- **Skill się nie uruchamia:** zrestartuj sesję; sprawdź, czy istnieje `~/.claude/skills/cykl-start/SKILL.md`.
- **`/start` zatrzymuje się z błędem:** to celowe; przeczytaj komunikat. Gdy stan nie przechodzi
  sprawdzenia, agent nie może jechać dalej na pamięci z rozmowy.
- **Cowork nie pokazuje skilli:** dodaj każdy zip skilla osobno (nie cały folder `skills/`) i zrestartuj.
