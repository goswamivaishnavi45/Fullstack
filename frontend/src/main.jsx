// ===== src/main.jsx =====
// Step 9 · Entry point: puts <App /> inside <div id="root"> in index.html
// StrictMode (dev only) runs effects twice to help catch bugs - so you may see 2 fetches.
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
