// ABOUTME: Reusable panel for sharing a resource (template/session/store) with other users
// ABOUTME: Owner-only; shows current shares and lets owner add/remove by email

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { createShare, deleteShare, getShares } from "../api";

interface Props {
  resourceType: "template" | "session" | "store";
  resourceId: number;
}

export default function SharePanel({ resourceType, resourceId }: Props) {
  const qc = useQueryClient();
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);

  const { data: shares = [] } = useQuery({
    queryKey: ["shares", resourceType, resourceId],
    queryFn: () => getShares(resourceType, resourceId),
  });

  const addMut = useMutation({
    mutationFn: () => createShare(resourceType, resourceId, email),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["shares", resourceType, resourceId] });
      setEmail("");
      setError(null);
    },
    onError: (err: any) => {
      setError(err?.response?.data?.detail ?? "Failed to share");
    },
  });

  const removeMut = useMutation({
    mutationFn: (shareId: number) => deleteShare(shareId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["shares", resourceType, resourceId] }),
  });

  return (
    <div className="share-panel">
      <h3 className="share-heading">Shared with</h3>
      {shares.length === 0 ? (
        <p className="share-empty">Not shared with anyone yet.</p>
      ) : (
        <ul className="share-list">
          {shares.map((s) => (
            <li key={s.id} className="share-row">
              <span className="share-email">{s.shared_with_email}</span>
              <button
                className="btn-danger sm"
                onClick={() => removeMut.mutate(s.id)}
                title="Remove access"
              >
                ✕
              </button>
            </li>
          ))}
        </ul>
      )}
      <form
        className="add-form share-form"
        onSubmit={(e) => {
          e.preventDefault();
          if (email.trim()) addMut.mutate();
        }}
      >
        <input
          type="email"
          value={email}
          onChange={(e) => { setEmail(e.target.value); setError(null); }}
          placeholder="Add by email…"
        />
        <button type="submit" disabled={!email.trim() || addMut.isPending}>
          Share
        </button>
      </form>
      {error && <p className="share-error">{error}</p>}
    </div>
  );
}
