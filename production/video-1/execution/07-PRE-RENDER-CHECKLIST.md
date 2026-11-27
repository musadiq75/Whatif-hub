# VIDEO 1 — PRE-RENDER CHECKLIST & COMPLETE ASSET MANIFEST (rev 4)

**Rev 4 (third review):** the timeline is now in the **canonical ABSOLUTE video timebase** — `build_timeline.py` applies the delay internally and writes absolute values (title 0.000→6.000; first narration word at 6.000; end card at narration end; TOTAL = narration end + 5s). Music spans, SFX times, captions, and concat verification all consume `timeline.csv` absolute values with zero conversion. The committed `03-CAPTIONS.srt` is now explicitly a **provisional text/structure template** (timings are planning estimates; uploadable file is `work/captions_final.srt`).

## A. Corrected counts

| Asset class | Count | Notes |
|---|---|---|
| Render units (clips) | **61** | 59 generated + 2 FFmpeg text cards (01-01, 06-08) |
| Generated footage files in `clips/` | **59** | All units except the two cards |
| Keyframe images | **59** | Same 59 units |
| Narration file | 1 | `audio/narration.wav` |
| Music tracks | 6 | `s1.mp3`–`s6.mp3`, looped to computed spans, full coverage 0 → TOTAL |
| SFX files | 27 | Per §7 cue table, placed at absolute timeline times |
| Caption cues | **94** | Provisional `03-CAPTIONS.srt` = template; uploadable = `work/captions_final.srt` (audio-verified) |

## B. Complete render-unit manifest (61 units, timeline order — ABSOLUTE timebase)

Cue = narration words where the unit begins. Min-dur = minimum pacing; actual duration = span to the next unit's cue in the real narration.

**Scene 1:** 01-01 `<title_card>` 6.0s (**starts 0.000**) · 01-02 `at midnight tonight` 7s (**starts 6.000 — actual first-word time**) · 01-03 `no announcement` 6s · 01-04 `the only evidence is you` 8s · 01-05 `you weigh a hundred and eighty` 9s · 01-06 `you haven't gained a single gram` 8s · 01-07a `for every rock` 3s · 01-07b `and bridge` 3s · 01-07c `and bird` 3s · 01-08 `here's what the next forty-eight` 7s

**Scene 2:** 02-01 `the first thing you notice` 8s · 02-02 `standing up, your heart` 7s · 02-03 `by mid-morning` 6s · 02-04 `you're not heavier` 7s · 02-05 `the stairs are a mountain` 7s · 02-06a `and you're one of the lucky ones` 4s · 02-06b `an elderly parent` 4s · 02-07 `for a small, quiet share` 6s · 02-08 `your bedroom, meanwhile` 8s · 02-09 `it's the last straw` 5s

**Scene 3:** 03-01 `outside, everyone moves` 8s · 03-02 `like hikers carrying loaded packs` 6s · 03-03 `birds are the first surprise` 6s · 03-04 `when gravity doubles` 9s · 03-05 `twice the weight` 8s · 03-06 `the same near-cancellation` 9s · 03-07 `flights start diverting` 8s · 03-08 `some of them are closed` 6s · 03-09 `cars barely notice` 5s · 03-10 `bridges are different` 9s · 03-11 `doubling live weight` 8s · 03-12 `the failures come one at a time` 9s · 03-13 `nothing breaks at midnight` 7s

**Scene 4:** 04-01 `by evening, your spine` 8s · 04-02 `you're measurably shorter` 6s · 04-03 `there's real science here` 8s · 04-04 `you're living at two g` 7s · 04-05 `space agencies have literally` 8s · 04-06 `and even modest increases` 7s · 04-07 `and here's the hopeful part` 8s · 04-08 `the ones who can't` 6s · 04-09 `that's the first month's quiet` 8s

**Scene 5:** 05-01 `raindrops hit harder` 8s · 05-02 `waves carry double` 7s · 05-03 `forests start shedding` 8s · 05-04 `architecture gets rebuilt` 9s · 05-05a `elevator cables` 3s · 05-05b `crane booms` 3s · 05-05c `aircraft wings` 3s · 05-06 `and over generations` 9s

**Scene 6:** 06-01a `a year later` 3s · 06-01b `the people broader` 3s · 06-01c `the cities squatter` 3s · 06-01d `the old bridges gone` 3s · 06-02 `catastrophe, then adaptation` 7s · 06-03 `but here's the creepiest part` 7s · 06-04 `tonight, at midnight` 5s · 06-05 `and then, one ordinary morning` 10s · 06-06 `and carry three hundred and sixty` 7s · 06-07 `it's what the world quietly` 8s · 06-08 `<narration_end>` 5s (**starts at narration end — absolute**)

### timeline_cues.csv (extract verbatim to `video1/timeline_cues.csv`)

```csv
unit,cue,min_dur
01-01,<title_card>,6.0
01-02,at midnight tonight,7
01-03,no announcement,6
01-04,the only evidence is you,8
01-05,you weigh a hundred and eighty,9
01-06,you haven't gained a single gram,8
01-07a,for every rock,3
01-07b,and bridge,3
01-07c,and bird,3
01-08,here's what the next forty-eight,7
02-01,the first thing you notice,8
02-02,standing up your heart,7
02-03,by mid-morning,6
02-04,you're not heavier,7
02-05,the stairs are a mountain,7
02-06a,and you're one of the lucky ones,4
02-06b,an elderly parent,4
02-07,for a small quiet share,6
02-08,your bedroom meanwhile,8
02-09,it's the last straw,5
03-01,outside everyone moves,8
03-02,like hikers carrying loaded packs,6
03-03,birds are the first surprise,6
03-04,when gravity doubles,9
03-05,twice the weight,8
03-06,the same near-cancellation,9
03-07,flights start diverting,8
03-08,some of them are closed,6
03-09,cars barely notice,5
03-10,bridges are different,9
03-11,doubling live weight,8
03-12,the failures come one at a time,9
03-13,nothing breaks at midnight,7
04-01,by evening your spine,8
04-02,you're measurably shorter,6
04-03,there's real science here,8
04-04,you're living at two g,7
04-05,space agencies have literally,8
04-06,and even modest increases,7
04-07,and here's the hopeful part,8
04-08,the ones who can't,6
04-09,that's the first month's quiet,8
05-01,raindrops hit harder,8
05-02,waves carry double,7
05-03,forests start shedding,8
05-04,architecture gets rebuilt,9
05-05a,elevator cables,3
05-05b,crane booms,3
05-05c,aircraft wings,3
05-06,and over generations,9
06-01a,a year later,3
06-01b,the people broader,3
06-01c,the cities squatter,3
06-01d,the old bridges gone,3
06-02,catastrophe then adaptation,7
06-03,but here's the creepiest part,7
06-04,tonight at midnight,5
06-05,and then one ordinary morning,10
06-06,and carry three hundred and sixty,7
06-07,it's what the world quietly,8
06-08,<narration_end>,5
```

## C. Pre-render existence checks (run BEFORE runbook Step 3)

```bash
cd video1
# 1. All 59 generated clips present, non-empty
python3 - <<'EOF'
import csv, os
rows = [r for r in csv.DictReader(open("timeline_cues.csv"))
        if r["unit"] not in ("01-01", "06-08")]
missing = [r["unit"] for r in rows
           if not (os.path.exists(f"clips/{r['unit']}.mp4") and os.path.getsize(f"clips/{r['unit']}.mp4") > 10000)]
print(f"generated clips: {len(rows)-len(missing)}/59 present")
assert not missing, f"MISSING: {missing}"
EOF
# 2. Timing artifacts (absolute timebase)
test -s work/narration_vo.wav && echo OK narration_vo
test -s work/timeline.csv && echo OK timeline
python3 -c "import csv; r=list(csv.DictReader(open('work/timeline.csv'))); print('title start:', r[0]['start'], '(expect 0.000)'); print('first word unit:', r[1]['start'], '(expect 6.000)')"
test -s work/captions_final.srt && echo OK captions_final || echo "WARNING: captions_final.srt not yet generated (runbook Step 2 gate)"
# 3. Music: 6 tracks; SFX: 27 files
ls audio/music/ | grep -c ".mp3"   # expect 6
ls audio/sfx/ | grep -c ".wav"    # expect >= 27
# 4. Font (runbook Step 3.5 discovery) resolves
fc-list : file | head -n1
```

## D. Pre-render sign-off checklist

- [ ] 59/59 generated clips exist, ≥10 KB, ≥ min-dur after timing, watermark-free
- [ ] Resolution gate passed (all ≥1080p native, or waivers documented ≥960×540)
- [ ] 59/59 keyframes in `refs/`; three continuity rules hold (6-2 from 4-9; 6-4 from 1-5; master bedroom family)
- [ ] Narration word-for-word identical to `02-NARRATION-TTS.md`
- [ ] `timeline.csv` is ABSOLUTE: title 0.000; 01-02 at 6.000; all units strictly increasing; last unit ends at narration end + 5s
- [ ] `work/captions_final.srt` generated and passed the runbook Step-2 validation (94 cues, no overlap, last cue ≤ TOTAL) — **provisional `03-CAPTIONS.srt` NOT used for upload**
- [ ] Music: 6 tracks selected, each long enough or loopable; spans to be COMPUTED by `tools/music_spans.py` (never hardcoded; no apad silence)
- [ ] 27 SFX present, licenses checked; placement times to be taken from `timeline.csv` absolute values
- [ ] Text cards: font discovery command resolves a TTF path on the render machine
- [ ] Disk ≥ 20 GB free

**Assembly may begin only when every box is checked.**
