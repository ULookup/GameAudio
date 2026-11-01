"""Convert the actual Wwise Recorder take to the handoff WAV format."""
from pathlib import Path
import argparse
import numpy as np
import soundfile as sf

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", default="Corridor_Final_Preview.wav")
args = parser.parse_args()
take = root / "Preview" / "Corridor_Soundcaster_Take.wav"
audio, sample_rate = sf.read(take, always_2d=True)
fade = min(round(0.4 * sample_rate), len(audio))
audio[:fade] *= np.linspace(0, 1, fade)[:, None]
tail = min(round(0.05 * sample_rate), len(audio))
audio[-tail:] *= np.linspace(1, 0, tail)[:, None]
output = root / "Preview" / args.output
sf.write(output, audio, sample_rate, subtype="PCM_24", format="WAV")
print(sf.info(output))
