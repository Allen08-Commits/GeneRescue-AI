
import streamlit as st
import pandas as pd
import plotly.express as px

from core.data_loader import load_csv
from core.crop_prediction import train_crop_model


def show_crop_predictor():

    # ---------------- PAGE HEADER ----------------

    st.title("📊 Crop Improvement Predictor")

    st.write(
        "Train a machine-learning model using labeled crop "
        "trait datasets."
    )

    # ---------------- FILE UPLOAD ----------------

    uploaded_file = st.file_uploader(
        "Upload labeled crop dataset (CSV)",
        type=["csv"],
        key="crop_prediction"
    )

    if uploaded_file is None:

        st.markdown(
            """
            <div style="
                background-color:#E8F3EA;
                border:1px solid #B7D6BE;
                border-left:5px solid #32865B;
                border-radius:10px;
                padding:18px;
            ">
                <p style="color:#174C35;font-weight:600;margin:0;">
                    📊 Upload a labeled crop dataset to train
                    a prediction model.
                </p>
                <p style="color:#52675A;font-size:13px;margin:6px 0 0 0;">
                    Upload a CSV containing crop characteristics
                    and a target classification column.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        return

    # ---------------- DATA LOADING ----------------

    try:

        data = load_csv(uploaded_file)

        if not isinstance(data, pd.DataFrame) or data.empty:
            st.warning("The uploaded dataset is empty or invalid.")
            return

        st.markdown(
            """
            <div style="
                background-color:#E5F3E9;
                border:1px solid #A9D2B5;
                border-radius:9px;
                padding:13px;
            ">
                <span style="color:#174C35;font-weight:600;">
                    ✓ Crop dataset loaded successfully.
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ---------------- DATASET PREVIEW ----------------

        st.subheader("Dataset Preview")

        st.dataframe(
            data.head(20),
            use_container_width=True,
            hide_index=True
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Records", len(data))

        with col2:
            st.metric("Total Features", len(data.columns))

        # ---------------- TARGET SELECTION ----------------

        st.subheader("Model Configuration")

        target = st.selectbox(
            "Select target column",
            data.columns,
            key="crop_target"
        )

        st.caption(
            "Choose the column containing the class or outcome "
            "that the model should predict."
        )

        if st.button(
            "🚀 Train Prediction Model",
            use_container_width=True
        ):

            with st.spinner("Training machine-learning model..."):

                results = train_crop_model(
                    data,
                    target
                )

                st.session_state["crop_model_results"] = results
                st.session_state["crop_model_target"] = target

        # ---------------- DISPLAY MODEL RESULTS ----------------

        results = st.session_state.get("crop_model_results")

        if results is None:
            return

        st.divider()

        st.subheader("Model Training Results")

        st.markdown(
            """
            <div style="
                background-color:#E5F3E9;
                border:1px solid #A9D2B5;
                border-radius:9px;
                padding:13px;
                margin-bottom:15px;
            ">
                <span style="color:#174C35;font-weight:600;">
                    ✓ Model training completed.
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ---------------- ACCURACY ----------------

        accuracy = float(results["accuracy"])

        st.metric(
            "Test Accuracy",
            f"{accuracy:.1f}%"
        )

        # ---------------- FEATURE IMPORTANCE ----------------

        st.subheader("Feature Importance")

        importance = results["feature_importance"].copy()

        if not importance.empty:

            importance["Importance"] = pd.to_numeric(
                importance["Importance"],
                errors="coerce"
            )

            importance = importance.dropna(
                subset=["Importance", "Feature"]
            )

            importance = importance.sort_values(
                "Importance",
                ascending=False
            ).head(15)

            if not importance.empty:

                fig = px.bar(
                    importance,
                    x="Importance",
                    y="Feature",
                    orientation="h",
                    text="Importance",
                    title="Top Predictive Features",
                    color="Importance",
                    color_continuous_scale=[
                        "#B7DCC0",
                        "#32865B",
                        "#174C35"
                    ]
                )

                fig.update_traces(
                    texttemplate="%{text:.3f}",
                    textposition="outside",
                    cliponaxis=False
                )

                fig.update_layout(
                    height=max(380, len(importance) * 42),
                    template="plotly_white",
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF",
                    font=dict(
                        family="Arial",
                        size=12,
                        color="#344B3D"
                    ),
                    title_font=dict(
                        size=18,
                        color="#174C35"
                    ),
                    xaxis_title="Feature Importance",
                    yaxis_title="",
                    yaxis=dict(
                        categoryorder="total ascending"
                    ),
                    coloraxis_showscale=False,
                    margin=dict(
                        l=30,
                        r=45,
                        t=65,
                        b=45
                    )
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False}
                )

        else:
            st.info("Feature importance is unavailable.")

        # ---------------- CLASSIFICATION PERFORMANCE ----------------

        st.subheader("Classification Performance")

        report = results["classification_report"]

        if isinstance(report, dict):

            report_rows = []

            for class_name, metrics in report.items():

                if isinstance(metrics, dict):

                    report_rows.append({
                        "Class": class_name,
                        "Precision": metrics.get("precision"),
                        "Recall": metrics.get("recall"),
                        "F1-Score": metrics.get("f1-score"),
                        "Support": metrics.get("support")
                    })

            if report_rows:

                report_df = pd.DataFrame(report_rows)

                st.dataframe(
                    report_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Precision": st.column_config.NumberColumn(
                            format="%.3f"
                        ),
                        "Recall": st.column_config.NumberColumn(
                            format="%.3f"
                        ),
                        "F1-Score": st.column_config.NumberColumn(
                            format="%.3f"
                        )
                    }
                )

        # ---------------- CONFUSION MATRIX ----------------

        st.subheader("Confusion Matrix")

        matrix = pd.DataFrame(
            results["confusion_matrix"],
            index=results["classes"],
            columns=results["classes"]
        )

        matrix.index.name = "Actual / Predicted"

        st.dataframe(
            matrix,
            use_container_width=True
        )

        # ---------------- SCIENTIFIC INTERPRETATION ----------------

        test_samples = int(matrix.to_numpy().sum())

        st.markdown(
            f"""
            <div style="
                background-color:#FFF7E6;
                border:1px solid #E8C982;
                border-left:5px solid #D69E28;
                border-radius:10px;
                padding:16px;
                margin-top:18px;
            ">
                <p style="
                    color:#76520C;
                    font-weight:700;
                    margin:0 0 7px 0;
                ">
                    Scientific Interpretation Notice
                </p>
                <p style="
                    color:#604A20;
                    font-size:14px;
                    margin:0;
                    line-height:1.6;
                ">
                    The reported accuracy is based on
                    {test_samples} held-out test samples.
                    A small test set may produce unstable
                    performance estimates. Results depend on
                    dataset quality, sample representativeness
                    and model validation. Predictions do not
                    establish biological causality or actual
                    crop improvement.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            "Model target: " +
            str(st.session_state.get("crop_model_target", target))
        )

    except Exception as e:

        st.error(f"Prediction model error: {e}")

        st.caption(
            "Check the CSV columns, missing values and target labels."
        )
