// ABOUTME: Pre-shopping pantry check mode
// ABOUTME: Walk through items and mark what you have / don't have before shopping

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import {
  createInventoryCheck,
  deleteInventoryCheck,
  getInventory,
  updateInventoryCheck,
} from "../api";

export default function InventoryPage() {
  const qc = useQueryClient();
  const { data: checks = [], isLoading } = useQuery({ queryKey: ["inventory"], queryFn: () => getInventory() });

  const [newItem, setNewItem] = useState("");
  const [notes, setNotes] = useState("");

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

  const undecided = checks.filter((c) => c.have_it === null);
  const haveIt = checks.filter((c) => c.have_it === true);
  const needIt = checks.filter((c) => c.have_it === false);

  if (isLoading) return <p>Loading…</p>;

  return (
    <div className="page">
      <h1>Pantry Check</h1>
      <p className="hint">Check what you already have before you shop.</p>

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
              <li key={c.id} className="item-row inventory-row">
                <span className="item-name">{c.name}</span>
                {c.notes && <span className="item-cat">{c.notes}</span>}
                <div className="inv-actions">
                  <button className="btn-have" onClick={() => updateMut.mutate({ id: c.id, have_it: true })}>✓ Have it</button>
                  <button className="btn-need" onClick={() => updateMut.mutate({ id: c.id, have_it: false })}>✗ Need it</button>
                  <button className="btn-danger sm" onClick={() => deleteMut.mutate(c.id)}>✕</button>
                </div>
              </li>
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
