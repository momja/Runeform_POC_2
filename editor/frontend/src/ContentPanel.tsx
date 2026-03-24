import type { ContentItem } from './types';

interface Props {
  content: ContentItem[];
  onChange: (content: ContentItem[]) => void;
}

export function ContentPanel({ content, onChange }: Props) {
  const update = (idx: number, patch: Partial<ContentItem>) => {
    onChange(content.map((c, i) => i === idx ? { ...c, ...patch } : c));
  };

  const add = () => {
    const role = `item_${Date.now().toString(36)}`;
    onChange([...content, {
      role,
      label: 'New Item',
      color: '#' + Math.floor(Math.random() * 0xffffff).toString(16).padStart(6, '0'),
    }]);
  };

  const remove = (idx: number) => {
    onChange(content.filter((_, i) => i !== idx));
  };

  return (
    <div>
      <h3>Content</h3>
      <button className="add-element-btn" onClick={add}>+ Add Content</button>
      <ul className="element-list">
        {content.map((c, i) => (
          <li key={c.role}>
            <span className="color-dot" style={{ background: c.color }} />
            <input
              className="inline-input"
              value={c.label}
              onChange={e => update(i, { label: e.target.value })}
              title={`Role: ${c.role}`}
            />
            <input
              type="color"
              className="inline-color"
              value={c.color}
              onChange={e => update(i, { color: e.target.value })}
            />
            <button className="delete-btn" onClick={() => remove(i)}>x</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
