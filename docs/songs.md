# Songs

Full tracks built entirely in Python with openwig. Each one is a single script
you can run against a clean Bitwig project.

## Nightdrive (~3 min progressive house/techno)

96 bars at 128 BPM = 384 beats = **3:00**, arranged as six 16-bar blocks that
each move the track forward:

| Block      | Bars  | What changes |
|------------|-------|--------------|
| Intro      | 1-16  | Pad chord (Beat-LFO + auto-pan); kick enters at bar 4 |
| Build      | 17-32 | Bass enters, the filter opens (automation ramp), hats fill in |
| Drop 1     | 33-48 | Full groove: 16th hats, sidechain duck, `Am F C G` stabs |
| Variation  | 49-64 | New progression `Dm Bb F C`, a lead melody, added shaker |
| Breakdown  | 65-80 | Drums drop out; new pad voicing + auto-pan, a lead arp |
| Drop 2     | 81-96 | Syncopated kick, rolling bass, busy hats, new lead, swell-in |

Movement comes from **two Beat-LFO modulators** (on the bass filter and the pad),
**automated** filter sweeps / sidechain duck / auto-pan / volume swell, an
**evolving chord progression**, and bass/hats/lead variations per block. openwig
ships no pattern helpers - the functions at the top are ordinary Python.

```python
"""Nightdrive - progressive house/techno, ~3 min, six evolving 16-bar blocks."""
import math
from openwig import Song, Note

# ── pattern helpers (ordinary Python) ─────────────────────────────────────────
def kick(bars, *, vel=1.0, offbeat=False):
    out = [Note(36, b, dur=0.24, vel=vel) for b in range(bars * 4)]
    if offbeat:
        out += [Note(36, bar * 4 + 3.5, dur=0.18, vel=vel * 0.7) for bar in range(bars)]
    return out

def hats(bars, *, div=0.5, vel=0.5):
    n = int(round(bars * 4 / div))
    return [Note(42, i * div, dur=min(0.12, div * 0.8), vel=vel * (0.7 if i % 2 else 1.0))
            for i in range(n)]

def clap(bars, *, vel=0.9):
    return [Note(39, bar * 4 + beat, dur=0.2, vel=vel) for bar in range(bars) for beat in (1, 3)]

def shaker(bars, *, vel=0.4):
    return [Note(70, b + 0.25, dur=0.1, vel=vel) for b in range(bars * 4)]

def bassline(bars, root, *, vel=0.85, pattern="offbeat"):
    out = []
    for bar in range(bars):
        base = bar * 4
        if pattern == "rolling":
            for i in range(8):
                out.append(Note(root + (12 if i % 4 == 3 else 0), base + i * 0.5, dur=0.3, vel=vel))
        else:  # offbeat
            for beat in range(4):
                out.append(Note(root, base + beat + 0.5, dur=0.4, vel=vel))
    return out

def stabs(bars, roots, *, vel=0.5):
    out = []
    for bar in range(bars):
        r = roots[bar % len(roots)]
        out += [Note(r + iv, bar * 4 + 0.5, dur=0.4, vel=vel) for iv in (0, 3, 7)]
    return out

def held(bars, root, *, vel=0.3, voicing=(0, 7, 12)):
    return [Note(root + iv, 0.0, dur=bars * 4.0, vel=vel) for iv in voicing]

def arp(bars, root, *, vel=0.45, step=0.5, shape=(0, 7, 12, 7, 3, 7)):
    n = int(round(bars * 4 / step))
    return [Note(root + shape[i % len(shape)], i * step, dur=step * 0.9, vel=vel) for i in range(n)]

def lead(bars, keys, *, vel=0.6):
    out = []
    for bar in range(bars):
        k = keys[bar % len(keys)]
        out += [Note(k, bar * 4, dur=1.5, vel=vel),
                Note(k + 12, bar * 4 + 2.5, dur=0.5, vel=vel * 0.7),
                Note(k + 7, bar * 4 + 3.0, dur=0.5, vel=vel * 0.6)]
    return out

def ramp(b0, b1, v0, v1, *, n=16):
    return [(b0 + (b1 - b0) * i / n, v0 + (v1 - v0) * i / n) for i in range(n + 1)]


s = Song(tempo=128, bars=96, clean=True)   # 6 blocks x 16 bars = 384 beats = 3:00
A1 = 33
PROG_A = [57, 53, 48, 55]      # Am F C G
PROG_B = [50, 46, 53, 48]      # Dm Bb F C  (variation block)

# KICK - out in the breakdown, syncopated in drop 2
kick_t = s.track("KICK", device="v9 Kick").fx("Saturator", Drive=0.2)
kick_t.clips([
    (16, 48, kick(12, vel=0.9)),
    (64, 192, kick(48)),
    (312, 8, kick(2)),
    (320, 64, kick(16, offbeat=True)),
])

# HATS - density rises into the drops
hats_t = s.track("HATS", device="v9 Hat Closed")
hats_t.clips([
    (32, 32, hats(8, vel=0.42)),
    (64, 64, hats(16, vel=0.5)),
    (128, 64, hats(16, div=0.25, vel=0.5)),
    (192, 64, hats(16, vel=0.5)),
    (256, 64, hats(16, vel=0.3)),
    (320, 64, hats(16, div=0.25, vel=0.55)),
])

clap_t = s.track("CLAP", device="v9 Clap").fx("Reverb", Mix=0.22)
clap_t.clips([(128, 64, clap(16)), (192, 64, clap(16)), (320, 64, clap(16))])

shk = s.track("SHAKER", device="v9 Hat Closed")
shk.clips([(192, 64, shaker(16)), (320, 64, shaker(16))])

# BASS - Beat-LFO on the filter (movement) + build sweep + sidechain duck
bass_t = s.track("BASS", device="FM-4").fx("Filter")
bass_t.add_modulator("Beat LFO")
bass_t.map_modulator(0, dest="remote", remote_index=0, amount=0.35)   # LFO -> cutoff
bass_t.automate("remote", ramp(64, 128, 0.20, 0.72), remote_index=0)  # filter opens
bass_t.clips([
    (64, 64, bassline(16, A1, vel=0.7)),
    (128, 64, bassline(16, A1, pattern="rolling")),
    (192, 64, bassline(16, A1)),
    (320, 64, bassline(16, A1, pattern="rolling")),
])
duck = []
for beat in list(range(128, 192)) + list(range(320, 384)):
    duck += [(beat, 0.0), (beat + 0.85, 1.0)]
bass_t.automate("volume", duck)

# STAB - progression changes in the variation block
stab_t = s.track("STAB", device="Polysynth").fx("Delay+", Mix=0.2)
stab_t.clips([
    (128, 64, stabs(16, PROG_A)),
    (192, 64, stabs(16, PROG_B)),
    (320, 64, stabs(16, PROG_A)),
])

# PAD - long chords + auto-pan + its own LFO
pad_t = s.track("PAD", device="Polysynth").fx("Reverb", Mix=0.5).fx("Delay+", Mix=0.25)
pad_t.select_device(0)                          # back to the Polysynth
pad_t.add_modulator("Beat LFO")
pad_t.map_modulator(0, dest="remote", remote_index=0, amount=0.25)
pad_t.clips([
    (0, 64, held(16, 45)),
    (256, 64, held(16, 41, voicing=(0, 5, 7, 12))),
])
pan = [(b * 0.5, 0.5 + 0.4 * math.sin(b * 0.4)) for b in range(128)]
pan += [(256 + b * 0.5, 0.5 + 0.4 * math.sin(b * 0.4)) for b in range(128)]
pad_t.automate("pan", pan)

# LEAD - arp in the breakdown, evolving melody in variation + drop 2
lead_t = s.track("LEAD", device="Polysynth").fx("Reverb", Mix=0.3).fx("Delay+", Mix=0.3)
lead_t.clips([
    (192, 64, lead(16, [69, 72, 76, 74])),
    (256, 64, arp(16, 57)),
    (320, 64, lead(16, [69, 72, 67, 71])),
])
lead_t.automate("volume", ramp(312, 320, 0.2, 0.9))   # swell into drop 2

s.master(["EQ+", "Compressor+", "Peak Limiter"])
print(s.render("nightdrive.wav"))    # captures the full ~3:00
```
