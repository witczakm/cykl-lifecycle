# Instalacja — Claude (Code / Cowork / web)

Trzy środowiska Claude. Wybierz swoje.

## Claude Code (terminal) — zalecane

```bash
# 1. Pobierz repo — URL skopiuj z zielonego przycisku "Code → HTTPS" na stronie repo
git clone https://github.com/UZYTKOWNIK/cykl-lifecycle.git
cd cykl-lifecycle

# 2. Wgraj skille globalnie
mkdir -p ~/.claude/skills
cp -r skills/cykl-* ~/.claude/skills/

# 3. Sprawdź
ls ~/.claude/skills/
# cykl-kickoff  cykl-lekcja  cykl-lekcja-globalna  cykl-migawka
# cykl-roadmap  cykl-start   cykl-zamknij
```

Otwórz nową sesję w katalogu projektu i wpisz `/kickoff`.

## Claude Cowork (desktop)

**Settings → Capabilities → Skills → Add skill.** Dodaj każdy z 7 folderów `skills/cykl-*` osobno. Zrestartuj Cowork, otwórz rozmowę, wpisz `/kickoff`.

> `/lekcja-g` (zapis globalny) w Cowork wymaga Claude Code do faktycznego zapisu do `~/.claude/` — Cowork wstawia „kandydata" i daje gotowe polecenie do wklejenia w terminalu. Pozostałe 6 komend działa w pełni.

## Claude.ai (web / mobile)

**Settings → Capabilities → Skills → Add skill** (każdy folder osobno). Ograniczenie: web nie ma dostępu do plików — pomoże w planowaniu, ale zapis do plików projektu wymaga Claude Code lub Cowork.

## Aktualizacja

```bash
rm -rf ~/.claude/skills/cykl-*
cp -r skills/cykl-* ~/.claude/skills/
```

Masz starą wersję `nsos-*`? Usuń, żeby uniknąć konfliktów:
```bash
rm -rf ~/.claude/skills/nsos-*
```

## Rozwiązywanie problemów

- **Skill się nie odpala** — zrestartuj sesję (skille ładują się na starcie). Sprawdź: `ls ~/.claude/skills/cykl-start/` (ma być `SKILL.md`).
- **Odpala się w złym momencie** — powiedz wprost: „nie używaj tu /start, piszemy kod". Każdy skill ma sekcję „NIE używaj gdy…".
- **W Cowork nie widać skilli** — dodaj każdy z 7 folderów osobno (nie cały katalog `skills/`), zrestartuj Cowork.
