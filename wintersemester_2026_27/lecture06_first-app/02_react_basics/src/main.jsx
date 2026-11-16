// Entry point: find <div id="root"> in index.html and let React draw the App component into it.
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./style.css";

createRoot(document.getElementById("root")).render(<App />);
