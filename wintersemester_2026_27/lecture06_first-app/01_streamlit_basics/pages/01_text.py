"""TEXT: everything that writes text on the page. Each call adds one element, top to bottom."""
import streamlit as st

st.title("Text")
st.caption("st.caption: small grey text. The page is built in the order the code runs.")

st.header("st.header")
st.subheader("st.subheader")
st.markdown("st.markdown: **bold**, *italic*, `code`, [a link](https://docs.streamlit.io), "
            ":orange[colored text], :material/rocket_launch: icons and emojis 🚀")
st.markdown("- lists\n- work\n- too")
st.badge("st.badge", icon=":material/check:", color="green")

st.latex(r"\hat{y} = w \cdot x + b")
st.code('st.write("Hello")', language="python")
st.divider()                                   # a horizontal line

st.subheader("st.write: takes almost anything")
st.write("A string,", 42, "and a dict:", {"symbol": "AAPL", "close": 342.37})

st.subheader("Magic")
"A string or a variable alone on a line is written to the page, as if it were wrapped in st.write:"
x = 6
x
