"""Project pipelines."""
import re
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

    datasets = ["20140910Timeseries", "20150910Timeseries"]

    exe_pipes = {}
    for dataset in datasets:
        start_date = re.findall("(\d+)", dataset)[0]
        exe_pipes[f"{start_date}_execution"] = pipeline(
            pipe=ep.create_pipeline(),
            inputs={"Timeseries": dataset},
            outputs={
                "region_submaps": f"{start_date}_region_submaps",
                "targets": f"{start_date}_targets",
            },
        )
    return pipelines | exe_pipes
