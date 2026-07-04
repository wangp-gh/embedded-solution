#!/usr/bin/env bash
# check_no_specs_dead_refs.sh
#
# Scans user-facing files (SKILL.md + references/ + scripts/*.py) for
# `specs/<Vendor>/<Part>.yaml` path references that could mislead a
# public-release user (who does NOT have the private `specs/` directory).
#
# Allowed contexts are lines containing one of these substrings:
#   - "maintainer-only — not shipped in the public release"
#   - "maintainer's private spec database"
#   - "(if installed)"
#   - "not shipped in the public package"
#   - "private spec database"
#
# Exits 0 if clean, 1 if any unreviewed dead ref is found.

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Pattern: `specs/<VendorKey>/<Part>.yaml`
SPECS_PATH_REGEX='`specs/[A-Za-z]+/[A-Za-z0-9_.-]+\.yaml`'

# Allowed context substrings (any match exempts the line)
ALLOWED_CONTEXTS=(
    "maintainer-only — not shipped in the public release"
    "maintainer's private spec database"
    "(if installed)"
    "not shipped in the public package"
    "private spec database"
)

# Build a single "if contains any allowed context, exempt" regex
exempt_regex=""
for ctx in "${ALLOWED_CONTEXTS[@]}"; do
    # Escape for egrep
    esc=$(printf '%s\n' "$ctx" | sed 's/[][\\.*^$/]/\\&/g')
    [ -z "$exempt_regex" ] && exempt_regex="$esc" || exempt_regex="$exempt_regex|$esc"
done

# Collect file list: SKILL.md + everything under references/ + scripts/*.py
files=$( {
    [ -f SKILL.md ] && echo SKILL.md
    find references -type f \( -name "*.md" -o -name "*.py" \) 2>/dev/null
    find scripts -maxdepth 1 -type f -name "*.py" 2>/dev/null
} | sort -u)

exit_code=0
files_scanned=0
files_with_dead_refs=0

while IFS= read -r f; do
    [ -z "$f" ] && continue
    [ ! -f "$f" ] && continue
    files_scanned=$((files_scanned + 1))

    # Lines matching specs_path but not matching any allowed context = dead ref.
    # Use awk for one-pass filtering (no fork per line).
    dead=$(/usr/bin/awk -v pat="$SPECS_PATH_REGEX" -v exempt="$exempt_regex" '
        $0 ~ pat && $0 !~ exempt { printf("%s:%d:%s\n", FILENAME, NR, $0); next }
    ' "$f")

    if [ -n "$dead" ]; then
        files_with_dead_refs=$((files_with_dead_refs + 1))
        echo ""
        echo "❌ $f"
        echo "$dead" | while IFS= read -r line; do
            echo "    $line"
        done
        exit_code=1
    fi
done <<< "$files"

echo ""
echo "Files scanned: $files_scanned"
if [ "$files_with_dead_refs" -eq 0 ]; then
    echo "✅ No dead references to specs/<Vendor>/<Part>.yaml found in user-facing files."
else
    echo "❌ $files_with_dead_refs file(s) have dead refs — see above."
fi

exit $exit_code
