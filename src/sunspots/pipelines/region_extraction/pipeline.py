"""
This is a boilerplate pipeline 'region_extraction'
generated using Kedro 0.18.3
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import get_region_coords, extract_regions


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=get_region_coords,
                inputs=["dataset", "targets", "params:override_me"],
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
