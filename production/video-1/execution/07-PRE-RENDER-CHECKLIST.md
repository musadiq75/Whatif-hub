# VIDEO 1 — PRE-RENDER CHECKLIST & COMPLETE ASSET MANIFEST (new, rev 2)

**Why this exists (PR #2 review corrections 5 + 6):** the original package said "43 shots" — that counts *shot rows*, not render units. Multi-part shots expand: 1-7 → 3 clips, 2-6 → 2, 5-5 → 3, 6-1 → 4. **The true render-unit count is 61.** This file is the single source of truth for asset counts and must be passed BEFORE assembly begins.

## A. Corrected counts

| Asset class | Count | Notes |
|---|---|---|
| Render units (video clips) | **61** | See manifest below |
| Keyframe images | **59** | All units except 01-01 and 06-08 (FFmpeg text cards) |
| Narration file | 1 | `audio/narration.wav` |
| Music tracks | 6 | `s1.mp3`–`s6.mp3`, one per scene mood |
| SFX files | 27 | Named per §7 cue table (clock tick, mattress creak, strained breath, distant dog, fabric strain, footfall thuds, cane clatter, fan squeak, wing flaps, jet cruise, touchdown roar, tire screech, bridge groan, crack tick, crowd footsteps, heartbeat, cockpit strain mic, centrifuge whirr, scan pings, effort grunts, rain impact, seawall detonation, branch shear, construction ticks, feet on floor, fan hum, final clock tick) |
| Caption file | 1 | SRT regenerated from WhisperX (runbook 2b) |

## B. Complete render-unit manifest (61 units, timeline order)

Cue = the narration words where each unit begins (drives `timeline_cues.csv` for the runbook Step 2 timeline script). Min-dur = minimum pacing duration from `01-SHOT-PROMPTS.md`; actual duration = span to the next unit's cue in the real narration.

**Scene 1:** 01-01 `<narration_start>` 6.0s · 01-02 `at midnight tonight` 7s · 01-03 `no announcement` 6s · 01-04 `the only evidence is you` 8s · 01-05 `you weigh a hundred and eighty` 9s · 01-06 `you haven't gained a single gram` 8s · 01-07a `for every rock` 3s · 01-07b `and bridge` 3s · 01-07c `and bird` 3s · 01-08 `here's what the next forty-eight` 7s

**Scene 2:** 02-01 `the first thing you notice` 8s · 02-02 `standing up, your heart` 7s · 02-03 `by mid-morning` 6s · 02-04 `you're not heavier` 7s · 02-05 `the stairs are a mountain` 7s · 02-06a `and you're one of the lucky ones` 4s · 02-06b `an elderly parent` 4s · 02-07 `for a small, quiet share` 6s · 02-08 `your bedroom, meanwhile` 8s · 02-09 `it's the last straw` 5s

**Scene 3:** 03-01 `outside, everyone moves` 8s · 03-02 `like hikers carrying loaded packs` 6s · 03-03 `birds are the first surprise` 6s · 03-04 `when gravity doubles` 9s · 03-05 `twice the weight` 8s · 03-06 `the same near-cancellation` 9s · 03-07 `flights start diverting` 8s · 03-08 `some of them are closed` 6s · 03-09 `cars barely notice` 5s · 03-10 `bridges are different` 9s · 03-11 `doubling live weight` 8s · 03-12 `the failures come one at a time` 9s · 03-13 `nothing breaks at midnight` 7s

**Scene 4:** 04-01 `by evening, your spine` 8s · 04-02 `you're measurably shorter` 6s · 04-03 `there's real science here` 8s · 04-04 `you're living at two g` 7s · 04-05 `space agencies have literally` 8s · 04-06 `and even modest increases` 7s · 04-07 `and here's the hopeful part` 8s · 04-08 `the ones who can't` 6s · 04-09 `that's the first month's quiet` 8s

**Scene 5:** 05-01 `raindrops hit harder` 8s · 05-02 `waves carry double` 7s · 05-03 `forests start shedding` 8s · 05-04 `architecture gets rebuilt` 9s · 05-05a `elevator cables` 3s · 05-05b `crane booms` 3s · 05-05c `aircraft wings` 3s · 05-06 `and over generations` 9s

**Scene 6:** 06-01a `a year later` 3s · 06-1b `the people broader` 3s · 06-1c `the cities squatter` 3s · 06-1d `the old bridges gone` 3s · 06-02 `catastrophe, then adaptation` 7s · 06-03 `but here's the creepiest part` 7s · 06-04 `tonight, at midnight` 5s · 06-05 `and then, one ordinary morning` 10s · 06-06 `and carry three hundred and sixty` 7s · 06-07 `it's what the world quietly` 8s · 06-08 `<narration_end>` 5s

### timeline_cues.csv (extract verbatim to `video1/timeline_cues.csv`)

```csv
unit,cue,min_dur
01-01,<narration_start>,6.0
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
(Commas removed from cue phrases for CSV safety; the timeline script matches on words, punctuation-insensitive.)

## C. Pre-render existence checks (run BEFORE Step 3 of the runbook)

```bash
cd video1
# 1. All 61 clips present, non-empty
python3 - <<'EOF'
import csv, os
rows = list(csv.DictReader(open("timeline_cues.csv")))
missing = [r["unit"] for r in rows
           if not (os.path.exists(f"clips/{r['unit']}.mp4") and os.path.getsize(f"clips/{r['unit']}.mp4") > 10000)]
print(f"clips: {len(rows)-len(missing)}/61 present")
assert not missing, f"MISSING: {missing}"
EOF
# 2. Narration + timing artifacts
test -s audio/narration.wav && echo OK narration
test -s work/narration_vo.wav && echo OK narration_vo
test -s work/timeline.csv && echo OK timeline
# 3. Music: 6 tracks
ls audio/music/ | grep -c ".mp3"   # expect 6
# 4. SFX: 27 files
ls audio/sfx/ | grep -c ".wav"    # expect >= 27
```

## D. Pre-render checklist (sign off every line before assembly)

- [ ] 61/61 clips exist, each ≥10 KB, each ≥ its min-dur (ffprobe), each watermark-free (eyeball every clip — reject + regenerate any with a provider mark)
- [ ] 59/59 keyframes exist in `refs/` (not strictly required at assembly, but confirm the 3 continuity rules: 6-2 derived from 4-9 keyframe; 6-4 reuses 1-5 keyframe; single master bedroom keyframe family for 1-3/2-1/2-8/4-7/6-3/6-5/6-7)
- [ ] Narration word-for-word identical to `02-NARRATION-TTS.md` (transcript diff = zero changes)
- [ ] `timeline.csv` built from WhisperX real timestamps (not scaled estimates)
- [ ] Captions regenerated from the same WhisperX pass; cue text verbatim
- [ ] 6 music tracks licensed for monetized YouTube (YouTube Audio Library / Pixabay)
- [ ] 27 SFX files present, licenses checked (CC0 preferred)
- [ ] All clips 16:9, ≥720p native (no upscaling needed), 23.976-compatible
- [ ] Scene 5 clips carry the speculation treatment (no confident-claim framing)
- [ ] Title/end cards ready as FFmpeg drawtext (01-01, 06-08) — no keyframe needed
- [ ] Disk space ≥ 20 GB free for work/ and out/

**Assembly (runbook Step 3) may begin only when every box above is checked.**
