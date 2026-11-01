"""Author the corridor ambience in the currently open Final.wproj via WAAPI."""
from pathlib import Path
import json
from wwise_api import call

ROOT = Path(__file__).resolve().parents[1]
CONTAINERS = r"\Containers\Default Work Unit"
SCENE = CONTAINERS + r"\AMB_Underground_Corridor"
RANDOM = SCENE + r"\RND_Pipe_And_Metal"
ATTENUATION = r"\Attenuations\Default Work Unit\ATT_Corridor_Metal_40m"


def create(parent, kind, name, **props):
    return call("ak.wwise.core.object.create", {
        "parent": parent, "type": kind, "name": name,
        "onNameConflict": "merge", **props})


def randomizer(obj, prop, minimum, maximum):
    call("ak.wwise.core.object.setRandomizer", {
        "object": obj, "property": prop, "enabled": True,
        "min": minimum, "max": maximum})


def author_structure():
    project = call("ak.wwise.core.object.get", {"waql": "$ from type Project"},
                   {"return": ["filePath"]})["return"][0]["filePath"]
    if Path(project).resolve() != (ROOT / "Final.wproj").resolve():
        raise RuntimeError("Open this folder's Final.wproj before authoring.")
    create(CONTAINERS, "BlendContainer", "AMB_Underground_Corridor",
           notes="地下设施混凝土通风走廊：持续空气及远端机械为基底，稀疏管道与金属支架轻响。")
    create(SCENE, "Sound", "AMB_Corridor_Bed_60s",
           **{"@IsLoopingEnabled": True, "@IsLoopingInfinite": True,
              "@OverridePositioning": True, "@ListenerRelativeRouting": False},
           notes="60秒双声道循环；原声空间与远端通风机混合，首尾交叉淡化。")
    create(SCENE, "RandomSequenceContainer", "RND_Pipe_And_Metal", **{
        "@RandomOrSequence": 1, "@NormalOrShuffle": 0,
        "@RandomAvoidRepeatingCount": 2,
        "@PlayMechanismStepOrContinuous": 0,
        "@PlayMechanismLoop": True, "@PlayMechanismInfiniteOrNumberOfLoops": 1,
        "@PlayMechanismSpecialTransitions": True,
        "@PlayMechanismSpecialTransitionsType": 1,
        "@PlayMechanismSpecialTransitionsValue": 10,
        "@InitialDelay": 5,
        "@OverridePositioning": True, "@ListenerRelativeRouting": True,
        "@3DSpatialization": 1, "@3DPosition": 0,
        "@EnableAttenuation": True,
    }, notes="Shuffle随机，避免重复最近2项；短声结束后等待6–14秒；首声延迟3–7秒。")
    randomizer(RANDOM, "PlayMechanismSpecialTransitionsValue", -4, 4)
    randomizer(RANDOM, "InitialDelay", -2, 2)
    create(r"\Attenuations\Default Work Unit", "Attenuation", "ATT_Corridor_Metal_40m",
           **{"@RadiusMax": 40},
           notes="距离单位米。0/5/10/20/40m对应0/-3/-8/-18/-48dB；远距离增加低通。")
    for curve, xy in [
        ("VolumeDryUsage", [(0, 0), (5, -3), (10, -8), (20, -18), (40, -48)]),
        ("LowPassFilterUsage", [(0, 0), (5, 5), (10, 15), (20, 35), (40, 65)]),
        ("SpreadUsage", [(0, 50), (5, 35), (10, 20), (40, 0)]),
    ]:
        call("ak.wwise.core.object.setAttenuationCurve", {
            "object": ATTENUATION, "curveType": curve, "use": "Custom",
            "points": [{"x": x, "y": y, "shape": "Linear"} for x, y in xy]})
    call("ak.wwise.core.object.setReference", {
        "object": RANDOM, "reference": "Attenuation", "value": ATTENUATION})
    events = [
        ("Play_Corridor_Ambience", SCENE, 1, 2),
        ("Stop_Corridor_Ambience", SCENE, 2, 2),
        ("Play_Bed_Only", SCENE + r"\AMB_Corridor_Bed_60s", 1, 1),
        ("Play_Random_Only", RANDOM, 1, 0),
    ]
    for name, target, action_type, fade in events:
        existing = call("ak.wwise.core.object.get", {"waql": '$ from type Event where name = "' + name + '"'})["return"]
        if not existing:
            create(r"\Events\Default Work Unit", "Event", name, children=[{
                "type": "Action", "name": "", "@ActionType": action_type,
                "@Target": target, "@FadeTime": fade, "@Scope": 1 if action_type == 2 else 0}])
    create(r"\Soundcaster Sessions\Default Work Unit", "SoundcasterSession", "SC_Corridor_Final",
           notes="播放总环境或单独试听两层。用Position Editor调整距离，以实际Attenuation检查远近。")
    call("ak.wwise.core.project.save")


def import_audio():
    original_names = ["AMB_Underground_Corridor_Loop_60s", "SFX_Pipe_Resonance_01",
                      "SFX_Pipe_Resonance_02", "SFX_Pipe_Resonance_03",
                      "SFX_Metal_Creak_01", "SFX_Metal_Creak_02"]
    files = [ROOT / "Audio" / "Exports" / (name + ".wav") for name in original_names]
    if not all(path.is_file() for path in files):
        raise RuntimeError("One or more original corridor assets are missing from Audio/Exports.")
    imports = []
    for path in files:
        is_bed = path.stem.startswith("AMB_")
        name = "AMB_Corridor_Bed_60s" if is_bed else path.stem
        parent = SCENE if is_bed else RANDOM
        imports.append({"audioFile": str(path), "objectPath": parent + r"\<Sound SFX>" + name})
    result = call("ak.wwise.core.audio.import", {
        "importOperation": "useExisting",
        "default": {"importLanguage": "SFX", "originalsSubFolder": "Corridor"},
        "imports": imports}, {"return": ["id", "name", "path", "type"]})
    for path in files:
        if not path.stem.startswith("AMB_"):
            randomizer(RANDOM + "\\" + path.stem, "Pitch", -70, 70)
            randomizer(RANDOM + "\\" + path.stem, "Volume", -2, 2)
    call("ak.wwise.core.project.save")
    return result


if __name__ == "__main__":
    import sys
    if "--import" in sys.argv:
        print(json.dumps(import_audio(), ensure_ascii=False, indent=2))
    else:
        author_structure()
        print("Corridor objects, events, random playback and attenuation saved.")
