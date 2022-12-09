"""
This is a boilerplate pipeline 'label_extraction'
generated using Kedro 0.18.3
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import generate_label_table


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=generate_label_table,
                inputs=["sunspot_selector", "params:override_me"],
                outputs="image_patch_labels",
                name="generate_label_table",
            ),
        ]
    )
