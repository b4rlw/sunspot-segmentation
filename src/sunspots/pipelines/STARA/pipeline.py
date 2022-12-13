"""
This is a boilerplate pipeline 'STARA'
generated using Kedro 0.18.3
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import stara_process_regions, get_segmentation_masks, get_region_dataframes


def create_pipeline(**kwargs) -> Pipeline:
    stara_pipeline = pipeline(
        [
            node(
                func=stara_process_regions,
                inputs=["region_submaps", "params:stara"],
                outputs="segmentations",
                name="stara_process_regions",
            ),
            node(
                func=get_segmentation_masks,
                inputs="segmentations",
                outputs="segmentation_masks",
                name="get_segmentation_masks",
            ),
            node(
                func=get_region_dataframes,
                inputs=["segmentations", "region_submaps"],
                outputs="region_dataframes",
                name="get_region_dataframes",
            ),
        ]
    )
    return pipeline(
        pipe=stara_pipeline,
        inputs={"region_submaps"},
        outputs={"segmentation_masks", "region_dataframes"},
        parameters={"params:stara"},
        namespace="stara",
    )
