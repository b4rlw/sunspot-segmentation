import re
import logging
from kedro.config import ConfigLoader
from kedro.framework.project import settings
from kedro.framework.hooks import hook_impl
from kedro.io import PartitionedDataSet
from sunspots.extras.datasets.sunpy_datasets import SunPyMapDataSet
from kedro.extras.datasets.pickle.pickle_dataset import PickleDataSet
from kedro.extras.datasets.pandas.parquet_dataset import ParquetDataSet


class ProjectHooks:
    cloud_keys = "dev_s3"

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

    def add_pickle_dataset(self, name, folder, layer=None):
        self.catalog.add(
            data_set_name=name,
            data_set=PickleDataSet(
                filepath=f"s3://sunspots/data/{folder}/{name}.pickle",
                credentials=self._get_credentials(self.cloud_keys),
            ),
            replace=True,
        )
        if layer:
            self.catalog.layers[layer].add(name)
        self._logger.info(f"Added dataset '{name}' to the data catalog.")

    def add_partitioned_dataset(self, name, folder, set, suffix, layer=None):
        self.catalog.add(
            data_set_name=name,
            data_set=PartitionedDataSet(
                path=f"s3://sunspots/data/{folder}/{name}",
                dataset=set,
                filename_suffix=suffix,
                credentials=self._get_credentials(self.cloud_keys),
                overwrite=True,
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
            self.add_partitioned_dataset(
                name=f"{start_date}Timeseries",
                folder="01_raw",
                set=SunPyMapDataSet,
                suffix=".fits",
                layer="Raw",
            )
            self.add_pickle_dataset(
                name=f"{start_date}_targets",
                folder="07_model_output",
                layer="Model Output",
            )
            self.add_partitioned_dataset(
                name=f"{start_date}_region_submaps",
                folder="07_model_output",
                set=SunPyMapDataSet,
                suffix=".fits",
                layer="Model Output",
            )
            self.add_partitioned_dataset(
                name=f"{start_date}_segmentations",
                folder="08_reporting",
                set=PickleDataSet,
                suffix=".pickle",
                layer="Reporting",
            )
            self.add_partitioned_dataset(
                name=f"{start_date}_segmentation_masks",
                folder="08_reporting",
                set=PickleDataSet,
                suffix=".pickle",
                layer="Reporting",
            )
            self.add_partitioned_dataset(
                name=f"{start_date}_region_dataframes",
                folder="08_reporting",
                set=ParquetDataSet,
                suffix=".parquet",
                layer="Reporting",
            )
