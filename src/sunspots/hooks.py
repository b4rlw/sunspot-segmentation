import re
import logging
from kedro.config import ConfigLoader
from kedro.framework.project import settings
from kedro.framework.hooks import hook_impl
from kedro.io import PartitionedDataSet
from sunspots.extras.datasets.sunpy_datasets import SunPyMapDataSet
from kedro.extras.datasets.pickle.pickle_dataset import PickleDataSet


class ProjectHooks:
    @property
    def _logger(self):
        return logging.getLogger(__name__)

    @hook_impl
    def after_context_created(self, context):
        self.project_path = context.project_path
        self._logger.info(f"Project path: {self.project_path}")

    def _get_credentials(self, key):
        conf_path = f"{self.project_path}/{settings.CONF_SOURCE}"
        conf_loader = ConfigLoader(conf_source=conf_path, env="local")
        return conf_loader.get("credentials*")[key]

    def add_sunpy_dataset(self, name, folder, layer=None):
        self.catalog.add(
            data_set_name=name,
            data_set=PartitionedDataSet(
                path=f"s3://sunspots/data/{folder}/{name}",
                dataset=SunPyMapDataSet,
                filename_suffix=".fits",
                credentials=self._get_credentials("dev_s3"),
                overwrite=True,
            ),
            replace=True,
        )
        if layer:
            self.catalog.layers[layer].add(name)
        self._logger.info(f"Added dataset '{name}' to the data catalog.")

    def add_pickle_dataset(self, name, folder, layer=None):
        self.catalog.add(
            data_set_name=name,
            data_set=PickleDataSet(
                filepath=f"s3://sunspots/data/{folder}/{name}",
                credentials=self._get_credentials("dev_s3"),
            ),
            replace=True,
        )
        if layer:
            self.catalog.layers[layer].add(name)
        self._logger.info(f"Added dataset '{name}' to the data catalog.")

    @hook_impl
    def after_catalog_created(self, catalog):
        self.catalog = catalog
        datasets = self.catalog.load("params:datasets")
        for dataset in datasets.keys():
            start_date = re.findall(r"(\d+)", dataset)[0]
            self.add_sunpy_dataset(
                name=f"{start_date}Timeseries", folder="01_raw", layer="Raw"
            )
            self.add_pickle_dataset(
                name=f"{start_date}_targets",
                folder="07_model_output",
                layer="Model Output",
            )
            self.add_sunpy_dataset(
                name=f"{start_date}_region_submaps",
                folder="07_model_output",
                layer="Model Output",
            )


# from os import path
# from typing import Any

# from kedro.framework.context import KedroContext
# from kedro.extras.datasets.dask import ParquetDataSet
# from kedro.extras.datasets.pickle import PickleDataSet
# from kedro.io import DataCatalog, Version
# from kedro.framework.hooks import hook_impl


# class AddDatasetsForViewsHook:
#     def __init__(
#         self,
#         your_params: dict[str, list[str]],
#     ) -> None:
#         self.your_params = your_params

#     @hook_impl
#     def after_context_created(
#         self,
#         context: KedroContext,
#     ) -> None:
#         # Base location is added to the config by templated config loader
#         self.base_location = context.params["base_location"]


#     def get_version(self, name: str, versioned: bool):
#         load_version = (
#             self.load_versions.get(name, None) if self.load_versions else None
#         )
#         if versioned:
#             return Version(load_version, self.save_version)
#         return None

#     def add_set(self, layer, name, path_seg, versioned=False):
#         self.catalog.add(
#             name,
#             ParquetDataSet(
#                 path.join(
#                     self.base_location,
#                     *path_seg[:-1],
#                     path_seg[-1] + ".pq",
#                 ),
#                 save_args=self.pq_save_args,
#                 version=self.get_version(name, versioned),
#             ),
#         )
#         if layer:
#             self.catalog.layers[layer].add(name)

#     def add_pkl(self, layer, name, path_seg, versioned=False):
#         self.catalog.add(
#             name,
#             PickleDataSet(
#                 path.join(
#                     self.base_location,
#                     *path_seg[:-1],
#                     path_seg[-1] + ".pkl",
#                 ),
#                 version=self.get_version(name, versioned),
#             ),
#         )
#         if layer:
#             self.catalog.layers[layer].add(name)

#     @hook_impl
#     def after_catalog_created(
#         self,
#         catalog: DataCatalog,
#         conf_catalog: dict[str, Any],
#         conf_creds: dict[str, Any],
#         save_version: str,
#         load_versions: dict[str, str],
#     ) -> None:
#         # Fixes a bug in my code with pyarrow timestamp limits
#         self.pq_save_args = {
#             "coerce_timestamps": "us",
#             "allow_truncated_timestamps": True,
#         }
#         self.catalog = catalog
#         self.save_version = save_version
#         self.load_versions = load_versions

#         for name, table in self.your_params.items():
#             #
#             # Add view datasets
#             #
#             self.add_pkl(
#                 "metadata",
#                 f"{view}.view.metadata",
#                 ["views", "metadata", view],
#             )
