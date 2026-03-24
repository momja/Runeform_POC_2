import { useRef, useMemo } from 'react';
import { Stage, Layer, Rect, Text, Group } from 'react-konva';
import type { Archetype, ContentItem, Slot } from './types';

interface Props {
  archetype: Archetype;
  content: ContentItem[];
  canvasWidth: number;
  canvasHeight: number;
  selectedSlotRole: string | null;
  onSelectSlot: (role: string | null) => void;
  onUpdateSlot: (role: string, patch: Partial<Slot>) => void;
}

const MAX_CANVAS_PX = 700;
const GRID_STEP = 54;

export function CanvasEditor({
  archetype, content, canvasWidth: cw, canvasHeight: ch,
  selectedSlotRole, onSelectSlot, onUpdateSlot,
}: Props) {
  const scale = Math.min(MAX_CANVAS_PX / cw, MAX_CANVAS_PX / ch);
  const stageW = cw * scale;
  const stageH = ch * scale;
  const stageRef = useRef<any>(null);

  const contentByRole = useMemo(() => {
    const m: Record<string, ContentItem> = {};
    content.forEach(c => { m[c.role] = c; });
    return m;
  }, [content]);

  const gridLines = useMemo(() => {
    const lines: { x: number; y: number; w: number; h: number }[] = [];
    for (let x = 0; x <= cw; x += GRID_STEP) lines.push({ x, y: 0, w: 1, h: ch });
    for (let y = 0; y <= ch; y += GRID_STEP) lines.push({ x: 0, y, w: cw, h: 1 });
    return lines;
  }, [cw, ch]);

  const clamp = (val: number, min: number, max: number) => Math.max(min, Math.min(max, val));

  return (
    <div className="canvas-container">
      <div className="canvas-controls">
        <span className="archetype-label">{archetype.label}</span>
        <span className="canvas-size">{cw} x {ch}</span>
      </div>
      <Stage
        ref={stageRef}
        width={stageW}
        height={stageH}
        scaleX={scale}
        scaleY={scale}
        onClick={(e: any) => { if (e.target === stageRef.current) onSelectSlot(null); }}
        style={{ background: '#f8f4ee', border: '1px solid #ccc' }}
      >
        <Layer>
          {/* Grid */}
          {gridLines.map((l, i) => (
            <Rect key={`g${i}`} x={l.x} y={l.y} width={l.w} height={l.h} fill="#e6e2dc" />
          ))}

          {/* Slots */}
          {Object.entries(archetype.slots).map(([role, slot]) => {
            const ci = contentByRole[role];
            const isSelected = role === selectedSlotRole;
            const fillColor = ci?.color ?? '#888888';

            return (
              <Group
                key={role}
                x={slot.x}
                y={slot.y}
                draggable
                onClick={(e: any) => { e.cancelBubble = true; onSelectSlot(role); }}
                onDragEnd={(e: any) => {
                  const newX = clamp(Math.round(e.target.x()), 0, cw - slot.width);
                  const newY = clamp(Math.round(e.target.y()), 0, ch - slot.height);
                  e.target.position({ x: newX, y: newY });
                  onUpdateSlot(role, { x: newX, y: newY });
                }}
              >
                <Rect
                  width={slot.width}
                  height={slot.height}
                  fill={fillColor}
                  stroke={isSelected ? '#fff' : '#141414'}
                  strokeWidth={isSelected ? 4 : 2}
                  cornerRadius={4}
                  opacity={0.85}
                  shadowBlur={isSelected ? 10 : 0}
                  shadowColor="#000"
                />
                <Text
                  text={ci?.label ?? role}
                  width={slot.width}
                  height={slot.height}
                  align="center"
                  verticalAlign="middle"
                  fill="#fff"
                  fontSize={14}
                  fontStyle="bold"
                />
                {/* Role tag */}
                <Text
                  text={role}
                  x={4}
                  y={4}
                  fill="rgba(255,255,255,0.6)"
                  fontSize={10}
                />
              </Group>
            );
          })}
        </Layer>
      </Stage>
    </div>
  );
}
