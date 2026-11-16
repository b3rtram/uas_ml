# React basics

The same ideas as in `01_streamlit_basics`, now the way web developers build pages:
**JavaScript in the browser**, built from small components.

```bash
# once: install Node.js (https://nodejs.org, version 20 or newer), then
npm install                       # downloads React and Vite into node_modules/
npm run dev                       # opens http://localhost:5173
```

| section | file | idea |
|---|---|---|
| 1 | `src/Greeting.jsx` | a **component** is a function that returns JSX; **props** are its parameters |
| 2 | `src/Counter.jsx` | **state** (`useState`) and **events** (`onClick`) |
| 3 | `src/App.jsx` | load data after the first render: `useEffect` + `fetch("/prices.json")` |
| 4 | `src/SymbolPicker.jsx`, `PriceChart.jsx`, `PriceTable.jsx` | one state in the parent, passed down to three components; lists with `.map()` and `key` |
| 5 | `src/Prediction.jsx` | call a REST backend: the Session 5 monolith |

`public/prices.json` holds made-up prices (random walk), not real ones.

## Section 5: the Session 5 backend

```bash
cd ../../lecture05_architecture/01_monolith
python -m uvicorn app:app --port 8000
```
`vite.config.js` passes every `/api/...` request on to port 8000. Without the backend, section 5 shows an error,
the rest of the page still works.
React never calls FMP directly: code in the browser is visible to everyone, so the API key would be too.

## Streamlit vs. React

| | Streamlit | React |
|---|---|---|
| language | Python | JavaScript (JSX) |
| runs where | on the server; the browser only displays | in the browser |
| after a click | the **whole script** runs again | only the components whose state changed (and their children) render again |
| remember a value | `st.session_state` | `useState` |
| slow work only once | `@st.cache_data` | `useEffect(..., [])` |
| a widget | `st.selectbox(...)` returns the value | `<select value onChange>` + state |
| good for | data apps and ML demos, fast | real products, full control over the page |

Look at the counters in section 2: "this function ran 3 times" after one click. 1 = first render,
2 = `App` rendered again when the data arrived (children render with their parent), 3 = the click.

## Exercises

1. **Required:** in `Counter.jsx`, replace `useState` with a normal variable `let count = 0`. What happens on a click, and why? Compare with page 7 in `01_streamlit_basics`.
2. **Recommended:** add a third `<Greeting />` with your own name. Which file do you change?
3. **Bonus:** show the daily return in `PriceTable.jsx` as a third column, green when positive, red when negative.
