# VIDEO 1 — EXECUTION PACKAGE (production-ready, handoff-complete) — rev 2

**Folder:** `production/video-1/execution/`
**Branch:** `production/execution-package-video-1`
**Rev 2 (2026-11-26):** corrections per PR #2 review — FFmpeg syntax audited, complete working examples, real-timestamp timing workflow, verified provider free tiers, corrected asset counts (61 render units / 59 keyframes), pre-render checklist added. Script untouched.

## File map

| File | Contents |
|---|---|
| `00-README.md` | This guide |
| `01-SHOT-PROMPTS.md` | All shot prompts (43 shot rows → **61 render units**), continuity tokens, camera, lighting, transitions |
| `02-NARRATION-TTS.md` | Complete approved Script 1, TTS-ready, timed blocks, pause markers — LOCKED VERBATIM |
| `03-CAPTIONS.srt` | Full caption timing structure (regenerate timings from WhisperX — runbook 2b; text verbatim) |
| `04-ASSEMBLY-RUNBOOK.md` | FFmpeg assembly + audio-mixing runbook (rev 2: audited syntax, working examples, real timestamps) |
| `05-TOOLING.md` | Free/low-cost tools per stage (rev 2: tiers verified 2026-11-26, tested vs documentation clearly flagged) |
| `06-ASSET-SPLIT.md` | What AshnaAI can generate vs external needs (rev 2: corrected counts) |
| `07-PRE-RENDER-CHECKLIST.md` | **Complete 61-unit manifest + timeline_cues.csv + pre-render existence checks + sign-off checklist** |

## Render sequence

1. **Narration:** generate from `02-NARRATION-TTS.md` (Edge-TTS per `05-TOOLING.md`) → `audio/narration.wav`.
2. **Real timestamps:** WhisperX word-level pass → regenerate caption timings AND build `timeline.csv` via the runbook Step 2 script. **Never scale estimated boundaries.**
3. **Footage:** generate 61 clips from `01-SHOT-PROMPTS.md` (Google Flow/Veo primary — 50 free credits/day; PixVerse overflow; all watermarked outputs rejected). Multi-part shots produce lettered files (01-07a.mp4 …).
4. **Assets:** 6 music tracks + 27 SFX per `05-TOOLING.md` (YouTube Audio Library / Pixabay / Freesound CC0).
5. **Pre-render gate:** complete `07-PRE-RENDER-CHECKLIST.md` section C existence checks and section D sign-off — assembly may not begin otherwise.
6. **Assembly + mix + export:** runbook Steps 3–7 in order, verifying after each stage.
7. **QC:** runbook §8 checklist; only then is Video 1 finished.

## Key rules baked into every file

- Script 1 is LOCKED verbatim. Nothing in this folder alters it.
- No watermarked assets in the final render (Veo SynthID-invisible is the only verified free tier that clears this bar).
- No slideshow: every shot has specified motion; pacing is driven by real narration timestamps.
- Scene 5 speculation is labeled; no invented statistics.
- Asset count of record: **61 render units / 59 keyframes / 6 music / 27 SFX / 1 narration / 1 caption file.**
