"""Render a timed Birthplace arrangement from the two original scene stems.

The original switches layers at spatial triggers, not a fixed timestamp.
This adaptation uses one 36s opening, a 36s transition, then a 36s full loop.
"""
import hashlib
import json
import math
from pathlib import Path
import wave

import numpy as np

parent = Path(__file__).parent
root = parent if (parent / "HollowKnightAudio.fspro").exists() else parent / "FullVoidHeartAudioProject"
config = json.loads((root / "DecodeInfo.json").read_text())
rate, frames = int(config["rate"]), int(config["frames"])
sub = np.fromfile(root / "Stem3.f32", dtype="<f4").reshape(-1, 2)
strings = np.fromfile(root / "Stem2.f32", dtype="<f4").reshape(-1, 2)
assert len(sub) == len(strings) and 0 <= frames - len(sub) <= 4
# Godot's resampler may return two fewer frames at the finite stream boundary.
padding = frames - len(sub)
if padding:
    sub = np.pad(sub, ((0, padding), (0, 0)), mode="edge")
    strings = np.pad(strings, ((0, padding), (0, 0)), mode="edge")
assert np.isfinite(sub).all() and np.isfinite(strings).all()
assert np.max(np.abs(sub)) > 0.001 and np.max(np.abs(strings)) > 0.001

def smooth_cycle(data):
    """Bridge the tiny decoded endpoint step over 5ms at each edge."""
    result = data.copy()
    size = round(rate * 0.005)
    blend = np.linspace(0, 1, size, dtype=np.float32)[:, None]
    anchor = (data[0] + data[-1]) * 0.5
    result[:size] = anchor * (1 - blend) + data[:size] * blend
    result[-size:] = data[-size:] * (1 - blend) + anchor * blend
    return result

sub, strings = smooth_cycle(sub), smooth_cycle(strings)

# Original Sub Area -> Action and Sub mixer gains. The transition is 10s.
sub_gain = 10 ** (-0.025776729 / 20)
strings_gain = 10 ** (3.704152 / 20)
mix = np.tile(sub, (3, 1)) * sub_gain
mix[:15 * rate] *= np.linspace(0, 1, 15 * rate, dtype=np.float32)[:, None]
strings_layer = np.tile(strings, (2, 1)) * strings_gain
strings_layer[:10 * rate] *= np.linspace(0, 1, 10 * rate, dtype=np.float32)[:, None]
mix[frames:] += strings_layer
raw_peak = float(np.max(np.abs(mix)))
# One constant gain for the entire piece preserves the original dynamics.
gain = min(1.0, 10 ** (-1 / 20) / raw_peak)
mix *= gain
assert np.max(np.abs(mix)) < 1.0
# The transition must add the missing complete string stem, not just repeat Sub.
expected_tail = (sub * sub_gain + strings * strings_gain) * gain
assert np.allclose(mix[2 * frames:], expected_tail, atol=2e-6)
assert np.sqrt(np.mean((mix[2 * frames:] - sub * sub_gain * gain) ** 2)) > 0.001

pcm = np.rint(mix * 32767).astype("<i2")
destination = root / "Assets/music/music/VoidHeart_Birthplace_Full.wav"
with wave.open(str(destination), "wb") as output:
    output.setnchannels(2)
    output.setsampwidth(2)
    output.setframerate(rate)
    output.writeframes(pcm.tobytes())

source_root = root / "Assets/music/music"
report = {
    "title": "Void Heart - Birthplace (timed two-stem arrangement)",
    "duration_seconds": len(mix) / rate,
    "sample_rate": rate,
    "channels": 2,
    "sources": [f"S59-55 Final Stage {n}.ogg" for n in (2, 3)],
    "source_sha256": {
        f"S59-55 Final Stage {n}.ogg": hashlib.sha256(
            (source_root / f"S59-55 Final Stage {n}.ogg").read_bytes()).hexdigest()
        for n in (2, 3)
    },
    "arrangement": [
        {"start": 0, "end": 36, "description": "Sub stem; initial 15-second fade-in"},
        {"start": 36, "end": 72, "description": "Sub + Action strings; 10-second strings fade-in"},
        {"start": 72, "end": 108, "description": "Both complete stems; this section loops"},
    ],
    "loop_start_seconds": 72,
    "loop_end_seconds": 108,
    "static_gain_db": 20 * math.log10(gain),
    "loop_edge_bridge_ms": 5,
    "peak_dbfs": 20 * math.log10(float(np.max(np.abs(mix)))),
    "final_loop_boundary_step": float(np.max(np.abs(mix[-1] - mix[2 * frames]))),
    "output_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
    "note": "Automatic timing is an adaptation; the original Dream_Abyss switches by player position.",
}
(root / "VoidHeartArrangement.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
