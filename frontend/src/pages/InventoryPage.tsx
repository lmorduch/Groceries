// ABOUTME: Pre-shopping pantry check mode - walk through items and mark have/need
// ABOUTME: Can be seeded from a template and launch a shopping session from "need it" items

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  addSessionItem,
  createInventoryCheck,
  createSession,
  deleteInventoryCheck,
  getInventory,
  getStores,
  getTemplate,
  updateInventoryCheck,
  type InventoryCheck,
} from "../api";

export default function InventoryPage() {
  const qc = useQueryClient();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const templateId = searchParams.get("template_id") ? Number(searchParams.get("template_id")) : null;
  const urlName = searchParams.get("name") ?? "";
  const urlStoreId = searchParams.get("store_id") ? Number(searchParams.get("store_id")) : null;

  const { data: checks = [], isLoading } = useQuery({
    queryKey: ["inventory"],
    queryFn: () => getInventory(),
  });
  const { data: template } = useQuery({
    queryKey: ["template", templateId],
    queryFn: () => getTemplate(templateId!),
    enabled: templateId !== null,
  });
  const { data: stores = [] } = useQuery({ queryKey: ["stores"], queryFn: getStores });

  const [newItem, setNewItem] = useState("");
  const [notes, setNotes] = useState("");
  const [seeded, setSeeded] = useState(false);

  // "Start Shopping" form state
  const [sessionName, setSessionName] = useState(urlName);
  const [sessionStoreId, setSessionStoreId] = useState<number | "">(urlStoreId ?? "");
  const [starting, setStarting] = useState(false);

  // Auto-seed from template once both template and inventory are loaded
  useEffect(() => {
    if (!template || seeded || isLoading) return;
    setSeeded(true);

    const existingNames = new Set(checks.map((c) => c.name.toLowerCase()));
    const toAdd = template.items.filter((item) => !existingNames.has(item.name.toLowerCase()));
    toAdd.forEach((item) => {
      createInventoryCheck({ name: item.name }).then(() => {
        qc.invalidateQueries({ queryKey: ["inventory"] });
      });
    });
  }, [template, checks, seeded, isLoading, qc]);

  const addMut = useMutation({
    mutationFn: () => createInventoryCheck({ name: newItem, notes: notes || undefined }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["inventory"] }); setNewItem(""); setNotes(""); },
  });

  const updateMut = useMutation({
    mutationFn: ({ id, have_it }: { id: number; have_it: boolean | null }) =>
      updateInventoryCheck(id, { have_it }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["inventory"] }),
  });

  const deleteMut = useMutation({
    mutationFn: deleteInventoryCheck,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["inventory"] }),
  });

  async function startShopping() {
    const needItems = checks.filter((c) => c.have_it === false);
    if (needItems.length === 0) return;
    setStarting(true);
    try {
      const session = await createSession({
        name: sessionName || "Shopping trip",
        store_id: sessionStoreId !== "" ? Number(sessionStoreId) : undefined,
      });
      await Promise.all(
        needItems.map((c) => addSessionItem(session.id, { name: c.name }))
      );
      qc.invalidateQueries({ queryKey: ["sessions"] });
      navigate(`/sessions/${session.id}`);
    } finally {
      setStarting(false);
    }
  }

  const undecided = checks.filter((c) => c.have_it === null);
  const haveIt = checks.filter((c) => c.have_it === true);
  const needIt = checks.filter((c) => c.have_it === false);

  if (isLoading) return <p>Loading…</p>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Pantry Check</h1>
        {template && <span className="store-badge">📋 {template.name}</span>}
      </div>
      <p className="hint">Mark what you already have — then start a shopping trip with just what you need.</p>

      <form className="add-form" onSubmit={(e) => { e.preventDefault(); if (newItem.trim()) addMut.mutate(); }}>
        <input value={newItem} onChange={(e) => setNewItem(e.target.value)} placeholder="Item to check…" />
        <input value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Notes (optional)" />
        <button type="submit" disabled={!newItem.trim()}>Add</button>
      </form>

      {undecided.length > 0 && (
        <div className="inventory-section">
          <h2>To check ({undecided.length})</h2>
          <ul className="item-list">
            {undecided.map((c) => (
              <InventoryRow key={c.id} check={c} onHave={() => updateMut.mutate({ id: c.id, have_it: true })} onNeed={() => updateMut.mutate({ id: c.id, have_it: false })} onDelete={() => deleteMut.mutate(c.id)} />
            ))}
          </ul>
        </div>
      )}

      {needIt.length > 0 && (
        <div className="inventory-section">
          <h2>Need to buy ({needIt.length})</h2>
          <ul className="item-list">
            {needIt.map((c) => (
              <li key={c.id} className="item-row need">
                <span className="item-name">{c.name}</span>
                <button className="btn-sm" onClick={() => updateMut.mutate({ id: c.id, have_it: null })}>Undo</button>
                <button className="btn-danger sm" onClick={() => deleteMut.mutate(c.id)}>✕</button>
              </li>
            ))}
          </ul>

          <div className="start-shopping-panel">
            <h3>Ready to shop?</h3>
            <div className="add-form">
              <input
                value={sessionName}
                onChange={(e) => setSessionName(e.target.value)}
                placeholder="Session name…"
              />
              <select
                value={sessionStoreId}
                onChange={(e) => setSessionStoreId(e.target.value === "" ? "" : Number(e.target.value))}
              >
                <option value="">No store</option>
                {stores.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
              <button
                className="btn-primary"
                onClick={startShopping}
                disabled={starting || needIt.length === 0}
              >
                {starting ? "Creating…" : `Start shopping (${needIt.length} items)`}
              </button>
            </div>
          </div>
        </div>
      )}

      {haveIt.length > 0 && (
        <div className="inventory-section muted">
          <h2>Already have ({haveIt.length})</h2>
          <ul className="item-list">
            {haveIt.map((c) => (
              <li key={c.id} className="item-row have">
                <span className="item-name">{c.name}</span>
                <button className="btn-sm" onClick={() => updateMut.mutate({ id: c.id, have_it: null })}>Undo</button>
                <button className="btn-danger sm" onClick={() => deleteMut.mutate(c.id)}>✕</button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {checks.length === 0 && <p className="empty">Add items to check above.</p>}
    </div>
  );
}

interface InventoryRowProps {
  check: InventoryCheck;
  onHave: () => void;
  onNeed: () => void;
  onDelete: () => void;
}

function InventoryRow({ check, onHave, onNeed, onDelete }: InventoryRowProps) {
  return (
    <li className="item-row inventory-row">
      <span className="item-name">{check.name}</span>
      {check.notes && <span className="item-cat">{check.notes}</span>}
      <div className="inv-actions">
        <button className="btn-have" onClick={onHave}>✓ Have it</button>
        <button className="btn-need" onClick={onNeed}>✗ Need it</button>
        <button className="btn-danger sm" onClick={onDelete}>✕</button>
      </div>
    </li>
  );
}
