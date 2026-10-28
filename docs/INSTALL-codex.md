# Install — OpenAI Codex
**English** · [Polski](INSTALL-codex.pl.md)

cykl-lifecycle 3.1 is 7 core skills plus the optional `cykl-prowadzacy` (multi-agent lead).
Install them together. Python 3.9+ is required.

## 0. Do you have Codex?

```bash
npm install -g @openai/codex
codex --version
```

## Option A — skills only (recommended)

```bash
# Local and GitHub editions (7 skills)
curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash -s -- codex

# GitHub + multi-agent edition (8 skills)
curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash -s -- codex --edition multi
```

Skills go to `~/.agents/skills/`. Use `both` instead of `codex` to install for Claude and Codex at once.
Offline: unzip [`cykl-lifecycle-skills.zip`](https://github.com/witczakm/cykl-lifecycle/releases/latest/download/cykl-lifecycle-skills.zip)
into `~/.agents/skills/` after removing old `cykl-*` folders.

Restart Codex, type `/skills` to check they are listed, then `$cykl-kickoff`.

## Option B — as a Codex plugin

The repository ships a plugin manifest (`.codex-plugin/plugin.json`) and a sample `marketplace.json`:

```bash
mkdir -p ~/.agents/plugins/cykl-lifecycle
cp -r .codex-plugin skills ~/.agents/plugins/cykl-lifecycle/
cp marketplace.json ~/.agents/plugins/marketplace.json
```

Then install the plugin from that marketplace in Codex and restart it.

## How to call the skills

| Way | How |
|---|---|
| explicitly | `$cykl-start`, `$cykl-kickoff`, … |
| from the menu | `/skills` → pick one |
| in a sentence | "where are we in this project?" |

`/start`-style slash commands are a Claude convention; in Codex use `$cykl-start`.

## Upgrading

```bash
grep -h "cykl-lifecycle v" ~/.agents/skills/cykl-*/SKILL.md | sort -u
# expected after upgrading: <!-- cykl-lifecycle v3.1.0 -->
```

More than one line means mixed versions: run the installer again. If you installed Option B,
replace `~/.agents/plugins/cykl-lifecycle/skills` too. Restart Codex afterwards.
From v2, follow [MIGRATION-v2.md](MIGRATION-v2.md) first.

## Safety — approval mode

Codex is an agent: it runs real commands and can reach outside the project folder.

- Set a sensible approval mode (`/approvals` in a session, or `approval_policy` / `--sandbox` in `~/.codex/config.toml`).
- Read what you approve; reject actions outside the current project you did not ask for.
- The lifecycle skills write only lifecycle files in the project, through `lifecycle.py`. They
  commit or publish only when you ask separately.

## /lesson-global on Codex

A global lesson is recorded as **proposed** in the project. It is applied to global instructions
(for example `~/.codex/AGENTS.md`) only with your explicit approval; the skill gives you the text
and never installs it on its own.
