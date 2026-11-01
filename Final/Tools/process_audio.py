"""Export the corridor ambience and five independent details as 48 kHz / PCM24 stereo WAV."""

from __future__ import annotations

import argparse
import json
from math import gcd
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, resample_poly, sosfiltfilt


RATE = 48000
PROJECT = Path(__file__).resolve().parents[1]
SOURCES = {
    "hallway": "474458__ecfike__concrete-hallway-with-air-conditioner.wav",
    "machine": "569432__sheyvan__machinery-ventilation-running-1-1.wav",
    "pipe": "824117__derjuli__metalpipe.wav",
    "creak": "172158__eaglestealthteam__creaking-metal-desk.wav",
}


def db(value: float) -> float:
    return 20.0 * np.log10(max(float(value), 1e-12))


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x * x)))


def read_stereo(path: Path) -> np.ndarray:
    audio, sample_rate = sf.read(path, dtype="float64", always_2d=True)
    if sample_rate != RATE:
        divisor = gcd(sample_rate, RATE)
        audio = resample_poly(audio, RATE // divisor, sample_rate // divisor, axis=0)
    if audio.shape[1] == 1:
        audio = np.repeat(audio, 2, axis=1)
    if audio.shape[1] != 2:
        raise ValueError(f"Expected mono or stereo source: {path}")
    return audio


def section(x: np.ndarray, start: float, end: float) -> np.ndarray:
    return x[round(start * RATE):round(end * RATE)].copy()


def filter_band(x: np.ndarray, highpass: float, lowpass: float) -> np.ndarray:
    x = sosfiltfilt(butter(2, highpass, "highpass", fs=RATE, output="sos"), x, axis=0)
    return sosfiltfilt(butter(2, lowpass, "lowpass", fs=RATE, output="sos"), x, axis=0)


def level_rms(x: np.ndarray, target_db: float) -> np.ndarray:
    return x * (10 ** (target_db / 20) / rms(x))


def level_peak(x: np.ndarray, target_db: float) -> np.ndarray:
    return x * (10 ** (target_db / 20) / float(np.max(np.abs(x))))


def circular_crossfade(x: np.ndarray, seconds: float) -> np.ndarray:
    """Overlap tail with head; the resulting length is input length minus fade length."""
    count = round(seconds * RATE)
    theta = np.linspace(0, np.pi / 2, count, endpoint=True)[:, None]
    blend = x[-count:] * np.cos(theta) + x[:count] * np.sin(theta)
    # End of the blend joins the original head at count, including on repeat.
    return np.concatenate((x[count:-count], blend), axis=0)


def fade_edges(x: np.ndarray, fade_in: float, fade_out: float) -> np.ndarray:
    begin, end = round(fade_in * RATE), round(fade_out * RATE)
    x[:begin] *= np.sin(np.linspace(0, np.pi / 2, begin))[:, None] ** 2
    x[-end:] *= np.cos(np.linspace(0, np.pi / 2, end))[:, None] ** 2
    return x


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=Path.home() / "Downloads")
    args = parser.parse_args()
    output = PROJECT / "Audio" / "Exports"
    output.mkdir(parents=True, exist_ok=True)
    source = {key: read_stereo(args.sources / name) for key, name in SOURCES.items()}
    exports = []
    rng = np.random.default_rng(20261101)

    def save(name: str, audio: np.ndarray, provenance: list[dict], processing: dict) -> None:
        # TPDF dither at the final 24-bit conversion; source files stay untouched.
        dither = (rng.random(audio.shape) - rng.random(audio.shape)) / (2 ** 23)
        path = output / name
        sf.write(path, audio + dither, RATE, subtype="PCM_24", format="WAV")
        info = sf.info(path)
        exports.append({
            "file": f"Audio/Exports/{name}", "duration_seconds": info.duration,
            "sample_rate": info.samplerate, "channels": info.channels,
            "subtype": info.subtype, "peak_dbfs": round(db(np.max(np.abs(audio))), 2),
            "rms_dbfs": round(db(rms(audio)), 2), "sources": provenance,
            "processing": processing,
        })

    hallway = filter_band(section(source["hallway"], 16.0, 80.0), 35, 6500)
    hallway = level_rms(hallway, -26.0)
    machinery = filter_band(section(source["machine"], 1.0, 24.0), 70, 1700)
    machinery = circular_crossfade(machinery, 2.0)
    machinery = level_rms(machinery, -39.0)
    machinery = np.tile(machinery, (4, 1))[:len(hallway)]
    bed = level_rms(circular_crossfade(hallway + machinery, 4.0), -26.0)
    save("AMB_Underground_Corridor_Loop_60s.wav", bed, [
        {"file": SOURCES["hallway"], "start_seconds": 16.0, "end_seconds": 80.0},
        {"file": SOURCES["machine"], "start_seconds": 1.0, "end_seconds": 24.0},
    ], {"hallway_highpass_hz": 35, "hallway_lowpass_hz": 6500,
        "machine_highpass_hz": 70, "machine_lowpass_hz": 1700,
        "hallway_layer_rms_dbfs": -26, "machine_layer_rms_dbfs": -39,
        "machine_crossfade_seconds": 2, "final_crossfade_seconds": 4,
        "crossfade_type": "equal_power", "final_rms_dbfs": -26,
        "mono_machine_conversion": "duplicate mono to L and R"})

    details = [
        ("SFX_Pipe_Resonance_01.wav", "pipe", 3.55, 6.50, 100, 4200, .060, .450, -16),
        ("SFX_Pipe_Resonance_02.wav", "pipe", 15.78, 18.65, 100, 3800, .050, .500, -17),
        ("SFX_Pipe_Resonance_03.wav", "pipe", 26.36, 29.90, 100, 4000, .070, .650, -15),
        ("SFX_Metal_Creak_01.wav", "creak", 5.35, 7.25, 160, 4200, .120, .220, -18),
        ("SFX_Metal_Creak_02.wav", "creak", 46.80, 50.35, 160, 4000, .150, .350, -18),
    ]
    for name, key, start, end, highpass, lowpass, fade_in, fade_out, peak in details:
        audio = filter_band(section(source[key], start, end), highpass, lowpass)
        if key == "pipe":
            # Keep the resonance audible without allowing a very short impact to set all gain.
            ceiling = 5.5 * rms(audio)
            audio = ceiling * np.tanh(audio / ceiling)
            audio = sosfiltfilt(butter(2, lowpass, "lowpass", fs=RATE, output="sos"), audio, axis=0)
        audio = level_peak(fade_edges(audio, fade_in, fade_out), peak)
        save(name, audio, [{"file": SOURCES[key], "start_seconds": start, "end_seconds": end}], {
            "highpass_hz": highpass, "lowpass_hz": lowpass,
            "fade_in_seconds": fade_in, "fade_out_seconds": fade_out,
            "peak_target_dbfs": peak,
            "transient_soft_limit_rms_ratio": 5.5 if key == "pipe" else None,
        })

    manifest = PROJECT / "Docs" / "AudioAssets.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({"format": "48 kHz / 24 bit PCM / stereo WAV", "exports": exports},
                                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(exports, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
