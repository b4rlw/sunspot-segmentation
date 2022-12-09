"""
This is a boilerplate pipeline 'feature_engineering'
generated using Kedro 0.18.3
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import select_features, fit_scaler, scale_features


def create_fit_pipeline() -> Pipeline:
    """
    This function selects from the dataframe the features specified in the
    parameters.yml. A standard scaler is created and fitted to that feature set.
    The features are then transformed by the scaler and returned.
    """
    fit_engineer_features_pipeline = pipeline(
        [
            node(
                func=select_features,
                inputs=["image_patch_features", "params:features"],
                outputs="chosen_features",
                name="select_features",
            ),
            node(
                func=fit_scaler,
                inputs="chosen_features",
                outputs="scaler",
                name="fit_scaler",
            ),
            node(
                func=scale_features,
                inputs=["chosen_features", "scaler"],
                outputs="engineered_features",
                name="scale_features",
            ),
        ]
    )
    return pipeline(
        pipe=fit_engineer_features_pipeline,
        inputs={"image_patch_features"},
        outputs={"engineered_features"},
        parameters={"params:features"},
        namespace="fit_engineer_features",
    )


def create_pipeline() -> Pipeline:
    """
    This function selects from the dataframe the features specified in the
    parameters.yml.
    The features are then transformed by the scaler and returned.
    """
    return pipeline(
        [
            node(
                func=select_features,
                inputs=["image_patch_features", "params:features"],
                outputs="chosen_features",
                name="select_features",
            ),
            node(
                func=scale_features,
                inputs=["chosen_features", "scaler"],
                outputs="engineered_features",
                name="scale_features",
            ),
        ]
    )
