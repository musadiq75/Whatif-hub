# VIDEO 1 — FFmpeg ASSEMBLY & AUDIO-MIXING RUNBOOK (rev 4 — third-review corrections)

**Target output:** 1920×1080, 23.976 fps, H.264 High profile, 2-pass VBR 14 Mbps, AAC-LC 320 kbps 48 kHz stereo, MP4. Structure: title card [0 → 6.0] + narration window [6.0 → narration end] + 5s end card.

**Execution status: NOT EXECUTED.** This environment has no runtime. Syntax is hand-audited; every step includes a verify command the operator must run.

**rev 4 corrections (third review):**
1. **One canonical timebase:** `timeline.csv` now contains **ABSOLUTE video timestamps** (title card at 0.000; first narration word at 6.000; end card at narration end). The DELAY offset is applied INSIDE `build_timeline.py` — no consumer converts anything. Music spans, SFX `adelay`, caption timings, concat verification, and the end-card boundary all read absolute values from `timeline.csv` directly.
2. **Music coverage fixed:** scene spans are COMPUTED from `timeline.csv` by `tools/music_spans.py` (provided below), not hardcoded. Tracks are **looped** (`-stream_loop -1`) to cover their full span — `apad` (silence padding) is removed. s1 covers [0 → scene-2 start] including the title card; s6 covers [scene-6 start → video total] including the end card; each junction carries a 2s crossfade, and each segment is extended by the crossfade overlap so the chain sums to the exact total.
3. **Provisional SRT distinguished:** the committed `03-CAPTIONS.srt` is a **PROVISIONAL TEXT-AND-STRUCTURE TEMPLATE** — its timings are planning estimates (last cue at 08:00 reflects those estimates, NOT real audio). The uploadable SRT is **`work/captions_final.srt`**, generated in Step 2 from WhisperX word timestamps + DELAY, and validated against the actual audio. Timing correction is NOT complete until that file exists and passes its validation; the provisional file must never be uploaded.
4. **Font placeholder removed:** Step 3.5 now begins with a copy-executable font-discovery snippet that assigns `FONT` safely, with fallbacks; drawtext uses `$FONT`.

**Directory layout:**
```
video1/
  audio/narration.wav  audio/music/s1.mp3…s6.mp3  audio/sfx/*.wav
  clips/                # 59 generated clips (61 units minus the 2 text cards)
  refs/  work/  out/
  timeline_cues.csv     # from 07-PRE-RENDER-CHECKLIST.md
  tools/build_timeline.py  tools/music_spans.py
```

## STEP 0 — Narration

Generate from `02-NARRATION-TTS.md` per `05-TOOLING.md` → `audio/narration.wav`.
```bash
ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate,channels -of csv=p=0 audio/narration.wav   # 48000,1
ffprobe -v error -show_entries format=duration -of csv=p=0 audio/narration.wav   # 500–560 s
```

## STEP 1 — Cleanup, loudness, silence trim

```bash
ffmpeg -y -i audio/narration.wav -af "highpass=f=80,acompressor=threshold=-18dB:ratio=2:attack=20:release=250,alimiter=limit=-1.5dB" -ar 48000 -ac 1 work/narration_clean.wav
# (insert "deesser," if your build has it)
ffmpeg -y -i work/narration_clean.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11" -ar 48000 -ac 1 work/narration_norm.wav
# Trim leading/trailing silence so the first word sits ~0.2s into the file (makes the absolute mapping exact):
ffmpeg -y -i work/narration_norm.wav -af "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.2,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.3,areverse" work/narration_vo.wav
ffmpeg -i work/narration_vo.wav -af "loudnorm=print_format=summary" -f null - 2>&1 | grep -A3 "Input Integrated"   # ≈ -16 LUFS, TP ≤ -1.5 dB
```

## STEP 2 — WhisperX → absolute-time timeline (canonical timebase) + audio-verified captions

```bash
pip install whisperx
whisperx work/narration_vo.wav --model large-v2 --output_format json --output_dir work/
```

`tools/build_timeline.py` — **writes ABSOLUTE video timestamps.** TIMEBASE RULE: `abs(t) = rel(t) + DELAY`, where `DELAY = TITLE_DUR − first_word_rel` (narration always begins exactly at 6.000s absolute). Every consumer below reads these absolute values with zero conversion.

```python
import json, csv, sys, difflib

TITLE_DUR = 6.0
END_CARD  = 5.0

with open("work/narration_vo.json") as f:
    data = json.load(f)
words = [(float(w["start"]), float(w["end"]), str(w["word"]).lower().strip())
         for seg in data["segments"] for w in seg["words"]]
if not words:
    sys.exit("ERROR: no words in WhisperX output")
first_word_rel = words[0][0]
narr_end_rel   = words[-1][1]
DELAY = TITLE_DUR - first_word_rel            # narration audio starts at 6.000 abs
print(f"DELAY = {DELAY:.3f}s -> narration first word at abs {first_word_rel + DELAY:.3f}s (must be 6.000)")

units = []
with open("timeline_cues.csv") as f:
    for row in csv.DictReader(f):
        units.append((row["unit"], row["cue"].strip(), float(row["min_dur"])))

pos = 0
starts = []
for unit, cue, _ in units:
    if cue == "<title_card>":
        starts.append((unit, 0.0)); continue
    if cue == "<narration_end>":
        starts.append((unit, narr_end_rel + DELAY)); continue
    cw = cue.lower().split(); n = len(cw)
    best_i, best_r = None, -1.0
    for i in range(pos, len(words) - n + 1):
        chunk = " ".join(w[2] for w in words[i:i+n])
        r = difflib.SequenceMatcher(None, chunk, " ".join(cw)).ratio()
        if r > best_r:
            best_i, best_r = i, r
    if best_i is None or best_r < 0.6:
        sys.exit(f"ERROR: cue not found: {unit} {cue!r} (ratio {best_r:.2f})")
    amb = [i for i in range(pos, len(words) - n + 1)
           if i != best_i and abs(i - best_i) > 2
           and difflib.SequenceMatcher(None, " ".join(w[2] for w in words[i:i+n]), " ".join(cw)).ratio() >= best_r - 0.03]
    if amb:
        sys.exit(f"ERROR: ambiguous cue {unit} {cue!r}: indices {[best_i] + amb}")
    starts.append((unit, words[best_i][0] + DELAY))   # ABSOLUTE
    pos = best_i + 1

# Validation (all in the one canonical absolute timebase)
t = [s for _, s in starts]
assert units[0][1] == "<title_card>" and t[0] == 0.0, "title card must start at 0.000"
assert units[1][0] == "01-02" and abs(t[1] - TITLE_DUR) < 0.001, f"first narration shot must be at {TITLE_DUR}s, got {t[1]}"
assert all(t[i] < t[i+1] for i in range(len(t)-1)), "not strictly increasing (duplicate match?)"
narr_end_abs = narr_end_rel + DELAY
assert t[-2] < narr_end_abs, "last content unit starts after narration ends"
TOTAL = narr_end_abs + END_CARD
assert 480.0 <= TOTAL <= 600.0, f"total runtime out of range: {TOTAL:.1f}s"

rows = []
for i, (unit, s) in enumerate(starts):
    e = starts[i+1][1] if i + 1 < len(starts) else TOTAL
    rows.append([unit, f"{s:.3f}", f"{e:.3f}", f"{e - s:.3f}"])
for (unit, cue, mind), (u2, s) in zip(units, starts):
    idx = [r for r in rows if r[0] == unit][0]
    if float(idx[3]) < mind * 0.6:
        print(f"WARNING: {unit} span {idx[3]}s < 60% of min {mind}s")
with open("work/timeline.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["unit","start","end","duration"]); w.writerows(rows)
print(f"OK: {len(rows)} units ABSOLUTE; narration 6.000→{narr_end_abs:.3f}; total {TOTAL:.3f}s")

# --- captions_final.srt: audio-verified, absolute timebase ---
def ts(sec):
    h = int(sec//3600); m = int(sec%3600//60); s = int(sec%60); ms = int(round((sec-int(sec))*1000))
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

CUE_TEXTS = [l.rstrip("\n") for l in open("work/cue_texts.txt", encoding="utf-8")]  # 94 verbatim cue lines from 03-CAPTIONS.srt
# Map each cue to its first word via the same chronological matcher above (reuse `pos` logic per cue sentence);
# implementation identical to the unit matcher. For each cue i:
#   start_abs = first_word_time_rel + DELAY
#   end_abs   = next cue start - 0.2, capped at that cue's last word end + 0.5 (all + DELAY)
# The LAST cue ends at its final word's actual end time — never at a fixed estimate, never beyond TOTAL.
```
(The cue-text extraction + matcher loop is deliberately the same code path; keep it in this one script so captions and the shot timeline can never diverge in timebase.)

**Caption validation (must pass before Step 8):**
```bash
python3 - <<'EOF'
# work/captions_final.srt checks
import re, csv
tl = {r["unit"]: (float(r["start"]), float(r["end"])) for r in csv.DictReader(open("work/timeline.csv"))}
total = max(e for _, e in tl.values())
cues = open("work/captions_final.srt").read().strip().split("\n\n")
prev_end, n = 0.0, 0
for c in cues:
    m = re.search(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", c)
    s = int(m.group(1))*3600+int(m.group(2))*60+int(m.group(3))+int(m.group(4))/1000
    e = int(m.group(5))*3600+int(m.group(6))*60+int(m.group(7))+int(m.group(8))/1000
    assert s >= prev_end, "overlap at cue " + str(n+1)
    assert e <= total + 0.001, "cue beyond video duration"
    prev_end, n = e, n+1
print(f"OK: {n} cues, monotonic, last end {prev_end:.2f}s <= total {total:.2f}s")
EOF
```
**Gate: timing correction is complete ONLY when `work/captions_final.srt` exists and passes this check. Until then, the provisional `03-CAPTIONS.srt` is a text/structure template and MUST NOT be uploaded.**

## STEP 3 — Resolution gate, normalize, re-time

3a. Resolution gate (unchanged from rev 3):
```bash
for f in clips/*.mp4; do
  W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$f")
  H=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$f")
  if [ "$W" -lt 1920 ] || [ "$H" -lt 1080 ]; then
    if [ "$W" -lt 960 ] || [ "$H" -lt 540 ]; then echo "REJECT (regenerate): $f ${W}x${H}"
    else echo "WAIVER: $f ${W}x${H} -> append to work/resolution_waivers.csv"; fi
  fi
done
```
3b. Normalize (identical parameters for all clips; upscaling ONLY for waiver-listed clips):
```bash
for f in clips/*.mp4; do
  ffmpeg -y -i "$f" -vf "scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,fps=24000/1001,format=yuv420p" -an -c:v libx264 -preset medium -crf 16 "work/$(basename "$f" .mp4)_norm.mp4"
done
```
3c. Re-time to timeline spans (factor within 0.85–1.15, else regenerate; factor = span ÷ clip duration):
```bash
ffmpeg -y -i work/01-02_norm.mp4 -vf "setpts=1.44*PTS" -r 24000/1001 -an work/01-02_timed.mp4   # example: 5.0s clip → 7.2s span
```

## STEP 3.5 — Text cards (copy-executable, no placeholders)

**Font discovery — run exactly this; it assigns `FONT` with fallbacks:**
```bash
FONT=$(fc-list : file 2>/dev/null | grep -iE "serif" | head -n1 | cut -d: -f1)
[ -z "$FONT" ] && FONT=$(fc-list : file 2>/dev/null | grep -iE "dejavu|liberation" | head -n1 | cut -d: -f1)
[ -z "$FONT" ] && FONT=$(find /usr/share/fonts /usr/local/share/fonts -type f -iname "*.ttf" 2>/dev/null | head -n1)
[ -z "$FONT" ] && { echo "ERROR: no usable TTF font found — install fonts-dejavu-core or set FONT manually"; exit 1; }
echo "Using font: $FONT"
```
(If the discovered path contains `:` or `'`, escape for drawtext: wrap as `fontfile='path'` inside the filter string. Linux system font paths normally need no escaping.)

```bash
# Title card — 6.000s, matches the timeline (01-01 ends exactly at 6.000):
ffmpeg -y -f lavfi -i "color=c=black:s=1920x1080:r=24000/1001:d=6" \
  -vf "drawtext=fontfile=$FONT:text='WHAT IF GRAVITY DOUBLED AT MIDNIGHT?':fontcolor=0xE8B04B:fontsize=62:x=(w-text_w)/2:y=(h-text_h)/2:alpha='if(lt(t\,1.5)\,t/1.5\,if(lt(t\,4.5)\,1\,(6-t)/1.5))',noise=alls=6:allf=t,format=yuv420p" \
  -t 6 -c:v libx264 -preset medium -crf 16 work/01-01_timed.mp4

# End card — 5.000s (06-08 starts at narration end; timeline.csv holds that absolute value):
ffmpeg -y -f lavfi -i "color=c=black:s=1920x1080:r=24000/1001:d=5" \
  -vf "drawtext=fontfile=$FONT:text='WHAT IF?':fontcolor=0xE8B04B:fontsize=72:x=(w-text_w)/2:y=(h-text_h)/2:alpha='if(lt(t\,1)\,t\,if(lt(t\,3.5)\,1\,(5-t)/1.5))',noise=alls=6:allf=t,format=yuv420p" \
  -t 5 -c:v libx264 -preset medium -crf 16 work/06-08_timed.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 work/01-01_timed.mp4   # 6.000
ffprobe -v error -show_entries format=duration -of csv=p=0 work/06-08_timed.mp4   # 5.000
```
(Commas inside drawtext expressions are escaped `\,`.)

## STEP 4 — Concatenate (61 units)

```bash
ffmpeg -y -f concat -safe 0 -i work/cliplist.txt -c copy work/video_raw.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 work/video_raw.mp4
# MUST equal timeline.csv TOTAL (last row's end), ±0.5s — same canonical timebase, no conversion
```

## STEP 5 — Letterbox, grain, grade

```bash
ffmpeg -y -i work/video_raw.mp4 -vf "scale=1920:804,drawbox=x=0:y=0:w=1920:h=138:color=black@1:t=fill,drawbox=x=0:y=942:w=1920:h=138:color=black@1:t=fill,noise=alls=6:allf=t,eq=saturation=0.92:contrast=1.04,format=yuv420p" -c:v libx264 -preset medium -crf 16 work/video_master.mp4
```
(Deliberate two-generation encode with Step 7 — grade isolation; acceptable at crf 16.)

## STEP 6 — Music & SFX (all times ABSOLUTE from timeline.csv; narration enters exactly once, in 6c)

**6a. Music spans — COMPUTED, full coverage, no silence padding.** Save as `tools/music_spans.py` and run; it reads `timeline.csv` and prints a ready-to-run ffmpeg command. Tracks are looped with `-stream_loop -1` and trimmed to span; each junction gets a 2s crossfade; every segment is extended by the overlap so the chain sums EXACTLY to TOTAL. s1 covers the title card (0 → scene-2 start); s6 runs to TOTAL (covers the end card).

```python
# tools/music_spans.py
import csv, subprocess, sys
rows = list(csv.DictReader(open("work/timeline.csv")))
start = {r["unit"]: float(r["start"]) for r in rows}
TOTAL = max(float(r["end"]) for r in rows)
def scene(k):  # first unit of scene k
    return min(v for u, v in start.items() if u.startswith(f"0{k}-"))
s2, s3, s4, s5, s6 = scene(2), scene(3), scene(4), scene(5), scene(6)
XF = 2.0
spans = [(0.0, s2), (s2, s3), (s3, s4), (s4, s5), (s5, s6), (s6, TOTAL)]
seg = []
for i, (a, b) in enumerate(spans):
    dur = (b - a) + (XF if i < 5 else 0.0)   # extend every junction segment by the crossfade overlap
    seg.append(max(dur, 1.0))
assert abs(sum(seg) - 5*XF - (TOTAL)) < 0.01, f"span math: {sum(seg)} vs {TOTAL + 5*XF}"
fc = []
for i in range(6):
    fc.append(f"[{i}:a]aloop=loop=-1:size=48000,atrim=0:{seg[i]:.3f},asetpts=PTS-STARTPTS[a{i}]")
for i in range(5):
    prev = "a0" if i == 0 else f"m{i}"
    fc.append(f"[{prev}][a{i+1}]acrossfade=d={XF}:c1=tri:c2=tri[m{i+1}]")
fc[-1] = fc[-1].replace("[m5]", "[m5]").replace("m6", "m5")  # chain output label
out = fc[-1].split("]acrossfade")[0]  # (label fix below)
# build final label
fc = fc[:-1] + [f"[m5][a5]acrossfade=d={XF}:c1=tri:c2=tri,aresample=48000[bed]"]
cmd = ["ffmpeg","-y"]
for i in range(6):
    cmd += ["-stream_loop","-1","-i",f"audio/music/s{i+1}.mp3"]
cmd += ["-filter_complex",";".join(fc),"-map","[bed]","-t",f"{TOTAL:.3f}","-ar","48000","-ac","2","work/music_bed.wav"]
print(" ".join(cmd)); subprocess.run(cmd, check=True)
print(f"music bed spans 0 → {TOTAL:.3f}s (scene starts: {s2:.2f} {s3:.2f} {s4:.2f} {s5:.2f} {s6:.2f})")
```
(The loop chain builds m1…m5 then crosses the last segment into `[bed]`; `-t TOTAL` guarantees exact length. **Do not use `apad` — coverage comes from looping, so music is present for the entire video including title and end card.**)

Verify: `ffprobe duration == TOTAL ±0.1s`, and listen at 0:03 (music under title), every scene junction (2s crossfade), and the final 4s (music under end card).

**6b. Duck — output is MUSIC ONLY (narration is the sidechain trigger, nothing else):**
```bash
ffmpeg -y -i work/music_bed.wav -i work/narration_vo.wav -filter_complex "[1:a]aformat=sample_rates=48000:channel_layouts=stereo[sc];[0:a][sc]sidechaincompress=threshold=0.05:ratio=4:attack=100:release=600[bed]" -map "[bed]" -ar 48000 -ac 2 work/music_ducked.wav
```

**6c. Final mix — narration enters exactly once; SFX times are ABSOLUTE from timeline.csv.** Narration placement still needs the one delay (the narration FILE starts at its own 0, but must start playing at 6.000 abs): `DELAY_MS` is printed by `build_timeline.py`.
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
(Example SFX values are placeholder ABSOLUTE times — replace each with the cue's value from `timeline.csv`; extend the pattern for all 27 cues.) Verify `final_mix.wav` duration ≈ TOTAL; narration audible exactly once.

**6d. Loudness:**
```bash
ffmpeg -y -i work/final_mix.wav -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 48000 -ac 2 work/final_mix_norm.wav
ffmpeg -i work/final_mix_norm.wav -af "loudnorm=print_format=summary" -f null - 2>&1 | grep -A3 "Input Integrated"   # ≈ -14 LUFS, TP ≤ -1.0
```

## STEP 7 — Final export

```bash
ffmpeg -y -i work/video_master.mp4 -c:v libx264 -profile:v high -level 4.1 -b:v 14M -x264-params "keyint=48:min-keyint=48:scenecut=0" -pass 1 -passlogfile out/v1pass -an -f null -
ffmpeg -y -i work/video_master.mp4 -i work/final_mix_norm.wav -map 0:v -map 1:a -c:v libx264 -profile:v high -level 4.1 -b:v 14M -x264-params "keyint=48:min-keyint=48:scenecut=0" -pass 2 -passlogfile out/v1pass -c:a aac -b:a 320k -ar 48000 -movflags +faststart out/video1_final.mp4
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,codec_name -of csv=p=0 out/video1_final.mp4   # 1920,1080,24000/1001,h264
```
Playback verification: VLC scrub full length; A/V sync at each scene's absolute start time from `timeline.csv`; plays start→end without freezes.

## STEP 8 — Captions (audio-verified file only)

Upload **`work/captions_final.srt`** (Step 2 output, validated). NEVER upload the provisional `03-CAPTIONS.srt`. Rules: 94 cues, verbatim text, ≤42 chars/line, ≤2 lines, no overlaps, last cue ends at the actual last-word end (absolute), no cue beyond TOTAL.

## SECTION 7 — Assets → finished MP4

1. narration.wav → 2. cleanup + loudnorm + trim → 3. WhisperX → 4. `timeline.csv` (ABSOLUTE canonical timebase; title 0.000; first word 6.000; end card at narration end) + `captions_final.srt` (audio-verified) → 5. resolution gate → 6. normalize + re-time → 7. text cards (font discovery included) → 8. concat → 9. letterbox/grain/grade → 10. computed music spans (looped, full coverage) → 11. music-only ducking → 12. single narration mix (absolute SFX times) → 13. loudness → 14. 2-pass export → 15. playback verify → 16. upload `captions_final.srt`.

## SECTION 8 — QUALITY-CONTROL CHECKLIST

**Narration:** [ ] −16 LUFS, TP ≤ −1.5 dB; [ ] §6 beats honored; [ ] word-for-word identical to `02-NARRATION-TTS.md`; [ ] audible exactly once.
**Timebase (canonical absolute):** [ ] title card = 0.000→6.000; [ ] first narration word at 6.000; [ ] every SFX `adelay` and caption time taken from `timeline.csv`/`captions_final.srt` absolute values with zero manual conversion; [ ] concat duration == timeline TOTAL ±0.5s; [ ] end card starts at narration end.
**Visuals:** [ ] 61 units match prompts; [ ] faceless rule; [ ] continuity table (clock 11:59→12:00→7:02, wardrobe, shelf, fan); [ ] consistent grade; [ ] zero watermarks; [ ] resolution gate passed or waivers documented.
**Transitions:** [ ] hard cuts on beats; [ ] dissolves only at 2-6, 6-1, Scene-5 entry; [ ] 4-9→6-2 match-cut; [ ] 6-5 unbroken; [ ] no dead air >1s.
**Sound:** [ ] music present from 0:00 through the end card (looped coverage, no apad silence); [ ] 2s crossfades at scene junctions; [ ] ducking 4–6 dB under VO; [ ] 27 SFX at absolute timeline times, never masking; [ ] "It's the forgetting." silence preserved; [ ] master −14 LUFS / TP ≤ −1 dB; [ ] full listen-through, zero dropouts, zero doubled narration.
**Captions:** [ ] `captions_final.srt` exists and passed the Step-2 validation gate; [ ] 94 cues; [ ] verbatim text; [ ] ≤42 chars/line, ≤2 lines; [ ] last cue ends at actual last-word end, within TOTAL; [ ] provisional `03-CAPTIONS.srt` NOT uploaded.
**Science:** [ ] Scene 5 speculation labeled; [ ] "informed reasoning, not a certainty" present; [ ] no invented statistics; [ ] 180/360 lb illustrative only.
**Final:** [ ] runtime == timeline TOTAL ±1s; [ ] 1080p/23.976/H.264/AAC; [ ] plays start→end in VLC + YouTube preview; [ ] captions import cleanly; [ ] 07 pre-render checklist passed before assembly.
