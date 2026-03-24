import type { Archetype, Slot } from './types';

interface Props {
  archetype: Archetype;
  selectedSlotRole: string | null;
  canvasWidth: number;
  canvasHeight: number;
  onUpdateArchetype: (patch: Partial<Archetype>) => void;
  onUpdateSlot: (role: string, patch: Partial<Slot>) => void;
  onSelectSlot: (role: string | null) => void;
}

export function ArchetypePanel({
  archetype, selectedSlotRole, canvasWidth, canvasHeight,
  onUpdateArchetype, onUpdateSlot, onSelectSlot,
}: Props) {
  const selectedSlot = selectedSlotRole ? archetype.slots[selectedSlotRole] : null;

  return (
    <div className="element-panel">
      <h3>Archetype</h3>

      <label>
        Name
        <input value={archetype.name} onChange={e => onUpdateArchetype({ name: e.target.value })} />
      </label>

      <label>
        Label
        <input value={archetype.label} onChange={e => onUpdateArchetype({ label: e.target.value })} />
      </label>

      <hr />
      <h4>Slots</h4>
      <ul className="slot-list">
        {Object.keys(archetype.slots).map(role => (
          <li
            key={role}
            className={role === selectedSlotRole ? 'active' : ''}
            onClick={() => onSelectSlot(role)}
          >
            {role}
          </li>
        ))}
      </ul>

      {selectedSlot && selectedSlotRole && (
        <>
          <hr />
          <h4>Slot: {selectedSlotRole}</h4>
          <div className="field-row">
            <label>
              X
              <input type="number" value={selectedSlot.x} min={0} max={canvasWidth}
                onChange={e => onUpdateSlot(selectedSlotRole, { x: parseInt(e.target.value) || 0 })} />
            </label>
            <label>
              Y
              <input type="number" value={selectedSlot.y} min={0} max={canvasHeight}
                onChange={e => onUpdateSlot(selectedSlotRole, { y: parseInt(e.target.value) || 0 })} />
            </label>
          </div>
          <div className="field-row">
            <label>
              W
              <input type="number" value={selectedSlot.width} min={10}
                onChange={e => onUpdateSlot(selectedSlotRole, { width: parseInt(e.target.value) || 10 })} />
            </label>
            <label>
              H
              <input type="number" value={selectedSlot.height} min={10}
                onChange={e => onUpdateSlot(selectedSlotRole, { height: parseInt(e.target.value) || 10 })} />
            </label>
          </div>
          <p className="region-info">
            {selectedSlot.width} x {selectedSlot.height} px
          </p>
        </>
      )}
    </div>
  );
}
