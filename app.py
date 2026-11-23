
import math
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


def _prepare_features(
    data,
    categorical_columns,
    numeric_medians,
    feature_columns=None
):
    """
    Prepare numeric and categorical features consistently
    for both training and prediction.
    """

    X = data.copy()

    # Ensure all expected input columns exist.
    for column in categorical_columns:
        if column not in X.columns:
            X[column] = "Missing"

    for column in numeric_medians:
        if column not in X.columns:
            X[column] = np.nan

    # Clean numerical columns using training-set medians.
    for column, median in numeric_medians.items():

        X[column] = pd.to_numeric(
            X[column],
            errors="coerce"
        )

        X[column] = X[column].replace(
            [np.inf, -np.inf],
            np.nan
        )

        X[column] = X[column].fillna(median)

    # Handle missing categorical values explicitly.
    for column in categorical_columns:

        X[column] = (
            X[column]
            .fillna("Missing")
            .astype(str)
        )

    # One-hot encode categorical columns.
    X = pd.get_dummies(
        X,
        columns=categorical_columns,
        dummy_na=False
    )

    # Match the exact training feature structure.
    if feature_columns is not None:
        X = X.reindex(
            columns=feature_columns,
            fill_value=0
        )

    X = X.apply(
        pd.to_numeric,
        errors="coerce"
    )

    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    ).fillna(0)

    return X


def train_crop_model(data, target_column):
    """
    Train a Random Forest model using a labeled crop dataset.
    Returns the trained model and evaluation information.
    """

    if target_column not in data.columns:
        raise ValueError("Target column not found in dataset.")

    df = data.copy()

    # Remove records without target labels.
    df = df.dropna(subset=[target_column])

    if len(df) < 10:
        raise ValueError(
            "At least 10 labeled records are required."
        )

    y = df[target_column].astype(str)

    if y.nunique() < 2:
        raise ValueError(
            "Target must contain at least two classes."
        )

    if y.value_counts().min() < 2:
        raise ValueError(
            "Each target class must contain at least two records."
        )

    # Remove the target and identifier columns.
    X = df.drop(columns=[target_column])

    X = X.drop(
        columns=[
            col for col in X.columns
            if col.lower() in [
                "id",
                "gene_id",
                "sequence_id",
                "name"
            ]
        ],
        errors="ignore"
    )

    if X.shape[1] == 0:
        raise ValueError(
            "No usable feature columns found."
        )

    # Identify categorical and numerical columns.
    categorical_columns = list(
        X.select_dtypes(
            include=["object", "category", "bool"]
        ).columns
    )

    numeric_columns = [
        column for column in X.columns
        if column not in categorical_columns
    ]

    # Convert numerical columns and identify medians.
    # Medians will be fitted ONLY on training data.
    for column in numeric_columns:

        X[column] = pd.to_numeric(
            X[column],
            errors="coerce"
        )

        X[column] = X[column].replace(
            [np.inf, -np.inf],
            np.nan
        )

    # Determine a suitable test set size.
    number_of_classes = y.nunique()

    test_count = max(
        math.ceil(len(df) * 0.2),
        number_of_classes
    )

    if test_count > len(df) - number_of_classes:
        raise ValueError(
            "The dataset is too small for a stratified train/test split. "
            "Provide more records across the target classes."
        )

    # Split raw data BEFORE fitting preprocessing.
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_count,
        random_state=42,
        stratify=y
    )

    # Calculate numerical medians using training data only.
    numeric_medians = {}

    for column in numeric_columns:

        median = X_train_raw[column].median()

        if pd.isna(median):
            median = 0

        numeric_medians[column] = float(median)

    # Prepare training and test features consistently.
    X_train = _prepare_features(
        X_train_raw,
        categorical_columns,
        numeric_medians
    )

    X_test = _prepare_features(
        X_test_raw,
        categorical_columns,
        numeric_medians,
        feature_columns=X_train.columns
    )

    if X_train.shape[1] == 0:
        raise ValueError(
            "No usable features remain after preprocessing."
        )

    # ---------------- RANDOM FOREST MODEL ----------------

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(X_test)

    # ---------------- MODEL EVALUATION ----------------

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    report = classification_report(
        y_test,
        predictions,
        output_dict=True,
        zero_division=0
    )

    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=model.classes_
    )

    importance = pd.DataFrame({
        "Feature": X_train.columns,
        "Importance": model.feature_importances_
    }).sort_values(
        "Importance",
        ascending=False
    ).reset_index(drop=True)

    return {
        "model": model,
        "features": list(X_train.columns),
        "input_features": list(X.columns),
        "categorical_columns": categorical_columns,
        "numeric_medians": numeric_medians,
        "accuracy": round(accuracy * 100, 2),
        "classification_report": report,
        "confusion_matrix": matrix,
        "feature_importance": importance,
        "classes": list(model.classes_),
        "training_samples": len(X_train),
        "test_samples": len(X_test)
    }


def predict_crop_trait(model_results, new_data):
    """Predict trait classes for new records."""

    model = model_results["model"]

    # Retain only the original model input columns.
    input_features = model_results["input_features"]

    X = new_data.copy()

    for column in input_features:
        if column not in X.columns:
            X[column] = np.nan

    X = X[input_features]

    # Apply the same preprocessing used during training.
    X = _prepare_features(
        X,
        model_results["categorical_columns"],
        model_results["numeric_medians"],
        feature_columns=model_results["features"]
    )

    predictions = model.predict(X)

    probabilities = model.predict_proba(X)

    results = pd.DataFrame({
        "Predicted_Trait": predictions,
        "Model_Confidence_Percentage": (
            probabilities.max(axis=1) * 100
        ).round(2)
    })

    return results
