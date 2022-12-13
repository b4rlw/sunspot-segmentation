"""
This is a boilerplate pipeline 'region_extraction'
generated using Kedro 0.18.3
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import get_region_coords, extract_regions


def create_pipeline(**kwargs) -> Pipeline:
    region_extraction_pipeline = pipeline(
        [
            node(
                func=get_region_coords,
                inputs=["dataset", "targets", "params:box_size"],
                outputs="region_coords",
                name="get_region_coords",
            ),
            node(
                func=extract_regions,
                inputs=["dataset", "region_coords"],
                outputs="region_submaps",
                name="extract_regions",
            ),
        ]
    )
    return pipeline(
        pipe=region_extraction_pipeline,
        inputs={"dataset": "timeseries", "targets": "targets"},
        outputs={"region_submaps"},
        parameters={"params:box_size"},
        namespace="region_extraction",
    )
