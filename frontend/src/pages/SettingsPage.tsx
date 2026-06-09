// ABOUTME: User settings page — currently manages the Anthropic API key for photo scanning
// ABOUTME: Key is stored server-side per user; only whether a key is set is exposed to the UI

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { getMe, updateMe } from "../api";

export default function SettingsPage() {
  const qc = useQueryClient();
  const { data: me } = useQuery({ queryKey: ["me"], queryFn: getMe });

  const [keyInput, setKeyInput] = useState("");
  const [showInput, setShowInput] = useState(false);

  const saveMut = useMutation({
    mutationFn: (key: string | null) => updateMe({ anthropic_api_key: key }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["me"] });
      setKeyInput("");
      setShowInput(false);
    },
  });

  function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (keyInput.trim()) saveMut.mutate(keyInput.trim());
  }

  return (
    <div className="page">
      <h1>Settings</h1>

      <section>
        <h2>Anthropic API key</h2>
        <p className="hint">
          Used for the 📷 Scan feature on the Pantry Check page. Your key is stored on the server
          and never returned to the browser.
        </p>

        {me?.has_anthropic_key ? (
          <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
            <span>✅ Key saved</span>
            <button className="btn-sm" onClick={() => setShowInput((v) => !v)}>
              Replace
            </button>
            <button
              className="btn-danger sm"
              onClick={() => saveMut.mutate(null)}
              disabled={saveMut.isPending}
            >
              Remove
            </button>
          </div>
        ) : (
          <p>No key set.</p>
        )}

        {(!me?.has_anthropic_key || showInput) && (
          <form className="add-form" onSubmit={handleSave} style={{ marginTop: "0.75rem" }}>
            <input
              type="password"
              value={keyInput}
              onChange={(e) => setKeyInput(e.target.value)}
              placeholder="sk-ant-…"
              style={{ flex: 1 }}
            />
            <button type="submit" disabled={!keyInput.trim() || saveMut.isPending}>
              {saveMut.isPending ? "Saving…" : "Save"}
            </button>
          </form>
        )}
      </section>
    </div>
  );
}
