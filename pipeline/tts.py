#!/usr/bin/env python3
"""Narration generator (EXECUTED on GitHub Actions).
Uses edge-tts (free, no API key) with WordBoundary events -> real word-level timestamps.
Text source: the 94 LOCKED caption cue texts in production/video-1/execution/03-CAPTIONS.srt,
so narration and captions share ONE verbatim source. The approved script is not modified."""
import asyncio, json, re, sys
import edge_tts

VOICE = "en-US-GuyNeural"
SRT_LOCKED = "production/video-1/execution/03-CAPTIONS.srt"

def parse_cue_texts(path):
    cues, block = [], []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("#"):
            continue
        if not line.strip():
            if block:
                if " --> " in "\n".join(block):
                    k = next(i for i, l in enumerate(block) if " --> " in l)
                    txt = "\n".join(block[k+1:]).strip()
                    if txt:
                        cues.append(txt)
                block = []
        else:
            block.append(line)
    if block and " --> " in "\n".join(block):
        k = next(i for i, l in enumerate(block) if " --> " in l)
        txt = "\n".join(block[k+1:]).strip()
        if txt:
            cues.append(txt)
    return cues

def g(c, k):
    try:
        return c[k]
    except Exception:
        return getattr(c, k, None)

async def main():
    cues = parse_cue_texts(SRT_LOCKED)
    assert len(cues) == 94, f"expected 94 locked cue texts, got {len(cues)}"
    text = "\n".join(cues)          # verbatim locked words, in order
    words = []
    com = edge_tts.Communicate(text, VOICE)
    with open("work/narration.mp3", "wb") as f:
        async for chunk in com.stream():
            ct = g(chunk, "type")
            if ct == "audio":
                f.write(g(chunk, "data"))
            elif ct == "WordBoundary":
                off = g(chunk, "offset") / 1e7
                dur = g(chunk, "duration") / 1e7
                words.append({"start": off, "end": off + dur, "word": g(chunk, "text")})
    if not words:
        sys.exit("FAIL: no WordBoundary events received from edge-tts")
    json.dump(words, open("work/words.json", "w"))
    cue_tokens = len(re.findall(r"[A-Za-z0-9']+", text))
    diff = abs(len(words) - cue_tokens) / cue_tokens * 100
    print(f"TTS OK: audio=work/narration.mp3 words={len(words)} locked_tokens={cue_tokens} diff={diff:.1f}%")
    if diff > 10:
        print("WARNING: word-boundary count differs from locked token count (hyphenation is expected; >10% needs review)")

asyncio.run(main())
