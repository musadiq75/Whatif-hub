# VIDEO 1 — EXECUTION PACKAGE (production-ready, handoff-complete) — rev 3

**Folder:** `production/video-1/execution/`
**Branch:** `production/execution-package-video-1` (PR #2 — NOT merged, awaiting second-review verification)
**Rev 3 (2026-11-26):** second-review corrections — narration single-mix fix, title-card boundary fix, 94-cue caption rule, `06-01a/b/c/d` naming standard, chronological validated timeline matching, resolution gate resolving the upscaling contradiction, plus re-audit fixes (text-card generation commands, computed narration delay, music bed covering lead-in/outro, silence trimming). Script untouched.

**Execution status:** NO command in this package has been executed — this environment has no runtime. Syntax is hand-audited; the operator verifies per-step outputs using the included check commands.

## File map

| File | Contents |
|---|---|
| `00-README.md` | This guide |
| `01-SHOT-PROMPTS.md` | All shot prompts (43 rows → 61 units), continuity tokens — rev 3 naming |
| `02-NARRATION-TTS.md` | Complete approved Script 1, TTS-ready — LOCKED VERBATIM (unchanged since rev 1) |
| `03-CAPTIONS.srt` | 94 cues, timing structure — rev 3: no end-card cue, last cue ends at last spoken word |
| `04-ASSEMBLY-RUNBOOK.md` | FFmpeg assembly + mix — rev 3: single narration mix, real-timestamp validated timeline, resolution gate, card commands, re-audited |
| `05-TOOLING.md` | Free/low-cost tools per stage — tiers verified 2026-11-26 (unchanged in rev 3) |
| `06-ASSET-SPLIT.md` | AshnaAI vs external capability split — rev 3 naming |
| `07-PRE-RENDER-CHECKLIST.md` | Complete manifest (61 units, `<title_card>` at 0.000), timeline_cues.csv, existence checks, sign-off gate |

## Render sequence

1. **Narration:** generate from `02-NARRATION-TTS.md` (Edge-TTS per `05-TOOLING.md`) → cleanup + loudnorm + silence trim (runbook Step 1).
2. **Real timestamps:** WhisperX → runbook Step 2 script → `timeline.csv` (chronological matching, ambiguity detection, validation; title card at 0.000, first narration shot at first-word time) + 94-cue SRT regeneration + computed narration delay.
3. **Footage:** 59 clips per `01-SHOT-PROMPTS.md` (Veo primary; watermarked outputs rejected; verify resolution before generation).
4. **Audio assets:** 6 music + 27 SFX per `05-TOOLING.md`.
5. **Pre-render gate:** `07` section C existence checks + section D sign-off.
6. **Assembly:** resolution gate → normalize → re-time → render 2 text cards → concat 61 units → letterbox/grain/grade → music bed → music-only ducking → single narration mix → loudness → 2-pass export → playback verify.
7. **QC:** runbook §8; only then is Video 1 finished.

## Key rules

- Script 1 LOCKED verbatim — `02-NARRATION-TTS.md` byte-identical since rev 1.
- Narration is mixed exactly once (runbook 6c); `music_ducked.wav` contains zero narration.
- No watermarked final assets; no sub-1080p clips except documented waivers (≥960×540, listed in `work/resolution_waivers.csv`).
- Title card starts at 0.000; first narration shot starts at the actual first-word timestamp.
- 94 caption cues; no cue beyond video duration; end card uncaptioned.
- Scene 5 speculation labeled; no invented statistics.
- Asset count of record: 61 units (59 generated + 2 cards) / 59 keyframes / 6 music / 27 SFX / 94 caption cues / 1 narration.
