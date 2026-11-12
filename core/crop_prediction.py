
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
from sklearn.preprocessing import LabelEncoder


def train_crop_model(data, target_column):
    """
    Train a Random Forest model using a labeled crop dataset.
    Returns the trained model and evaluation information.
    """

    if target_column not in data.columns:
        raise ValueError("Target column not found in dataset.")

    df = data.copy().dropna(subset=[target_column])

    if len(df) < 10:
        raise ValueError("At least 10 labeled records are required.")

    y = df[target_column].astype(str)

    if y.nunique() < 2:
        raise ValueError("Target must contain at least two classes.")

    X = df.drop(columns=[target_column])

    # Remove columns that cannot be used as model features.
    X = X.drop(
        columns=[
            col for col in X.columns
            if col.lower() in ["id", "gene_id", "sequence_id", "name"]
        ],
        errors="ignore"
    )

    # Convert categorical features into numerical columns.
    X = pd.get_dummies(X, dummy_na=True)

    if X.shape[1] == 0:
        raise ValueError("No usable feature columns found.")

    X = X.apply(pd.to_numeric, errors="coerce")
    X = X.replace([float("inf"), float("-inf")], float("nan"))
    X = X.fillna(X.median()).fillna(0)

    if y.value_counts().min() < 2:
        raise ValueError(
            "Each target class must contain at least two records."
        )

    stratify = y if y.value_counts().min() >= 2 else None

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=stratify
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

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
        "Feature": X.columns,
        "Importance": model.feature_importances_
    }).sort_values(
        "Importance",
        ascending=False
    )

    return {
        "model": model,
        "features": list(X.columns),
        "accuracy": round(accuracy * 100, 2),
        "classification_report": report,
        "confusion_matrix": matrix,
        "feature_importance": importance,
        "classes": list(model.classes_)
    }


def predict_crop_trait(model_results, new_data):
    """Predict trait classes for new records."""

    model = model_results["model"]
    features = model_results["features"]

    X = pd.get_dummies(new_data.copy(), dummy_na=True)
    X = X.reindex(columns=features, fill_value=0)

    X = X.apply(pd.to_numeric, errors="coerce")
    X = X.replace([float("inf"), float("-inf")], float("nan"))
    X = X.fillna(0)

    predictions = model.predict(X)

    probabilities = model.predict_proba(X)

    results = pd.DataFrame({
        "Predicted_Trait": predictions,
        "Model_Confidence_Percentage": (
            probabilities.max(axis=1) * 100
        ).round(2)
    })

    return results

