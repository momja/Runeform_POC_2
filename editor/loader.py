"""
Load a template JSON file (from the editor) and convert it into
the data structures expected by poc.compose().
"""

import json
from pathlib import Path

from poc import Archetype, Slot, ContentItem


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def load_template(path: str | Path) -> tuple[list[Archetype], list[ContentItem], int, int]:
    """
    Load a template JSON and return (archetypes, content, canvas_width, canvas_height).
    """
    data = json.loads(Path(path).read_text())

    archetypes = []
    for a in data["archetypes"]:
        slots = {}
        for role, s in a["slots"].items():
            slots[role] = Slot(x=s["x"], y=s["y"], width=s["width"], height=s["height"])
        archetypes.append(Archetype(name=a["name"], label=a["label"], slots=slots))

    content = []
    for c in data["content"]:
        content.append(ContentItem(
            role=c["role"],
            label=c["label"],
            color=hex_to_rgb(c["color"]),
        ))

    return archetypes, content, data.get("canvas_width", 1080), data.get("canvas_height", 1080)
