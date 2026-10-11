#!/bin/sh
# Commit and push the generated corpus in batches (one commit per category / per group of years),
# so that each push stays small. Usage: scripts/publish.sh [category ...]
set -e
cd "$(dirname "$0")/.."
TRAILER="Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BATCH=${BATCH:-3000}

commit_push() {
  if ! git diff --cached --quiet; then
    git commit -q -m "$1" -m "$TRAILER"
    git push -q origin master
    echo "pushed: $1"
  fi
}

for cat in "${@:-constitution codes lois ordonnances decrets decrets-lois}"; do
  for c in $cat; do
    [ -d "$c" ] || { git add -A "$c" 2>/dev/null || true; commit_push "Update $c"; continue; }
    case "$c" in
      constitution|codes)
        git add -A "$c"; commit_push "Update $c" ;;
      *)
        n=0; first=""; last=""
        for y in $(ls "$c" | sort); do
          git add -A "$c/$y"
          [ -z "$first" ] && first=$y
          last=$y
          n=$((n + $(find "$c/$y" -type f | wc -l)))
          if [ "$n" -ge "$BATCH" ]; then
            commit_push "Update $c ($first-$last)"; n=0; first=""
          fi
        done
        git add -A "$c"
        commit_push "Update $c (${first:-removals}-$last)" ;;
    esac
  done
done
