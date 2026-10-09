import React from "react";
import { createRoot } from "react-dom/client";
import "@fontsource/barlow/500.css";
import "@fontsource/barlow/600.css";
import "@fontsource/barlow/700.css";
import "@fontsource/source-sans-3/400.css";
import "@fontsource/source-sans-3/600.css";
import "./styles.css";
import App from "./App.jsx";

createRoot(document.getElementById("root")).render(<React.StrictMode><App /></React.StrictMode>);
