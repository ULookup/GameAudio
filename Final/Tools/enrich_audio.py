"""Export six additional corridor layers without changing the original six assets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt

from process_audio import (
    PROJECT, RATE, circular_crossfade, db, fade_edges, filter_band,
    level_peak, level_rms, read_stereo, rms, section,
)


SOURCES = {
    "deep_ventilation": "451924__kyles__room-tone-large-room-church-basement-heavy-deep-ventilation-or-furnace-hum.flac",
    "bunker": "817225__nox_sound__atmosphere_scifi_bunker_loop_stereo.wav",
    "spacecraft": "343738__vospi__empty-corridor-of-a-spacecraft.wav",
    "groan": "496836__hinchinbrook__metallic-groan.wav",
    "machine": "260815__iccleste__industrial-machine-cycle.wav",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=Path.home() / "Downloads")
    args = parser.parse_args()
    source = {key: read_stereo(args.sources / name) for key, name in SOURCES.items()}
    output = PROJECT / "Audio" / "Exports"
    output.mkdir(parents=True, exist_ok=True)
    records = []
    rng = np.random.default_rng(20261102)

    def provenance(key: str, start: float, end: float) -> dict:
        return {"file": SOURCES[key], "start_seconds": start, "end_seconds": end}

    def save(name: str, audio: np.ndarray, sources: list[dict], processing: dict) -> None:
        dither = (rng.random(audio.shape) - rng.random(audio.shape)) / (2 ** 23)
        path = output / name
        sf.write(path, audio + dither, RATE, subtype="PCM_24", format="WAV")
        info = sf.info(path)
        records.append({
            "file": f"Audio/Exports/{name}", "duration_seconds": info.duration,
            "sample_rate": info.samplerate, "channels": info.channels,
            "subtype": info.subtype, "peak_dbfs": round(db(np.max(np.abs(audio))), 2),
            "rms_dbfs": round(db(rms(audio)), 2),
            "sources": sources, "processing": processing,
        })

    deep = filter_band(section(source["deep_ventilation"], 1.0, 68.0), 40, 1400)
    deep = level_rms(circular_crossfade(deep, 3.0), -34.0)
    save("AMB_Deep_Ventilation_Loop_64s.wav", deep,
         [provenance("deep_ventilation", 1.0, 68.0)],
         {"highpass_hz": 40, "lowpass_hz": 1400,
          "crossfade_seconds": 3, "crossfade_type": "equal_power",
          "target_rms_dbfs": -34})

    bunker = filter_band(section(source["bunker"], .5, 57.5), 80, 600)
    bunker = level_rms(bunker, -37)
    spacecraft = filter_band(section(source["spacecraft"], 1.0, 20.5), 40, 250)
    spacecraft = circular_crossfade(spacecraft, 3.0)
    spacecraft = np.tile(spacecraft, (4, 1))[:len(bunker)]
    spacecraft = level_rms(spacecraft, -47)
    # Both layers share the final gain, preserving the 10 dB layer RMS difference.
    spatial = level_rms(circular_crossfade(bunker + spacecraft, 3.0), -37)
    save("AMB_Subtle_Space_Resonance_Loop_54s.wav", spatial,
         [provenance("bunker", .5, 57.5), provenance("spacecraft", 1.0, 20.5)],
         {"bunker_highpass_hz": 80, "bunker_lowpass_hz": 600,
          "bunker_layer_rms_dbfs": -37,
          "spacecraft_highpass_hz": 40, "spacecraft_lowpass_hz": 250,
          "spacecraft_layer_rms_dbfs": -47,
          "spacecraft_internal_loop_seconds": 16.5,
          "spacecraft_internal_crossfade_seconds": 3,
          "final_crossfade_seconds": 3, "crossfade_type": "equal_power",
          "target_rms_dbfs": -37,
          "note": "The source spacecraft drone has tonal content; mixed 10 dB below the bunker layer."})

    details = [
        ("SFX_Structure_Groan_01.wav", "groan", .30, 1.45, 100, 2500, .120, .350, -14),
        ("SFX_Structure_Groan_02.wav", "groan", 1.65, 8.65, 100, 2200, .450, .800, -15),
        ("SFX_Machine_Cycle_01.wav", "machine", 5.0, 13.0, 100, 1400, 1.100, 1.200, -14),
        ("SFX_Machine_Cycle_02.wav", "machine", 30.0, 38.0, 100, 1200, 1.200, 1.100, -14),
    ]
    for name, key, start, end, highpass, lowpass, fade_in, fade_out, peak in details:
        audio = filter_band(section(source[key], start, end), highpass, lowpass)
        soft_limit = key == "groan" and db(np.max(np.abs(audio)) / rms(audio)) > 16
        if soft_limit:
            ceiling = 5.5 * rms(audio)
            audio = ceiling * np.tanh(audio / ceiling)
            audio = sosfiltfilt(butter(2, lowpass, "lowpass", fs=RATE, output="sos"), audio, axis=0)
        audio = level_peak(fade_edges(audio, fade_in, fade_out), peak)
        save(name, audio, [provenance(key, start, end)],
             {"highpass_hz": highpass, "lowpass_hz": lowpass,
              "fade_in_seconds": fade_in, "fade_out_seconds": fade_out,
              "peak_target_dbfs": peak,
              "transient_soft_limit_rms_ratio": 5.5 if soft_limit else None,
              "playback": "one_shot"})

    manifest = PROJECT / "Docs" / "AudioExpansion.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({"format": "48 kHz / 24 bit PCM / stereo WAV", "exports": records},
                                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(records, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
