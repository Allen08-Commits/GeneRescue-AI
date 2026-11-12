
import streamlit as st
import pandas as pd
import plotly.express as px

from core.data_loader import load_csv
from core.crop_prediction import train_crop_model


def show_crop_predictor():

    st.title("📊 Crop Improvement Predictor")

    st.write(
        "Train a machine-learning model using labeled crop "
        "trait datasets."
    )

    uploaded_file = st.file_uploader(
        "Upload labeled crop dataset (CSV)",
        type=["csv"],
        key="crop_prediction"
    )

    if uploaded_file:

        try:
            data = load_csv(uploaded_file)

            st.subheader("Dataset Preview")

            st.dataframe(
                data.head(20),
                use_container_width=True
            )

            target = st.selectbox(
                "Select target column",
                data.columns
            )

            if st.button("Train Prediction Model"):

                with st.spinner("Training model..."):

                    results = train_crop_model(
                        data,
                        target
                    )

                st.session_state["crop_model_results"] = results

                st.success("Model training completed!")

                st.metric(
                    "Test Accuracy",
                    f"{results['accuracy']}%"
                )

                st.subheader("Feature Importance")

                importance = results["feature_importance"]

                fig = px.bar(
                    importance.head(15),
                    x="Importance",
                    y="Feature",
                    orientation="h",
                    title="Top Predictive Features"
                )

                fig.update_layout(yaxis={"categoryorder": "total ascending"})

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                st.subheader("Classification Performance")

                st.json(results["classification_report"])

                matrix = pd.DataFrame(
                    results["confusion_matrix"],
                    index=results["classes"],
                    columns=results["classes"]
                )

                st.write("Confusion Matrix")
                st.dataframe(matrix)

                st.caption(
                    "Accuracy reflects held-out dataset performance. "
                    "It does not prove biological causality or actual "
                    "crop improvement."
                )

        except Exception as e:
            st.error(f"Prediction model error: {e}")

    else:
        st.info(
            "Upload a labeled crop dataset to train a prediction model."
        )

