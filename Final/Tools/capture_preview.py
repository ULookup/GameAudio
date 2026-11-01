"""Record one running Soundcaster audition and retain its voice/attenuation evidence."""
from pathlib import Path
import json
import time
import argparse
import xml.etree.ElementTree as ET
from wwise_api import call, require_final_project

ROOT = Path(__file__).resolve().parents[1]
require_final_project()
BUS = r"\Busses\Default Work Unit\Main Audio Bus"
PREVIEW = ROOT / "Preview" / "Corridor_Soundcaster_Take.wav"
PREVIEW.parent.mkdir(exist_ok=True)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--seconds", type=float, default=100)
duration = parser.parse_args().seconds
call("ak.wwise.core.project.save")
bus_xml = ET.parse(ROOT / "Busses" / "Default Work Unit.wwu").find(".//Bus[@Name='Main Audio Bus']")
if any("effect" in node.tag.lower() or node.get("Name", "").lower().startswith("effect") for node in bus_xml.iter()):
    raise RuntimeError("Main Audio Bus already has effect settings; preserve them before recording.")
call("ak.wwise.core.profiler.enableProfilerData", {"dataTypes": [
    {"dataType": "voices"}, {"dataType": "voiceInspector"}]})
call("ak.wwise.core.profiler.startCapture")

call("ak.wwise.core.object.set", {"objects": [{"object": BUS, "@Effects": [{
    "name": "", "type": "EffectSlot", "@Effect": {
        "name": "FinalPreviewRecorder", "type": "Effect", "classId": 8650755,
        "@AuthoringFilename": str(PREVIEW), "@Format": 0,
        "@DownmixToStereo": True, "@ApplyDownstreamVolume": True,
    }}]}], "listMode": "append"})

observations = []
seen = set()
print("Recorder ready. Start Play_Corridor_Ambience in Soundcaster within 30 seconds.", flush=True)
try:
    waiting = time.monotonic()
    while True:
        voices = call("ak.wwise.core.profiler.getVoices", {"time": "capture"},
                      {"return": ["pipelineID", "objectName", "gameObjectName"]})["return"]
        if any(v["objectName"] == "AMB_Corridor_Bed_60s" for v in voices):
            break
        if time.monotonic() - waiting > 30:
            raise RuntimeError("Soundcaster playback did not begin.")
        time.sleep(0.25)
    start = time.monotonic()
    while time.monotonic() - start < duration:
        voices = call("ak.wwise.core.profiler.getVoices", {"time": "capture"},
                      {"return": ["pipelineID", "objectName", "gameObjectName"]})["return"]
        observation = {"seconds": round(time.monotonic() - start, 2), "voices": voices}
        for voice in voices:
            if voice["pipelineID"] not in seen:
                seen.add(voice["pipelineID"])
                voice["contributions"] = call("ak.wwise.core.profiler.getVoiceContributions", {
                    "voicePipelineID": voice["pipelineID"], "time": "capture"})["return"]
                print(json.dumps({"seconds": observation["seconds"], "sound": voice["objectName"],
                      "volume": voice["contributions"]["volume"], "LPF": voice["contributions"]["LPF"]}), flush=True)
        observations.append(observation)
        time.sleep(0.5)
finally:
    transport = call("ak.wwise.core.transport.create", {
        "object": r"\Events\Default Work Unit\Stop_Corridor_Ambience"})["transport"]
    call("ak.wwise.core.transport.executeAction", {"transport": transport, "action": "play"})
    time.sleep(3)
    call("ak.wwise.core.object.set", {"objects": [{"object": BUS, "@Effects": []}], "listMode": "replaceAll"})
    call("ak.wwise.core.profiler.stopCapture")
    call("ak.wwise.core.project.save")
    (ROOT / "Docs" / "SoundcasterPlayback.json").write_text(json.dumps(observations, ensure_ascii=False, indent=2), encoding="utf-8")
print("Soundcaster take saved; playback stopped and temporary recorder removed.", flush=True)
