"""
This is a boilerplate pipeline 'model_evaluation'
generated using Kedro 0.18.3
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import predict_evaluation_targets, evaluate_model


def create_pipeline(**kwargs) -> Pipeline:
    evaluation_pipeline = pipeline(
        [
            node(
                func=predict_evaluation_targets,
                inputs=["model", "X_test"],
                outputs="evaluation_targets",
                name="predict_evaluation_targets",
            ),
            node(
                func=evaluate_model,
                inputs=["y_test", "evaluation_targets"],
                outputs=None,
                name="evaluate_model",
            ),
        ]
    )
    return pipeline(
        pipe=evaluation_pipeline,
        inputs={"model", "X_test", "y_test"},
        namespace="model_evaluation",
    )
