#!/usr/bin/env python3
"""Timeline + captions (EXECUTED on GitHub Actions). Canonical ABSOLUTE video timebase.
Reads work/words.json (real edge-tts word timestamps, narration-relative) and:
  - applies TITLE_DUR=6.0 shift (title [0,6), first narration word AT 6.000)
  - builds work/timeline.csv (61 units, absolute) via chronological, ambiguity-checked cue matching
  - builds work/captions_final.srt (94 cues) from REAL word timestamps (audio-verified)
  - validates: title 0.000, first word 6.000, strict increase, narration end, total duration
Missing/ambiguous matches ABORT (no silent guesses; estimated captions are never labeled synced)."""
import csv, json, re, sys, difflib

TITLE_DUR = 6.0
END_CARD = 5.0
CUES_CSV = "production/video-1/execution/timeline_cues.csv"
SRT_LOCKED = "production/video-1/execution/03-CAPTIONS.srt"

raw_words = json.load(open("work/words.json"))
if not raw_words:
    sys.exit("FAIL: words.json empty")

def norm_tokens(s):
    s = s.lower().replace("\u2014", " ").replace("\u2013", " ").replace("-", " ")
    return [t for t in re.sub(r"[^a-z0-9' ]", " ", s).split() if t]

# Token stream: each TTS WordBoundary may emit multi-token text (e.g. "forty-eight");
# split into comparison tokens, all anchored at that boundary's time.
toks = []
for w in raw_words:
    s, e, txt = float(w["start"]), float(w["end"]), str(w.get("word", ""))
    parts = norm_tokens(txt)
    if not parts:
        continue
    for p in parts:
        toks.append((s, e, p))
if not toks:
    sys.exit("FAIL: no usable tokens in words.json")

def match(cw, pos):
    """Chronological fuzzy match of token list cw starting at/after pos.
    Returns (index, ratio). Ambiguity is reported by caller."""
    n = len(cw)
    best_i, best_r = None, -1.0
    for i in range(pos, len(toks) - n + 1):
        chunk = " ".join(t[2] for t in toks[i:i+n])
        r = difflib.SequenceMatcher(None, chunk, " ".join(cw)).ratio()
        if r > best_r:
            best_i, best_r = i, r
    return best_i, best_r

def must_match(label, cue, pos):
    cw = norm_tokens(cue)
    best_i, best_r = match(cw, pos)
    if best_i is None or best_r < 0.60:
        sys.exit(f"FAIL: cue not found reliably: {label} {cue!r} (best {best_r if best_i is not None else 'none'})")
    n = len(cw)
    amb = [i for i in range(pos, len(toks) - n + 1)
           if i != best_i and abs(i - best_i) > 2
           and difflib.SequenceMatcher(None, " ".join(t[2] for t in toks[i:i+n]),
                                        " ".join(cw)).ratio() >= best_r - 0.03]
    if amb:
        sys.exit(f"FAIL: ambiguous cue match: {label} {cue!r} candidates {[best_i] + amb}")
    return best_i, best_i + n

# ---- 61 unit boundaries ----
units = []
for r in csv.DictReader(open(CUES_CSV)):
    units.append((r["unit"], r["cue"].strip(), float(r["min_dur"])))

starts, pos = [], 0
for unit, cue, mind in units:
    if cue == "<title_card>":
        starts.append((unit, 0.0)); continue
    if cue == "<narration_end>":
        starts.append((unit, None)); continue
    i, pos = must_match(unit, cue, pos)
    starts.append((unit, toks[i][0] + TITLE_DUR))     # ABSOLUTE

narr_end_rel = max(float(w["end"]) for w in raw_words)
narr_end_abs = narr_end_rel + TITLE_DUR
starts = [(u, narr_end_abs if s is None else s) for u, s in starts]

# ---- validations (one canonical absolute timebase) ----
t = [s for _, s in starts]
assert units[0][1] == "<title_card>" and t[0] == 0.0, "title must start at 0.000"
assert abs(t[1] - TITLE_DUR) < 0.001, f"first narration shot must be 6.000, got {t[1]:.3f}"
assert all(t[i] < t[i+1] for i in range(len(t) - 1)), "timestamps not strictly increasing"
TOTAL = narr_end_abs + END_CARD
assert 480.0 <= TOTAL <= 600.0, f"TOTAL out of range: {TOTAL:.1f}s"
assert t[-2] < narr_end_abs, "last content unit starts after narration ends"

rows = []
for i, (unit, s) in enumerate(starts):
    e = starts[i+1][1] if i + 1 < len(starts) else TOTAL
    rows.append([unit, f"{s:.3f}", f"{e:.3f}", f"{e - s:.3f}"])
    span = e - s
    mind = dict((u, m) for u, c, m in units)[unit]
    if span < mind * 0.6:
        print(f"WARNING: {unit} span {span:.2f}s < 60% of min {mind}s")
with open("work/timeline.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["unit", "start", "end", "duration"]); w.writerows(rows)
print(f"timeline OK: 61 units ABSOLUTE; narration 6.000->{narr_end_abs:.3f}; TOTAL={TOTAL:.3f}s")

# ---- 94 caption cues from the SAME real word timestamps ----
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

cap_rows, pos = [], 0
for idx, txt in enumerate(cue_texts, 1):
    i, pos = must_match(f"caption#{idx}", txt, pos)
    cap_rows.append((idx, toks[i][0] + TITLE_DUR, txt))

def ts(sec):
    h = int(sec // 3600); m = int(sec % 3600 // 60); s = int(sec % 60)
    return f"{h:02}:{m:02}:{s:02},{int(round((sec - int(sec)) * 1000)):03}"

out, prev_end = [], 0.0
for j, (idx, s_abs, txt) in enumerate(cap_rows):
    if j + 1 < len(cap_rows):
        e_abs = cap_rows[j+1][1] - 0.2
    else:
        e_abs = narr_end_abs                       # LAST cue ends at actual last-word end
    e_abs = min(e_abs, narr_end_abs)
    if e_abs <= s_abs:
        e_abs = s_abs + 0.8
    assert s_abs >= prev_end - 0.001, f"caption {idx} overlaps"
    prev_end = e_abs
    assert e_abs <= TOTAL, f"caption {idx} beyond video duration"
    out.append(f"{idx}\n{ts(s_abs)} --> {ts(e_abs)}\n{txt}\n")
open("work/captions_final.srt", "w", encoding="utf-8").write("\n".join(out))
print(f"captions OK: 94 cues from real word timestamps; last end={prev_end:.3f}s <= TOTAL {TOTAL:.3f}s")
