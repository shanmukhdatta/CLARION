import React from "react";
import ReactDOM from "react-dom/client";
import App from "./app/App";
import "./styles/tokens.css";
import "./styles/print.css";

const root = document.getElementById("root");
if (!root) throw new Error("CLARION application root not found");
ReactDOM.createRoot(root).render(
  <React.StrictMode><App /></React.StrictMode>,
);
