// The whole page. It is a component like all others: a function that returns what to show.
import { useEffect, useState } from "react";
import Greeting from "./Greeting.jsx";
import Counter from "./Counter.jsx";
import SymbolPicker from "./SymbolPicker.jsx";
import PriceChart from "./PriceChart.jsx";
import PriceTable from "./PriceTable.jsx";
import Prediction from "./Prediction.jsx";

function Section({ n, title, children }) {      // children = whatever is written between <Section> and </Section>
  return (
    <section>
      <h2>{n} · {title}</h2>
      {children}
    </section>
  );
}

export default function App() {
  const [data, setData] = useState(null);       // null = not loaded yet
  const [symbol, setSymbol] = useState("AAPL"); // lives here because picker, chart and table all need it

  useEffect(() => {                             // runs after the first render, not during it
    fetch("/prices.json")
      .then((response) => response.json())
      .then((json) => setData(json));           // new state -> React renders App again, now with data
  }, []);                                       // [] = only once. Without it: after every render, forever

  return (
    <main>
      <h1>React basics</h1>
      <p className="note">Every section is one file in src/. Open it next to the browser.</p>

      <Section n={1} title="A component with props">
        <Greeting name="Frankfurt UAS" />
        <Greeting name="Stock App" />
      </Section>

      <Section n={2} title="State and events">
        <Counter />
        <Counter />
        <p className="note">Two counters, two separate states: each component remembers its own.</p>
      </Section>

      <Section n={3} title="Load data: useEffect + fetch">
        {data === null
          ? <p>Loading ...</p>
          : <p>Loaded {data.dates.length} days for {Object.keys(data.prices).join(", ")}. ({data.note})</p>}
      </Section>

      <Section n={4} title="One state, three components">
        <SymbolPicker symbols={["AAPL", "MSFT", "NVDA"]} value={symbol} onChange={setSymbol} />
        {data && (
          <>
            <PriceChart dates={data.dates} closes={data.prices[symbol]} />
            <PriceTable dates={data.dates} closes={data.prices[symbol]} />
          </>
        )}
      </Section>

      <Section n={5} title="Ask a backend (Session 5)">
        <Prediction symbol={symbol} />
      </Section>
    </main>
  );
}
