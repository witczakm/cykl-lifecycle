# Instalacja — Claude (Code / Cowork / web)

Trzy środowiska Claude. Wybierz swoje.

## Najprościej: gotowa paczka ZIP (bez gita)

Pobierz **[`cykl-lifecycle-skills.zip`](https://github.com/witczakm/cykl-lifecycle/releases/latest/download/cykl-lifecycle-skills.zip)** z najnowszego wydania. Archiwum zawiera 7 folderów `cykl-*` **w korzeniu**, więc rozpakowujesz je wprost do katalogu skilli:

```bash
mkdir -p ~/.claude/skills
unzip -o ~/Downloads/cykl-lifecycle-skills.zip -d ~/.claude/skills/
ls ~/.claude/skills/
# cykl-kickoff  cykl-lekcja  cykl-lekcja-globalna  cykl-migawka
# cykl-roadmap  cykl-start   cykl-zamknij
```

`-o` nadpisuje istniejące pliki — ta sama komenda instaluje i aktualizuje. Zrestartuj sesję i wpisz `/kickoff`.

## Claude Code (terminal) — zalecane

```bash
# 1. Pobierz repo — URL skopiuj z zielonego przycisku "Code → HTTPS" na stronie repo
git clone https://github.com/witczakm/cykl-lifecycle.git
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

## Aktualizacja do nowszej wersji

**Najpierw sprawdź, co masz zainstalowane:**

```bash
grep -h "cykl-lifecycle v" ~/.claude/skills/cykl-*/SKILL.md | sort -u
# oczekiwane po aktualizacji: <!-- cykl-lifecycle v2.8.0 -->
```

Marker siedzi w każdym `SKILL.md` tuż pod frontmatterem. Jeśli komenda zwróci **więcej niż jedną linię**, masz wymieszane wersje — usuń wszystko i wgraj od nowa.

### Claude Code — jedną komendą

```bash
curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash -s -- claude
```

Pobiera skille wprost z GitHuba i nadpisuje istniejące. Nie musisz mieć klonu repo.

### Claude Code — z paczki ZIP

```bash
unzip -o ~/Downloads/cykl-lifecycle-skills.zip -d ~/.claude/skills/
```

`-o` nadpisuje w miejscu, więc stare pliki znikają razem z podmienianymi. Jeśli poprzednia wersja miała plik, którego nowa już nie ma, usuń katalogi przed rozpakowaniem: `rm -rf ~/.claude/skills/cykl-*`.

### Claude Code — ręcznie

```bash
cd cykl-lifecycle && git pull      # jeśli masz klon
rm -rf ~/.claude/skills/cykl-*     # usuń stare — inaczej zostaną pliki, których nowa wersja już nie ma
cp -r skills/cykl-* ~/.claude/skills/
```

### Cowork (desktop)

Pobierz świeży **[`cykl-lifecycle.plugin`](https://github.com/witczakm/cykl-lifecycle/raw/main/cykl-lifecycle.plugin)** i przeciągnij do rozmowy — instalacja nadpisze poprzednią wersję wszystkich 7 skilli naraz.

> ⚠️ Paczka `.plugin` zawiera **własną kopię** skilli. Aktualizacja repo nie aktualizuje paczki i odwrotnie — jeśli używasz obu ścieżek, odśwież obie.

### Claude.ai (web / mobile)

**Settings → Capabilities → Skills** — usuń 7 starych wpisów `cykl-*` i dodaj foldery na nowo. Web nie ma mechanizmu podmiany w miejscu.

### Po aktualizacji

**Zrestartuj agenta** — skille ładują się na starcie sesji, więc bez restartu nadal działa stara wersja. Potem zweryfikuj markerem (komenda na górze tej sekcji).

Masz starą wersję `nsos-*`? Usuń, żeby uniknąć konfliktów:
```bash
rm -rf ~/.claude/skills/nsos-*
```

> **Czy aktualizacja zepsuje istniejące projekty?** Nie. 2.6.0 nie łamie kompatybilności: nowe pole `STATE_PROBE` w `PROJECT_CONFIG` jest opcjonalne — jego brak daje zachowanie sprzed zmiany, a `/start` pominie pomiar zewnętrzny. Dokumenty stanu założone starszą wersją czytają się bez migracji. Jeśli chcesz włączyć pomiar w istniejącym projekcie, dopisz do `PROJECT_CONFIG.md` jedną linię, np. `STATE_PROBE=git rev-parse --short HEAD; git rev-list --left-right --count origin/main...HEAD`.

## Rozwiązywanie problemów

- **Skill się nie odpala** — zrestartuj sesję (skille ładują się na starcie). Sprawdź: `ls ~/.claude/skills/cykl-start/` (ma być `SKILL.md`).
- **Odpala się w złym momencie** — powiedz wprost: „nie używaj tu /start, piszemy kod". Każdy skill ma sekcję „NIE używaj gdy…".
- **W Cowork nie widać skilli** — dodaj każdy z 7 folderów osobno (nie cały katalog `skills/`), zrestartuj Cowork.
