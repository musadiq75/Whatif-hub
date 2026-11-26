# VIDEO 1 — FFmpeg ASSEMBLY & AUDIO-MIXING RUNBOOK (rev 3 — second-review corrections)

**Target output:** 1920×1080, 23.976 fps, H.264 High profile, 2-pass VBR 14 Mbps, AAC-LC 320 kbps 48 kHz stereo, MP4. Structure: title card [0 → first-word time] + narration window + 5s end card.

**IMPORTANT — execution status:** NO command in this runbook has been executed. This environment has no runtime (see CAPABILITY-AUDIT.md). Syntax was hand-audited only; the first operator session must verify each step's output before proceeding (verify commands included per step).

**rev 3 corrections (PR #2 second review):**
1. **Audio duplication fixed:** Step 6b now exports ONLY the ducked music bed (zero narration). Narration is mixed exactly once, in Step 6c.
2. **Title-card boundary fixed:** the title card unit is `<title_card>` and starts at 0.000; the first narration shot (01-02) starts at the actual first-word timestamp. No unit receives the first word's timestamp as its start except 01-02.
3. **Captions:** final-cue rule corrected — 94 cues, last cue ends at the actual last-word end, never beyond video duration; end card carries no caption (the old 58-second bracketed cue is removed from `03-CAPTIONS.srt`).
4. **Chronological matching:** the timeline script now searches only forward of the previous match, detects ambiguous/duplicate matches, validates every timestamp, and pins first/last boundaries.
5. **Resolution contradiction resolved:** explicit gate before normalization — undersized clips are rejected unless on a documented waiver list; the only permitted upscale path is the flagged lanczos scale for waiver-listed clips.
6. **Re-audit findings fixed:** (a) title/end-card generation commands were MISSING entirely (concat would have failed with 59 clips) — now Step 3.5 with complete commands; (b) narration `adelay` was hardcoded 6000ms — now computed from the actual first-word time; (c) music bed now covers the title lead-in and end card; (d) leading/trailing silence trimming added so word timestamps align with the delay; (e) double-encode (Step 5 grade + Step 7 final) is intentional and now documented.

**Directory layout:**
```
video1/
  audio/narration.wav        # TTS output
  audio/music/s1.mp3 ... s6.mp3
  audio/sfx/*.wav
  clips/                     # 59 generated clips (61 units minus the 2 text cards)
  refs/                      # keyframes
  work/                      # intermediates
  out/                       # final render
  timeline_cues.csv          # from 07-PRE-RENDER-CHECKLIST.md
  tools/build_timeline.py    # from Step 2 below
```

## STEP 0 — Narration

Generate from `02-NARRATION-TTS.md` per `05-TOOLING.md` → `audio/narration.wav`.
```bash
ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate,channels -of csv=p=0 audio/narration.wav   # expect 48000,1
ffprobe -v error -show_entries format=duration -of csv=p=0 audio/narration.wav   # expect 500–560 s
```

## STEP 1 — Cleanup, loudness, silence trim

```bash
ffmpeg -y -i audio/narration.wav -af "highpass=f=80,acompressor=threshold=-18dB:ratio=2:attack=20:release=250,alimiter=limit=-1.5dB" -ar 48000 -ac 1 work/narration_clean.wav
# (add "deesser," after acompressor if your build has it)
ffmpeg -y -i work/narration_clean.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11" -ar 48000 -ac 1 work/narration_norm.wav
# Trim leading/trailing silence so first word starts ~0.2s in and tail ≤0.3s (makes the Step-2 delay arithmetic exact):
ffmpeg -y -i work/narration_norm.wav -af "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.2,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.3,areverse" work/narration_vo.wav
ffmpeg -i work/narration_vo.wav -af "loudnorm=print_format=summary" -f null - 2>&1 | grep -A3 "Input Integrated"   # ≈ -16 LUFS, TP ≤ -1.5 dB
```

## STEP 2 — Real timestamps → timeline (chronological, validated)

```bash
pip install whisperx
whisperx work/narration_vo.wav --model large-v2 --output_format json --output_dir work/
```

Save as `tools/build_timeline.py` and run `python3 tools/build_timeline.py`:

```python
import json, csv, sys, difflib

with open("work/narration_vo.json") as f:
    data = json.load(f)
words = [(float(w["start"]), float(w["end"]), str(w["word"]).lower().strip())
         for seg in data["segments"] for w in seg["words"]]
if not words:
    sys.exit("ERROR: WhisperX output contains no words")
NARR_END = words[-1][1]            # end of last spoken word (narration-relative)

units = []
with open("timeline_cues.csv") as f:
    for row in csv.DictReader(f):
        units.append((row["unit"], row["cue"].strip(), float(row["min_dur"])))

# Chronological matching: each cue is searched ONLY forward of the previous match.
pos = 0
starts = []
for unit, cue, _ in units:
    if cue == "<title_card>":
        starts.append((unit, 0.0)); continue
    if cue == "<narration_end>":
        starts.append((unit, NARR_END)); continue
    cw = cue.lower().split(); n = len(cw)
    best_i, best_r = None, -1.0
    for i in range(pos, len(words) - n + 1):
        chunk = " ".join(w[2] for w in words[i:i+n])
        r = difflib.SequenceMatcher(None, chunk, " ".join(cw)).ratio()
        if r > best_r:
            best_i, best_r = i, r
    if best_i is None or best_r < 0.6:
        sys.exit(f"ERROR: cue not found reliably: {unit} {cue!r} (best ratio {best_r:.2f})")
    # Ambiguity detection: any other strong candidate more than 2 words away?
    amb = [i for i in range(pos, len(words) - n + 1)
           if i != best_i and abs(i - best_i) > 2
           and difflib.SequenceMatcher(None,
                " ".join(w[2] for w in words[i:i+n]), " ".join(cw)).ratio() >= best_r - 0.03]
    if amb:
        sys.exit(f"ERROR: ambiguous cue match for {unit} {cue!r}: word indices {[best_i] + amb}")
    starts.append((unit, words[best_i][0]))
    pos = best_i + 1        # next cue must match AFTER this one (no duplicates/backtracking)

# Validation
t = [s for _, s in starts]
assert units[0][1] == "<title_card>" and t[0] == 0.0, "first unit must be title card at 0.0"
assert units[1][0] == "01-02", "second unit must be the first narration shot"
narr_start = t[1]
assert 1.0 <= narr_start <= 3.0, f"first-word time implausible: {narr_start:.2f}s"
assert all(t[i] < t[i+1] for i in range(len(t)-1)), "timestamps not strictly increasing (duplicate match?)"
assert t[-2] < NARR_END, "last content unit starts after narration ends"
assert 480.0 <= NARR_END <= 600.0, f"narration length out of range: {NARR_END:.1f}s"

END_CARD = 5.0
rows = []
for i, (unit, s) in enumerate(starts):
    e = starts[i+1][1] if i + 1 < len(starts) else NARR_END + END_CARD
    rows.append([unit, f"{s:.3f}", f"{e:.3f}", f"{e - s:.3f}"])
for (unit, cue, mind), (u2, s) in zip(units, starts):
    idx = [r for r in rows if r[0] == unit][0]
    if float(idx[3]) < mind * 0.6:
        print(f"WARNING: {unit} span {idx[3]}s < 60% of min duration {mind}s — re-pace or merge units")
with open("work/timeline.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["unit","start","end","duration"]); w.writerows(rows)
print(f"OK: {len(rows)} units; first word {narr_start:.2f}s; narration ends {NARR_END:.2f}s; total {NARR_END + END_CARD:.2f}s")
```

**Delay constant (used by Steps 3.5, 6a, 6c):** narration words are narration-relative; the video-absolute time of any word = relative + DELAY, where DELAY places the first word exactly at the end of the 6.0s title card:
```bash
DELAY_MS=$(python3 -c "import json;d=json.load(open('work/narration_vo.json'));print(int(round((6.0-d['segments'][0]['words'][0]['start'])*1000)))")
echo "narration delay: ${DELAY_MS} ms"
```
Title card duration = 6.0s (fixed). Video total = 6.0 + NARR_END + 5.0 − first_word_rel, ≈ 9:00 ± 15s.

**Caption regeneration (from the same JSON):** cue text = the 94 verbatim cue texts in `03-CAPTIONS.srt`; cue start = first word's relative start + DELAY_MS/1000; cue end = next cue's start − 0.2s (capped at that cue's last word end + 0.5s); **the last cue ends at the actual last-word end (absolute), never beyond video duration; the end card carries no caption.** Validate: strictly increasing, no overlaps, every end ≤ video total.

## STEP 3 — Resolution gate, then normalize + re-time

**3a. Resolution gate (resolves the 'never upscale' contradiction):** the final render is 1080p. Preferred: every clip is generated at ≥1920×1080 native. Before normalization:
```bash
for f in clips/*.mp4; do
  W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$f")
  H=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$f")
  if [ "$W" -lt 1920 ] || [ "$H" -lt 1080 ]; then
    if [ "$W" -lt 960 ] || [ "$H" -lt 540 ]; then echo "REJECT (regenerate): $f ${W}x${H}"
    else echo "WAIVER required: $f ${W}x${H} -> append to work/resolution_waivers.csv"; fi
  fi
done
```
**Policy:** clips below 1080p are rejected unless (a) the provider's free tier genuinely caps below 1080p — verify BEFORE generation; (b) each such clip is listed in `work/resolution_waivers.csv` (unit, native size, reason); (c) native size ≥960×540. Waiver-listed clips are the ONLY permitted upscale, performed by the flagged lanczos scale in 3b. Anything smaller than 960×540 is regenerated, never upscaled.

**3b. Normalize (identical parameters for all clips — concat in Step 4 requires this):**
```bash
for f in clips/*.mp4; do
  ffmpeg -y -i "$f" -vf "scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,fps=24000/1001,format=yuv420p" -an -c:v libx264 -preset medium -crf 16 "work/$(basename "$f" .mp4)_norm.mp4"
done
```
(The scale step crops 1080p+ sources and upscales ONLY waiver-listed clips — the documented deviation.)

**3c. Re-time each clip to its timeline span** (factor = span ÷ clip duration; keep within 0.85–1.15, else regenerate the clip at a closer length):
```bash
ffmpeg -y -i work/01-02_norm.mp4 -vf "setpts=1.44*PTS" -r 24000/1001 -an work/01-02_timed.mp4   # example: 5.0s clip → 7.2s span
ffprobe -v error -show_entries format=duration -of csv=p=0 work/01-02_timed.mp4   # must equal timeline span ±0.15s
```

## STEP 3.5 — Generate the two text cards (01-01, 06-08)

These are FFmpeg-rendered; no generated clip needed. Replace `<fontfile>` with any installed serif TTF (e.g. `/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf`).

```bash
# Title card, duration 6.0s (matches STEP 2 delay constant):
ffmpeg -y -f lavfi -i "color=c=black:s=1920x1080:r=24000/1001:d=6" \
  -vf "drawtext=fontfile=<fontfile>:text='WHAT IF GRAVITY DOUBLED AT MIDNIGHT?':fontcolor=0xE8B04B:fontsize=62:x=(w-text_w)/2:y=(h-text_h)/2:alpha='if(lt(t\,1.5)\,t/1.5\,if(lt(t\,4.5)\,1\,(6-t)/1.5))',noise=alls=6:allf=t,format=yuv420p" \
  -t 6 -c:v libx264 -preset medium -crf 16 work/01-01_timed.mp4

# End card, duration 5.0s:
ffmpeg -y -f lavfi -i "color=c=black:s=1920x1080:r=24000/1001:d=5" \
  -vf "drawtext=fontfile=<fontfile>:text='WHAT IF?':fontcolor=0xE8B04B:fontsize=72:x=(w-text_w)/2:y=(h-text_h)/2:alpha='if(lt(t\,1)\,t\,if(lt(t\,3.5)\,1\,(5-t)/1.5))',noise=alls=6:allf=t,format=yuv420p" \
  -t 5 -c:v libx264 -preset medium -crf 16 work/06-08_timed.mp4
```
(Commas inside drawtext expressions are escaped `\,` because the filtergraph parser treats unescaped commas as filter separators.) Verify both play and durations are exactly 6.000/5.000.

## STEP 4 — Concatenate (61 units)

`work/cliplist.txt`, one line per unit in timeline order, then:
```bash
ffmpeg -y -f concat -safe 0 -i work/cliplist.txt -c copy work/video_raw.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 work/video_raw.mp4
# must equal timeline total (6.0 + NARR_END + 5.0 − first_word_rel), ±0.5s
```

## STEP 5 — Letterbox, grain, grade

```bash
ffmpeg -y -i work/video_raw.mp4 -vf "scale=1920:804,drawbox=x=0:y=0:w=1920:h=138:color=black@1:t=fill,drawbox=x=0:y=942:w=1920:h=138:color=black@1:t=fill,noise=alls=6:allf=t,eq=saturation=0.92:contrast=1.04,format=yuv420p" -c:v libx264 -preset medium -crf 16 work/video_master.mp4
```
Note: this intermediate encode plus the Step 7 final encode is a deliberate two-generation chain (grade isolation); acceptable quality impact at crf 16. Verify bars at [0:30], [2:30], [4:30], [6:00], [7:30].

## STEP 6 — Music & SFX mix (narration enters EXACTLY ONCE — in 6c)

**6a. Music bed.** Trims come from `work/timeline.csv` in ABSOLUTE time: the s1 segment spans [0 → scene-1 end] (covers the title lead-in); s2–s5 span their scene windows; s6 spans [scene-6 start → video total] (covers the end card). Example values are planned-timeline placeholders — REPLACE with your numbers:
```bash
ffmpeg -y -i audio/music/s1.mp3 -i audio/music/s2.mp3 -i audio/music/s3.mp3 -i audio/music/s4.mp3 -i audio/music/s5.mp3 -i audio/music/s6.mp3 -filter_complex "[0:a]atrim=0:75,asetpts=PTS-STARTPTS[a0];[1:a]atrim=0:62,asetpts=PTS-STARTPTS[a1];[2:a]atrim=0:98,asetpts=PTS-STARTPTS[a2];[3:a]atrim=0:66,asetpts=PTS-STARTPTS[a3];[4:a]atrim=0:50,asetpts=PTS-STARTPTS[a4];[5:a]atrim=0:89,asetpts=PTS-STARTPTS[a5];[a0][a1]acrossfade=d=2:c1=tri:c2=tri[m1];[m1][a2]acrossfade=d=2:c1=tri:c2=tri[m2];[m2][a3]acrossfade=d=2:c1=tri:c2=tri[m3];[m3][a4]acrossfade=d=2:c1=tri:c2=tri[m4];[m4][a5]acrossfade=d=2:c1=tri:c2=tri,apad=whole_dur=<TOTAL>" -ar 48000 -ac 2 work/music_bed.wav
```
(`<TOTAL>` = the Step-4 duration; `apad` guarantees the bed reaches exactly video length.)

**6b. Duck the music — OUTPUT IS MUSIC ONLY, no narration mixed here:**
```bash
ffmpeg -y -i work/music_bed.wav -i work/narration_vo.wav -filter_complex "[1:a]aformat=sample_rates=48000:channel_layouts=stereo[sc];[0:a][sc]sidechaincompress=threshold=0.05:ratio=4:attack=100:release=600[bed]" -map "[bed]" -ar 48000 -ac 2 work/music_ducked.wav
```
(The narration input is used ONLY as the sidechain trigger. Verify: during a pure narration pause, music should still be present in `music_ducked.wav` — if you hear narration in this file, the command was altered; restore this exact form.)

**6c. Final mix — narration enters here, once.** `adelay` uses the STEP 2 delay constant, not a hardcoded value. SFX timestamps = relative cue time + DELAY_MS (example values shown; extend the pattern for all 27 SFX — one `-i` and one `[N:a]adelay=…,volume=…[sN]` chain each, incrementing `inputs=`):
```bash
ffmpeg -y -i work/narration_vo.wav -i work/music_ducked.wav \
  -i audio/sfx/clock_tick.wav -i audio/sfx/mattress_creak.wav -i audio/sfx/cane_drop.wav \
  -filter_complex "[0:a]adelay=${DELAY_MS}:all=1,apad[n]; \
[2:a]adelay=25400:all=1,volume=-14dB[s0]; \
[3:a]adelay=32000:all=1,volume=-10dB[s1]; \
[4:a]adelay=119300:all=1,volume=-8dB[s2]; \
[1:a][s0][s1][s2]amix=inputs=4:duration=longest:normalize=0[mix]; \
[mix][n]amix=inputs=2:duration=longest:normalize=0" \
  -ar 48000 -ac 2 work/final_mix.wav
```
Structure guarantee against duplication: input 0 (narration) appears in exactly one `amix`; `music_ducked.wav` contains zero narration by construction. Verify `final_mix.wav` duration ≈ video total.

**6d. Loudness:**
```bash
ffmpeg -y -i work/final_mix.wav -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 48000 -ac 2 work/final_mix_norm.wav
ffmpeg -i work/final_mix_norm.wav -af "loudnorm=print_format=summary" -f null - 2>&1 | grep -A3 "Input Integrated"   # ≈ -14 LUFS, TP ≤ -1.0
```
Listen-check: VO clear throughout; music never masks VO; the 1.5–2s pause after "It's the forgetting." stays silent; narration is never audible twice.

## STEP 7 — Final export

```bash
ffmpeg -y -i work/video_master.mp4 -c:v libx264 -profile:v high -level 4.1 -b:v 14M -x264-params "keyint=48:min-keyint=48:scenecut=0" -pass 1 -passlogfile out/v1pass -an -f null -
ffmpeg -y -i work/video_master.mp4 -i work/final_mix_norm.wav -map 0:v -map 1:a -c:v libx264 -profile:v high -level 4.1 -b:v 14M -x264-params "keyint=48:min-keyint=48:scenecut=0" -pass 2 -passlogfile out/v1pass -c:a aac -b:a 320k -ar 48000 -movflags +faststart out/video1_final.mp4
```
Playback verification (MANDATORY): ffprobe confirms 1920×1080, 24000/1001, h264 + aac/48000/2ch; VLC scrub full length; A/V sync at each scene's first word (absolute times from timeline.csv); plays start→end without freezes.

## STEP 8 — Captions

Upload the regenerated SRT (Step 2 rules): **94 cues**; text verbatim; ≤42 chars/line, ≤2 lines; no cue extends beyond the video's total duration; last cue ends at the actual last-word end; the end card has no caption.

## SECTION 7 — Assets → finished MP4

1. narration.wav → 2. cleanup + loudnorm + silence trim → 3. WhisperX → 4. timeline.csv (chronological matching, validated; title card at 0; first narration shot at first-word time) → 5. resolution gate → 6. normalize + re-time 59 clips → 7. render 2 text cards → 8. concat 61 units → 9. letterbox/grain/grade → 10. music bed + music-only ducking + single narration mix → 11. loudness → 12. 2-pass export → 13. playback verify → 14. captions. No step skipped; no step alters the script.

## SECTION 8 — QUALITY-CONTROL CHECKLIST (all must pass)

**Narration:** [ ] −16 LUFS, TP ≤ −1.5 dB; [ ] §6 beats honored; [ ] word-for-word identical to `02-NARRATION-TTS.md`; [ ] narration audible exactly once in the final mix (no doubling).
**Visuals:** [ ] all 61 units match prompts; [ ] faceless rule holds; [ ] continuity table satisfied (bedroom layout, clock 11:59→12:00→7:02, wardrobe after Scene 2, shelf sag, fan arc); [ ] consistent grade; [ ] zero watermarks; [ ] no text except the two cards; [ ] resolution gate passed or waivers documented.
**Transitions:** [ ] hard cuts on narration beats; [ ] dissolves only at 2-6, 6-1, Scene-5 entry; [ ] 4-9→6-2 match-cut frames match; [ ] 6-5 unbroken; [ ] no dead air >1s.
**Sound:** [ ] ducking 4–6 dB under VO; [ ] 27 SFX cues placed at timeline times, never masking; [ ] "It's the forgetting." silence preserved; [ ] master −14 LUFS / TP ≤ −1 dB; [ ] full listen-through, zero dropouts, zero doubled narration.
**Captions:** [ ] 94 cues; [ ] timings from WhisperX + DELAY offset; [ ] text verbatim; [ ] ≤42 chars/line, ≤2 lines; [ ] no overlaps; [ ] no cue beyond video duration.
**Science:** [ ] Scene 5 speculation labeled; [ ] "informed reasoning, not a certainty" present; [ ] no invented statistics; [ ] 180/360 lb illustrative only.
**Final:** [ ] runtime = timeline total ±1s; [ ] 1080p/23.976/H.264/AAC; [ ] plays start→end in VLC + YouTube preview; [ ] captions import cleanly; [ ] 07 pre-render checklist passed before assembly.
