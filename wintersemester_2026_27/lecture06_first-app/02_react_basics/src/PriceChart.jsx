// 4b · A chart without a library: turn the prices into points of an SVG line.
const W = 600, H = 200, PAD = 30;               // size of the drawing in pixels

export default function PriceChart({ dates, closes }) {
  const min = Math.min(...closes), max = Math.max(...closes);
  const x = (i) => PAD + (i / (closes.length - 1)) * (W - 2 * PAD);   // day number -> pixel from the left
  const y = (c) => H - PAD - ((c - min) / (max - min)) * (H - 2 * PAD); // price -> pixel from the top
  const points = closes.map((c, i) => `${x(i)},${y(c)}`).join(" ");

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="chart">
      <polyline points={points} fill="none" stroke="currentColor" strokeWidth="2" />
      <text x={4} y={y(max) + 4}>{max.toFixed(0)}</text>
      <text x={4} y={y(min) + 4}>{min.toFixed(0)}</text>
      <text x={PAD} y={H - 6}>{dates[0]}</text>
      <text x={W - PAD} y={H - 6} textAnchor="end">{dates[dates.length - 1]}</text>
    </svg>
  );
}
