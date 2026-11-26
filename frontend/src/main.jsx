import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./styles.css";
import "./food-covers.css";

// Old bookmarks open the visitor website; there is no administrator route.
if (window.location.hash === "#admin") window.location.hash = "#top";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
