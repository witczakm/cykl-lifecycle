#!/usr/bin/env bash
# cykl-lifecycle — instalator. Pobiera 7 skilli WPROST z GitHuba i kopiuje do agenta.
#
# Użycie (wprost z GitHuba, nic nie trzeba ściągać ręcznie):
#   curl -fsSL https://raw.githubusercontent.com/witczakm/cykl-lifecycle/main/install.sh | bash
#   ... | bash -s -- claude    # tylko ~/.claude/skills (Claude Code / Cowork)
#   ... | bash -s -- codex     # tylko ~/.agents/skills (OpenAI Codex)
#   ... | bash -s -- both      # oba (domyślnie)
set -euo pipefail

REPO="witczakm/cykl-lifecycle"
BRANCH="main"
TARGET="${1:-both}"

command -v curl >/dev/null || { echo "Brak 'curl'."; exit 1; }
command -v tar  >/dev/null || { echo "Brak 'tar'.";  exit 1; }

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
echo "→ Pobieram cykl-lifecycle z github.com/$REPO ($BRANCH)…"
curl -fsSL "https://github.com/$REPO/archive/refs/heads/$BRANCH.tar.gz" | tar -xz -C "$tmp"

src="$(echo "$tmp"/*/skills)"
[ -d "$src" ] || { echo "Nie znalazłem katalogu skills/ w repo — sprawdź REPO/BRANCH."; exit 1; }

install_to() {
  dest="$1"; mkdir -p "$dest"; cp -R "$src"/cykl-* "$dest"/
  n="$(ls -d "$dest"/cykl-* 2>/dev/null | wc -l | tr -d ' ')"
  echo "✓ $dest  (skille cykl-*: $n)"
}

case "$TARGET" in
  claude) install_to "$HOME/.claude/skills" ;;
  codex)  install_to "$HOME/.agents/skills" ;;
  both)   install_to "$HOME/.claude/skills"; install_to "$HOME/.agents/skills" ;;
  *) echo "Nieznany cel: '$TARGET' (użyj: claude | codex | both)"; exit 1 ;;
esac

echo ""
echo "Gotowe. Zrestartuj agenta, potem:"
echo "  • Claude:  /kickoff"
echo "  • Codex:   \$cykl-kickoff   (oraz /skills, by sprawdzić listę)"
