// 2 · STATE: a value React remembers between renders. EVENTS: functions that run on a click.
import { useRef, useState } from "react";

export default function Counter() {
  const [count, setCount] = useState(0);        // count = current value, setCount = the only way to change it
  const renders = useRef(0);                    // a box React keeps, but changing it does not render again
  renders.current += 1;                         // this function runs on every render

  // let count2 = 0; count2 += 1  would NOT work: a normal variable starts at 0 in every render
  return (
    <p>
      <button onClick={() => setCount(count + 1)}>+1</button>{" "}
      count = {count} <span className="note">(this function ran {renders.current} times)</span>
    </p>
  );
}
