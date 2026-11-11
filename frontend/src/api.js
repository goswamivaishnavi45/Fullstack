// ===== src/api.js =====
// Step 9 · One place for ALL calls to the backend
// Concepts: fetch, async/await, JSON body, Authorization header, turning HTTP errors into JS errors.

const API_URL = "http://localhost:8000"; // our FastAPI server

export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("token"); // saved after login (Step 10)

  const res = await fetch(API_URL + path, {
    ...options, // method, body ...
    headers: {
      "Content-Type": "application/json", // we send JSON
      ...(token ? { Authorization: `Bearer ${token}` } : {}), // add token only if we have one
    },
  });

  // fetch does NOT throw on 401/403/404/422 - we must check res.ok ourselves
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const msg = typeof body.detail === "string" ? body.detail : `Request failed (${res.status})`;
    throw new Error(msg); // the component's catch() will show this
  }

  return res.status === 204 ? null : res.json(); // 204 (delete) has no body
}
