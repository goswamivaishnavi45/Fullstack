// ===== src/App.jsx =====
// Step 9 · Root component  ·  Step 10 · AuthProvider + routes + protected page
// Concepts: Context Provider at the top, React Router (BrowserRouter, Routes, Route).
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import InitiativesPage from "./pages/InitiativesPage";
import LoginPage from "./pages/LoginPage";

export default function App() {
  return (
    // AuthProvider wraps everything → every page can call useAuth()
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          {/* "/" is protected: no token → redirected to /login */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <InitiativesPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
