# Instalacja — OpenAI Codex
[English](INSTALL-codex.md) · **Polski**

cykl-lifecycle 3.1 to 7 podstawowych skilli plus opcjonalny `cykl-prowadzacy` (prowadzący
wieloagentowy). Instaluj je razem. Wymagany jest Python 3.9+.

## 0. Masz Codeksa?

```bash
npm install -g @openai/codex
codex --version
```

## Wariant A — same skille (zalecany)

```bash
# Edycje Lokalna i GitHub (7 skilli)
curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash -s -- codex

# Edycja GitHub + wielu agentów (8 skilli)
curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash -s -- codex --edition multi
```

Skille trafiają do `~/.agents/skills/`. Zamiast `codex` użyj `both`, żeby zainstalować naraz dla
Claude i Codeksa. Offline: usuń stare foldery `cykl-*` i rozpakuj
[`cykl-lifecycle-skills.zip`](https://github.com/witczakm/cykl-lifecycle/releases/latest/download/cykl-lifecycle-skills.zip)
do `~/.agents/skills/`.

Zrestartuj Codeksa, wpisz `/skills`, żeby sprawdzić, czy są na liście, potem `$cykl-kickoff`.

## Wariant B — jako plugin Codeksa

Repozytorium zawiera manifest pluginu (`.codex-plugin/plugin.json`) i przykładowy `marketplace.json`:

```bash
mkdir -p ~/.agents/plugins/cykl-lifecycle
cp -r .codex-plugin skills ~/.agents/plugins/cykl-lifecycle/
cp marketplace.json ~/.agents/plugins/marketplace.json
```

Potem zainstaluj plugin z tego marketplace w Codeksie i zrestartuj go.

## Jak wołać skille

| Sposób | Jak |
|---|---|
| jawnie | `$cykl-start`, `$cykl-kickoff`, … |
| z menu | `/skills` → wybierz |
| zdaniem | „gdzie jesteśmy w tym projekcie?” |

Komendy w stylu `/start` to konwencja Claude; w Codeksie użyj `$cykl-start`.

## Aktualizacja

```bash
grep -h "cykl-lifecycle v" ~/.agents/skills/cykl-*/SKILL.md | sort -u
# po aktualizacji powinno być: <!-- cykl-lifecycle v3.1.0 -->
```

Więcej niż jedna linia oznacza wymieszane wersje: uruchom instalator ponownie. Jeśli instalowałeś
wariantem B, podmień też `~/.agents/plugins/cykl-lifecycle/skills`. Na koniec zrestartuj Codeksa.
Z v2 najpierw przejdź [MIGRATION-v2.md](MIGRATION-v2.md) (po angielsku).

## Bezpieczeństwo — tryb zatwierdzania

Codex to agent: wykonuje prawdziwe komendy i może sięgnąć poza folder projektu.

- Ustaw rozsądny tryb zatwierdzania (`/approvals` w sesji albo `approval_policy` / `--sandbox` w `~/.codex/config.toml`).
- Czytaj, co zatwierdzasz; odrzucaj akcje spoza bieżącego projektu, o które nie prosiłeś.
- Skille cyklu zapisują tylko pliki stanu w projekcie, przez `lifecycle.py`. Commit albo publikację
  robią tylko na Twoją osobną prośbę.

## /lekcja-g w Codeksie

Lekcja globalna jest zapisywana w projekcie jako **proponowana**. Do instrukcji globalnych
(np. `~/.codex/AGENTS.md`) trafia wyłącznie za Twoją wyraźną zgodą; skill daje Ci gotowy tekst
i nigdy nie wstawia go sam.
