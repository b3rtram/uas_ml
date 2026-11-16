// 4c · LISTS: build one row per element with .map(). key= tells React which row is which.
export default function PriceTable({ dates, closes }) {
  const rows = dates.map((d, i) => ({ date: d, close: closes[i] })).slice(-5).reverse();   // last 5 days
  return (
    <table>
      <thead><tr><th>date</th><th>close</th></tr></thead>
      <tbody>
        {rows.map((r) => (
          <tr key={r.date}><td>{r.date}</td><td>${r.close.toFixed(2)}</td></tr>
        ))}
      </tbody>
    </table>
  );
}
