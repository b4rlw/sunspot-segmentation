"""
This is a boilerplate pipeline 'data_ingestion'
generated using Kedro 0.18.3
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import generate_feature_table


def create_pipeline(**kwargs) -> Pipeline:
    ingestion_pipeline = pipeline(
        [
            node(
                func=generate_feature_table,
                inputs=["dataset", "params:override_me"],
                outputs="dataset_chunk_features",
                name="generate_feature_table",
            ),
        ]
    )
    return ingestion_pipeline
