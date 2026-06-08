// ABOUTME: Lists all stores and allows creating new ones
// ABOUTME: Each store links to its section/keyword management page

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { createStore, deleteStore, getStores } from "../api";

export default function StoresPage() {
  const qc = useQueryClient();
  const { data: stores = [], isLoading } = useQuery({ queryKey: ["stores"], queryFn: getStores });
  const [newName, setNewName] = useState("");

  const createMut = useMutation({
    mutationFn: () => createStore({ name: newName }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["stores"] }); setNewName(""); },
  });

  const deleteMut = useMutation({
    mutationFn: deleteStore,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["stores"] }),
  });

  if (isLoading) return <p>Loading…</p>;

  return (
    <div className="page">
      <h1>Stores</h1>
      <p className="hint">Define stores and their sections. Items in a shopping session are auto-sorted into sections using keywords you configure.</p>

      <form className="add-form" onSubmit={(e) => { e.preventDefault(); if (newName.trim()) createMut.mutate(); }}>
        <input value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Store name…" />
        <button type="submit" disabled={!newName.trim()}>Add</button>
      </form>

      <ul className="card-list">
        {stores.map((s) => (
          <li key={s.id} className="card">
            <Link to={`/stores/${s.id}`} className="card-title">{s.name}</Link>
            <span className="card-meta">{s.sections.length} sections</span>
            <button className="btn-danger" onClick={() => deleteMut.mutate(s.id)}>Delete</button>
          </li>
        ))}
        {stores.length === 0 && <li className="empty">No stores yet.</li>}
      </ul>
    </div>
  );
}
