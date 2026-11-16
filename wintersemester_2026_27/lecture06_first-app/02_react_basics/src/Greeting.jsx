// 1 · A COMPONENT is a function that returns JSX: HTML-like code inside JavaScript.
// PROPS are its parameters: <Greeting name="Frankfurt UAS" /> calls Greeting({ name: "Frankfurt UAS" }).
export default function Greeting({ name }) {
  return <p>Hello, <strong>{name}</strong>! {/* {...} puts a JavaScript value into the HTML */}</p>;
}
