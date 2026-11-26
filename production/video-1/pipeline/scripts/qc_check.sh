#!/usr/bin/env bash
# Automated QC for the rendered MP4 (Phase 7 checks).
# Usage: bash qc_check.sh /path/to/final.mp4
set -euo pipefail

MP4="${1:-}"
[ -n "$MP4" ] && [ -f "$MP4" ] || { echo "Usage: qc_check.sh <final.mp4>"; exit 1; }

echo "== 1. Container / streams =="
ffprobe -v error -show_entries format=format_name -of csv=p=0 "$MP4"
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate -of csv=p=0 "$MP4"
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate -of csv=p=0 "$MP4"

echo "== 2. Duration =="
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$MP4")
echo "duration=${DUR}s"
python3 - "$DUR" <<'PY'
import sys
d = float(sys.argv[1])
ok = 8*60 <= d <= 9*60+30
print("duration check:", "PASS" if ok else "FAIL (target 8:00-9:30)")
sys.exit(0 if ok else 1)
PY

echo "== 3. Resolution 1920x1080 =="
RES=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$MP4")
[ "$RES" = "1920,1080" ] && echo "resolution: PASS" || { echo "resolution: FAIL ($RES)"; exit 1; }

echo "== 4. Audio present and loudness =="
AUDIO_OK=$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_type -of csv=p=0 "$MP4")
[ "$AUDIO_OK" = "audio" ] && echo "audio stream: PASS" || { echo "audio stream: FAIL"; exit 1; }
ffmpeg -hide_banner -nostats -i "$MP4" -af loudnorm=I=-14:TP=-1:LRA=11 -f null - 2>&1 | grep -E "Input (Integrated|True Peak)" || true

echo "== 5. Black-screen detection (unintended long blacks) =="
BLACKS=$(ffmpeg -hide_banner -i "$MP4" -vf "blackdetect=d=2:pix_th=0.05" -an -f null - 2>&1 | grep -c black_start || true)
if [ "$BLACKS" -gt 0 ]; then
  echo "blackdetect: WARN ($BLACKS black sections >= 2s) - review manually"
else
  echo "blackdetect: PASS (no blacks >= 2s)"
fi

echo "== 6. Subtitle file (srt) next to output =="
SRT="$(dirname "$MP4")/$(basename "${MP4%.mp4}").srt"
[ -f "$SRT" ] && echo "subtitles: PASS ($SRT)" || echo "subtitles: WARN (.srt not found next to MP4 - check MPT storage/tasks/<id>)"

echo ""
echo "QC COMPLETE - verify A/V sync at 2:30, 4:30, 6:00 by scrubbing once."
