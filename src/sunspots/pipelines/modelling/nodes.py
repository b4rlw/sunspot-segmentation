"""
This is a boilerplate pipeline 'modelling'
generated using Kedro 0.18.3
"""
import logging
from collections import Counter
import pandas as pd
from sklearn import svm
from sklearn.base import BaseEstimator
from imblearn.over_sampling import RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler


def resample_data(
    features: pd.DataFrame, labels: pd.Series, resample_options: dict
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Resamples the training data in accordance with specified parameters.
    """
    mode = resample_options["mode"]
    ratio = resample_options["ratio"]
    logger = logging.getLogger(__name__)
    logger.info(f"Initial counts: {Counter(labels)}")

    if mode == "oversample":
        over = RandomOverSampler(sampling_strategy=ratio)
        X, y = over.fit_resample(features.values, labels.values)
        logger.info(f" Post oversample counts: {Counter(y)}")

    if mode == "undersample":
        under = RandomUnderSampler(sampling_strategy=ratio)
        X, y = under.fit_resample(features.values, labels.values)
        logger.info(f"Post undersample counts: {Counter(y)}\n")

    return pd.DataFrame(X, columns=features.columns), pd.Series(y, name=labels.name)


def train_svm(X_train: pd.DataFrame, y_train: pd.Series) -> BaseEstimator:
    """
    Trains a support vector machine.
    """
    model = svm.SVC()
    model.fit(X_train, y_train)
    return model
