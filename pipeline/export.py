#!/usr/bin/env python3
"""Final export + QC verification (EXECUTED on GitHub Actions).
Muxes video_master + final_mix_norm, 2-pass H.264, faststart; verifies:
dimensions, fps, codecs, duration vs timeline TOTAL, audio presence,
caption validity (94 cues, monotonic, within TOTAL)."""
import csv, re, subprocess, sys

TL = "work/timeline.csv"
rows = list(csv.DictReader(open(TL)))
TOTAL = max(float(r["end"]) for r in rows)

def run(cmd, cap=True):
    if cap:
        r = subprocess.run(cmd, capture_output=True, text=True)
    else:
        r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit(f"command failed: {cmd}\n{getattr(r, 'stderr', '')[-1500:]}")
    return r

def probe(f, sel, entries):
    return run(["ffprobe", "-v", "error", "-select_streams", sel,
                "-show_entries", entries, "-of", "csv=p=0", f]).stdout.strip()

# 2-pass export
run(["ffmpeg", "-y", "-i", "work/video_master.mp4", "-c:v", "libx264",
     "-profile:v", "high", "-level", "4.1", "-b:v", "14M",
     "-x264-params", "keyint=48:min-keyint=48:scenecut=0",
     "-pass", "1", "-passlogfile", "work/v1pass", "-an", "-f", "null", "-"])
run(["ffmpeg", "-y", "-i", "work/video_master.mp4", "-i", "work/final_mix_norm.wav",
     "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-profile:v", "high",
     "-level", "4.1", "-b:v", "14M", "-x264-params", "keyint=48:min-keyint=48:scenecut=0",
     "-pass", "2", "-passlogfile", "work/v1pass", "-c:a", "aac", "-b:a", "320k",
     "-ar", "48000", "-movflags", "+faststart", "-t", f"{TOTAL:.3f}",
     "out/video1_final.mp4"], cap=False)

# ---- QC ----
ok = True
v = probe("out/video1_final.mp4", "v:0", "width,height,r_frame_rate,codec_name")
print("video stream:", v)
assert v == "1920,1080,24000/1001,h264", f"unexpected video stream: {v}"
a = probe("out/video1_final.mp4", "a:0", "codec_name,sample_rate,channels")
print("audio stream:", a)
assert a == "aac,48000,2", f"unexpected audio stream: {a}"
d = float(probe("out/video1_final.mp4", None, "format=duration"))
print(f"duration: {d:.3f}s vs timeline TOTAL {TOTAL:.3f}s")
assert abs(d - TOTAL) < 1.0, "final duration deviates from timeline"

# audio presence: mean volume near the narration region must be well above silence
r = run(["ffmpeg", "-i", "out/video1_final.mp4", "-ss", "6", "-t", "30",
         "-af", "volumedetect", "-f", "null", "-"])
m = re.search(r"mean_volume: ([-\d.]+) dB", r.stderr)
print("mean volume (6-36s):", m.group(1) if m else "n/a", "dB")
assert m and float(m.group(1)) > -60, "no audible content in narration region"

# caption file validity
srt = open("work/captions_final.srt", encoding="utf-8").read()
cues = [b for b in srt.strip().split("\n\n") if b.strip()]
print("caption cues:", len(cues))
assert len(cues) == 94, f"expected 94 cues, got {len(cues)}"
prev_end, pat = 0.0, re.compile(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+),(\d+),(\d+)")
for b in cues:
    m = pat.search(b)
    s = int(m.group(1))*3600 + int(m.group(2))*60 + int(m.group(3)) + int(m.group(4))/1000
    e = int(m.group(5))*3600 + int(m.group(6))*60 + int(m.group(7)) + int(m.group(8))/1000
    assert s >= prev_end - 0.001, "caption overlap"
    assert e <= TOTAL + 0.001, "caption beyond video duration"
    prev_end = e
print(f"captions valid: monotonic, last end {prev_end:.3f}s <= TOTAL {TOTAL:.3f}s")

print("QC PASS: video1_final.mp4 plays the full timeline with audio and valid captions")
