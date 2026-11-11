// ===== src/pages/LoginPage.jsx =====
// Step 10 · Login form
// Concepts: controlled inputs, calling login() from context, useNavigate (redirect after login).
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function LoginPage() {
  const { login } = useAuth(); // from AuthContext, no props needed
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    try {
      await login(email, password); // saves the token
      navigate("/"); // go to the initiatives page
    } catch (err) {
      setError(err.message); // e.g. "Wrong email or password"
    }
  }

  return (
    <div className="page">
      <h1>Login</h1>
      <form onSubmit={handleSubmit} className="form">
        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <button>Login</button>
      </form>
      {error && <p className="error">{error}</p>}
    </div>
  );
}
