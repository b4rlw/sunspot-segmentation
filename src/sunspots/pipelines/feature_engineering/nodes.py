"""
This is a boilerplate pipeline 'feature_engineering'
generated using Kedro 0.18.3
"""
import pandas as pd
from sklearn.preprocessing import StandardScaler


def select_features(data: pd.DataFrame, column_names: list[str]) -> pd.DataFrame:
    """
    This function accepts a pandas DataFrame as well as a list of columns to
    keep in scope. A DataFrame limited to the provided feature names is
    returned.
    """
    return data[column_names]


def fit_scaler(features: pd.DataFrame) -> StandardScaler:
    """
    Creates a standard scaler and fits it to a given set of features. The
    fitted scaler is then returned.
    """
    scaler = StandardScaler()
    scaler.fit(features.values)
    return scaler


def scale_features(features: pd.DataFrame, scaler: StandardScaler) -> pd.DataFrame:
    """
    This function scales a feature array in accordance with a supplied, fitted
    scaler.
    """
    scaled_features = scaler.transform(features.values)
    return pd.DataFrame(
        scaled_features,
        index=features.index,
        columns=features.columns,
    )
