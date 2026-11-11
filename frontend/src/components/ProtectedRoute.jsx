// ===== src/components/ProtectedRoute.jsx =====
// Step 10 · Only logged-in users may see the page inside
// Concepts: reading context, <Navigate> redirect, children prop.
import { Navigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function ProtectedRoute({ children }) {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />; // no token → go to login
  return children; // has token → show the protected page
}
