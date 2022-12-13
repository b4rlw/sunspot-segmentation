"""Project pipelines."""
import re
import yaml
from yaml.loader import SafeLoader
from typing import Dict
from kedro.pipeline import Pipeline, pipeline
from sunspots.pipelines.training_pipeline import pipeline as tp
from sunspots.pipelines.execution_pipeline import pipeline as ep


def register_pipelines() -> Dict[str, Pipeline]:
    """
    Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """
    training_pipeline = tp.create_pipeline()
    execution_pipeline = ep.create_pipeline()
    pipelines = {
        "__default__": training_pipeline,
        "training_pipeline": training_pipeline,
        "execution_pipeline": execution_pipeline,
    }

    with open("conf/base/parameters.yml") as f:
        datasets = yaml.load(f, Loader=SafeLoader)["datasets"]

    execution_pipes = {}
    for dataset in datasets.keys():
        start_date = re.findall("(\d+)", dataset)[0]
        execution_pipes[f"{start_date}_execution"] = pipeline(
            pipe=ep.create_pipeline(),
            inputs={"timeseries": f"{start_date}Timeseries"},
            outputs={
                "targets": f"{start_date}_targets",
                "region_submaps": f"{start_date}_region_submaps",
                "stara.segmentations": f"{start_date}_segmentations",
                "segmentation_masks": f"{start_date}_segmentation_masks",
                "region_dataframes": f"{start_date}_region_dataframes",
            },
        )
    return pipelines | execution_pipes
