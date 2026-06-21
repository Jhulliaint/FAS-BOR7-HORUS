#!/usr/bin/env bash
# Package a skill directory into a .zip ready for upload to claude.ai
# (Organization settings ▸ Skills — Team/Enterprise, Owner only).
#
# Usage:   scripts/package_skill.sh commissions-detailed-sales
#          scripts/package_skill.sh                # packages every skill under skills/
#
# Output:  dist/<skill-name>.zip   (top-level entry = the skill folder, containing SKILL.md)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$ROOT/skills"
DIST_DIR="$ROOT/dist"
mkdir -p "$DIST_DIR"

package_one() {
  local name="$1"
  local dir="$SKILLS_DIR/$name"
  [ -f "$dir/SKILL.md" ] || { echo "✗ $name: no SKILL.md, skipping"; return 1; }
  local out="$DIST_DIR/$name.zip"
  rm -f "$out"
  # zip the folder so the archive contains <name>/SKILL.md, <name>/references/…, …
  ( cd "$SKILLS_DIR" && zip -r -q -X "$out" "$name" \
      -x '*/.DS_Store' -x '*/__pycache__/*' -x '*.pyc' )
  echo "✓ $out"
  unzip -l "$out" | sed 's/^/    /'
}

if [ "$#" -ge 1 ]; then
  package_one "$1"
else
  for d in "$SKILLS_DIR"/*/; do
    package_one "$(basename "$d")" || true
  done
fi
