// ABOUTME: Detail view for a single template - edit name and manage items
// ABOUTME: Items can be added, reordered by position, and deleted

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router-dom";
import {
  addTemplateItem,
  deleteTemplateItem,
  getTemplate,
  updateTemplate,
  updateTemplateItem,
} from "../api";

export default function TemplatePage() {
  const { id } = useParams<{ id: string }>();
  const templateId = Number(id);
  const qc = useQueryClient();

  const { data: template, isLoading } = useQuery({
    queryKey: ["template", templateId],
    queryFn: () => getTemplate(templateId),
  });

  const [editingName, setEditingName] = useState(false);
  const [name, setName] = useState("");
  const [newItem, setNewItem] = useState("");
  const [newCategory, setNewCategory] = useState("");

  const renameMut = useMutation({
    mutationFn: () => updateTemplate(templateId, { name }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["template", templateId] }); setEditingName(false); },
  });

  const addItemMut = useMutation({
    mutationFn: () => addTemplateItem(templateId, { name: newItem, category: newCategory || undefined }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["template", templateId] }); setNewItem(""); setNewCategory(""); },
  });

  const deleteItemMut = useMutation({
    mutationFn: (itemId: number) => deleteTemplateItem(templateId, itemId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["template", templateId] }),
  });

  const updateItemMut = useMutation({
    mutationFn: ({ itemId, data }: { itemId: number; data: { name?: string; category?: string } }) =>
      updateTemplateItem(templateId, itemId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["template", templateId] }),
  });

  if (isLoading || !template) return <p>Loading…</p>;

  const categories = Array.from(new Set(template.items.map((i) => i.category).filter(Boolean)));

  return (
    <div className="page">
      <div className="page-header">
        {editingName ? (
          <form onSubmit={(e) => { e.preventDefault(); renameMut.mutate(); }} className="inline-form">
            <input value={name} onChange={(e) => setName(e.target.value)} autoFocus />
            <button type="submit">Save</button>
            <button type="button" onClick={() => setEditingName(false)}>Cancel</button>
          </form>
        ) : (
          <h1 onClick={() => { setName(template.name); setEditingName(true); }} className="editable-title">
            {template.name} <span className="edit-hint">✏️</span>
          </h1>
        )}
      </div>

      <form className="add-form" onSubmit={(e) => { e.preventDefault(); if (newItem.trim()) addItemMut.mutate(); }}>
        <input value={newItem} onChange={(e) => setNewItem(e.target.value)} placeholder="Item name…" />
        <input value={newCategory} onChange={(e) => setNewCategory(e.target.value)} placeholder="Category (optional)" list="cats" />
        <datalist id="cats">{categories.map((c) => <option key={c} value={c!} />)}</datalist>
        <button type="submit" disabled={!newItem.trim()}>Add</button>
      </form>

      <ul className="item-list">
        {template.items.map((item) => (
          <li key={item.id} className="item-row">
            <span className="item-name">{item.name}</span>
            {item.category && <span className="item-cat">{item.category}</span>}
            <button className="btn-danger sm" onClick={() => deleteItemMut.mutate(item.id)}>✕</button>
          </li>
        ))}
        {template.items.length === 0 && <li className="empty">No items yet.</li>}
      </ul>
    </div>
  );
}
