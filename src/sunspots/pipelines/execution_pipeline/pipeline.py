"""
This is a boilerplate pipeline 'execution_pipeline'
generated using Kedro 0.18.3
"""

from kedro.pipeline import Pipeline, pipeline

from sunspots.pipelines.data_ingestion import pipeline as di
from sunspots.pipelines.feature_engineering import pipeline as fe
from sunspots.pipelines.prediction import pipeline as pr
from sunspots.pipelines.region_extraction import pipeline as re
from sunspots.pipelines.STARA import pipeline as st


def create_pipeline() -> Pipeline:
    """
    A pipeline to visually validate the performance of a trained model by
    processing and plotting previously unseen SunPy maps.
    """
    data_ingestion_pipeline = pipeline(
        pipe=di.create_pipeline(),
        inputs={"dataset": "timeseries"},
        outputs={"image_patch_features": "patch_features"},
        parameters={"params:override_me": "params:box_size"},
        namespace="data_ingestion",
    )
    feature_engineering_pipeline = pipeline(
        pipe=fe.create_pipeline(),
        inputs={"image_patch_features": "patch_features"},
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
        inputs={"dataset": "timeseries", "targets": "targets"},
        outputs={"region_submaps": "region_submaps"},
        parameters={"params:override_me": "params:box_size"},
        namespace="region_extraction",
    )
    stara_analysis_pipeline = pipeline(
        pipe=st.create_pipeline(),
        inputs={"region_submaps"},
        outputs={"segmentations", "segmentation_masks", "region_dataframes"},
        parameters={"params:override_me": "params:stara"},
        namespace="STARA",
    )
    return (
        data_ingestion_pipeline
        + feature_engineering_pipeline
        + prediction_pipeline
        + region_extraction_pipeline
        + stara_analysis_pipeline
    )
