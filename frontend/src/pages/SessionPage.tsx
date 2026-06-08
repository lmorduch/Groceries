// ABOUTME: Active shopping session view - check off items, grouped by store section
// ABOUTME: Shows section groups when a store is set; allows manual section reassignment per item

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  addSessionItem,
  deleteSessionItem,
  getSession,
  getStore,
  updateSession,
  updateSessionItem,
  type SessionItem,
  type StoreSection,
} from "../api";

export default function SessionPage() {
  const { id } = useParams<{ id: string }>();
  const sessionId = Number(id);
  const qc = useQueryClient();
  const navigate = useNavigate();

  const { data: session, isLoading: sessionLoading } = useQuery({
    queryKey: ["session", sessionId],
    queryFn: () => getSession(sessionId),
  });

  const { data: store } = useQuery({
    queryKey: ["store", session?.store_id],
    queryFn: () => getStore(session!.store_id!),
    enabled: !!session?.store_id,
  });

  const [newItem, setNewItem] = useState("");
  const [newCategory, setNewCategory] = useState("");

  const checkMut = useMutation({
    mutationFn: ({ itemId, checked }: { itemId: number; checked: boolean }) =>
      updateSessionItem(sessionId, itemId, { checked }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["session", sessionId] }),
  });

  const sectionMut = useMutation({
    mutationFn: ({ itemId, store_section_id }: { itemId: number; store_section_id: number | null }) =>
      updateSessionItem(sessionId, itemId, { store_section_id }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["session", sessionId] }),
  });

  const addItemMut = useMutation({
    mutationFn: () => addSessionItem(sessionId, { name: newItem, category: newCategory || undefined }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["session", sessionId] });
      setNewItem("");
      setNewCategory("");
    },
  });

  const deleteMut = useMutation({
    mutationFn: (itemId: number) => deleteSessionItem(sessionId, itemId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["session", sessionId] }),
  });

  const completeMut = useMutation({
    mutationFn: () => updateSession(sessionId, { completed: true }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["sessions"] }); navigate("/"); },
  });

  if (sessionLoading || !session) return <p>Loading…</p>;

  const checkedCount = session.items.filter((i) => i.checked).length;
  const sections = store ? [...store.sections].sort((a, b) => a.position - b.position) : [];

  return (
    <div className="page">
      <div className="page-header">
        <h1>{session.name}</h1>
        {store && <span className="store-badge">🏪 {store.name}</span>}
        <span className="progress">{checkedCount}/{session.items.length}</span>
        {!session.completed && (
          <button className="btn-primary" onClick={() => completeMut.mutate()}>Mark Complete</button>
        )}
      </div>

      {!session.completed && (
        <form className="add-form" onSubmit={(e) => { e.preventDefault(); if (newItem.trim()) addItemMut.mutate(); }}>
          <input value={newItem} onChange={(e) => setNewItem(e.target.value)} placeholder="Add item…" />
          <input value={newCategory} onChange={(e) => setNewCategory(e.target.value)} placeholder="Category" list="session-cats" />
          <datalist id="session-cats">
            {Array.from(new Set(session.items.map((i) => i.category).filter(Boolean))).map((c) => (
              <option key={c} value={c!} />
            ))}
          </datalist>
          <button type="submit" disabled={!newItem.trim()}>Add</button>
        </form>
      )}

      {sections.length > 0
        ? <SectionedView items={session.items} sections={sections} completed={session.completed} onCheck={checkMut.mutate} onSection={sectionMut.mutate} onDelete={deleteMut.mutate} />
        : <CategoryView items={session.items} completed={session.completed} onCheck={checkMut.mutate} onDelete={deleteMut.mutate} />
      }

      {session.items.length === 0 && <p className="empty">No items. Add some above.</p>}
    </div>
  );
}

// --- Sectioned view (when a store is selected) ---

interface SectionedViewProps {
  items: SessionItem[];
  sections: StoreSection[];
  completed: boolean;
  onCheck: (args: { itemId: number; checked: boolean }) => void;
  onSection: (args: { itemId: number; store_section_id: number | null }) => void;
  onDelete: (itemId: number) => void;
}

function SectionedView({ items, sections, completed, onCheck, onSection, onDelete }: SectionedViewProps) {
  const unsorted = items.filter((i) => i.store_section_id === null);

  return (
    <>
      {sections.map((section) => {
        const sectionItems = items.filter((i) => i.store_section_id === section.id);
        if (sectionItems.length === 0) return null;
        return (
          <div key={section.id} className="category-group">
            <h3 className="category-label">{section.name}</h3>
            <ul className="item-list">
              {sectionItems.map((item) => (
                <ItemRow
                  key={item.id}
                  item={item}
                  sections={sections}
                  completed={completed}
                  onCheck={onCheck}
                  onSection={onSection}
                  onDelete={onDelete}
                />
              ))}
            </ul>
          </div>
        );
      })}

      {unsorted.length > 0 && (
        <div className="category-group">
          <h3 className="category-label unsorted-label">Unsorted</h3>
          <ul className="item-list">
            {unsorted.map((item) => (
              <ItemRow
                key={item.id}
                item={item}
                sections={sections}
                completed={completed}
                onCheck={onCheck}
                onSection={onSection}
                onDelete={onDelete}
              />
            ))}
          </ul>
        </div>
      )}
    </>
  );
}

// --- Category view (no store) ---

interface CategoryViewProps {
  items: SessionItem[];
  completed: boolean;
  onCheck: (args: { itemId: number; checked: boolean }) => void;
  onDelete: (itemId: number) => void;
}

function CategoryView({ items, completed, onCheck, onDelete }: CategoryViewProps) {
  const categories = Array.from(new Set(items.map((i) => i.category ?? "Other")));
  return (
    <>
      {categories.map((cat) => (
        <div key={cat} className="category-group">
          <h3 className="category-label">{cat}</h3>
          <ul className="item-list">
            {items.filter((i) => (i.category ?? "Other") === cat).map((item) => (
              <li key={item.id} className={`item-row ${item.checked ? "checked" : ""}`}>
                <input
                  type="checkbox"
                  checked={item.checked}
                  onChange={(e) => onCheck({ itemId: item.id, checked: e.target.checked })}
                />
                <span className="item-name">{item.name}</span>
                {!completed && (
                  <button className="btn-danger sm" onClick={() => onDelete(item.id)}>✕</button>
                )}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </>
  );
}

// --- Single item row with section picker ---

interface ItemRowProps {
  item: SessionItem;
  sections: StoreSection[];
  completed: boolean;
  onCheck: (args: { itemId: number; checked: boolean }) => void;
  onSection: (args: { itemId: number; store_section_id: number | null }) => void;
  onDelete: (itemId: number) => void;
}

function ItemRow({ item, sections, completed, onCheck, onSection, onDelete }: ItemRowProps) {
  return (
    <li className={`item-row ${item.checked ? "checked" : ""}`}>
      <input
        type="checkbox"
        checked={item.checked}
        onChange={(e) => onCheck({ itemId: item.id, checked: e.target.checked })}
      />
      <span className="item-name">{item.name}</span>
      {item.category && <span className="item-cat">{item.category}</span>}
      {item.section_overridden && <span className="override-badge" title="Manually assigned">📌</span>}
      {!completed && (
        <>
          <select
            className="section-select"
            value={item.store_section_id ?? ""}
            onChange={(e) => onSection({
              itemId: item.id,
              store_section_id: e.target.value === "" ? null : Number(e.target.value),
            })}
          >
            <option value="">Unsorted</option>
            {sections.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <button className="btn-danger sm" onClick={() => onDelete(item.id)}>✕</button>
        </>
      )}
    </li>
  );
}
