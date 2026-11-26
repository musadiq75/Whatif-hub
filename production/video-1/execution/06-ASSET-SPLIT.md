# VIDEO 1 — ASSET SPLIT (rev 2 — counts corrected)

## Corrected counts (PR #2 review correction 5)

| Asset class | Count | Source of truth |
|---|---|---|
| Render units (video clips) | **61** (43 shot rows, with 1-7→3, 2-6→2, 5-5→3, 6-1→4) | `07-PRE-RENDER-CHECKLIST.md` manifest |
| Keyframe images | **59** (all units except 01-01 and 06-08, which are FFmpeg drawtext cards) | `07-PRE-RENDER-CHECKLIST.md` manifest |
| Music tracks | 6 | `04-ASSEMBLY-RUNBOOK.md` Step 6a |
| SFX files | 27 | §7 cue table / `07` §A |

## The rule, stated plainly

- My image tool can generate cinematic stills matching the style bible (verified with the Scene 1 keyframe test) — **but free-tier outputs are watermarked**, and the project rule forbids watermarked images as final YouTube assets. Therefore ALL 59 final keyframes and ALL 61 motion clips must come from external unbranded sources (`05-TOOLING.md` — realistically Google Flow/Veo, the only verified free tier that is unbranded + commercial-safe).
- My stills serve exactly two purposes: (1) **style pre-flight / continuity validation** before spending external generation credits, and (2) reference images for providers that accept uploaded keyframes (only if unbranded — mine are not, so external keyframes are preferred).

## Shot-by-shot table

`EXT-KEY` = external keyframe (free Gemini/Imagen or Flux) then external image-to-video (Veo/PixVerse, per `05-TOOLING.md`). `REF` = optional AshnaAI style-pre-flight still first. Multi-part shots expand to individual units with letter suffixes (01-07a/b/c etc.) — clip files must be named accordingly.

| Shot(s) | Final asset path | AshnaAI still useful? |
|---|---|---|
| 1-1 title card | FFmpeg drawtext on black (no keyframe) | No |
| 1-2 street | EXT-KEY | Optional REF |
| 1-3 bedroom wide | EXT-KEY | REF strongly recommended (bedroom layout continuity) |
| 1-4 mattress CU | EXT-KEY | REF recommended |
| 1-5 clock flip | EXT-KEY | REF recommended (clock continuity) |
| 1-6 ceiling pan | EXT-KEY | Optional REF |
| 1-7 montage A/B/C → 01-07a/b/c | EXT-KEY ×3 | Optional REF |
| 1-8 POV ceiling | EXT-KEY | Optional REF |
| 2-1 straining to rise | EXT-KEY | REF strongly recommended |
| 2-2 heart X-ray | EXT-KEY | Optional REF |
| 2-3 ankle CU | EXT-KEY | Optional REF |
| 2-4 dressing | EXT-KEY | REF recommended |
| 2-5 stairs | EXT-KEY | Optional REF |
| 2-6 A/B → 02-06a/b | EXT-KEY ×2 | Optional REF |
| 2-7 ward corridor | EXT-KEY | Optional REF |
| 2-8 shelf + fan | EXT-KEY | REF strongly recommended (shelf/fan continuity) |
| 2-9 cane drop | EXT-KEY | Optional REF |
| 3-1 leaning street | EXT-KEY | REF recommended (street continuity) |
| 3-2 legs CU | EXT-KEY | Optional REF |
| 3-3 sparrow | EXT-KEY | Optional REF |
| 3-4 atmosphere render | EXT-KEY | Optional REF (diagram style check) |
| 3-5 sparrow launch | EXT-KEY | Optional REF |
| 3-6 airliner cruise | EXT-KEY | Optional REF |
| 3-7 heavy landing | EXT-KEY | REF recommended (airliner continuity) |
| 3-8 closed runway | EXT-KEY | Optional REF |
| 3-9 cars | EXT-KEY | Optional REF |
| 3-10 old bridge | EXT-KEY | REF strongly recommended (bridge continuity) |
| 3-11 new bridge | EXT-KEY | REF recommended |
| 3-12 slow collapse | EXT-KEY | Optional REF |
| 3-13 hairline crack | EXT-KEY | Optional REF |
| 4-1 spine | EXT-KEY | REF recommended |
| 4-2 height marks | EXT-KEY | Optional REF |
| 4-3 fighter pilot | EXT-KEY | Optional REF |
| 4-4 split screen | EXT-KEY (or FFmpeg hstack from 4-3 + new pajamas frame) | Optional REF |
| 4-5 centrifuge | EXT-KEY | Optional REF |
| 4-6 body scans | EXT-KEY | Optional REF |
| 4-7 adapting montage | EXT-KEY | REF recommended (bedroom continuity) |
| 4-8 the ones who can't | EXT-KEY | Optional REF |
| 4-9 window dusk | EXT-KEY | REF strongly recommended (sets up 6-2 match-cut) |
| 5-1 hard rain | EXT-KEY | Optional REF |
| 5-2 heavy waves | EXT-KEY | Optional REF |
| 5-3 forest sheds | EXT-KEY | Optional REF |
| 5-4 skyline compress | EXT-KEY | REF recommended (city continuity) |
| 5-5 A/B/C → 05-05a/b/c | EXT-KEY ×3 | Optional REF |
| 5-6 generations | EXT-KEY | Optional REF |
| 6-1 A/B/C/D → 06-01a/b/c/d | EXT-KEY ×4 | REF recommended (reuses established sets) |
| 6-2 window match-cut | EXT-KEY — MUST be generated FROM the exact 4-9 keyframe, re-lit | REF required (regenerate from 4-9 reference) |
| 6-3 bedroom return | EXT-KEY | REF strongly recommended (bedroom continuity) |
| 6-4 clock flashback | EXT-KEY — reuse the exact 1-5 keyframe | REF required |
| 6-5 ordinary morning | EXT-KEY | REF strongly recommended |
| 6-6 feet + clock 7:02 | EXT-KEY | REF recommended (clock continuity) |
| 6-7 empty room | EXT-KEY | REF strongly recommended |
| 6-8 end card | FFmpeg drawtext on black (no keyframe) | No |

## Continuity-critical reuse rules (the three hard ones)

1. **6-2 must be generated FROM the 4-9 keyframe** (same window, re-lit a year later) — the match-cut only reads if the framing matches.
2. **6-4 must reuse the exact 1-5 clock keyframe** (the flashback sting depends on identical framing).
3. **1-3/2-1/2-8/4-7/6-3/6-5/6-7 bedroom shots** must all derive from one master bedroom keyframe (re-lit per scene) — generate the master first, then variations, so layout never drifts.

## What I can fully deliver in-environment (no external dependency)

- All creative/planning assets (done — this execution package).
- Style-pre-flight stills on request during production (fast, zero cost) — reference aids only, never final assets.
- Post-render QC review: upload rendered clips/final MP4 to me and I audit against runbook §8 and the continuity table before anything is declared finished.
