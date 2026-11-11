// ===== src/components/Summary.jsx =====
// Step 11 · Read a STREAMING response piece by piece
// Concepts: res.body.getReader(), TextDecoder, while loop over chunks, append to state.
import { useState } from "react";
import { API_URL } from "../api";

export default function Summary({ initiativeId }) {
  const [text, setText] = useState("");
  const [streaming, setStreaming] = useState(false);

  async function handleClick() {
    setText("");
    setStreaming(true);
    try {
      // not apiFetch: apiFetch waits for the WHOLE body (res.json); we want pieces
      const res = await fetch(`${API_URL}/initiatives/${initiativeId}/summary`, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });
      if (!res.ok) throw new Error(`Request failed (${res.status})`);

      const reader = res.body.getReader(); // reads the body chunk by chunk
      const decoder = new TextDecoder(); // bytes -> text
      while (true) {
        const { done, value } = await reader.read(); // wait for the next chunk
        if (done) break; // server finished
        setText((prev) => prev + decoder.decode(value)); // add it -> screen updates
      }
    } catch (err) {
      setText(err.message);
    } finally {
      setStreaming(false);
    }
  }

  return (
    <div className="summary">
      <button onClick={handleClick} disabled={streaming}>
        {streaming ? "Writing..." : "AI summary"}
      </button>
      {text && <p>{text}</p>}
    </div>
  );
}
