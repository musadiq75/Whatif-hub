#!/usr/bin/env bash
# Video 1 driver: renders "What If Gravity Doubled at Midnight?" with MoneyPrinterTurbo.
# The approved script is read VERBATIM from the production package on this branch -
# it is never rewritten, and no pause tags are injected (keeps subtitles verbatim).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/../../.." && pwd)"
MATERIALS_DIR="${REPO_ROOT}/production/video-1/materials"
SCRIPT_FILE="${REPO_ROOT}/production/video-1/pipeline/script.txt"
BGM_FILE="${REPO_ROOT}/production/video-1/assets/bgm.mp3"
MPT_DIR="${MPT_HOME:-$HOME/MoneyPrinterTurbo}"

command -v python3 >/dev/null || { echo "python3 not found"; exit 1; }
[ -d "$MPT_DIR" ] || { echo "MoneyPrinterTurbo not found at $MPT_DIR (see README-PIPELINE.md)"; exit 1; }
[ -f "$SCRIPT_FILE" ] || { echo "script.txt missing"; exit 1; }
[ -d "$MATERIALS_DIR" ] || { echo "materials/ missing - run fetch_materials.py first"; exit 1; }
[ -f "$BGM_FILE" ] || { echo "assets/bgm.mp3 missing - see README-PIPELINE.md step 4"; exit 1; }

# Ordered clip list matching storyboard sequence
CLIPS="$(find "$MATERIALS_DIR" -maxdepth 1 -name '*.mp4' | sort | paste -sd, -)"
[ -n "$CLIPS" ] || { echo "no .mp4 clips found"; exit 1; }

TASK_ID="$(python3 -c 'import uuid;print(uuid.uuid4())')"

cd "$MPT_DIR"
# Voice: en-US-AndrewMultilingualNeural = deep calm male US English (Edge TTS, free, no API key)
uv run python cli.py \
  --video-script "$(cat "$SCRIPT_FILE")" \
  --video-source local \
  --video-materials "$CLIPS" \
  --match-materials-to-script \
  --video-aspect 16:9 \
  --video-fit-mode cover \
  --video-concat-mode sequential \
  --video-clip-duration 5 \
  --voice-name en-US-AndrewMultilingualNeural \
  --voice-rate 0.92 \
  --bgm-type custom \
  --bgm-file "$BGM_FILE" \
  --subtitle-enabled \
  --subtitle-position bottom \
  --subtitle-display-mode sentence \
  --font-size 52 \
  --stroke-width 2 \
  --n-threads 2 \
  --task-id "$TASK_ID"

echo ""
echo "TASK_ID=$TASK_ID"
echo "Rendered file locations:"
find "$MPT_DIR/storage/tasks/$TASK_ID" -name '*.mp4' 2>/dev/null || true
