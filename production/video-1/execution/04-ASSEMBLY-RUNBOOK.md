# VIDEO 1 — FFmpeg ASSEMBLY & AUDIO-MIXING RUNBOOK

**Target output:** 1920×1080, 23.976 fps, H.264 High profile, 2-pass VBR 12–16 Mbps, AAC-LC 320 kbps 48 kHz stereo, MP4. Runtime ≈9:03 (6s title + 8:52 narration + 5s end card).

**Directory layout (create these first):**
```
video1/
  audio/narration.wav        # from TTS step (48kHz 24-bit mono)
  audio/music/               # music beds per scene (from 05-TOOLING sources)
  audio/sfx/                 # SFX per cue table
  clips/                     # 43 generated video clips: 01-01.mp4 ... 06-08.mp4
  refs/                      # keyframe stills (style reference / keyframe-first workflow)
  work/                      # intermediates (created by runbook)
  out/                       # final renders
```
**Clip naming rule:** scene-shot, zero-padded: `1-1` → `01-01.mp4`, `6-8` → `06-08.mp4`. Rename generated clips to match before assembly.

---

## STEP 0 — Narration first (the spine)

Generate narration per `02-NARRATION-TTS.md` and `05-TOOLING.md` → save as `audio/narration.wav` (48 kHz, 24-bit, mono).

Verify: `ffprobe -v error -show_streams audio/narration.wav` → must show 48000 Hz, 1 channel. Expected duration ≈ 8:52 ± 30s. If narration >9:10 total, regenerate at a slightly faster rate (do NOT trim words — script is locked).

## STEP 1 — Narration cleanup

```bash
ffmpeg -i audio/narration.wav -af "highpass=f=80,acompressor=threshold=-18dB:ratio=2:attack=20:release=250,deesser,alimiter=limit=-1.5dB" -ar 48000 -ac 1 work/narration_clean.wav
ffmpeg -loudnorm I=-16:TP=-1.5:LRA=11 -i work/narration_clean.wav -ar 48000 work/narration_vo.wav
```
Verify: `ffmpeg -i work/narration_vo.wav -af loudnorm=print_format=summary -f null -` → integrated ≈ −16 LUFS, TP ≤ −1.5 dB.

## STEP 2 — Build the shot timing table

Measure the real narration: `ffprobe work/narration_vo.wav` → note exact total duration. Then use the scene start markers from `02-NARRATION-TTS.md` (S1 0:06, S2 ≈1:15, S3 ≈2:40, S4 ≈4:35, S5 ≈6:05, S6 ≈7:35) — adjust proportionally if narration runs long/short: scale every scene start and shot boundary by (actual narration duration ÷ 8:52). Apply the per-shot durations from `01-SHOT-PROMPTS.md` within each scene's window. Record the final 43-row table (start, end, clip) — this is the timeline contract; every later step uses it.

**Regenerate captions:** run WhisperX (or `05-TOOLING.md` fallback) on `narration_vo.wav` for word-level timestamps; regenerate `03-CAPTIONS.srt` timings from them using the sentence splits already in the file. Caption TEXT must stay verbatim — only timings change.

## STEP 3 — Normalize footage

All clips to the timeline contract (23.976 fps, 1920×1080, yuv420p; do NOT upscale small clips):

```bash
for f in clips/*.mp4; do
  ffmpeg -y -i "$f" -vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=23.976,format=yuv420p" -an -c:v libx264 -preset medium -crf 16 "work/$(basename "$f" .mp4)_norm.mp4"
done
```
Re-time each clip to its table duration (slow down or speed up by at most ±15% — beyond that, regenerate the clip at closer target duration):
```bash
ffmpeg -y -i work/01-01_norm.mp4 -vf "setpts=PTS*<factor>" -r 23.976 -an work/01-01_timed.mp4
```
Verify each: `ffprobe -v error -show_entries format=duration work/01-01_timed.mp4` must equal the table value ±0.1s.

## STEP 4 — Concatenate the video track

Create `work/cliplist.txt` with one line per shot in order:
```
file 'work/01-01_timed.mp4'
file 'work/01-02_timed.mp4'
... (all 43)
```
```bash
ffmpeg -y -f concat -safe 0 -i work/cliplist.txt -c copy work/video_raw.mp4
```
Verify duration = title(6s) + narration window (≈8:52) + end card(5s) − verify with ffprobe; must be 8:58–9:08.

## STEP 5 — Letterbox, grain, grade

```bash
ffmpeg -y -i work/video_raw.mp4 -vf "scale=1920:804,drawbox=x=0:y=0:w=1920:h=138:color=black@1:t=fill,drawbox=x=0:y=942:w=1920:h=138:color=black@1:t=fill,noise=alls=6:allf=t,eq=saturation=0.92:contrast=1.04,format=yuv420p" -c:v libx264 -preset medium -crf 16 work/video_master.mp4"
```
This produces the 2.39:1 letterboxed image with gentle film grain and the unified grade. Verify visually at [0:30], [2:30], [4:30], [6:00], [7:30] — the bars must be pure black and identical width top/bottom.

## STEP 6 — Music & SFX mix

Per production package §7 cue table, place music beds and SFX against the timeline contract. Duck music 4–6 dB under narration:
```bash
# 1. Concatenate music segments per scene into music_bed.wav (crossfade 2s at scene changes via acrossfade)
ffmpeg -y -i audio/music/s1.mp3 -i audio/music/s2.mp3 -filter_complex "[0:a]volume=0.7,apad[a0];[1:a]volume=0.7,atrim=0:87[a1];[a0][a1]acrossfade=d=2:c1=tri:c2=tri" work/music_bed.wav
# (repeat pattern through s6; total length must match timeline)
# 2. SFX: place each cue at its timeline timestamp
ffmpeg -y -i audio/sfx/clock_tick.wav -i audio/sfx/mattress_creak.wav ... -filter_complex "[0:a]adelay=6800|6800,volume=-14dB[s0];[1:a]adelay=25000|25000,volume=-10dB[s1];...[s0][s1]...amix=inputs=N:normalize=0" work/sfx_bed.wav
# 3. Duck music under narration
ffmpeg -y -i work/music_bed.wav -i work/narration_vo.wav -filter_complex "[0:a]volume=0.9[bg];[1:a]asplit=2[n1][n2];[n2]volume=-28dB,silencedetect=n=-35dB:d=0.3[duck];[bg][duck]sidechaincompress=threshold=0.05:ratio=4:attack=100:release=600[bed];[bed][n1]amix=inputs=2:normalize=0:duration=longest" work/music_ducked.wav
# 4. Final mix: narration + ducked music + SFX
ffmpeg -y -i work/narration_vo.wav -i work/music_ducked.wav -i work/sfx_bed.wav -filter_complex "[0:a]adelay=6000|6000,apad[n];[1:a]apad[m];[2:a]apad[s];[n][m][s]amix=inputs=3:normalize=0:duration=longest,sidechaincompress=threshold=0.02:ratio=2[a]" -map "[a]" -ar 48000 -ac 2 work/final_mix.wav
```
Loudness normalize the mix:
```bash
ffmpeg -i work/final_mix.wav -af loudnorm=I=-14:TP=-1:LRA=11 -ar 48000 -ac 2 work/final_mix_norm.wav
```
Verify: integrated −14 LUFS ±1, true peak ≤ −1 dB; listen for: VO clarity at all times, music never masking VO, SFX accents audible but subtle, the 1.5–2s silence after "It's the forgetting." (≈7:27) must be intact and music must dip with it.

## STEP 7 — Final export (MP4)

```bash
ffmpeg -y -i work/video_master.mp4 -i work/final_mix_norm.wav -map 0:v -map 1:a -c:v libx264 -profile:v high -level 4.1 -pass 1 -b:v 14M -x264-params "keyint=48:min-keyint=48:scenecut=0" -an -f mp4 /dev/null
ffmpeg -y -i work/video_master.mp4 -i work/final_mix_norm.wav -map 0:v -map 1:a -c:v libx264 -profile:v high -level 4.1 -pass 2 -b:v 14M -x264-params "keyint=48:min-keyint=48:scenecut=0" -c:a aac -b:a 320k -ar 48000 -movflags +faststart out/video1_final.mp4
```
Playback verification (MANDATORY): `ffprobe out/video1_final.mp4` → confirm 1920×1080, 23.976, h264+aac; open in VLC, scrub full length; A/V sync check at [0:06], [2:31], [4:36], [6:06], [7:36] (first narration word of each scene must align with its scene's first shot); confirm the file plays start to end with no freezes.

## STEP 8 — Captions deliverable

Burn-in optional; upload `03-CAPTIONS.srt` (regenerated in step 2) to YouTube Studio. SRT rules from package §8: max 42 chars/line, max 2 lines, 1.5–2s per cue (except the long final cue 95, which is intentional end-card silence).

## SECTION 7 — From assets to finished cinematic MP4 (the exact path, summarized)

1. narration.wav (TTS) → 2. clean + loudnorm → 3. timing table from real audio → 4. 43 clips normalized + timed → 5. concat → 6. letterbox+grain+grade → 7. music/SFX mix with ducking → 8. 2-pass H.264 export → 9. playback verify → 10. captions upload. **No step may be skipped; no step alters the script.**

## SECTION 8 — QUALITY-CONTROL CHECKLIST (all must pass)

**Narration:** [ ] integrated −16 LUFS; [ ] diction clear, no clipping; [ ] all §6 beats honored (flat open, arithmetic numbers, quiet "last straw," crisp parallel "Twice the weight," slowed "slow motion," somber "never leave the bed," longest pause after "It's the forgetting," warm clean ending); [ ] no added/omitted words vs `02-NARRATION-TTS.md`.

**Visuals:** [ ] all 43 clips match their shot prompts; [ ] protagonist face never visible in any frame; [ ] continuity table from package §4 satisfied (bedroom layout, clock digits 11:59→12:00→7:02, wardrobe change after Scene 2, shelf sag progression, fan wobble→steady arc); [ ] consistent grade — no clip visibly off-palette; [ ] no watermarks anywhere (reject any watermarked clip — regenerate); [ ] no text/logos except title and end cards.

**Transitions:** [ ] hard cuts land on narration beats; [ ] dissolves ONLY where prompts specify (2-6, 6-1 montage, into Scene 5); [ ] match-cut 4-9→6-2 reads as the same window; [ ] 6-5 is one unbroken take; [ ] no dead air >1s anywhere.

**Sound:** [ ] music ducks 4–6 dB under VO; [ ] SFX accents present per cue table but never masking; [ ] silence beat at "It's the forgetting." preserved; [ ] master −14 LUFS, TP ≤ −1 dB; [ ] full-length listen-through with zero dropouts.

**Captions:** [ ] timings regenerated from WhisperX word timestamps; [ ] text verbatim vs script; [ ] ≤42 chars/line, ≤2 lines; [ ] no overlapping cues; [ ] cue 95 end-card silence intentional.

**Scientific accuracy:** [ ] speculation labeled on-screen in Scene 5 (5-1/5-5 use the "informed speculation" visual treatment — no confident claims); [ ] "informed reasoning, not a certainty" line present and audible; [ ] no invented statistics; 180/360 lb stays illustrative, no on-screen numbers graphics; [ ] physics claims match package §2 sources block.

**Final:** [ ] runtime 8:58–9:08; [ ] 1080p/23.976/H.264/AAC; [ ] file plays start→end in VLC and YouTube Studio preview; [ ] captions import cleanly; [ ] only after every box above: Video 1 is finished.
