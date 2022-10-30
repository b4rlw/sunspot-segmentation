# from kedro.framework.hooks import hook_impl


# class Hooks:
#     @hook_impl
#     def after_context_created(self, context):
#         self.project_path = context.project_path

#     @hook_impl
#     def after_catalog_created(self, catalog):
#         catalog.add(...)  # use self.project_path here


# import logging
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

#     @property
#     def _logger(self):
#         return logging.getLogger(self.__class__.__name__)

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
