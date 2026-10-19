"""Page 1 — manual input form that calls the model directly."""

import streamlit as st

from model_service import get_schema, predict_income

# Nice min/max/step per numerical feature (the schema only gives a default).
NUM_RANGES = {
    "age":            {"min": 17, "max": 90,    "step": 1},
    "education-num":  {"min": 1,  "max": 16,    "step": 1},
    "capital-gain":   {"min": 0,  "max": 99999, "step": 100},
    "capital-loss":   {"min": 0,  "max": 4356,  "step": 10},
    "hours-per-week": {"min": 1,  "max": 99,    "step": 1},
}

LABELS = {
    "age": "Age",
    "education-num": "Education (years)",
    "capital-gain": "Capital gain",
    "capital-loss": "Capital loss",
    "hours-per-week": "Hours per week",
    "workclass": "Workclass",
    "marital-status": "Marital status",
    "occupation": "Occupation",
    "relationship": "Relationship",
    "race": "Race",
    "sex": "Sex",
    "native-country": "Native country",
}

schema = get_schema()

st.title("📝 Income prediction")
st.caption(
    "Enter a person's features. The saved Gradient Boosting model estimates "
    "whether their yearly income is above **$50,000**."
)

with st.form("income_form"):
    col1, col2 = st.columns(2)
    inputs = {}

    # Numerical features in the left column.
    with col1:
        st.subheader("Numerical")
        for c in schema["num_cols"]:
            rng = NUM_RANGES[c]
            inputs[c] = st.number_input(
                LABELS.get(c, c),
                min_value=rng["min"],
                max_value=rng["max"],
                value=int(schema["num_defaults"][c]),
                step=rng["step"],
            )

    # Categorical features in the right column.
    with col2:
        st.subheader("Categorical")
        for c in schema["cat_cols"]:
            options = schema["cat_options"][c]
            default_idx = options.index("United-States") if c == "native-country" and "United-States" in options else 0
            inputs[c] = st.selectbox(LABELS.get(c, c), options, index=default_idx)

    submitted = st.form_submit_button("Predict", type="primary", use_container_width=True)

if submitted:
    result = predict_income(**inputs)
    proba = result["probability_over_50k"]
    is_high = result["prediction"] == ">50K"

    st.divider()
    left, right = st.columns([1, 1])
    with left:
        if is_high:
            st.success("### Prediction: **> 50K** 💰")
        else:
            st.info("### Prediction: **≤ 50K**")
    with right:
        st.metric("Probability of > 50K", f"{proba:.1%}")

    st.progress(proba)
    st.caption(
        "Decision threshold 0.5. This probability is the model's `predict_proba` "
        "output for the `>50K` class."
    )

    with st.expander("Inputs used (passed to the model)"):
        st.json(result["used_features"])
