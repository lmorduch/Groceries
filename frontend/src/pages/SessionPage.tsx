// ABOUTME: Active shopping session view - check off items, add ad-hoc items
// ABOUTME: Items grouped by category; completion tracked per-item

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  addSessionItem,
  deleteSessionItem,
  getSession,
  updateSession,
  updateSessionItem,
} from "../api";

export default function SessionPage() {
  const { id } = useParams<{ id: string }>();
  const sessionId = Number(id);
  const qc = useQueryClient();
  const navigate = useNavigate();

  const { data: session, isLoading } = useQuery({
    queryKey: ["session", sessionId],
    queryFn: () => getSession(sessionId),
  });

  const [newItem, setNewItem] = useState("");
  const [newCategory, setNewCategory] = useState("");

  const checkMut = useMutation({
    mutationFn: ({ itemId, checked }: { itemId: number; checked: boolean }) =>
      updateSessionItem(sessionId, itemId, { checked }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["session", sessionId] }),
  });

  const addItemMut = useMutation({
    mutationFn: () => addSessionItem(sessionId, { name: newItem, category: newCategory || undefined }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["session", sessionId] }); setNewItem(""); setNewCategory(""); },
  });

  const deleteMut = useMutation({
    mutationFn: (itemId: number) => deleteSessionItem(sessionId, itemId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["session", sessionId] }),
  });

  const completeMut = useMutation({
    mutationFn: () => updateSession(sessionId, { completed: true }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["sessions"] }); navigate("/"); },
  });

  if (isLoading || !session) return <p>Loading…</p>;

  const categories = Array.from(new Set(session.items.map((i) => i.category ?? "Other")));
  const checkedCount = session.items.filter((i) => i.checked).length;

  return (
    <div className="page">
      <div className="page-header">
        <h1>{session.name}</h1>
        <span className="progress">{checkedCount}/{session.items.length}</span>
        {!session.completed && (
          <button className="btn-primary" onClick={() => completeMut.mutate()}>Mark Complete</button>
        )}
      </div>

      {!session.completed && (
        <form className="add-form" onSubmit={(e) => { e.preventDefault(); if (newItem.trim()) addItemMut.mutate(); }}>
          <input value={newItem} onChange={(e) => setNewItem(e.target.value)} placeholder="Add item…" />
          <input value={newCategory} onChange={(e) => setNewCategory(e.target.value)} placeholder="Category" list="session-cats" />
          <datalist id="session-cats">{categories.map((c) => <option key={c} value={c} />)}</datalist>
          <button type="submit" disabled={!newItem.trim()}>Add</button>
        </form>
      )}

      {categories.map((cat) => {
        const items = session.items.filter((i) => (i.category ?? "Other") === cat);
        return (
          <div key={cat} className="category-group">
            <h3 className="category-label">{cat}</h3>
            <ul className="item-list">
              {items.map((item) => (
                <li key={item.id} className={`item-row ${item.checked ? "checked" : ""}`}>
                  <input
                    type="checkbox"
                    checked={item.checked}
                    onChange={(e) => checkMut.mutate({ itemId: item.id, checked: e.target.checked })}
                  />
                  <span className="item-name">{item.name}</span>
                  {!session.completed && (
                    <button className="btn-danger sm" onClick={() => deleteMut.mutate(item.id)}>✕</button>
                  )}
                </li>
              ))}
            </ul>
          </div>
        );
      })}

      {session.items.length === 0 && <p className="empty">No items. Add some above.</p>}
    </div>
  );
}
