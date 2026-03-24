import type { Template } from './types';

const BASE = '/api';

export async function listTemplates(): Promise<Template[]> {
  const res = await fetch(`${BASE}/templates`);
  return res.json();
}

export async function getTemplate(id: string): Promise<Template> {
  const res = await fetch(`${BASE}/templates/${id}`);
  return res.json();
}

export async function createTemplate(t: Template): Promise<Template> {
  const res = await fetch(`${BASE}/templates`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(t),
  });
  return res.json();
}

export async function updateTemplate(id: string, t: Template): Promise<Template> {
  const res = await fetch(`${BASE}/templates/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(t),
  });
  return res.json();
}

export async function deleteTemplate(id: string): Promise<void> {
  await fetch(`${BASE}/templates/${id}`, { method: 'DELETE' });
}
