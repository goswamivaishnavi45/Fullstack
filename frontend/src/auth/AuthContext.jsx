// ===== src/auth/AuthContext.jsx =====
// Step 10 · Share the login state with the WHOLE app
// Concepts: createContext, Provider, useContext, custom hook (useAuth), token in localStorage.
import { createContext, useContext, useState } from "react";
import { apiFetch } from "../api";

const AuthContext = createContext(null); // the "shared box"

export function AuthProvider({ children }) {
  // start with the saved token, so a page refresh keeps you logged in
  const [token, setToken] = useState(localStorage.getItem("token"));

  async function login(email, password) {
    const data = await apiFetch("/auth/login", {
      method: "POST",
      body: new URLSearchParams({ username: email, password }), // FORM data (OAuth2), not JSON
    });
    localStorage.setItem("token", data.access_token); // survive refresh; api.js reads it
    setToken(data.access_token); // state change → app re-renders as "logged in"
  }

  function logout() {
    localStorage.removeItem("token");
    setToken(null);
  }

  // everything inside <AuthProvider> can read these 3 values
  return <AuthContext.Provider value={{ token, login, logout }}>{children}</AuthContext.Provider>;
}

// shortcut so components write useAuth() instead of useContext(AuthContext)
export function useAuth() {
  return useContext(AuthContext);
}
