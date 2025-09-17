import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App"; // .tsx extension is optional in imports

// Get the root element with type assertion
const rootElement = document.getElementById("root");

// Check if root element exists (TypeScript null check)
if (!rootElement) {
  throw new Error("Failed to find the root element");
}

// Create root and render app with proper typing
const root = createRoot(rootElement);

root.render(
  <StrictMode>
    <App />
  </StrictMode>
);