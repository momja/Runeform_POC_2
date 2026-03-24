export interface Slot {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Archetype {
  name: string;
  label: string;
  slots: Record<string, Slot>;
}

export interface ContentItem {
  role: string;
  label: string;
  color: string;
}

export interface Template {
  id?: string;
  name: string;
  canvas_width: number;
  canvas_height: number;
  archetypes: Archetype[];
  content: ContentItem[];
}
