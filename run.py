"""
Run the full Runeform pipeline on a template created in the editor.

Usage:
    uv run python run.py <template>  [--event "description"]

<template> can be:
    - A template ID (looks up templates/<id>.json)
    - A path to a JSON file
"""

import argparse
import shutil
from pathlib import Path

from editor.loader import load_template
from poc import compose, render_all, rank_with_claude


TEMPLATES_DIR = Path("templates")


def resolve_template(ref: str) -> Path:
    p = Path(ref)
    if p.exists():
        return p
    by_id = TEMPLATES_DIR / f"{ref}.json"
    if by_id.exists():
        return by_id
    raise FileNotFoundError(
        f"Template not found: tried '{ref}' and '{by_id}'"
    )


def main():
    parser = argparse.ArgumentParser(description="Run Runeform pipeline on a template")
    parser.add_argument("template", help="Template ID or path to JSON file")
    parser.add_argument("--event", "-e", default="", help="Event description for Claude ranking context")
    parser.add_argument("--no-rank", action="store_true", help="Skip Claude ranking step")
    args = parser.parse_args()

    path = resolve_template(args.template)
    archetypes, content, cw, ch = load_template(path)

    print("=" * 60)
    print("Runeform — Running template pipeline")
    print("=" * 60)
    print(f"\nTemplate:   {path.name}")
    print(f"Canvas:     {cw} x {ch}")
    print(f"Archetypes: {[a.name for a in archetypes]}")
    print(f"Content:    {[c.role for c in content]}")
    if args.event:
        print(f"Event:      {args.event}")

    # Step 1 — Compose
    print(f"\n[1/3] Composing {len(archetypes)} archetype variants...")
    layouts = compose(archetypes, content)
    print(f"      Generated {len(layouts)} layouts")

    # Step 2 — Render
    output_dir = Path("output")
    print("\n[2/3] Rendering layouts (Pillow)...")
    paths = render_all(layouts, output_dir)

    # Step 3 — Rank
    if args.no_rank or not args.event:
        if not args.event:
            print("\n[3/3] Skipping ranking (no --event provided)")
        else:
            print("\n[3/3] Skipping ranking (--no-rank)")
        print(f"      View all layouts in: {output_dir}/")
    else:
        print("\n[3/3] Ranking layouts (Claude)...")
        try:
            best_i = rank_with_claude(paths, args.event)
            best_out = output_dir / "best_layout.png"
            shutil.copy(paths[best_i], best_out)
            print(f"      Best layout (#{best_i + 1}) saved -> {best_out}")
        except Exception as exc:
            print(f"      Ranking failed: {exc}")
            print(f"      View all layouts in: {output_dir}/")

    print("\nDone!")


if __name__ == "__main__":
    main()
