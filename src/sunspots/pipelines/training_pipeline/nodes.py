"""
This is a boilerplate pipeline 'training_pipeline'
generated using Kedro 0.18.3
"""
import pandas as pd
from sklearn.model_selection import train_test_split


def create_master_table(
    scaled_features: pd.DataFrame, labels: pd.DataFrame
) -> pd.DataFrame:
    """
    Creates a master table of the transformed image chunk features and labels.
    """
    return pd.merge(labels.label, scaled_features, left_index=True, right_index=True)


def split_data(
    data: pd.DataFrame, split_options: dict
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Splits data into features and targets training and test sets.
    Args:
        data: Data containing features and target.
        parameters: Parameters defined in parameters.yml.
    Returns:
        Split data.
    """
    target_variable = split_options["target"]
    independent_variables = [x for x in data.columns if x != target_variable]
    test_size = split_options["test_size"]
    X = data[independent_variables]
    y = data[target_variable]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)
    return X_train, X_test, y_train, y_test
