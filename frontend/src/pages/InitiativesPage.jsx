// ===== src/pages/InitiativesPage.jsx =====
// Step 9 · List + create + delete
// Concepts: useState, useEffect (fetch on load), loading / error / empty states,
//           lists with key, lifting state up (form -> page), updating state immutably.
import { useEffect, useState } from "react";
import { apiFetch } from "../api";
import InitiativeForm from "../components/InitiativeForm";

export default function InitiativesPage() {
  const [items, setItems] = useState([]);       // the data
  const [loading, setLoading] = useState(true); // true until the first fetch finishes
  const [error, setError] = useState(null);     // error message, or null

  // Runs once after the first render ([] = no dependencies) -> load the list
  useEffect(() => {
    apiFetch("/initiatives")
      .then((data) => setItems(data.items)) // backend returns {items, total, skip, limit}
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  // Called by the form. Errors are thrown back so the form can show them.
  async function handleCreate(newData) {
    const created = await apiFetch("/initiatives", {
      method: "POST",
      body: JSON.stringify(newData),
    });
    setItems((prev) => [...prev, created]); // new array, don't push() into the old one
  }

  async function handleDelete(id) {
    if (!window.confirm("Delete this initiative?")) return;
    try {
      await apiFetch(`/initiatives/${id}`, { method: "DELETE" });
      setItems((prev) => prev.filter((item) => item.id !== id)); // remove it from the screen
    } catch (err) {
      alert(err.message); // e.g. 403 "You can only change your own initiatives"
    }
  }

  // The 3 states every data screen needs: loading, error, empty
  if (loading) return <p>Loading...</p>;
  if (error) return <p className="error">Error: {error}</p>;

  return (
    <div className="page">
      <h1>Initiatives</h1>
      <InitiativeForm onCreate={handleCreate} />

      {items.length === 0 ? (
        <p>No initiatives yet. Add one above.</p>
      ) : (
        <ul className="list">
          {/* key = stable unique id so React knows which row is which */}
          {items.map((item) => (
            <li key={item.id}>
              <span>
                <strong>{item.name}</strong> · {item.status} · budget {item.budget}
              </span>
              <button onClick={() => handleDelete(item.id)}>Delete</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
