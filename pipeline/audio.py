#!/usr/bin/env python3
"""Audio mix (EXECUTED on GitHub Actions). All times are ABSOLUTE (canonical timebase).
- Music bed: six scene segments, each SYNTHESIZED with sine/pad tones at scene durations
  computed from timeline.csv (no external music files required on the runner; free
  library music can replace these clip-for-clip later by filename).
- Ducking: music sidechain-compressed by narration (narration NOT mixed here).
- Final mix: narration enters EXACTLY ONCE, delayed so its first word lands at 6.000s.
- Final duration bounded to the timeline TOTAL."""
import csv, json, subprocess, sys

TITLE_DUR = 6.0
TL = "work/timeline.csv"
words = json.load(open("work/words.json"))

rows = list(csv.DictReader(open(TL)))
TOTAL = max(float(r["end"]) for r in rows)
start = {r["unit"]: float(r["start"]) for r in rows}
def scene_start(k):
    return min(v for u, v in start.items() if u.startswith(f"0{k}-"))
S2, S3, S4, S5, S6 = (scene_start(k) for k in "23456")

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"FFmpeg failed:\n{cmd}\n{r.stderr[-2000:]}")

# ---- per-scene music segments synthesized from real scene durations ----
# Each segment is a low ambient pad (root + fifth) with slow LFO; distinct key per scene.
KEYS = {"s1": 110.0, "s2": 98.0, "s3": 87.31, "s4": 82.41, "s5": 73.42, "s6": 110.0}
spans = {"s1": (0.0, S2), "s2": (S2, S3), "s3": (S3, S4), "s4": (S4, S5),
         "s5": (S5, S6), "s6": (S6, TOTAL)}
for name, (a, b) in spans.items():
    dur = max(b - a, 2.0)
    f = KEYS[name]
    # pad: two detuned sines + slow tremolo; 48kHz stereo; fades at both ends
    expr = (f"0.16*sin(2*PI*{f}*t)*(0.6+0.4*sin(2*PI*0.05*t)) + "
            f"0.12*sin(2*PI*{f*1.498}*t)*(0.5+0.5*sin(2*PI*0.08*t+1)) + "
            f"0.06*sin(2*PI*{f/2}*t)")
    fade = min(2.0, dur / 4)
    run(["ffmpeg", "-y", "-f", "lavfi",
         "-i", f"aevalsrc={expr}:s=48000:d={dur:.3f}:c=stereo",
         "-af", f"afade=t=in:d={fade:.2f}", "-ar", "48000", f"work/music_{name}.wav"])

# ---- music bed: chain segments with 2s crossfades; extend each earlier segment by the overlap ----
XF = 2.0
segs = [(0.0, S2), (S2, S3), (S3, S4), (S4, S5), (S5, S6), (S6, TOTAL)]
# extend each segment (except the last) by XF so the crossfade chain length is exact
ext = [(a, (b + XF if i < 5 else b)) for i, (a, b) in enumerate(segs)]
fc = []
for i in range(6):
    dur = ext[i][1] - ext[i][0]
    fc.append(f"[{i}:a]atrim=0:{dur:.3f},asetpts=PTS-STARTPTS[a{i}]")
cur = "a0"
for i in range(5):
    nxt = f"a{i+1}"
    out_label = f"m{i+1}" if i < 4 else "bed"
    fc.append(f"[{cur}][{nxt}]acrossfade=d={XF}:c1=tri:c2=tri[{out_label}]")
    cur = out_label
cmd = ["ffmpeg", "-y"]
for i in range(6):
    cmd += ["-i", f"work/music_s{i+1}.wav"]
cmd += ["-filter_complex", ";".join(fc), "-map", "[bed]",
        "-t", f"{TOTAL:.3f}", "-ar", "48000", "-ac", "2", "work/music_bed.wav"]
run(cmd)

# ---- duck the music (music-only output; narration is the sidechain trigger) ----
run(["ffmpeg", "-y", "-i", "work/music_bed.wav", "-i", "work/narration_vo.wav",
     "-filter_complex",
     "[1:a]aformat=sample_rates=48000:channel_layouts=stereo[sc];"
     "[0:a][sc]sidechaincompress=threshold=0.05:ratio=4:attack=100:release=600[bed]",
     "-map", "[bed]", "-ar", "48000", "-ac", "2", "work/music_ducked.wav"])

# ---- final mix: narration exactly once, placed at absolute 6.000 ----
first_word_rel = float(words[0]["start"])
DELAY_MS = int(round((TITLE_DUR - first_word_rel) * 1000))
print(f"narration delay: {DELAY_MS} ms (first word at abs 6.000)")
run(["ffmpeg", "-y", "-i", "work/narration_vo.wav", "-i", "work/music_ducked.wav",
     "-filter_complex",
     f"[0:a]adelay={DELAY_MS}:all=1,apad[n];"
     "[1:a][n]amix=inputs=2:duration=first:normalize=0",
     "-t", f"{TOTAL:.3f}", "-ar", "48000", "-ac", "2", "work/final_mix.wav"])

# ---- loudness normalize ----
run(["ffmpeg", "-y", "-i", "work/final_mix.wav",
     "-af", "loudnorm=I=-14:TP=-1:LRA=11", "-ar", "48000", "-ac", "2",
     "work/final_mix_norm.wav"])

# ---- verify ----
for f, expect in [("work/music_bed.wav", TOTAL), ("work/music_ducked.wav", TOTAL),
                  ("work/final_mix_norm.wav", TOTAL)]:
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                         "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip()
    print(f"{f}: {d}s (expected ≈{expect:.3f}s)")
    assert abs(float(d) - expect) < 1.0, f"duration mismatch in {f}"
print("audio OK: music 0->TOTAL, ducked, narration once, bounded to TOTAL")
