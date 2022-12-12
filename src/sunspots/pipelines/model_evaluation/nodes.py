"""
This is a boilerplate pipeline 'model_evaluation'
generated using Kedro 0.18.3
"""
import logging
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report


def predict_evaluation_targets(
    model: BaseEstimator, features: pd.DataFrame
) -> np.ndarray:
    """
    Predicts targets for evaluation.
    """
    return model.predict(features.values)


def evaluate_model(
    labels: pd.Series,
    targets: np.ndarray,
) -> None:
    """
    Evaluates the quality of a passed model.
    """
    logger = logging.getLogger(__name__)
    logger.info(
        f"Accuracy:\n{accuracy_score(labels, targets):.3f}\n"
        f"Confusion Matrix:\n{confusion_matrix(labels, targets)}\n"
        f"Classification Report:\n{classification_report(labels, targets)}"
    )
