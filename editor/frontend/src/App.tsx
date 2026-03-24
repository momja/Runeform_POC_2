import { useState, useEffect, useCallback } from 'react';
import type { Template, Archetype, ContentItem, Slot } from './types';
import { listTemplates, createTemplate, updateTemplate, deleteTemplate } from './api';
import { CanvasEditor } from './CanvasEditor';
import { ContentPanel } from './ContentPanel';
import { ArchetypePanel } from './ArchetypePanel';
import './App.css';

const DEFAULT_CONTENT: ContentItem[] = [
  { role: 'title', label: 'EVENT TITLE', color: '#d24646' },
  { role: 'hero', label: 'HERO IMAGE', color: '#50a05a' },
  { role: 'details', label: 'DATE / LOCATION', color: '#be7832' },
  { role: 'logo', label: 'LOGO', color: '#3c6ec8' },
];

const EMPTY_TEMPLATE: Template = {
  name: 'Untitled Template',
  canvas_width: 1080,
  canvas_height: 1080,
  archetypes: [],
  content: [...DEFAULT_CONTENT],
};

function App() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [current, setCurrent] = useState<Template>(structuredClone(EMPTY_TEMPLATE));
  const [selectedArchIdx, setSelectedArchIdx] = useState<number>(0);
  const [selectedSlotRole, setSelectedSlotRole] = useState<string | null>(null);
  const [dirty, setDirty] = useState(false);

  const refreshList = useCallback(async () => {
    setTemplates(await listTemplates());
  }, []);

  useEffect(() => { refreshList(); }, [refreshList]);

  const handleSave = async () => {
    if (current.id) {
      const saved = await updateTemplate(current.id, current);
      setCurrent(saved);
    } else {
      const saved = await createTemplate(current);
      setCurrent(saved);
    }
    setDirty(false);
    refreshList();
  };

  const handleLoad = (t: Template) => {
    setCurrent(structuredClone(t));
    setSelectedArchIdx(0);
    setSelectedSlotRole(null);
    setDirty(false);
  };

  const handleNew = () => {
    setCurrent(structuredClone(EMPTY_TEMPLATE));
    setSelectedArchIdx(0);
    setSelectedSlotRole(null);
    setDirty(false);
  };

  const handleDelete = async (id: string) => {
    await deleteTemplate(id);
    if (current.id === id) handleNew();
    refreshList();
  };

  const updateCurrent = (patch: Partial<Template>) => {
    setCurrent(prev => ({ ...prev, ...patch }));
    setDirty(true);
  };

  // Archetype operations
  const addArchetype = () => {
    const name = `archetype_${Date.now().toString(36)}`;
    const roles = current.content.map(c => c.role);
    const cw = current.canvas_width;
    const ch = current.canvas_height;
    const m = 60;
    // Default: stack slots vertically
    const slotH = Math.floor((ch - m * 2) / roles.length);
    const slots: Record<string, Slot> = {};
    roles.forEach((role, i) => {
      slots[role] = { x: m, y: m + i * slotH, width: cw - m * 2, height: slotH - 20 };
    });
    const arch: Archetype = { name, label: 'New Archetype', slots };
    updateCurrent({ archetypes: [...current.archetypes, arch] });
    setSelectedArchIdx(current.archetypes.length);
  };

  const updateArchetype = (idx: number, patch: Partial<Archetype>) => {
    const archetypes = current.archetypes.map((a, i) => i === idx ? { ...a, ...patch } : a);
    updateCurrent({ archetypes });
  };

  const removeArchetype = (idx: number) => {
    updateCurrent({ archetypes: current.archetypes.filter((_, i) => i !== idx) });
    if (selectedArchIdx >= current.archetypes.length - 1) {
      setSelectedArchIdx(Math.max(0, current.archetypes.length - 2));
    }
    setSelectedSlotRole(null);
  };

  const updateSlot = (archIdx: number, role: string, slotPatch: Partial<Slot>) => {
    const archetypes = current.archetypes.map((a, i) => {
      if (i !== archIdx) return a;
      return { ...a, slots: { ...a.slots, [role]: { ...a.slots[role], ...slotPatch } } };
    });
    updateCurrent({ archetypes });
  };

  const selectedArch = current.archetypes[selectedArchIdx] ?? null;

  return (
    <div className="app">
      <header className="toolbar">
        <h1>Runeform</h1>
        <div className="toolbar-actions">
          <input
            className="template-name"
            value={current.name}
            onChange={e => updateCurrent({ name: e.target.value })}
          />
          <button onClick={handleNew}>New</button>
          <button onClick={handleSave} className={dirty ? 'primary' : ''}>
            {dirty ? 'Save*' : 'Save'}
          </button>
        </div>
      </header>

      <div className="main-layout">
        <aside className="sidebar">
          <h3>Templates</h3>
          <ul className="template-list">
            {templates.map(t => (
              <li key={t.id} className={t.id === current.id ? 'active' : ''}>
                <button className="template-btn" onClick={() => handleLoad(t)}>{t.name}</button>
                <button className="delete-btn" onClick={() => handleDelete(t.id!)}>x</button>
              </li>
            ))}
          </ul>

          <hr />

          <h3>Archetypes</h3>
          <button className="add-element-btn" onClick={addArchetype}>+ Add Archetype</button>
          <ul className="element-list">
            {current.archetypes.map((arch, i) => (
              <li
                key={arch.name}
                className={i === selectedArchIdx ? 'active' : ''}
                onClick={() => { setSelectedArchIdx(i); setSelectedSlotRole(null); }}
              >
                {arch.label}
                <button className="delete-btn" onClick={e => { e.stopPropagation(); removeArchetype(i); }}>x</button>
              </li>
            ))}
          </ul>

          <hr />

          <ContentPanel
            content={current.content}
            onChange={content => updateCurrent({ content })}
          />
        </aside>

        <main className="canvas-area">
          {selectedArch ? (
            <CanvasEditor
              archetype={selectedArch}
              content={current.content}
              canvasWidth={current.canvas_width}
              canvasHeight={current.canvas_height}
              selectedSlotRole={selectedSlotRole}
              onSelectSlot={setSelectedSlotRole}
              onUpdateSlot={(role, patch) => updateSlot(selectedArchIdx, role, patch)}
            />
          ) : (
            <div className="empty-canvas">
              <p>Add an archetype to start designing</p>
            </div>
          )}
        </main>

        <aside className="properties">
          {selectedArch ? (
            <ArchetypePanel
              archetype={selectedArch}
              selectedSlotRole={selectedSlotRole}
              canvasWidth={current.canvas_width}
              canvasHeight={current.canvas_height}
              onUpdateArchetype={patch => updateArchetype(selectedArchIdx, patch)}
              onUpdateSlot={(role, patch) => updateSlot(selectedArchIdx, role, patch)}
              onSelectSlot={setSelectedSlotRole}
            />
          ) : (
            <div className="no-selection">
              <p>Select an archetype to edit its slot positions</p>
              <hr />
              <h3>Canvas</h3>
              <label>
                Width
                <input type="number" value={current.canvas_width}
                  onChange={e => updateCurrent({ canvas_width: parseInt(e.target.value) || 1080 })} />
              </label>
              <label>
                Height
                <input type="number" value={current.canvas_height}
                  onChange={e => updateCurrent({ canvas_height: parseInt(e.target.value) || 1080 })} />
              </label>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}

export default App;
