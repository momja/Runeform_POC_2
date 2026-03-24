"""
Runeform Proof of Concept: Compositional Layout Engine
-------------------------------------------------------
Pipeline:
  1. Define content (hero image, title, details, logo — as placeholders)
  2. Compose content into each layout archetype (predefined spatial recipes)
  3. Render each variant as a PNG
  4. Claude (multimodal) ranks the variants and selects the best

Use case: Yoga class poster for Serenity Woods Yoga Collective
"""

from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Slot:
    """A positioned rectangle within a layout archetype."""
    x: int
    y: int
    width: int
    height: int


@dataclass
class Archetype:
    """A named layout recipe: maps content roles to positioned slots."""
    name: str
    label: str
    slots: dict[str, Slot]  # role -> slot (e.g. "hero", "title", "details", "logo")


@dataclass
class ContentItem:
    """A piece of content to place in a slot."""
    role: str           # matches archetype slot keys
    label: str          # display text
    color: tuple[int, int, int]
    image_path: str | None = None  # placeholder for real images


@dataclass
class ComposedLayout:
    """An archetype with content placed into its slots."""
    archetype: Archetype
    placements: dict[str, tuple[ContentItem, Slot]]  # role -> (content, slot)


# ---------------------------------------------------------------------------
# Canvas
# ---------------------------------------------------------------------------

CANVAS_W = 1080
CANVAS_H = 1080
MARGIN = 60


# ---------------------------------------------------------------------------
# Archetypes — predefined layout recipes
# ---------------------------------------------------------------------------

ARCHETYPES = [
    Archetype(
        name="hero_left_text_right",
        label="Hero Left, Text Right",
        slots={
            "hero":    Slot(x=MARGIN, y=MARGIN, width=520, height=960),
            "title":   Slot(x=620, y=MARGIN, width=400, height=120),
            "details": Slot(x=620, y=220, width=400, height=200),
            "logo":    Slot(x=620, y=840, width=120, height=120),
        },
    ),
    Archetype(
        name="hero_center_text_overlay",
        label="Hero Center, Text Overlay",
        slots={
            "hero":    Slot(x=MARGIN, y=MARGIN, width=960, height=960),
            "title":   Slot(x=120, y=700, width=840, height=120),
            "details": Slot(x=120, y=830, width=500, height=100),
            "logo":    Slot(x=MARGIN, y=MARGIN, width=120, height=120),
        },
    ),
    Archetype(
        name="hero_top_text_bottom",
        label="Hero Top, Text Bottom",
        slots={
            "hero":    Slot(x=MARGIN, y=MARGIN, width=960, height=540),
            "title":   Slot(x=MARGIN, y=660, width=700, height=100),
            "details": Slot(x=MARGIN, y=780, width=500, height=120),
            "logo":    Slot(x=860, y=780, width=120, height=120),
        },
    ),
    Archetype(
        name="split_equal",
        label="Split Equal",
        slots={
            "hero":    Slot(x=MARGIN, y=MARGIN, width=460, height=460),
            "title":   Slot(x=560, y=MARGIN, width=460, height=460),
            "details": Slot(x=MARGIN, y=560, width=460, height=460),
            "logo":    Slot(x=560, y=560, width=460, height=460),
        },
    ),
]


# ---------------------------------------------------------------------------
# Demo content
# ---------------------------------------------------------------------------

CONTENT = [
    ContentItem(role="title",   label="MORNING FLOW\nYOGA", color=(210, 70, 70)),
    ContentItem(role="hero",    label="HERO IMAGE",          color=(80, 160, 90)),
    ContentItem(role="details", label="Sunday 9 AM\nSerenity Woods\nOutdoor Studio", color=(190, 120, 50)),
    ContentItem(role="logo",    label="LOGO",                color=(60, 110, 200)),
]


# ---------------------------------------------------------------------------
# Composition — place content into archetypes
# ---------------------------------------------------------------------------

def compose(archetypes: list[Archetype], content: list[ContentItem]) -> list[ComposedLayout]:
    """Place content items into each archetype by matching roles to slots."""
    content_by_role = {c.role: c for c in content}
    layouts = []
    for arch in archetypes:
        placements = {}
        for role, slot in arch.slots.items():
            if role in content_by_role:
                placements[role] = (content_by_role[role], slot)
        layouts.append(ComposedLayout(archetype=arch, placements=placements))
    return layouts


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

BACKGROUND = (248, 244, 238)
GRID_COLOR = (230, 226, 220)


def render_layout(layout: ComposedLayout, index: int, output_dir: Path) -> Path:
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (CANVAS_W, CANVAS_H), BACKGROUND)
    draw = ImageDraw.Draw(img)

    # Subtle grid
    for x in range(0, CANVAS_W, 108):
        draw.line([(x, 0), (x, CANVAS_H)], fill=GRID_COLOR, width=1)
    for y in range(0, CANVAS_H, 108):
        draw.line([(0, y), (CANVAS_W, y)], fill=GRID_COLOR, width=1)

    # Draw each placed content item
    for role, (content, slot) in layout.placements.items():
        x1, y1 = slot.x, slot.y
        x2, y2 = slot.x + slot.width, slot.y + slot.height

        # Filled rectangle with role color
        draw.rectangle([x1, y1, x2, y2], fill=content.color, outline=(20, 20, 20), width=3)

        # Label (multiline centered)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        draw.multiline_text((cx, cy), content.label, fill=(255, 255, 255), anchor="mm", align="center")

    # Layout label (archetype name)
    draw.text((16, 16), f"Layout {index}: {layout.archetype.label}", fill=(80, 80, 80))

    path = output_dir / f"layout_{index:02d}.png"
    img.save(path)
    return path


def render_all(layouts: list[ComposedLayout], output_dir: Path) -> list[Path]:
    output_dir.mkdir(exist_ok=True)
    paths = []
    for i, layout in enumerate(layouts, 1):
        path = render_layout(layout, i, output_dir)
        paths.append(path)
        print(f"    Saved: {path.name}")
    return paths


# ---------------------------------------------------------------------------
# Claude ranker
# ---------------------------------------------------------------------------

def rank_with_claude(paths: list[Path], event_context: str) -> int:
    """
    Send all layout images to Claude and ask it to pick the best.
    Returns the 0-based index of the winning layout.
    """
    import anthropic
    import base64
    import json

    client = anthropic.Anthropic()

    content: list[dict] = []
    for i, path in enumerate(paths, 1):
        content.append({"type": "text", "text": f"Layout {i}:"})
        with open(path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode()
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": "image/png", "data": data},
        })

    content.append({
        "type": "text",
        "text": f"""You are a graphic design critic evaluating {len(paths)} layout options
for a marketing poster. Each layout uses a different compositional archetype.

Event context: {event_context}

Content legend:
  RED    -- Event title (most important element; should have visual prominence)
  GREEN  -- Hero image (large visual anchor)
  ORANGE -- Date / location details (supporting information)
  BLUE   -- Logo / branding (secondary, but must be visible)

Each layout applies a different spatial arrangement to the same content.

Rank the layouts on:
  1. Visual hierarchy (eye naturally finds the title first)
  2. Composition balance (elements well-distributed, no awkward clustering)
  3. Whitespace quality (breathing room without feeling empty)
  4. Contextual fit for the event described

Reply with ONLY valid JSON -- no markdown, no extra text:
{{"best": <number 1-{len(paths)}>, "reasoning": "<one concise sentence>"}}""",
    })

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{"role": "user", "content": content}],
    )

    text = response.content[0].text.strip()
    result = json.loads(text[text.find("{") : text.rfind("}") + 1])
    best_1indexed = result["best"]
    print(f"    Claude chose Layout {best_1indexed}: {result.get('reasoning', '')}")
    return best_1indexed - 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("Runeform PoC — Compositional Layout Engine")
    print("=" * 60)

    event = (
        "Beginner yoga class at Serenity Woods Yoga Collective. "
        "Sunday 9 am, held outdoors. Calm, welcoming, nature-inspired."
    )
    print(f"\nEvent:      {event}")
    print(f"Canvas:     {CANVAS_W} x {CANVAS_H}")
    print(f"Archetypes: {[a.name for a in ARCHETYPES]}")
    print(f"Content:    {[c.role for c in CONTENT]}")

    # Step 1 — Compose
    print("\n[1/3] Composing content into archetypes...")
    layouts = compose(ARCHETYPES, CONTENT)
    print(f"      Generated {len(layouts)} layout variants")
    for i, layout in enumerate(layouts, 1):
        print(f"      {i}. {layout.archetype.label}")

    # Step 2 — Render
    print("\n[2/3] Rendering layouts (Pillow)...")
    try:
        paths = render_all(layouts, Path("output"))
    except ImportError:
        print("      Pillow not installed. Run: uv add pillow")
        return

    # Step 3 — Rank
    print("\n[3/3] Ranking layouts (Claude)...")
    try:
        best_i = rank_with_claude(paths, event)
        import shutil
        best_out = Path("output") / "best_layout.png"
        shutil.copy(paths[best_i], best_out)
        print(f"      Best layout (#{best_i + 1}) saved -> {best_out}")
    except ImportError:
        print("      anthropic not installed. Run: uv add anthropic")
        print(f"      View all layouts in: output/")
    except Exception as exc:
        print(f"      Claude ranking failed: {exc}")
        print(f"      View all layouts in: output/")

    print("\nDone!")


if __name__ == "__main__":
    main()
