# VIDEO 1 — TOOLING (rev 2 — free tiers verified 2026-11-26)

**Verification method:** web research against each provider's current published plans, cross-checked across multiple independent sources (search dated Nov 26, 2026). "TESTED" = I or the production operator have actually generated output through it; "VERIFIED DOCUMENTATION" = confirmed from current provider pages/third-party audits, not personal trial. **No video provider was tested from this environment — this environment cannot execute generation APIs** (documented in the capability audit). Plan availability changes frequently; re-verify week-of-use.

## Stage 1 — Narration (TTS)

| Option | Status | Free-tier facts (verified 2026-11-26) |
|---|---|---|
| **Edge-TTS (`edge-tts` Python package)** | VERIFIED DOCUMENTATION | Free, no API key, runs offline after install. Voices `en-US-GuyNeural` / `en-US-AndrewNeural` fit the calm-documentary profile. Not tested from this environment (no runtime). **Primary recommendation.** |
| ElevenLabs free tier | VERIFIED DOCUMENTATION | 10,000 credits/month; website TTS input up to 10,000 chars per generation with Eleven v4 (5,000 other models); MP3 (128 kbps) or WAV downloads from the website; **non-commercial use only with attribution on the free tier** — commercial rights start at Starter ($6/mo). Script 1 ≈ 6,500 characters fits in one month's quota. |
| Piper TTS | VERIFIED DOCUMENTATION | Free, open-source, offline; more synthetic quality. Fallback. |

**Verdict:** Edge-TTS (free, unlimited for our use, no key, no watermark/licensing issues). ElevenLabs free tier is higher quality but non-commercial attribution terms make it a **risky fit for a monetized channel** — flagged, not recommended while monetization is intended.

## Stage 2 — Word-level timestamps

| Option | Status |
|---|---|
| **WhisperX** | VERIFIED DOCUMENTATION (repo inspected directly; install not tested — no runtime here). Open-source; CPU-viable for 9 min. Primary. |
| faster-whisper (`word_timestamps=True`) | VERIFIED DOCUMENTATION. Fallback if WhisperX install fails. |

## Stage 3 — Footage (61 render units) — free tiers re-verified 2026-11-26

| Provider | Free tier (verified) | Watermark on free output | Commercial use on free tier |
|---|---|---|---|
| **Google Flow (Veo 3 / Gemini)** | 50 credits/day, refreshed daily | Invisible (SynthID) in most countries | Yes, per Google terms for Flow outputs |
| Kling AI (Basic) | Monthly free credits, **amount not published** (the "66/day" figure is obsolete since Oct 2026 — credits policy changed) | **Yes — visible watermark** | **No — non-commercial, sub-1080p** |
| Hailuo (MiniMax) | One-time welcome credits, **expire 3 days after signup** | **Yes — visible watermark** | **No on free** |
| PixVerse | 30 credits/day, 60 at start | **Yes** | Unclear — verify terms |
| Luma Dream Machine | **No free plan listed (removed; verified Nov 15–16, 2026).** Older free/Lite plans gone. | n/a | n/a — do not plan on it |
| Runway | One-time starter credits | Yes | No |
| Vidu | Sign-up + daily login credits | Yes | Verify terms |

**Strategy (updated, honest):** the only free tiers that satisfy the project's "no watermarked final assets + commercial-safe" rules are **Google Flow/Veo (50 credits/day, SynthID-invisible watermark, commercial use allowed)** and **PixVerse (verify commercial terms first)**. Kling, Hailuo, Runway, Vidu free outputs are watermarked and/or non-commercial — usable only as throwaway motion tests, never in the final render. Realistic plan: **Veo at ~5–8 clips/day × several days, or Veo for the bulk + PixVerse overflow.** This is the pipeline's biggest scheduling constraint — plan a multi-day generation calendar.

## Stage 4 — Keyframe stills

| Option | Status |
|---|---|
| **Google Gemini/Imagen (free tier)** | VERIFIED DOCUMENTATION — free image generations/day; unbranded. Primary for the 50 keyframes (see 07 manifest). |
| Flux (HF Spaces) | VERIFIED DOCUMENTATION — free playgrounds; unbranded. Backup. |
| AshnaAI image tool | **TESTED** — works (Scene 1 keyframe test, this environment). BUT free-tier output is watermarked → reference only, never final. |

## Stage 5 — Music & SFX

| Option | Status |
|---|---|
| **YouTube Audio Library** | VERIFIED DOCUMENTATION — free, YouTube-safe, monetization-safe. Primary music source (6 tracks per §7 mood table). |
| Pixabay Music/SFX | VERIFIED DOCUMENTATION — free, clear license. |
| Freesound (CC0 filter) | VERIFIED DOCUMENTATION — free; check per-sound license. |

## Stage 6 — Runtime

| Option | Status |
|---|---|
| **Google Colab free** | VERIFIED DOCUMENTATION — runs Edge-TTS, WhisperX CPU, FFmpeg. One session executes the deterministic pipeline. |
| GitHub Codespaces free tier | VERIFIED DOCUMENTATION — 60 personal hours/month. Equivalent. |

## Cost summary

Total required spend: **$0.** Constraints to plan around: (1) Veo 50 credits/day caps footage throughput; (2) keyframe generation spread across days; (3) Colab session length — state persists in the repo, so multi-session resumption is fine.

## Honest access legend

- **TESTED** (evidence exists): AshnaAI image generation only.
- **VERIFIED DOCUMENTATION** (current, cross-checked): all other entries above.
- No video generation, TTS, WhisperX, or FFmpeg execution has been tested from this environment — it has no runtime. The first operator session should run Step 0 and Step 2 of the runbook and confirm outputs before committing to the full generation calendar.
