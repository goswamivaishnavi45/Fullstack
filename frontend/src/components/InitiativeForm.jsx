// ===== src/components/InitiativeForm.jsx =====
// Step 9 · Create form
// Concepts: controlled inputs (value + onChange), props (onCreate from the parent), preventDefault.
import { useState } from "react";

export default function InitiativeForm({ onCreate }) {
  // one state per input: React state is the "single source of truth"
  const [name, setName] = useState("");
  const [budget, setBudget] = useState(0);
  const [status, setStatus] = useState("planned");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault(); // stop the browser from reloading the page
    setError(null);
    setSaving(true);
    try {
      await onCreate({ name, status, budget: Number(budget) }); // parent does the API call
      setName(""); // clear the form after success
      setBudget(0);
      setStatus("planned");
    } catch (err) {
      setError(err.message); // e.g. backend 401 / 422
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="form">
      {/* controlled input: shows state, and every keystroke updates state */}
      <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} required />
      <input type="number" min="0" value={budget} onChange={(e) => setBudget(e.target.value)} />
      <select value={status} onChange={(e) => setStatus(e.target.value)}>
        <option value="planned">planned</option>
        <option value="active">active</option>
        <option value="done">done</option>
      </select>
      <button disabled={saving}>{saving ? "Saving..." : "Add"}</button>
      {error && <p className="error">{error}</p>}
    </form>
  );
}
