# VIDEO 1 PRODUCTION LOG

Branch: `feature/video-1-mpt-pipeline` | Status date: 2026-11-26

## Verified facts (no assumptions)
- GitHub connection verified (read/write as musadiq75). Pipeline committed on this branch.
- Approved Script 1 located in `production/video-1/Video-1-Production-Package.md` §2,
  copied character-for-character to `pipeline/script.txt`. VERBATIM — not rewritten.
- MoneyPrinterTurbo CLI flags verified against the official `cli.py` source (not docs
  alone): --video-script, --video-source local, --video-materials, --match-materials-to-script,
  --video-aspect 16:9, --video-fit-mode cover, --video-concat-mode sequential,
  --video-clip-duration, --voice-name, --voice-rate, --bgm-type custom, --bgm-file,
  --subtitle-enabled, --subtitle-position, --subtitle-display-mode, --font-size,
  --stroke-width, --n-threads, --task-id. All flags used by make_video.sh are real.
- Free-service audit (Nov 26, 2026): Edge TTS free/no key; Pexels free
  (200 req/hr, 20K/mo, key required, commercial use allowed with attribution);
  Pixabay free (100 req/min, key required); rejected non-commercial free tiers
  (ElevenLabs free, Suno free, Runway/Kling/PixVerse free — watermarked or
  non-commercial).

## Pipeline steps (what runs, in order)
1. `fetch_materials.py` — downloads ~40 ordered clips per scenes.json + ATTRIBUTION.md
2. `make_video.sh` — Edge TTS narration → subtitles → clip assembly → music mix → render
3. `qc_check.sh` — duration/resolution/audio/loudness/black-detect/srt checks

## Render record (fill in when run)
| Field | Value |
|---|---|
| Machine used | _ |
| Date/time | _ |
| TASK_ID | _ |
| Output MP4 path | _ |
| QC results | _ |
| Duration | _ |
| Loudness | _ |
| Defects found | _ |
| Final status | _ |

## Remaining blockers
- Render not yet executed (requires a machine with Python 3.11+ per README
  Option A/B/C — PC, Termux, or Colab). The pipeline itself is complete and
  ready; nothing else blocks the render except a runtime to run it in.
- Background music track must be downloaded once from the free YouTube Audio
  Library into `production/video-1/assets/bgm.mp3` before render.
- Pexels API key required once (free signup, no card).
