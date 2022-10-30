"""
This is a boilerplate pipeline 'execution_pipeline'
generated using Kedro 0.18.3
"""

from kedro.pipeline import Pipeline, node, pipeline

from sunspots.pipelines.data_ingestion import pipeline as di
from sunspots.pipelines.feature_engineering import pipeline as fe
from sunspots.pipelines.prediction import pipeline as pr
from sunspots.pipelines.region_extraction import pipeline as re


def create_pipeline() -> Pipeline:
    """
    A pipeline to visually validate the performance of a trained model by
    processing and plotting previously unseen SunPy maps.
    """
    data_ingestion_pipeline = pipeline(
        pipe=di.create_pipeline(),
        inputs={"dataset": "Timeseries"},
        outputs={"dataset_chunk_features": "chunk_features"},
        parameters={"params:override_me": "params:box_size"},
        namespace="data_ingestion",
    )
    feature_engineering_pipeline = pipeline(
        pipe=fe.create_pipeline(),
        inputs={"image_chunk_features": "chunk_features"},
        outputs={"engineered_features": "engineered_features"},
        parameters={"params:features"},
        namespace="feature_engineering",
    )
    prediction_pipeline = pipeline(
        pipe=pr.create_pipeline(),
        inputs={"engineered_features": "engineered_features"},
        outputs={"training_targets": "targets"},
        parameters={"params:override_me": "params:box_size"},
        namespace="target_prediction",
    )
    region_extraction_pipeline = pipeline(
        pipe=re.create_pipeline(),
        inputs={"dataset": "Timeseries", "targets": "targets"},
        outputs={"region_submaps": "region_submaps"},
        parameters={"params:override_me": "params:box_size"},
        namespace="region_extraction",
    )
    return (
        data_ingestion_pipeline
        + feature_engineering_pipeline
        + prediction_pipeline
        + region_extraction_pipeline
    )
