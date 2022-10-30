"""
This is a boilerplate pipeline 'prediction'
generated using Kedro 0.18.3
"""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator


def predict_dataset_targets(
    model: BaseEstimator, features: pd.DataFrame, box_size: int
) -> np.ndarray:
    """
    Predicts targets. Reshapes targets into a list of masks, each of which can
    be over-plotted on the orignal Map files for visually inspecting the
    performance of the model.
    """
    targets = model.predict(features.values)
    num_files = int(len(targets) / box_size / box_size)
    return targets.reshape(num_files, box_size, box_size)
