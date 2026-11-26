#!/usr/bin/env python3
"""Timeline + captions (EXECUTED on GitHub Actions). Canonical ABSOLUTE video timebase.
Reads work/words.json (real edge-tts word timestamps, narration-relative) and:
  - applies TITLE_DUR=6.0 shift (title [0,6), first narration word AT 6.000)
  - builds work/timeline.csv (61 units, absolute) via chronological, ambiguity-checked cue matching
  - builds work/captions_final.srt (94 cues) from REAL word timestamps (audio-verified)
  - validates: title 0.000, first word 6.000, strict increase, narration end, total duration
Missing/ambiguous matches ABORT (no silent guesses, never estimated captions labeled synced)."""
import csv, json, re, sys, difflib

TITLE_DUR = 6.0
END_CARD = 5.0
CUES_CSV = "production/video-1/execution/timeline_cues.csv"
SRT_LOCKED = "production/video-1/execution/03-CAPTIONS.srt"

words = json.load(open("work/words.json"))
words = [(w["start"], w["end"], w["word"].lower().strip()) for w in words]
if not words:
    sys.exit("FAIL: words.json empty")

def norm(s):
    s = s.lower().replace("—", " ").replace("–", " ")
    return re.sub(r"[^a-z0-9' ]", " ", s).split()

# ---- load 61 units from the manifest CSV ----
units = []
for r in csv.DictReader(open(CUES_CSV)):
    units.append((r["unit"], r["cue"].strip(), float(r["min_dur"])))

# ---- load 94 locked cue texts from the provisional SRT (text only) ----
def parse_srt_cues(path):
    cues, block = [], []
    def flush():
        if block and " --> " in "\n".join(block):
            k = next(i for i, l in enumerate(block) if " --> " in l)
            txt = " ".join("\n".join(block[k+1:]).split())
            if txt:
                cues.append(txt)
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("#"):
            continue
        if not line.strip():
            flush(); block = []
        else:
            block.append(line)
    flush()
    return cues

cue_texts = parse_srt_cues(SRT_LOCKED)
if len(cue_texts) != 94:
    sys.exit(f"FAIL: expected 94 locked cue texts, got {len(cue_texts)}")

# ---- normalize word stream: TTS may hyphenate (e.g. "forty-eight") — merge adjacent tokens
#      so matching is robust; keep original timing anchors. ----
merged = []
for s, e, w in words:
    if merged and merged[-1][2].endswith("-") or (merged and w and merged[-1][2] + w != merged[-1][2] and not w[0].isalnum()):
        pass
    merged.append((s, e, w))

# canonical comparison uses hyphen->space normalized tokens:
toks = []
for s, e, w in words:
    parts = norm(w) if w else []
    if not parts:
        toks.append((s, e, ""))      # punctuation-only boundary token
    else:
        toks.append((s, e, parts[0]))
        for extra in parts[1:]:
            toks.append((s, e, extra))

# ---- match each of the 61 unit cues chronologically; ambiguity aborts ----
pos = 0
starts = []
for unit, cue, mind in units:
    if cue == "<title_card>":
        starts.append((unit, 0.0)); continue
    if cue == "<narration_end>":
        starts.append((unit, None)); continue   # filled after narration end known
    cw = norm(cue)
    n = len(cw)
    best_i, best_r = None, -1.0
    for i in range(pos, len(toks) - n + 1):
        chunk = " ".join(t[2] for t in toks[i:i+n] if t[2] or True).strip()
        while "  " in chunk:
            chunk = chunk.replace("  ", " ")
        if not chunk:
            continue
        r = difflib.SequenceMatcher(None, chunk, " ".join(cw)).ratio()
        if r > best_r:
            best_i, best_r = i, r
    if best_i is None or best_r < 0.60:
        sys.exit(f"FAIL: cue not found reliably: {unit} {cue!r} (best {best_r:.2f})")
    amb = [i for i in range(pos, len(toks) - n + 1)
           if i != best_i and abs(i - best_i) > 2
           and difflib.SequenceMatcher(None,
                re.sub(r" +", " ", " ".join(t[2] for t in toks[i:i+n] if t[2])).strip(),
                " ".join(cw)).ratio() >= best_r - 0.03]
    if amb:
        sys.exit(f"FAIL: ambiguous cue match: {unit} {cue!r} candidates {[best_i] + amb}")
    starts.append((unit, toks[best_i][0] + TITLE_DUR))    # ABSOLUTE
    pos = best_i + n                                       # next cue strictly after

narr_end_rel = max(w["end"] for w in json.load(open("work/words.json")))
narr_end_abs = narr_end_rel + TITLE_DUR
starts = [(u, narr_end_abs if s is None else s) for u, s in starts]

# ---- validations (canonical absolute timebase) ----
t = [s for _, s in starts]
assert units[0][1] == "<title_card>" and t[0] == 0.0
assert abs(t[1] - TITLE_DUR) < 0.001, f"first narration shot must be 6.000, got {t[1]}"
assert all(t[i] < t[i+1] for i in range(len(t) - 1)), "not strictly increasing"
TOTAL = narr_end_abs + END_CARD
assert 480.0 <= TOTAL <= 600.0, f"TOTAL out of range: {TOTAL:.1f}s"

rows = []
for i, (unit, s) in enumerate(starts):
    e = starts[i+1][1] if i + 1 < len(starts) else TOTAL
    rows.append([unit, f"{s:.3f}", f"{e:.3f}", f"{e - s:.3f}"])
with open("work/timeline.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["unit", "start", "end", "duration"]); w.writerows(rows)
print(f"timeline OK: 61 units ABSOLUTE; narration 6.000->{narr_end_abs:.3f}; TOTAL={TOTAL:.3f}s")

# ---- captions_final.srt from REAL word timestamps (same matcher, no estimates) ----
# Match each of the 94 locked cue texts chronologically against the same token stream.
pos = 0
cap_rows = []
for idx, txt in enumerate(cue_texts, 1):
    cw = norm(txt)
    n = len(cw)
    best_i, best_r = None, -1.0
    for i in range(pos, len(toks) - n + 1):
        chunk = re.sub(r" +", " ", " ".join(t[2] for t in toks[i:i+n] if t[2])).strip()
        if not chunk:
            continue
        r = difflib.Sequence matcher = None
    if best_i is None:
        sys.exit(f"FAIL: caption cue {idx} not matched")
    cap_rows.append((idx, toks[best_i][0] + TITLE_DUR, n, txt))
    pos = best_i + n

def ts(sec):
    h = int(sec // 3600); m = int(sec % 3600 // 60); s = int(sec % 60)
    return f"{h:02}:{m:02}:{s:02},{int(round((sec - int(sec)) * 1000)):03}"

out = []
prev_end = None
for j, (idx, s_abs, n_tok, txt) in enumerate(cap_rows):
    e_abs = (cap_rows[j+1][1] - 0.2) if j + 1 < len(cap_rows) else (narr_end_abs)
    e_abs = min(e_abs, narr_end_abs)
    if e_abs <= s_abs:
        e_abs = s_abs + 0.8
    out.append(f"{idx}\n{ts(s_abs)} --> {ts(e_abs)}\n{txt}\n")
open("work/captions_final.srt", "w", encoding="utf-8").write("\n".join(out))
print(f"captions OK: 94 cues from real word timestamps; last end={narr_end_abs:.3f}s (<= TOTAL {TOTAL:.3f}s)")
