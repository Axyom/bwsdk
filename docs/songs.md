# Songs

Full tracks built entirely in Python with openwig. Each one is a single script
you can run against a clean Bitwig project.

## Nightdrive (~3 min house/techno)

96 bars at 128 BPM = 384 beats = **3:00**, arranged in six sections:

| Section    | Bars  | What's playing |
|------------|-------|----------------|
| Intro      | 1-16  | Pad chord; kick enters at bar 4; hats from bar 8 |
| Build      | 17-32 | + off-beat bass (quieter), busier hats |
| Drop 1     | 33-56 | Full groove: kick, clap, hats, ducked bass, chord stabs |
| Breakdown  | 57-72 | Drums drop out; new pad chord, soft hats |
| Build 2    | 73-80 | Hats rebuild, kick rolls back in |
| Drop 2     | 81-96 | Full groove again **+ a lead melody** (the big variation) |

openwig ships no pattern or arrangement helpers - the functions at the top are
ordinary Python you write once and reuse. The arrangement is just `clips()`
calls placing each section's notes at the right beat.

```python
"""Nightdrive - a ~3-minute house/techno track built with openwig.

96 bars @ 128 BPM = 384 beats = 3:00. Six sections: intro, build, drop,
breakdown, second build, second drop.
"""
from openwig import Song, Note

# ── pattern helpers (ordinary Python - openwig ships none) ────────────────────
def four_on_floor(bars, *, key=36, vel=1.0):
    """A kick (or any key) on every beat."""
    return [Note(key, b, dur=0.24, vel=vel) for b in range(bars * 4)]

def offbeat_hats(bars, *, vel=0.5):
    return [Note(42, b + 0.5, dur=0.18, vel=vel) for b in range(bars * 4)]

def backbeat(bars, *, key=39, vel=0.9):
    """Clap/snare on beats 2 and 4 of every bar."""
    return [Note(key, bar * 4 + beat, dur=0.2, vel=vel)
            for bar in range(bars) for beat in (1, 3)]

def offbeat_bass(bars, root, *, vel=0.85):
    """Rolling off-beat bass on the root note."""
    return [Note(root, bar * 4 + beat + 0.5, dur=0.4, vel=vel)
            for bar in range(bars) for beat in range(4)]

def stabs(bars, roots, *, vel=0.55):
    """One minor-triad stab per bar, cycling through `roots`."""
    out = []
    for bar in range(bars):
        root = roots[bar % len(roots)]
        out += [Note(root + iv, bar * 4 + 0.5, dur=0.4, vel=vel) for iv in (0, 3, 7)]
    return out

def held_chord(bars, root, *, vel=0.32):
    """One long pad chord spanning the whole clip."""
    return [Note(root + iv, 0.0, dur=bars * 4.0, vel=vel) for iv in (0, 7, 12)]

def lead_line(bars, keys, *, vel=0.6):
    """A melody: one key per bar plus an octave passing note."""
    out = []
    for bar in range(bars):
        k = keys[bar % len(keys)]
        out += [Note(k, bar * 4, dur=1.5, vel=vel),
                Note(k + 12, bar * 4 + 2.5, dur=1.0, vel=vel * 0.8)]
    return out


s = Song(tempo=128, bars=96, clean=True)

A1 = 33                       # bass root (A1)
CHORDS = [57, 53, 48, 55]     # Am - F - C - G, one per bar

# ── drums ──────────────────────────────────────────────────────────────────────
# KICK everywhere except the breakdown
kick = s.track("KICK", device="v9 Kick").fx("Saturator", Drive=0.18)
kick.clips([
    (16,  48, four_on_floor(12)),   # intro (enters at bar 4)
    (64,  64, four_on_floor(16)),   # build
    (128, 96, four_on_floor(24)),   # drop 1
    (312,  8, four_on_floor(2)),    # build 2 (rolls back in)
    (320, 64, four_on_floor(16)),   # drop 2
])

hats = s.track("HATS", device="v9 Hat Closed")
hats.clips([
    (32,  32, offbeat_hats(8)),
    (64,  64, offbeat_hats(16, vel=0.55)),
    (128, 96, offbeat_hats(24, vel=0.6)),
    (224, 64, offbeat_hats(16, vel=0.35)),   # softer in the breakdown
    (288, 32, offbeat_hats(8, vel=0.5)),     # build 2
    (320, 64, offbeat_hats(16, vel=0.6)),
])

clap = s.track("CLAP", device="v9 Clap").fx("Reverb", Mix=0.22)
clap.clips([
    (128, 96, backbeat(24)),
    (320, 64, backbeat(16)),
])

# ── bass (ducked on every beat of the drops) ────────────────────────────────────
bass = s.track("BASS", device="FM-4").fx("Filter")
bass.clips([
    (64,  64, offbeat_bass(16, A1, vel=0.7)),   # build (quieter)
    (128, 96, offbeat_bass(24, A1)),            # drop 1
    (320, 64, offbeat_bass(16, A1)),            # drop 2
])
duck = []
for beat in list(range(128, 224)) + list(range(320, 384)):
    duck += [(beat, 0.0), (beat + 0.85, 1.0)]
bass.automate("volume", duck)

# ── harmony ──────────────────────────────────────────────────────────────────────
pad = s.track("PAD", device="Polysynth").fx("Reverb", Mix=0.5).fx("Delay+", Mix=0.25)
pad.clips([
    (0,   64, held_chord(16, 45)),    # intro pad
    (224, 64, held_chord(16, 41)),    # breakdown pad
])

stab = s.track("STAB", device="Polysynth").fx("Delay+", Mix=0.2)
stab.clips([
    (128, 96, stabs(24, CHORDS)),
    (320, 64, stabs(16, CHORDS)),
])

# LEAD only in the second drop - the big variation
lead = s.track("LEAD", device="Polysynth").fx("Reverb", Mix=0.3).fx("Delay+", Mix=0.3)
lead.clips([
    (320, 64, lead_line(16, [69, 72, 67, 71])),
])

# ── master + render ───────────────────────────────────────────────────────────────
s.master(["EQ+", "Compressor+", "Peak Limiter"])
print(s.render("nightdrive.wav"))    # captures the full ~3:00
```
