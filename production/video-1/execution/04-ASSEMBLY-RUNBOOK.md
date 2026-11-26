# VIDEO 1 — FFmpeg ASSEMBLY & AUDIO-MIXING RUNBOOK (rev 2 — corrected)

**Target output:** 1920×1080, 23.976 fps, H.264 High profile, 2-pass VBR 14 Mbps, AAC-LC 320 kbps 48 kHz stereo, MP4. Runtime ≈9:03 (6s title card + 8:52 narration window + 5s end card).

**Corrections in this revision (per PR #2 review):**
- Every FFmpeg command rewritten with valid syntax (loudnorm moved into `-af`; removed invalid `silencedetect`-as-signal pattern; removed stray quote in Step 5; 2-pass pass 1 now uses `-f null -`).
- All placeholder commands replaced with complete working examples (values shown are from the planned timeline; replace with your `timeline.csv` values where noted).
- Timing workflow now builds the shot timeline from **real WhisperX word timestamps**, never by scaling estimates.
- Duration columns in `01-SHOT-PROMPTS.md` are **minimum pacing targets**; actual shot durations = span from each shot's cue word to the next shot's cue word in the real narration (Step 2). The minimum durations sum to ≈6:37, which is intentional: narration spans stretch shots to fill ≈8:52.

**Directory layout:**
```
video1/
  audio/narration.wav        # TTS output (48kHz mono)
  audio/music/s1.mp3 ... s6.mp3
  audio/sfx/*.wav
  clips/                     # 61 render units, named per 07 manifest (01-01.mp4, 01-07a.mp4 ...)
  refs/                      # keyframes
  work/                      # intermediates
  out/                       # final render
```

## STEP 0 — Narration (the spine)

Generate narration from `02-NARRATION-TTS.md` per `05-TOOLING.md` → `audio/narration.wav`.

Verify:
```bash
ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate,channels -of csv=p=0 audio/narration.wav
# expect: 48000,1
ffprobe -v error -show_entries format=duration -of csv=p=0 audio/narration.wav
# expect 500–560 s (8:20–9:20). If outside range, regenerate at adjusted rate — NEVER trim words (script locked).
```

## STEP 1 — Narration cleanup + loudness

```bash
ffmpeg -y -i audio/narration.wav -af "highpass=f=80,acompressor=threshold=-18dB:ratio=2:attack=20:release=250,deesser,alimiter=limit=-1.5dB" -ar 48000 -ac 1 work/narration_clean.wav
```
(If your FFmpeg build lacks `deesser`, drop it — `highpass` + compressor + limiter still meet spec.)

```bash
ffmpeg -y -i work/narration_clean.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11" -ar 48000 -ac 1 work/narration_vo.wav
```
Verify loudness:
```bash
ffmpeg -i work/narration_vo.wav -af "loudnorm=print_format=summary" -f null - 2>&1 | grep -A3 "Input Integrated"
# expect Input Integrated ≈ -16 LUFS, Input True Peak ≤ -1.5 dB
```

## STEP 2 — Build the shot timeline from REAL timestamps

**Do not scale estimated boundaries.** Every shot boundary comes from actual word timestamps.

2a. Transcribe with WhisperX (CPU is fine for 9 min):
```bash
pip install whisperx
whisperx work/narration_vo.wav --model large-v2 --output_format json --output_dir work/
# produces work/narration_vo.json with word-level timestamps
```

2b. Regenerate captions from the same JSON (text stays verbatim; only timings change). Sentence boundaries are exactly the 95 cue texts in `03-CAPTIONS.srt`.

2c. Build `timeline.csv` — each render unit's start = timestamp of its cue's first word (cue table in `07-PRE-RENDER-CHECKLIST.md`); its end = the next unit's start; last unit ends at narration end. Save this as `tools/build_timeline.py` and run it:

```python
# tools/build_timeline.py — reads WhisperX JSON + cue table, writes timeline.csv
import json, csv, sys, difflib

words = []  # [(start, end, word), ...]
with open("work/narration_vo.json") as f:
    data = json.load(f)
for seg in data["segments"]:
    for w in seg["words"]:
        words.append((float(w["start"]), float(w["end"]), w["word"].lower().strip()))

units = []  # (unit_id, cue_first_words, min_duration) — from 07-PRE-RENDER-CHECKLIST.md
with open("timeline_cues.csv") as f:
    for row in csv.DictReader(f):
        units.append((row["unit"], row["cue"], float(row["min_dur"])))

def find_cue_time(cue):
    cue_words = cue.lower().split()
    n = len(cue_words)
    best, best_r = None, -1.0
    for i in range(len(words) - n + 1):
        chunk = " ".join(w[2] for w in words[i:i+n])
        r = difflib.SequenceMatcher(None, chunk, " ".join(cue_words)).ratio()
        if r > best_r:
            best_r, best = r, words[i][0]
    if best_r < 0.6:
        sys.exit(f"ERROR: cue not found reliably: {cue!r} (best ratio {best_r:.2f})")
    return best

NARR_START = find_cue_time("at midnight tonight")   # first narration word
starts = []
for unit, cue, _ in units:
    starts.append((unit, NARR_START if cue == "<narration_start>" else find_cue_time(cue)))

with open("work/timeline.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["unit", "start", "end", "duration"])
    for i, (unit, s) in enumerate(starts):
        e = starts[i+1][1] if i+1 < len(starts) else None
        w.writerow([unit, f"{s:.3f}", f"{e:.3f}" if e else "<narration_end>", ""])
print("timeline.csv written:", len(starts), "units")
```

2d. Sanity-check the result:
```bash
python3 - <<'EOF'
import csv
rows = list(csv.DictReader(open("work/timeline.csv")))
prev = 0.0
for r in rows:
    s = float(r["start"])
    assert s >= prev - 0.05, f"non-monotonic at {r['unit']}"
    prev = s
print("OK:", len(rows), "units, monotonic")
EOF
```
Every later step reads `work/timeline.csv` — nothing uses estimated boundaries.

## STEP 3 — Normalize + re-time the 61 clips

Normalize (never upscale):
```bash
for f in clips/*.mp4; do
  ffmpeg -y -i "$f" -vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=23.976,format=yuv420p" -an -c:v libx264 -preset medium -crf 16 "work/$(basename "$f" .mp4)_norm.mp4"
done
```

Re-time to the timeline (worked example: a clip rendered at 5.0s must fill 7.2s → factor = 7.2/5.0 = 1.44; keep factors within 0.85–1.15 — outside that, regenerate the clip at a closer length):
```bash
ffmpeg -y -i work/01-02_norm.mp4 -vf "setpts=1.44*PTS" -r 23.976 -an work/01-02_timed.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 work/01-02_timed.mp4
# must equal the timeline.csv span for 01-02, ±0.15s
```
Repeat per clip using each clip's own factor from `timeline.csv`. (Clips may also be trimmed longer-than-needed with `-t` instead of slowed.)

## STEP 4 — Concatenate

`work/cliplist.txt` (61 lines, timeline order — the unit ids are the manifest in `07-PRE-RENDER-CHECKLIST.md`):
```
file 'work/01-01_timed.mp4'
file 'work/01-02_timed.mp4'
...
file 'work/06-08_timed.mp4'
```
```bash
ffmpeg -y -f concat -safe 0 -i work/cliplist.txt -c copy work/video_raw.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 work/video_raw.mp4
# expect 535–555 s (8:55–9:15); title 6s + narration window + end card 5s
```

## STEP 5 — Letterbox, grain, grade

```bash
ffmpeg -y -i work/video_raw.mp4 -vf "scale=1920:804,drawbox=x=0:y=0:w=1920:h=138:color=black@1:t=fill,drawbox=x=0:y=942:w=1920:h=138:color=black@1:t=fill,noise=alls=6:allf=t,eq=saturation=0.92:contrast=1.04,format=yuv420p" -c:v libx264 -preset medium -crf 16 work/video_master.mp4
```
(804 = 2.39:1 image height; 138px black bars top and bottom complete 1080.) Visually verify bars at [0:30], [2:30], [4:30], [6:00], [7:30].

## STEP 6 — Music & SFX mix (complete working examples)

6a. Music bed — 6 scene tracks, 2s crossfades, full daisy-chain. Example durations are scene spans from the planned timeline (60/62/98/66/50/61 s); **replace with your `timeline.csv` scene spans**:
```bash
ffmpeg -y -i audio/music/s1.mp3 -i audio/music/s2.mp3 -i audio/music/s3.mp3 -i audio/music/s4.mp3 -i audio/music/s5.mp3 -i audio/music/s6.mp3 -filter_complex "[0:a]atrim=0:60,asetpts=PTS-STARTPTS[a0];[1:a]atrim=0:62,asetpts=PTS-STARTPTS[a1];[2:a]atrim=0:98,asetpts=PTS-STARTPTS[a2];[3:a]atrim=0:66,asetpts=PTS-STARTPTS[a3];[4:a]atrim=0:50,asetpts=PTS-STARTPTS[a4];[5:a]atrim=0:61,asetpts=PTS-STARTPTS[a5];[a0][a1]acrossfade=d=2:c1=tri:c2=tri[m1];[m1][a2]acrossfade=d=2:c1=tri:c2=tri[m2];[m2][a3]acrossfade=d=2:c1=tri:c2=tri[m3];[m3][a4]acrossfade=d=2:c1=tri:c2=tri[m4];[m4][a5]acrossfade=d=2:c1=tri:c2=tri,apad=whole_dur=543" -ar 48000 -ac 2 work/music_bed.wav
```
(`whole_dur` = total video duration from Step 4; example uses 543 s ≈ 9:03.)

6b. Duck the music under narration (sidechaincompress; narration is the sidechain — no detection heuristics):
```bash
ffmpeg -y -i work/music_bed.wav -i work/narration_vo.wav -filter_complex "[1:a]asplit=2[sc][vo];[sc]aformat=sample_rates=48000:channel_layouts=stereo[scs];[0:a][scs]sidechaincompress=threshold=0.05:ratio=4:attack=100:release=600[bed];[vo]adelay=6000:all=1[vo2];[bed][vo2]amix=inputs=2:duration=first:normalize=0" -ar 48000 -ac 2 work/music_ducked.wav
```
(`adelay=6000` = title card length; narration starts at 6.0s. `duration=first` trims to the music bed length = full video.)

6c. SFX + final mix — complete example with three real cues; add further SFX by extending the pattern (one more `-i`, one more `[N:a]adelay=…,volume=…[sN]` chain, and increment `inputs=`):
```bash
ffmpeg -y -i work/narration_vo.wav -i work/music_ducked.wav \
  -i audio/sfx/clock_tick.wav -i audio/sfx/mattress_creak.wav -i audio/sfx/cane_drop.wav \
  -filter_complex "[0:a]adelay=6000:all=1,apad[n]; \
[2:a]adelay=25400:all=1,volume=-14dB[s0]; \
[3:a]adelay=32000:all=1,volume=-10dB[s1]; \
[4:a]adelay=119300:all=1,volume=-8dB[s2]; \
[1:a][s0][s1][s2]amix=inputs=4:duration=longest:normalize=0[mix]; \
[mix][n]amix=inputs=2:duration=longest:normalize=0" \
  -ar 48000 -ac 2 work/final_mix.wav
```
(SFX timestamps come from `timeline.csv`; example values: clock tick at the 1-5 clock flip ≈25.4s, mattress creak in 1-4 ≈32s, cane drop at 2-9 ≈119.3s. Every SFX from the §7 cue table follows this exact pattern.)

6d. Final loudness:
```bash
ffmpeg -y -i work/final_mix.wav -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 48000 -ac 2 work/final_mix_norm.wav
ffmpeg -i work/final_mix_norm.wav -af "loudnorm=print_format=summary" -f null - 2>&1 | grep -A3 "Input Integrated"
# expect ≈ -14 LUFS, TP ≤ -1.0 dB
```
Listen-check: VO always clear; the 1.5–2s pause after "It's the forgetting." must remain silent (music dips with it via the sidechain — verify at ≈7:27).

## STEP 7 — Final export (2-pass H.264)

```bash
ffmpeg -y -i work/video_master.mp4 -c:v libx264 -profile:v high -level 4.1 -b:v 14M -x264-params "keyint=48:min-keyint=48:scenecut=0" -pass 1 -passlogfile out/v1pass -an -f null -
ffmpeg -y -i work/video_master.mp4 -i work/final_mix_norm.wav -map 0:v -map 1:a -c:v libx264 -profile:v high -level 4.1 -b:v 14M -x264-params "keyint=48:min-keyint=48:scenecut=0" -pass 2 -passlogfile out/v1pass -c:a aac -b:a 320k -ar 48000 -movflags +faststart out/video1_final.mp4
```

Playback verification (MANDATORY):
```bash
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,codec_name -of csv=p=0 out/video1_final.mp4
# expect: 1920,1080,24000/1001,h264
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels -of csv=p=0 out/video1_final.mp4
# expect: aac,48000,2
```
Open in VLC, scrub full length; A/V sync at [0:06], [2:31], [4:36], [6:06], [7:36] (each scene's first word aligns with its first shot); plays start→end without freezes.

## STEP 8 — Captions

Upload the regenerated SRT (from Step 2b) to YouTube Studio. Rules: ≤42 chars/line, ≤2 lines, 1.5–2s cues (cue 95's long span is the intentional end-card silence).

## SECTION 7 — Assets → finished MP4 (the complete path)

1. narration.wav (TTS) → 2. cleanup + loudnorm → 3. WhisperX real word timestamps → 4. timeline.csv (real timestamps only) → 5. 61 clips normalized + re-timed to timeline → 6. concat → 7. letterbox+grain+grade → 8. music bed + sidechain ducking + SFX mix → 9. 2-pass export → 10. playback verify → 11. captions upload. No step skipped; no step alters the script.

## SECTION 8 — QUALITY-CONTROL CHECKLIST (all must pass)

**Narration:** [ ] −16 LUFS, TP ≤ −1.5 dB; [ ] diction clear, no clipping; [ ] all §6 beats honored; [ ] word-for-word identical to `02-NARRATION-TTS.md` (diff the SRT text vs the script — zero tolerance).

**Visuals:** [ ] all 61 units match their prompts; [ ] protagonist face never visible; [ ] continuity table satisfied (bedroom layout, clock 11:59→12:00→7:02, wardrobe change after Scene 2, shelf sag, fan wobble→steady); [ ] consistent grade; [ ] zero watermarks (reject + regenerate any marked clip); [ ] no text/logos except title and end cards.

**Transitions:** [ ] hard cuts on narration beats; [ ] dissolves only where prompts specify (2-6, 6-1, into Scene 5); [ ] match-cut 4-9→6-2 same framing; [ ] 6-5 unbroken take; [ ] no dead air >1s.

**Sound:** [ ] ducking 4–6 dB under VO; [ ] SFX present per cue table, never masking; [ ] "It's the forgetting." silence preserved; [ ] master −14 LUFS / TP ≤ −1 dB; [ ] full listen-through, zero dropouts.

**Captions:** [ ] timings from WhisperX; [ ] text verbatim; [ ] ≤42 chars/line, ≤2 lines; [ ] no overlaps; [ ] cue 95 intentional.

**Scientific accuracy:** [ ] Scene 5 speculation labeled; [ ] "informed reasoning, not a certainty" audible + captioned; [ ] no invented statistics; [ ] 180/360 lb illustrative only, no on-screen numbers.

**Final:** [ ] runtime 8:55–9:15; [ ] 1080p/23.976/H.264/AAC; [ ] plays start→end in VLC and YouTube preview; [ ] captions import cleanly; [ ] pre-render checklist (07) passed BEFORE assembly began.
