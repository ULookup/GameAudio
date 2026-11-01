"""Add the approved depth and occasional machinery layers to Final.wproj."""
from pathlib import Path
import json
from wwise_api import call, require_final_project
from build_wwise import create, randomizer, SCENE, RANDOM, ATTENUATION

ROOT = Path(__file__).resolve().parents[1]
LAYERS = SCENE + r"\AMB_Atmosphere_Layers"
MECHANISM = SCENE + r"\RND_Distant_Mechanism"
LOOPS = ["AMB_Deep_Ventilation_Loop_64s", "AMB_Subtle_Space_Resonance_Loop_54s"]
DETAILS = ["SFX_Structure_Groan_01", "SFX_Structure_Groan_02",
           "SFX_Machine_Cycle_01", "SFX_Machine_Cycle_02"]


def ensure_play_event(name, target, fade=0):
    path = "\\Events\\Default Work Unit\\" + name
    found = call("ak.wwise.core.object.get", {"waql": '$ from type Event where name = "' + name + '"'})["return"]
    if not found:
        create(r"\Events\Default Work Unit", "Event", name, children=[{
            "type": "Action", "name": "", "@ActionType": 1,
            "@Target": target, "@FadeTime": fade}])
    return path


def ensure_bed_event():
    """Keep separate Play actions for the original bed and additional layers."""
    path = ensure_play_event("Play_Bed_Only", SCENE + r"\AMB_Corridor_Bed_60s", 1.5)
    actions = call("ak.wwise.core.object.get", {"from": {"path": [path]},
        "transform": [{"select": ["children"]}]}, {"return": ["@Target"]})["return"]
    targets = {a.get("@Target", {}).get("name") for a in actions}
    for target in [SCENE + r"\AMB_Corridor_Bed_60s", LAYERS]:
        if target.rsplit("\\", 1)[-1] not in targets:
            # Actions have empty names; merging by name would overwrite the other target.
            call("ak.wwise.core.object.create", {
                "parent": path, "type": "Action", "name": "", "onNameConflict": "rename",
                "@ActionType": 1, "@Target": target, "@FadeTime": 1.5})
    return path


def main():
    require_final_project()
    create(SCENE, "BlendContainer", "AMB_Atmosphere_Layers",
           notes="增强背景：64秒深层通风与54秒微弱空间共鸣，异步循环。")
    for name in LOOPS:
        create(LAYERS, "Sound", name, **{
            "@IsLoopingEnabled": True, "@IsLoopingInfinite": True,
            "@OverridePositioning": True, "@ListenerRelativeRouting": False})
    create(SCENE, "RandomSequenceContainer", "RND_Distant_Mechanism", **{
        "@RandomOrSequence": 1, "@NormalOrShuffle": 0,
        "@RandomAvoidRepeatingCount": 1,
        "@PlayMechanismStepOrContinuous": 0,
        "@PlayMechanismLoop": True, "@PlayMechanismInfiniteOrNumberOfLoops": 1,
        "@PlayMechanismSpecialTransitions": True,
        "@PlayMechanismSpecialTransitionsType": 1,
        "@PlayMechanismSpecialTransitionsValue": 26,
        "@InitialDelay": 11, "@Volume": 4,
        "@OverridePositioning": True, "@ListenerRelativeRouting": True,
        "@3DSpatialization": 1, "@3DPosition": 0, "@EnableAttenuation": True,
    }, notes="较少出现的金属结构与机器工作周期。Shuffle避免重复最近1条；结束后18–34秒；首声8–14秒。")
    randomizer(MECHANISM, "PlayMechanismSpecialTransitionsValue", -8, 8)
    randomizer(MECHANISM, "InitialDelay", -3, 3)
    call("ak.wwise.core.object.setReference", {
        "object": MECHANISM, "reference": "Attenuation", "value": ATTENUATION})
    call("ak.wwise.core.object.setProperty", {
        "object": RANDOM, "property": "PlayMechanismSpecialTransitionsValue", "value": 12})
    randomizer(RANDOM, "PlayMechanismSpecialTransitionsValue", -5, 5)
    call("ak.wwise.core.object.setNotes", {"object": RANDOM,
         "value": "Shuffle随机，避免最近2项；结束后等待7–17秒；首声3–7秒。为新增机器层留出间隔。"})

    imports = [{"audioFile": str(ROOT / "Audio" / "Exports" / (name + ".wav")),
                "objectPath": (LAYERS if name in LOOPS else MECHANISM) + r"\<Sound SFX>" + name}
               for name in LOOPS + DETAILS]
    result = call("ak.wwise.core.audio.import", {
        "importOperation": "useExisting",
        "default": {"importLanguage": "SFX", "originalsSubFolder": "Corridor"},
        "imports": imports}, {"return": ["name", "type", "path"]})
    for name in DETAILS:
        randomizer(MECHANISM + "\\" + name, "Pitch", -35, 35)
        randomizer(MECHANISM + "\\" + name, "Volume", -1.5, 1.5)

    ensure_play_event("Play_Distant_Mechanism_Only", MECHANISM)
    ensure_play_event("Play_Deep_Ventilation_Only", LAYERS + "\\" + LOOPS[0], 1.5)
    ensure_play_event("Play_Space_Resonance_Only", LAYERS + "\\" + LOOPS[1], 1.5)
    ensure_bed_event()
    call("ak.wwise.core.object.setNotes", {
        "object": r"\Soundcaster Sessions\Default Work Unit\SC_Corridor_Final",
        "value": "整体、三层基底、原金属短声、新机器层、深通风、共鸣层共6个试听入口。试听切换前先总停止。"})
    call("ak.wwise.core.project.save")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
