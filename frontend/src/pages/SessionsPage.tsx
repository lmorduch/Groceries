// ABOUTME: Lists active and past shopping sessions
// ABOUTME: Allows spawning a new session from a template and optionally a store

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { createSession, deleteSession, getSessions, getStores, getTemplates } from "../api";

export default function SessionsPage() {
  const qc = useQueryClient();
  const { data: sessions = [], isLoading } = useQuery({ queryKey: ["sessions"], queryFn: getSessions });
  const { data: templates = [] } = useQuery({ queryKey: ["templates"], queryFn: getTemplates });
  const { data: stores = [] } = useQuery({ queryKey: ["stores"], queryFn: getStores });

  const [name, setName] = useState("");
  const [templateId, setTemplateId] = useState<number | "">("");
  const [storeId, setStoreId] = useState<number | "">("");

  const createMut = useMutation({
    mutationFn: () => createSession({
      name,
      template_list_id: templateId !== "" ? Number(templateId) : undefined,
      store_id: storeId !== "" ? Number(storeId) : undefined,
    }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["sessions"] });
      setName("");
      setTemplateId("");
      setStoreId("");
    },
  });

  const deleteMut = useMutation({
    mutationFn: deleteSession,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["sessions"] }),
  });

  const active = sessions.filter((s) => !s.completed);
  const done = sessions.filter((s) => s.completed);

  if (isLoading) return <p>Loading…</p>;

  return (
    <div className="page">
      <h1>Shopping Sessions</h1>

      <form className="add-form" onSubmit={(e) => { e.preventDefault(); if (name.trim()) createMut.mutate(); }}>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Session name (e.g. Weekly shop)" />
        <select value={templateId} onChange={(e) => setTemplateId(e.target.value === "" ? "" : Number(e.target.value))}>
          <option value="">Blank list</option>
          {templates.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
        </select>
        <select value={storeId} onChange={(e) => setStoreId(e.target.value === "" ? "" : Number(e.target.value))}>
          <option value="">No store</option>
          {stores.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
        <button type="submit" disabled={!name.trim()}>Start</button>
      </form>

      {active.length > 0 && (
        <>
          <h2>Active</h2>
          <ul className="card-list">
            {active.map((s) => {
              const store = stores.find((st) => st.id === s.store_id);
              return (
                <li key={s.id} className="card">
                  <Link to={`/sessions/${s.id}`} className="card-title">{s.name}</Link>
                  {store && <span className="store-badge">🏪 {store.name}</span>}
                  <span className="card-meta">
                    {s.items.filter((i) => i.checked).length}/{s.items.length} checked
                  </span>
                  <button className="btn-danger" onClick={() => deleteMut.mutate(s.id)}>Delete</button>
                </li>
              );
            })}
          </ul>
        </>
      )}

      {done.length > 0 && (
        <>
          <h2>Completed</h2>
          <ul className="card-list muted">
            {done.map((s) => (
              <li key={s.id} className="card">
                <Link to={`/sessions/${s.id}`} className="card-title">{s.name}</Link>
                <span className="card-meta">{new Date(s.date).toLocaleDateString()}</span>
                <button className="btn-danger" onClick={() => deleteMut.mutate(s.id)}>Delete</button>
              </li>
            ))}
          </ul>
        </>
      )}

      {sessions.length === 0 && <p className="empty">No sessions yet. Start one above.</p>}
    </div>
  );
}
