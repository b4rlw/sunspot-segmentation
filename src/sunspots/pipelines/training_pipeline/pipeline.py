"""
This is a boilerplate pipeline 'training_pipeline'
generated using Kedro 0.18.3
"""

from kedro.pipeline import Pipeline, node, pipeline

from sunspots.pipelines.data_ingestion import pipeline as di
from sunspots.pipelines.label_extraction import pipeline as le
from sunspots.pipelines.feature_engineering import pipeline as fe
from sunspots.pipelines.modelling import pipeline as md
from sunspots.pipelines.evaluation import pipeline as ev
from sunspots.pipelines.prediction import pipeline as pr

from .nodes import (
    create_master_table,
    split_data,
)


def create_pipeline() -> Pipeline:
    """
    Create pipeline using the specified nodes.
    """
    ingestion_pipeline = pipeline(
        pipe=di.create_pipeline(),
        inputs={"dataset": "training_dataset"},
        outputs={"dataset_chunk_features": "image_chunk_features"},
        parameters={"params:override_me": "params:box_size"},
        namespace="data_ingestion",
    )
    labels_pipeline = pipeline(
        pipe=le.create_pipeline(),
        inputs={"sunspot_selector"},
        outputs={"image_chunk_labels"},
        parameters={"params:override_me": "params:box_size"},
        namespace="label_extraction",
    )
    fit_engineer_features_pipeline = fe.create_fit_pipeline()
    modelling_pipeline = md.create_pipeline()
    evaluation_pipeline = ev.create_pipeline()

    prediction_pipeline = pipeline(
        pipe=pr.create_pipeline(),
        inputs={"model", "engineered_features"},
        outputs={"training_targets"},
        parameters={"params:override_me": "params:box_size"},
        namespace="prediction",
    )
    helper_pipe = pipeline(
        [
            node(
                func=create_master_table,
                inputs=["engineered_features", "image_chunk_labels"],
                outputs="master_table",
                name="create_master_table",
            ),
            node(
                func=split_data,
                inputs=["master_table", "params:split_options"],
                outputs=["X_train", "X_test", "y_train", "y_test"],
                name="split_data",
            ),
        ]
    )
    return (
        ingestion_pipeline
        + labels_pipeline
        + fit_engineer_features_pipeline
        + helper_pipe
        + modelling_pipeline
        + evaluation_pipeline
        + prediction_pipeline
    )
