# VIDEO 1 — EXECUTION PACKAGE (production-ready, handoff-complete) — rev 4

**Folder:** `production/video-1/execution/`
**Branch:** `production/execution-package-video-1` (PR #2 — NOT merged, awaiting review)
**Rev 4 (2026-11-26, third review):** canonical **absolute** timebase end-to-end; music coverage computed from the real timeline with looped tracks (apad removed); provisional SRT explicitly labeled (text locked, timings are planning estimates — uploadable file is `work/captions_final.srt`, audio-verified); `<fontfile>` placeholder replaced by a copy-executable font-discovery snippet. `02-NARRATION-TTS.md` byte-for-byte unchanged.

**Execution status:** NOTHING in this package has been executed — this environment has no runtime. Syntax hand-audited only; every step carries a verify command for the operator.

## File map

| File | Contents |
|---|---|
| `00-README.md` | This guide |
| `01-SHOT-PROMPTS.md` | All shot prompts (43 rows → 61 units), continuity tokens |
| `02-NARRATION-TTS.md` | Approved Script 1, TTS-ready — **LOCKED VERBATIM, unchanged** |
| `03-CAPTIONS.srt` | **PROVISIONAL template** — 94 locked cue texts; timings are planning estimates (last cue 08:00 is an estimate artifact, not synchronized evidence); DO NOT UPLOAD |
| `04-ASSEMBLY-RUNBOOK.md` | rev 4 — absolute timebase, computed music spans, font discovery, audio-verified caption generation + validation gate |
| `05-TOOLING.md` | Free/low-cost tools per stage (tiers verified 2026-11-26) |
| `06-ASSET-SPLIT.md` | AshnaAI vs external capability split |
| `07-PRE-RENDER-CHECKLIST.md` | Complete manifest (absolute timebase), timeline_cues.csv, existence checks, sign-off gate |

## Render sequence

1. **Narration:** `02-NARRATION-TTS.md` → Edge-TTS → cleanup + loudnorm + silence trim (runbook Step 1).
2. **Absolute timeline + captions:** WhisperX → `build_timeline.py` writes `timeline.csv` in the **canonical absolute timebase** (title 0.000→6.000; first narration word at 6.000; every boundary absolute; TOTAL = narration end + 5s) and generates `work/captions_final.srt`; validation gate must pass. **No consumer converts time again — SFX, music spans, concat checks all read absolute values.**
3. **Footage:** 59 clips per `01-SHOT-PROMPTS.md` (Veo primary; watermarked outputs rejected; resolution verified before generation).
4. **Audio assets:** 6 music + 27 SFX per `05-TOOLING.md`.
5. **Pre-render gate:** `07` section C + D sign-off.
6. **Assembly:** resolution gate → normalize → re-time → text cards (font discovery included) → concat → letterbox/grain/grade → **computed music spans (looped, full coverage, 2s crossfades)** → music-only ducking → single narration mix (absolute SFX times) → loudness → 2-pass export → playback verify.
7. **Captions:** upload `work/captions_final.srt` (never the provisional file).
8. **QC:** runbook §8; only then is Video 1 finished.

## Key rules

- Script 1 LOCKED verbatim (`02-NARRATION-TTS.md` unchanged).
- **One canonical timebase: absolute video time.** The delay math lives in exactly one place (`build_timeline.py`).
- Music covers 0:00 → end card via looping (no silence padding); spans computed from `timeline.csv`.
- Caption timing correction is complete ONLY when `work/captions_final.srt` exists and passes validation. The committed SRT is a text template.
- No watermarked final assets; no sub-1080p clips except documented waivers.
- Asset count of record: 61 units (59 generated + 2 cards) / 59 keyframes / 6 music / 27 SFX / 94 caption cues / 1 narration.
