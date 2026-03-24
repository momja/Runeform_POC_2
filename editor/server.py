"""
Runeform Template Editor — FastAPI backend.

Serves the React frontend and provides CRUD endpoints for templates
stored as JSON files in the templates/ directory.

A template defines:
  - Canvas dimensions
  - A list of archetypes (named layout recipes with slot positions)
  - A list of content items (role, label, color)
"""

import json
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
TEMPLATES_DIR.mkdir(exist_ok=True)

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend" / "dist"

app = FastAPI(title="Runeform Template Editor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class Slot(BaseModel):
    x: int
    y: int
    width: int
    height: int


class Archetype(BaseModel):
    name: str
    label: str
    slots: dict[str, Slot]  # role -> slot position


class ContentItem(BaseModel):
    role: str
    label: str
    color: str  # hex color


class Template(BaseModel):
    id: str | None = None
    name: str
    canvas_width: int = 1080
    canvas_height: int = 1080
    archetypes: list[Archetype] = []
    content: list[ContentItem] = []


# ---------------------------------------------------------------------------
# Template CRUD
# ---------------------------------------------------------------------------

def _template_path(template_id: str) -> Path:
    safe_id = Path(template_id).name
    return TEMPLATES_DIR / f"{safe_id}.json"


@app.get("/api/templates")
def list_templates() -> list[dict]:
    templates = []
    for f in sorted(TEMPLATES_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            templates.append(data)
        except (json.JSONDecodeError, KeyError):
            continue
    return templates


@app.get("/api/templates/{template_id}")
def get_template(template_id: str) -> dict:
    path = _template_path(template_id)
    if not path.exists():
        raise HTTPException(404, "Template not found")
    return json.loads(path.read_text())


@app.post("/api/templates", status_code=201)
def create_template(template: Template) -> dict:
    if not template.id:
        template.id = uuid.uuid4().hex[:8]
    path = _template_path(template.id)
    data = template.model_dump()
    path.write_text(json.dumps(data, indent=2))
    return data


@app.put("/api/templates/{template_id}")
def update_template(template_id: str, template: Template) -> dict:
    path = _template_path(template_id)
    if not path.exists():
        raise HTTPException(404, "Template not found")
    template.id = template_id
    data = template.model_dump()
    path.write_text(json.dumps(data, indent=2))
    return data


@app.delete("/api/templates/{template_id}")
def delete_template(template_id: str):
    path = _template_path(template_id)
    if not path.exists():
        raise HTTPException(404, "Template not found")
    path.unlink()
    return {"deleted": template_id}


# ---------------------------------------------------------------------------
# Serve React frontend (production build)
# ---------------------------------------------------------------------------

if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        file_path = FRONTEND_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")
