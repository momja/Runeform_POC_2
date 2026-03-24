# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Runeform is a **compositional layout engine** that places content into predefined layout archetypes, renders each variant as an image, and uses multimodal LLMs to rank and select the best result. AI is used only for aesthetic ranking — not generation.

Target users are marketing/social media agents and small businesses (first customer: Sequoia Fabrica makerspace). The core value is "Canva speed + Bannerbear automation + creative variety" — multiple layout variants per template, with brand consistency guaranteed.

## Commands

```bash
uv sync                        # Install dependencies
uv run python poc.py           # Run full pipeline: compose → render → rank
uv run python run.py <id>      # Run pipeline on a saved template
```

### Editor

```bash
# Terminal 1 — Backend
uv run uvicorn editor.server:app --reload --port 8000

# Terminal 2 — Frontend (dev)
cd editor/frontend && npm run dev
```

Then open http://localhost:5173

Python 3.13+, managed with `uv`. Claude ranking requires `ANTHROPIC_API_KEY`.

## Architecture

### Core pipeline (`poc.py`)

Single-file pipeline with three stages:

1. **Compose** — `compose()` places content items into each archetype by matching roles to slots
2. **Render** — `render_all()` draws colored rectangles on a Pillow canvas for each composed layout
3. **Rank** — `rank_with_claude()` sends all PNGs to Claude multimodal API, gets back JSON with best layout index and reasoning

Key data types:
- `Archetype` — a named layout recipe with `slots: dict[str, Slot]` mapping roles to positioned rectangles
- `ContentItem` — a piece of content with a `role` (matching slot keys), label, and color
- `ComposedLayout` — an archetype with content placed into its slots

### Editor (`editor/`)

- **Backend** (`editor/server.py`) — FastAPI serving CRUD for templates (JSON files in `templates/`)
- **Frontend** (`editor/frontend/`) — React + Konva canvas for visual archetype editing
- **Loader** (`editor/loader.py`) — converts template JSON into pipeline data structures

A template defines: canvas dimensions, a list of archetypes (slot positions), and content items.

### Key design principles

- LLM ranks deterministic outputs — it never generates pixels
- Archetypes are predefined spatial recipes; variety comes from having multiple archetypes
- Content is role-based: each content item has a role that maps to archetype slots
- Templates are portable JSON files
