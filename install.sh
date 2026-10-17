#!/usr/bin/env bash
# cykl-lifecycle installer. Downloads the skills from GitHub and copies them to your agent.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash
#   ... | bash -s -- claude                    # ~/.claude/skills (Claude Code / Cowork)
#   ... | bash -s -- codex                     # ~/.agents/skills (OpenAI Codex)
#   ... | bash -s -- both                      # both (default)
#   ... | bash -s -- claude --edition multi    # also install cykl-prowadzacy (multi-agent lead)
# Default edition is "core": the seven core skills. Existing cykl-* skills are replaced
# together, so versions never mix.
# CYKL_SKILLS_DIR=/path/to/skills installs from a local checkout instead of downloading.
set -euo pipefail

REPO="witczakm/cykl-lifecycle"
BRANCH="main"
TARGET="both"
EDITION="core"
while [ $# -gt 0 ]; do
  case "$1" in
    --edition) EDITION="${2:-}"; shift 2 || { echo "--edition needs a value (core | multi)"; exit 1; } ;;
    claude|codex|both) TARGET="$1"; shift ;;
    *) echo "Unknown argument: '$1' (use: claude | codex | both, --edition core|multi)"; exit 1 ;;
  esac
done
case "$EDITION" in core|multi) ;; *) echo "Unknown edition: '$EDITION' (use: core | multi)"; exit 1 ;; esac

if [ -n "${CYKL_SKILLS_DIR:-}" ]; then
  src="$CYKL_SKILLS_DIR"
else
  command -v curl >/dev/null || { echo "curl is required."; exit 1; }
  command -v tar  >/dev/null || { echo "tar is required.";  exit 1; }
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
  echo "-> Downloading cykl-lifecycle from github.com/$REPO ($BRANCH)..."
  curl -fsSL "https://github.com/$REPO/archive/refs/heads/$BRANCH.tar.gz" | tar -xz -C "$tmp"
  src="$(echo "$tmp"/*/skills)"
fi
[ -d "$src" ] || { echo "No skills/ directory found - check REPO/BRANCH."; exit 1; }

install_to() {
  dest="$1"; mkdir -p "$dest"
  rm -rf "$dest"/cykl-*
  for d in "$src"/cykl-*; do
    [ "$(basename "$d")" = "cykl-prowadzacy" ] && [ "$EDITION" != "multi" ] && continue
    cp -R "$d" "$dest"/
  done
  n="$(ls -d "$dest"/cykl-* 2>/dev/null | wc -l | tr -d ' ')"
  echo "OK $dest  (cykl-* skills: $n, edition: $EDITION)"
}

case "$TARGET" in
  claude) install_to "$HOME/.claude/skills" ;;
  codex)  install_to "$HOME/.agents/skills" ;;
  both)   install_to "$HOME/.claude/skills"; install_to "$HOME/.agents/skills" ;;
esac

echo ""
echo "Done. Restart your agent, then:"
echo "  - Claude:  /kickoff"
echo "  - Codex:   \$cykl-kickoff   (and /skills to list them)"
