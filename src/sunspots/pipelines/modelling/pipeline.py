"""
This is a boilerplate pipeline 'modelling'
generated using Kedro 0.18.3
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import resample_data, train_svm


def create_pipeline(**kwargs) -> Pipeline:
    modelling_pipeline = pipeline(
        [
            node(
                func=resample_data,
                inputs=["X_train", "y_train", "params:resample_options"],
                outputs=["X_train_resampled", "y_train_resampled"],
                name="resample_data",
            ),
            node(
                func=train_svm,
                inputs=["X_train_resampled", "y_train_resampled"],
                outputs="model",
                name="train_svm",
            ),
        ]
    )
    return pipeline(
        pipe=modelling_pipeline,
        inputs={"X_train", "y_train"},
        outputs={"model"},
        # parameters={""},
        namespace="modelling",
    )
