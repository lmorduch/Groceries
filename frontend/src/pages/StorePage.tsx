// ABOUTME: Detail page for a single store - manage sections and their keywords
// ABOUTME: Sections are ordered by position; keywords drive auto-sort of session items

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router-dom";
import {
  addSectionKeyword,
  addStoreSection,
  deleteSectionKeyword,
  deleteStoreSection,
  getStore,
  updateStore,
  updateStoreSection,
  type StoreSection,
} from "../api";

export default function StorePage() {
  const { id } = useParams<{ id: string }>();
  const storeId = Number(id);
  const qc = useQueryClient();

  const { data: store, isLoading } = useQuery({
    queryKey: ["store", storeId],
    queryFn: () => getStore(storeId),
  });

  const [editingName, setEditingName] = useState(false);
  const [storeName, setStoreName] = useState("");
  const [newSection, setNewSection] = useState("");
  const [keywordInputs, setKeywordInputs] = useState<Record<number, string>>({});

  const renameMut = useMutation({
    mutationFn: () => updateStore(storeId, { name: storeName }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["store", storeId] }); setEditingName(false); },
  });

  const addSectionMut = useMutation({
    mutationFn: () => addStoreSection(storeId, { name: newSection, position: store?.sections.length ?? 0 }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["store", storeId] }); setNewSection(""); },
  });

  const deleteSectionMut = useMutation({
    mutationFn: (sectionId: number) => deleteStoreSection(storeId, sectionId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["store", storeId] }),
  });

  const moveSection = useMutation({
    mutationFn: ({ sectionId, position }: { sectionId: number; position: number }) =>
      updateStoreSection(storeId, sectionId, { position }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["store", storeId] }),
  });

  const addKeywordMut = useMutation({
    mutationFn: ({ sectionId, keyword }: { sectionId: number; keyword: string }) =>
      addSectionKeyword(storeId, sectionId, keyword),
    onSuccess: (_data, { sectionId }) => {
      qc.invalidateQueries({ queryKey: ["store", storeId] });
      setKeywordInputs((prev) => ({ ...prev, [sectionId]: "" }));
    },
  });

  const deleteKeywordMut = useMutation({
    mutationFn: ({ sectionId, keywordId }: { sectionId: number; keywordId: number }) =>
      deleteSectionKeyword(storeId, sectionId, keywordId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["store", storeId] }),
  });

  if (isLoading || !store) return <p>Loading…</p>;

  const sections = [...store.sections].sort((a, b) => a.position - b.position);

  const swapPositions = (idx: number, direction: -1 | 1) => {
    const a = sections[idx];
    const b = sections[idx + direction];
    if (!b) return;
    moveSection.mutate({ sectionId: a.id, position: b.position });
    moveSection.mutate({ sectionId: b.id, position: a.position });
  };

  return (
    <div className="page">
      <div className="page-header">
        {editingName ? (
          <form onSubmit={(e) => { e.preventDefault(); renameMut.mutate(); }} className="inline-form">
            <input value={storeName} onChange={(e) => setStoreName(e.target.value)} autoFocus />
            <button type="submit">Save</button>
            <button type="button" onClick={() => setEditingName(false)}>Cancel</button>
          </form>
        ) : (
          <h1
            onClick={() => { setStoreName(store.name); setEditingName(true); }}
            className="editable-title"
          >
            {store.name} <span className="edit-hint">✏️</span>
          </h1>
        )}
      </div>

      <p className="hint">
        Sections appear in the order below during shopping. Keywords (case-insensitive) are matched against item names and categories to auto-assign items.
      </p>

      <form className="add-form" onSubmit={(e) => { e.preventDefault(); if (newSection.trim()) addSectionMut.mutate(); }}>
        <input value={newSection} onChange={(e) => setNewSection(e.target.value)} placeholder="New section name…" />
        <button type="submit" disabled={!newSection.trim()}>Add section</button>
      </form>

      <div className="section-list">
        {sections.map((section, idx) => (
          <SectionCard
            key={section.id}
            section={section}
            isFirst={idx === 0}
            isLast={idx === sections.length - 1}
            keywordInput={keywordInputs[section.id] ?? ""}
            onKeywordInputChange={(val) => setKeywordInputs((prev) => ({ ...prev, [section.id]: val }))}
            onAddKeyword={(keyword) => addKeywordMut.mutate({ sectionId: section.id, keyword })}
            onDeleteKeyword={(keywordId) => deleteKeywordMut.mutate({ sectionId: section.id, keywordId })}
            onDelete={() => deleteSectionMut.mutate(section.id)}
            onMoveUp={() => swapPositions(idx, -1)}
            onMoveDown={() => swapPositions(idx, 1)}
          />
        ))}
        {sections.length === 0 && <p className="empty">No sections yet. Add one above.</p>}
      </div>
    </div>
  );
}

interface SectionCardProps {
  section: StoreSection;
  isFirst: boolean;
  isLast: boolean;
  keywordInput: string;
  onKeywordInputChange: (val: string) => void;
  onAddKeyword: (keyword: string) => void;
  onDeleteKeyword: (keywordId: number) => void;
  onDelete: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
}

function SectionCard({
  section, isFirst, isLast,
  keywordInput, onKeywordInputChange, onAddKeyword, onDeleteKeyword,
  onDelete, onMoveUp, onMoveDown,
}: SectionCardProps) {
  return (
    <div className="section-card">
      <div className="section-header">
        <span className="section-name">{section.name}</span>
        <div className="section-actions">
          <button className="btn-sm" onClick={onMoveUp} disabled={isFirst} title="Move up">↑</button>
          <button className="btn-sm" onClick={onMoveDown} disabled={isLast} title="Move down">↓</button>
          <button className="btn-danger sm" onClick={onDelete}>Delete</button>
        </div>
      </div>

      <div className="keyword-area">
        <div className="keyword-chips">
          {section.keywords.map((kw) => (
            <span key={kw.id} className="keyword-chip">
              {kw.keyword}
              <button className="chip-remove" onClick={() => onDeleteKeyword(kw.id)}>✕</button>
            </span>
          ))}
          {section.keywords.length === 0 && <span className="kw-empty">No keywords — items won't auto-sort here</span>}
        </div>
        <form
          className="add-form kw-form"
          onSubmit={(e) => { e.preventDefault(); if (keywordInput.trim()) onAddKeyword(keywordInput.trim()); }}
        >
          <input
            value={keywordInput}
            onChange={(e) => onKeywordInputChange(e.target.value)}
            placeholder="Add keyword…"
          />
          <button type="submit" disabled={!keywordInput.trim()}>Add</button>
        </form>
      </div>
    </div>
  );
}
