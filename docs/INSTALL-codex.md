# Instalacja — OpenAI Codex

Wszystkie 7 skilli zweryfikowane na żywo na Codex v0.140.0 / gpt-5.5 (2026-06-17).

## 0. Masz Codeksa?

```bash
npm install -g @openai/codex   # pakiet @openai/codex (nie "codex")
codex --version
codex                          # pierwsze uruchomienie: zaloguj się kontem ChatGPT
```

## Wariant A — same skille (najprostszy, zalecany na start)

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
- Skille cykla zapisują tylko dokumenty stanu w katalogu projektu i **nigdy nie wykonują git**.

**Higiena (opcjonalna).** Przy wielu zainstalowanych skillach Codex skraca opisy (budżet ~2%) i chętnie odpala inne skille. Na czysto-cyklowe sesje możesz wyłączyć nieużywane w `~/.codex/config.toml`:
```toml
[[skills.config]]
path = "/ścieżka/do/SKILL.md"
enabled = false
```

## /lekcja-g na Codeksie

Lekcja globalna ląduje w **`~/.codex/AGENTS.md`** (sekcja „cykl-lifecycle — global lessons", numeracja GL-NNN) — to plik globalnych instrukcji czytany na starcie każdej sesji w każdym projekcie. Zawsze za Twoją zgodą; sandbox może poprosić o zatwierdzenie zapisu poza katalogiem projektu (to oczekiwane).
