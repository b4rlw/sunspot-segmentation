"""
This is a boilerplate pipeline 'prediction'
generated using Kedro 0.18.3
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import predict_dataset_targets


def create_pipeline(**kwargs) -> Pipeline:
    prediction_pipeline = pipeline(
        [
            node(
                func=predict_dataset_targets,
                inputs=["model", "engineered_features", "params:override_me"],
                outputs="targets",
                name="predict_dataset_targets",
            ),
        ]
    )
    return prediction_pipeline
