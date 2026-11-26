# VIDEO 1 RENDER PIPELINE — "What If Gravity Doubled at Midnight?"

One command on any machine with Python 3.11+ produces the finished 1080p MP4:
narration (Edge TTS, free), your ordered footage (Pexels/Pixabay, free),
synchronized subtitles, background music, and automated QC.

Cost: **0 rupees / 0 dollars.** No paid API, no credits, no card.

## Files in this folder
| File | Purpose |
|---|---|
| `scenes.json` | 16 environments, ordered search terms (storyboard order) |
| `make_video.sh` | Main driver: runs MoneyPrinterTurbo with the verbatim script |
| `scripts/fetch_materials.py` | Downloads ordered clips + writes ATTRIBUTION.md |
| `scripts/qc_check.sh` | Automated quality checks on the final MP4 |
| `scripts/config.example.toml` | WebUI config (CLI path doesn't need it) |

## Prerequisites (one-time, ~10 minutes)
1. **Pexels API key (free, no card):** pexels.com/api → Get Started → copy key.
   Set it as an env var in each session: `export PEXELS_API_KEY=your_key`
2. Background music: download one cinematic ambient track from the
   **YouTube Audio Library** (studio.youtube.com → Audio library, free for
   commercial use) and save as `production/video-1/assets/bgm.mp3`.

---

## OPTION A — Install on a PC/Mac/Linux (recommended, fastest render)
```bash
# 1. Install MoneyPrinterTurbo (official method, ~5 min)
python3.11 -m venv ~/mpt-venv && source ~/mpt-venv/bin/activate
pip install mpt            # official PyPI package by harry0703

# 2. Get the pipeline files
git clone https://github.com/musadiq75/Whatif-hub.git
cd Whatif-hub && git checkout feature/video-1-mpt-pipeline

# 3. Put a cinematic track at production/video-1/assets/bgm.mp3
export PEXELS_API_KEY=your_key

# 4. Fetch footage (~10 min, ~40 clips)
cd production/video-1/pipeline
python3 scripts/fetch_materials.py scenes.json --out-dir ../materials

# 5. Render (~30-90 min on a normal PC)
bash make_video.sh

# 6. QC the result
bash scripts/qc_check.sh <path/to/final.mp4>
```

## OPTION B — Install on Android with Termux (works, slower)
Termux gives a full Linux environment with Python and FFmpeg. A phone CPU
renders a 9-minute 1080p video slowly (expect 1-3+ hours) but it works.

```bash
# In Termux:
pkg update && pkg upgrade
pkg install python git ffmpeg rust binutils libjpeg-turbo
# (rust is needed to build some Python packages on Android)

# 1. Install MoneyPrinterTurbo
git clone https://github.com/harry0703/MoneyPrinterTurbo.git ~/MoneyPrinterTurbo
cd ~/MoneyPrinterTurbo
pip install -r requirements.txt          # may take 15-30 min on a phone

# 2. Clone your pipeline
git clone https://github.com/musadiq75/Whatif-hub.git ~/Whatif-hub
cd ~/Whatif-hub && git checkout feature/video-1-mpt-pipeline

# 3. Music + key + footage + render (same as Option A steps 3-5)
cd production/video-1/pipeline
export PEXELS_API_KEY=your_key
python3 scripts/fetch_materials.py scenes.json --out-dir ../materials
bash make_video.sh

# 4. QC
bash scripts/qc_check.sh ~/MoneyPrinterTurbo/storage/tasks/<TASK_ID>/final-1.mp4
```

**Termux tips:** keep the phone plugged in and screen on; run inside a
`tmux` session (`pkg install tmux`, run `tmux`, start render, detach with
Ctrl+B then D) so the render survives app switching.

## OPTION C — Google Colab (free cloud, no install on your device)
MoneyPrinterTurbo officially supports Colab - open the official notebook
linked in its README. Then upload the `pipeline/` folder from this branch,
install keys as above, and run the same steps. Free tier renders are
usually faster than a phone.

---

## How the script stays verbatim
`make_video.sh` reads `production/video-1/pipeline/script.txt`, which is the
approved Script 1 copied character-for-character from
`production/video-1/Video-1-Production-Package.md` §2. Nothing is rewritten
and no `[pause]` tags are injected, so subtitles are verbatim too.

## Output location
MoneyPrinterTurbo writes results to `storage/tasks/<task-id>/` inside the
MoneyPrinterTurbo folder (or the WebUI "download" panel). The driver prints
the exact path when it finishes.

## QC pass criteria (from the production package §8/§9)
- Duration 8:00–9:30, 1920×1080, audio present, integrated loudness ≈ −14 LUFS
- No unintended black sections ≥ 2 s
- `.srt` subtitle file present alongside the MP4
- Manual scrub at 2:30 / 4:30 / 6:00 to confirm A/V sync before upload

## Attribution (license requirement)
`fetch_materials.py` writes `materials/ATTRIBUTION.md` with every clip's
author and source link. Put these in the YouTube description when publishing.
