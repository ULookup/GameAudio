"""Save/close Wwise, add static spatial paths and Soundcaster modules, then reopen."""
from pathlib import Path
import copy
import json
import shutil
import time
import uuid
import xml.etree.ElementTree as ET
from wwise_api import call, require_final_project

ROOT = Path(__file__).resolve().parents[1]


def guid():
    return "{" + str(uuid.uuid4()).upper() + "}"


def prop(parent, name, typ, value):
    properties = parent.find("PropertyList")
    if properties is None:
        properties = ET.Element("PropertyList")
        parent.insert(1 if parent.find("Comment") is not None else 0, properties)
    item = properties.find(f"Property[@Name='{name}']")
    if item is None:
        item = ET.SubElement(properties, "Property", Name=name)
    item.set("Type", typ)
    item.set("Value", str(value))


def save_tree(tree, path):
    ET.indent(tree, space="\t")
    tree.write(path, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    require_final_project()
    call("ak.wwise.core.project.save")
    call("ak.wwise.ui.project.close", {"bypassSave": False})
    for attempt in range(100):
        try:
            projects = call("ak.wwise.core.object.get", {"waql": "$ from type Project"})["return"]
            if not projects:
                break
        except RuntimeError as error:
            if "no project" in str(error).lower() or "project_not_loaded" in str(error):
                break
        time.sleep(0.2)
    else:
        raise RuntimeError("The project did not close; no work-unit files were changed.")
    container_file = ROOT / "Containers" / "Default Work Unit.wwu"
    session_file = ROOT / "Soundcaster Sessions" / "Default Work Unit.wwu"
    backup = ROOT / ".backup_authoring"
    backup.mkdir(exist_ok=True)
    shutil.copy2(container_file, backup / "Containers.before_positions.wwu")
    shutil.copy2(session_file, backup / "Soundcaster.before_modules.wwu")
    tree = ET.parse(container_file)
    random = tree.find(".//RandomSequenceContainer[@Name='RND_Pipe_And_Metal']")
    attenuation = random.find("ReferenceList/Reference[@Name='Attenuation']")
    points = {
        "SFX_Pipe_Resonance_01": (-2, 7, 2),
        "SFX_Pipe_Resonance_02": (3, 11, 2.5),
        "SFX_Pipe_Resonance_03": (-1.5, 17, 3),
        "SFX_Metal_Creak_01": (2, 5, 2),
        "SFX_Metal_Creak_02": (-2, 12, 1),
        "SFX_Structure_Groan_01": (-2, 8, 2),
        "SFX_Structure_Groan_02": (2, 13, 2.5),
        "SFX_Machine_Cycle_01": (-3, 10, 0.5),
        "SFX_Machine_Cycle_02": (3, 14, 0.8),
    }
    for name, xyz in points.items():
        sound = tree.find(f".//Sound[@Name='{name}']")
        if sound is None:
            continue
        for pname, typ, value in [
            ("OverridePositioning", "bool", "True"),
            ("ListenerRelativeRouting", "bool", "True"),
            ("3DSpatialization", "int16", 1),
            ("3DPosition", "int16", 2),
            ("EnableAttenuation", "bool", "True"),
        ]:
            prop(sound, pname, typ, value)
        refs = sound.find("ReferenceList")
        old = refs.find("Reference[@Name='Attenuation']")
        if old is not None:
            refs.remove(old)
        refs.append(copy.deepcopy(attenuation))
        old = sound.find("PositioningInfo")
        if old is not None:
            sound.remove(old)
        info = ET.Element("PositioningInfo")
        position = ET.SubElement(info, "Position", Name="", ID=guid())
        prop(position, "NewPathForEachSound", "bool", "True")
        paths = ET.SubElement(position, "ChildrenList")
        path = ET.SubElement(paths, "Path2D", Name="Corridor_Fixture", ID=guid())
        point = ET.SubElement(ET.SubElement(path, "PointList"), "Point")
        for axis, meters in zip(("XPos", "YPos", "ZPos"), xyz):
            ET.SubElement(point, axis).text = str(meters / 40 * 100)
        ET.SubElement(point, "Flags").text = "12"
        ET.SubElement(point, "Time").text = "0"
        active = sound.find("ActiveSourceList")
        sound.insert(list(sound).index(active) if active is not None else len(sound), info)
    save_tree(tree, container_file)

    events = ET.parse(ROOT / "Events" / "Default Work Unit.wwu")
    event_workunit = events.find(".//WorkUnit").get("ID")
    session_tree = ET.parse(session_file)
    session = session_tree.find(".//SoundcasterSession[@Name='SC_Corridor_Final']")
    old = session.find("ModuleList")
    if old is not None:
        session.remove(old)
    modules = ET.SubElement(session, "ModuleList")
    module_events = ("Play_Corridor_Ambience", "Play_Bed_Only", "Play_Random_Only",
                     "Play_Distant_Mechanism_Only", "Play_Deep_Ventilation_Only", "Play_Space_Resonance_Only")
    for index, name in enumerate(module_events):
        event = events.find(f".//Event[@Name='{name}']")
        if event is None:
            continue
        module = ET.SubElement(modules, "Module")
        ET.SubElement(module, "ObjectRef", Name=name, ID=event.get("ID"), WorkUnitID=event_workunit)
        ET.SubElement(module, "Position", X=str(index % 3), Y=str(index // 3))
    save_tree(session_tree, session_file)
    (ROOT / "Docs" / "SpatialPositions.json").write_text(json.dumps({
        "units": "meters", "axes": ["right", "forward", "up"],
        "maximum_attenuation_distance": 40, "positions": points,
    }, indent=2), encoding="utf-8")
    call("ak.wwise.ui.project.open", {"path": str(ROOT / "Final.wproj"),
        "onMigrationRequired": "fail", "bypassSave": False})
    print("Spatial paths and Soundcaster modules saved; project opening requested.")
