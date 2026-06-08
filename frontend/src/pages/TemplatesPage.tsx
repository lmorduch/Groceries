// ABOUTME: Lists all template lists and allows creating new ones
// ABOUTME: Each template links to its detail/edit page

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { createTemplate, deleteTemplate, getTemplates } from "../api";

export default function TemplatesPage() {
  const qc = useQueryClient();
  const { data: templates = [], isLoading } = useQuery({ queryKey: ["templates"], queryFn: getTemplates });
  const [newName, setNewName] = useState("");

  const createMut = useMutation({
    mutationFn: () => createTemplate({ name: newName }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["templates"] }); setNewName(""); },
  });

  const deleteMut = useMutation({
    mutationFn: deleteTemplate,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["templates"] }),
  });

  if (isLoading) return <p>Loading…</p>;

  return (
    <div className="page">
      <h1>Templates</h1>
      <p className="hint">Templates are reusable lists you can spawn into a shopping session.</p>

      <form className="add-form" onSubmit={(e) => { e.preventDefault(); if (newName.trim()) createMut.mutate(); }}>
        <input
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="New template name…"
        />
        <button type="submit" disabled={!newName.trim()}>Add</button>
      </form>

      <ul className="card-list">
        {templates.map((t) => (
          <li key={t.id} className="card">
            <Link to={`/templates/${t.id}`} className="card-title">{t.name}</Link>
            <span className="card-meta">{t.items.length} items</span>
            <button className="btn-danger" onClick={() => deleteMut.mutate(t.id)}>Delete</button>
          </li>
        ))}
        {templates.length === 0 && <li className="empty">No templates yet.</li>}
      </ul>
    </div>
  );
}
