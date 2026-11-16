// 5 · Call a REST backend: the Session 5 monolith (lecture05 01_monolith, port 8000).
// The browser never sees the FMP key: the backend has it. That is why React does not call FMP directly.
import { useState } from "react";

export default function Prediction({ symbol }) {
  const [status, setStatus] = useState("idle"); // idle -> loading -> done or error
  const [result, setResult] = useState(null);

  async function ask() {
    setStatus("loading");
    try {
      const response = await fetch(`/api/predict/${symbol}`, { method: "POST" });   // vite.config.js passes it on
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setResult(await response.json());
      setStatus("done");
    } catch (error) {
      setResult(String(error));
      setStatus("error");
    }
  }

  return (
    <div>
      <button onClick={ask} disabled={status === "loading"}>Predict {symbol}</button>
      {status === "loading" && <p>Asking the backend ...</p>}
      {status === "done" && (
        <p>{result.symbol}: close ${result.close} on {result.as_of} → predicted ${result.close_next} ({result.return_pct} %)</p>
      )}
      {status === "error" && (
        <p className="error">No answer ({result}). Start the Session 5 backend: see README.</p>
      )}
    </div>
  );
}
