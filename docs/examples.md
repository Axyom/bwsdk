# Examples

Short, focused snippets for each part of the API. They assume you already have a
connected song:

```python
from openwig import Song, Note
s = Song(tempo=120, bars=8, clean=True)
```

## Notes and clips

```python
lead = s.track("LEAD", device="Polysynth")

# One arranger clip spanning the whole song
lead.clip([Note(60, b, dur=0.5) for b in range(8)])

# Several arranger clips with gaps - (start, duration, notes); notes are
# RELATIVE to each clip's start
lead.clips([
    (0, 4, [Note(60, 0, dur=1), Note(64, 1, dur=1), Note(67, 2, dur=2)]),
    (8, 4, [Note(62, 0, dur=1), Note(65, 1, dur=1), Note(69, 2, dur=2)]),
])
```

`Note(...)` and raw tuples are interchangeable everywhere notes are accepted:

```python
lead.clip([Note(60, 0, dur=0.5, vel=0.8)])
lead.clip([(60, 0, 0.5, 0.8)])              # exactly the same
```

## Launcher clips and scenes

```python
lead.scene(0, [Note(60, 0, dur=0.5), Note(63, 0.5, dur=0.5)])   # clip in slot 0
lead.launch(0)                                                  # fire it
s.scene_launch(0)                                               # launch a whole scene row
```

## Devices and FX

```python
kick = s.track("KICK", device="v9 Kick")    # factory device by name
kick.fx("Saturator", Drive=0.25)            # insert an FX + set named remotes
kick.fx("EQ+")

synth = s.track("LEAD", device="Polysynth")
synth.preset(r"C:\path\to\My Lead.bwpreset")  # load a preset
print(synth.remote_pages())                   # discover remote-control params
```

## Mix and master

```python
bass = s.track("BASS", device="FM-4")
bass.fader(0.8)        # volume, 0..1 (clamped)
bass.pan(-0.3)         # -1 left .. 0 center .. +1 right
bass.mute(False)
bass.color(0.2, 0.6, 1.0)

s.master(["EQ+", "Compressor+", "Peak Limiter"])
```

## Effect (return) tracks and sends

```python
rev = s.fx_track("REVERB", device="Reverb")   # a return track
lead.send(0, 0.4)                              # send LEAD into the first return
```

## Automation (you build the curves)

Points are `(beat, value)` with `value` normalized `0..1`. Build them with
ordinary Python.

```python
# Sidechain-style volume duck: drop on each beat, rebound
duck = []
for beat in range(16):
    duck += [(beat, 0.0), (beat + 0.85, 1.0)]
bass.automate("volume", duck)

# Linear filter sweep over 8 beats on a device remote parameter
synth.automate("remote", [(0, 0.2), (8, 1.0)], remote_index=0)

# A pan LFO you compute yourself
import math
pan = [(b * 0.25, 0.5 + 0.45 * math.sin(b * 0.4)) for b in range(64)]
synth.automate("pan", pan)
```

## Sidechain between tracks

```python
kick = s.track("KICK", device="v9 Kick")
bass = s.track("BASS", device="FM-4")
bass.fx("Compressor+")
bass.sidechain_from(kick)        # BASS's compressor listens to KICK
```

## Tempo, markers, transport

```python
s.set_tempo(124)
s.automate_tempo([(0, 120), (32, 128)])   # tempo ramp over 32 beats
s.marker()                                # cue marker at the playhead
s.metronome(True)
s.play(loop=True)
s.stop()
```

## Render

```python
res = s.render("out.wav")
print(res["silent"], res["seconds"])      # confirm it actually made sound
```

For a full arrangement that puts these together, see [Songs](songs.md).
