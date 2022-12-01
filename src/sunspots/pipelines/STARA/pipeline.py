"""
This is a boilerplate pipeline 'STARA'
generated using Kedro 0.18.3
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import process_extractions


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=process_extractions,
                inputs=["region_submaps", "params:override_me"],
                outputs=["segmentations", "segmentation_masks", "region_dataframes"],
                name="process_extractions",
            ),
        ]
    )
