# Install — Claude (Code / Cowork / web)
**English** · [Polski](INSTALL-claude.pl.md)

cykl-lifecycle 3.1 is 7 core skills plus the optional `cykl-prowadzacy` (multi-agent lead).
Install them together: the other skills call `cykl-start/scripts/lifecycle.py`. Python 3.9+ is required.

## Claude Code (terminal) — recommended

```bash
# Local and GitHub editions (7 skills)
curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash -s -- claude

# GitHub + multi-agent edition (8 skills)
curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash -s -- claude --edition multi
```

The installer replaces every `cykl-*` skill in `~/.claude/skills/`, so versions never mix.
Restart Claude Code, open your project and type `/kickoff`.

**Without curl | bash** — download [`cykl-lifecycle-skills.zip`](https://github.com/witczakm/cykl-lifecycle/releases/latest/download/cykl-lifecycle-skills.zip)
(all 8 skill folders at the root of the archive):

```bash
mkdir -p ~/.claude/skills
rm -rf ~/.claude/skills/cykl-*
unzip ~/Downloads/cykl-lifecycle-skills.zip -d ~/.claude/skills/
rm -rf ~/.claude/skills/cykl-prowadzacy   # only if you want the 7-skill editions
```

**From a clone:**

```bash
git clone https://github.com/witczakm/cykl-lifecycle.git
CYKL_SKILLS_DIR="$PWD/cykl-lifecycle/skills" bash cykl-lifecycle/install.sh claude
```

## Claude Cowork (desktop)

Drag [`cykl-lifecycle.plugin`](https://github.com/witczakm/cykl-lifecycle/releases/latest/download/cykl-lifecycle.plugin)
into a conversation. Alternatively, **Settings → Capabilities → Skills → Add skill** and upload each
`cykl-*.zip` from the [latest release](https://github.com/witczakm/cykl-lifecycle/releases/latest)
separately (one zip = one skill; the combined skills ZIP is rejected there). Restart Cowork and type `/kickoff`.

## Claude.ai (web / mobile)

**Settings → Capabilities → Skills → Add skill**, one skill at a time. Limitation: the web app
cannot run the script or write project files, so it helps with planning only. Saving state needs
Claude Code or Cowork.

## Upgrading

Check what you have:

```bash
grep -h "cykl-lifecycle v" ~/.claude/skills/cykl-*/SKILL.md | sort -u
# expected after upgrading: <!-- cykl-lifecycle v3.1.0 -->
```

More than one line means mixed versions: run the installer again. Then **restart the agent**;
skills load when a session starts.

- From 3.0.x: just install 3.1.0; no migration.
- From v2: version 3 is breaking. Follow [MIGRATION-v2.md](MIGRATION-v2.md) before using it on an existing project.
- The `.plugin` file carries its own copy of the skills: if you use both the plugin and the
  folder install, update both.

## Troubleshooting

- **A skill does not trigger:** restart the session; check that `~/.claude/skills/cykl-start/SKILL.md` exists.
- **`/start` stops with an error:** that is deliberate; read the message. The agent must not
  continue from chat memory when the state fails validation.
- **Cowork shows no skills:** add each skill zip separately, not the whole `skills/` folder, then restart.
