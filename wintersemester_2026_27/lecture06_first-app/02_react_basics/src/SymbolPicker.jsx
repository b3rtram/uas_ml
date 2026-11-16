// 4a · A CONTROLLED INPUT: the parent owns the value; the picker only shows it and reports changes.
export default function SymbolPicker({ symbols, value, onChange }) {
  return (
    <label>
      Symbol{" "}
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {symbols.map((s) => <option key={s}>{s}</option>)}
      </select>
    </label>
  );
}
