# Runeform

A compositional layout engine that generates multiple layout variants from predefined archetypes, renders them as images, and uses a multimodal LLM to rank and select the best result.

AI is used only for aesthetic ranking — never for generation. Every pixel is deterministic.

## How it works

1. **Compose** — Content items are placed into layout archetypes by matching roles (title, hero, details, logo) to positioned slots
2. **Render** — Each variant is drawn as a PNG using Pillow
3. **Rank** — All rendered images are sent to Claude's vision API, which returns a structured JSON ranking

Variety comes from having multiple archetypes (spatial recipes) for the same content. Brand consistency is guaranteed because the content and colors are fixed — only the arrangement changes.

## Quick start

```bash
# Install dependencies
uv sync

# Run the demo pipeline (compose + render + rank)
uv run python poc.py

# Run on a saved template
uv run python run.py <template-id> --event "description of your event"
```

Rendering works without any API key. Claude ranking requires `ANTHROPIC_API_KEY` to be set.

## Template editor

A visual editor for creating and managing layout templates.

```bash
# Terminal 1 — Backend (FastAPI)
uv run uvicorn editor.server:app --reload --port 8000

# Terminal 2 — Frontend dev server (React + Konva)
cd editor/frontend && npm install && npm run dev
```

Open http://localhost:5173 for the dev server, or build the frontend (`npm run build`) and access everything through http://localhost:8000.

The editor lets you:
- Create templates with custom canvas dimensions
- Add multiple archetypes (layout recipes) per template
- Drag and resize slots on a visual canvas
- Define content items with roles, labels, and colors
- Save/load templates as JSON files

## Project structure

```
poc.py              # Core pipeline: compose → render → rank
run.py              # Run pipeline on a saved template
editor/
  server.py         # FastAPI backend (template CRUD)
  loader.py         # Convert template JSON → pipeline data structures
  frontend/         # React + Konva canvas editor
templates/          # Saved template JSON files
output/             # Rendered layout PNGs
```

## Requirements

- Python 3.13+, managed with [uv](https://docs.astral.sh/uv/)
- Node.js (for the editor frontend)
- `ANTHROPIC_API_KEY` (only for the Claude ranking step)
