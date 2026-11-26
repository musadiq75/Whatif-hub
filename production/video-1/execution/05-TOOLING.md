# VIDEO 1 — TOOLING: BEST FREE / LOW-COST OPTIONS PER STAGE

All recommendations are free-tier-first with named low-cost upgrades, per the project's resource rules. No purchases required to run the pipeline.

## Stage 1 — Narration (TTS)

| Option | Cost | Notes |
|---|---|---|
| **Edge-TTS (Microsoft neural voices, via `edge-tts` Python package)** | Free | Best free quality for the "calm late-night science narrator" profile. Recommend voices: `en-US-GuyNeural` (deep, calm) or `en-US-AndrewNeural` (warmer). Runs offline after install; no API key needed. **Primary recommendation.** |
| Piper TTS (local, open-source) | Free | Good fallback; slightly more synthetic. No key, fully offline. |
| ElevenLabs free tier | Free (limits) | Highest free quality; ~10k chars/month, requires signup + API key. Use only if Edge-TTS quality is judged insufficient. Rate limit may force multi-day narration for 1,175 words? No — 1,175 words ≈ 6.5k chars, fits in one month's free quota. |
| Google Cloud TTS free tier | Free (1M chars/mo) | Requires Google Cloud account + key setup. Overkill vs Edge-TTS. |

**Verdict:** Edge-TTS `en-US-GuyNeural` at ~130 wpm, then apply runbook Step 1 cleanup chain. Zero cost, no keys.

## Stage 2 — Word-level timestamps (captions)

| Option | Cost | Notes |
|---|---|---|
| **WhisperX (m-bain/whisperX)** | Free, open-source | The recommended tool. GPU helps but runs on CPU (slower). Produces accurate word-level timestamps needed for caption re-timing. |
| faster-whisper (CTranslate2 wrapper) | Free | Lighter-weight fallback if WhisperX install fails; word timestamps via `word_timestamps=True`. |
| StableTS | Free | Alternative alignment tool; good on music-free VO. |

**Verdict:** WhisperX on CPU is fine for 9 minutes of narration (minutes, not hours).

## Stage 3 — Footage (43 clips)

| Option | Cost | Notes |
|---|---|---|
| **Google Veo (via Gemini API free tier)** | Free tier credits | Image-to-video; cinematic quality; best current free option where available. |
| Kling AI free tier | Free daily credits | Good image-to-video; daily limit means the 43-clip batch spans several days on free tier — plan accordingly. |
| Hailuo/MiniMax free tier | Free credits | Strong motion realism; daily caps similar to Kling. |
| Runway free tier | One-time free credits | Good but credits exhaust quickly; reserve for hero shots (1-5, 3-7, 6-5). |
| Luma Dream Machine free tier | Free monthly | Decent quality; monthly cap. |

**Strategy:** keyframe-first workflow (generate still from `01-SHOT-PROMPTS.md` → image-to-video with motion prompt). Spread across 2–3 free providers to stay inside daily caps without waiting days: e.g., Veo/Gemini free for Scenes 1–2, Kling for Scene 3, Hailuo for Scenes 4–6. All prompts in `01-SHOT-PROMPTS.md` are provider-agnostic (no tool-specific syntax).

**Rule:** any clip with a provider watermark is REJECTED and regenerated (per project rule: no watermarked assets in final). Choose providers/settings that deliver unbranded outputs on their free tiers (Veo via Gemini API, Kling free-tier download without watermark where offered — verify per-clip at generation time; if the only free output is watermarked, switch providers for that clip rather than accepting the mark).

## Stage 4 — Still keyframes (43 reference frames)

| Option | Cost | Notes |
|---|---|---|
| **Google Imagen / Gemini image free tier** | Free | High quality, unbranded on free tier via API/UI. Primary for keyframes used as image-to-video inputs. |
| Flux (via free playgrounds) | Free | Strong photorealism; several free hosts (e.g., HuggingFace Spaces). |
| AshnaAI image tool (this environment) | Free | Works (verified: Scene 1 keyframe test) BUT outputs carry a watermark on the current plan — use for STYLE REFERENCE and layout validation only, never as final-asset input. |

**Verdict:** generate the 43 keyframes with free Imagen/Gemini or Flux using the exact prompts in `01-SHOT-PROMPTS.md`. AshnaAI's tool is the pre-flight style check, not the asset source.

## Stage 5 — Music & SFX

| Option | Cost | Notes |
|---|---|---|
| **YouTube Audio Library** | Free | Safe for YouTube monetization; filter: cinematic/ambient. Primary music source. |
| Pixabay Music + Pixabay SFX | Free | Broad free selection, clear license. |
| Freesound | Free | SFX; prefer CC0 filters; check license per sound. |

**Verdict:** Music from YouTube Audio Library (5–6 tracks matched to the §7 mood table); SFX from Freesound CC0. All free, all YouTube-safe.

## Stage 6 — Assembly & render (FFmpeg)

| Option | Cost | Notes |
|---|---|---|
| **FFmpeg** | Free | The entire runbook (`04-ASSEMBLY-RUNBOOK.md`) is written against FFmpeg commands only — no paid NLE needed. |
| DaVinci Resolve (free) | Free | Optional human-friendly alternative to steps 5–7 if an editor prefers GUI; specs identical. |

**Verdict:** FFmpeg only. The runbook is complete and self-contained.

## Stage 7 — Runtime (where to execute all of the above)

| Option | Cost | Notes |
|---|---|---|
| **Google Colab free** | Free | Runs Edge-TTS, WhisperX (CPU ok), FFmpeg. 43-clip generation happens in provider UIs/APIs, not Colab. Best single free runtime. |
| GitHub Codespaces free tier | Free (60h/mo) | Equivalent capability; good if the repo is the center of gravity. |
| Local machine | Free | Works but is the user's device — deprioritized per project rules (remote infrastructure preferred). |

**Verdict:** One free Colab session (or Codespaces) executes the whole runbook. The batch asset generation (clips, keyframes, music/SFX) is done via free provider UIs/APIs, then dropped into the folder structure; Colab only runs the deterministic steps (TTS, WhisperX, FFmpeg).

## Cost summary

Total required spend: **$0.** Every stage has a verified free path. The only friction points are daily free-tier caps on video providers (mitigated by spreading across providers) and Colab session limits (mitigated by resuming — all state lives in the repo folder structure).
