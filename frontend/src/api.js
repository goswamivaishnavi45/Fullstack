// ===== src/api.js =====
// Step 9 · One place for ALL calls to the backend
// Step 10 · JSON header only for JSON bodies (login sends form data) · 401 → log out
// Concepts: fetch, async/await, JSON body, Authorization header, turning HTTP errors into JS errors.

const API_URL = "http://localhost:8000"; // our FastAPI server

export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("token"); // saved by login() in AuthContext

  const res = await fetch(API_URL + path, {
    ...options, // method, body ...
    headers: {
      // JSON bodies are strings (JSON.stringify); form data (login) sets its own type
      ...(typeof options.body === "string" ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}), // add token only if we have one
    },
  });

  // token expired or invalid → forget it and go to the login page
  if (res.status === 401 && path !== "/auth/login") {
    localStorage.removeItem("token");
    window.location.href = "/login";
  }

  // fetch does NOT throw on 401/403/404/422 - we must check res.ok ourselves
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const msg = typeof body.detail === "string" ? body.detail : `Request failed (${res.status})`;
    throw new Error(msg); // the component's catch() will show this
  }

  return res.status === 204 ? null : res.json(); // 204 (delete) has no body
}
