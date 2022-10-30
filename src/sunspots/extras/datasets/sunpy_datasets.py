"""
Module housing a Kedro custom dataset for SunPy Maps.
"""
import warnings
from copy import deepcopy
from pathlib import PurePosixPath
from typing import Any, Dict
import fsspec
from kedro.io.core import (
    AbstractVersionedDataSet,
    DataSetError,
    Version,
    get_filepath_str,
    get_protocol_and_path,
)
import numpy as np
from astropy.io import fits
from sunpy.map import Map

warnings.filterwarnings("ignore")


class SunPyMapDataSet(AbstractVersionedDataSet):
    """
    This class handles I/O for SunPy Maps within the Kedro framework.
    Astropy is used as an intermediary to achieve this.
    Loading directly from SunPy was unsuccessful, but may be possible.
    """

    DEFAULT_SAVE_ARGS = {"overwrite": False}

    def __init__(
        self,
        filepath: str,
        save_args: Dict[str, Any] = None,
        version: Version = None,
        credentials: Dict[str, Any] = None,
        fs_args: Dict[str, Any] = None,
    ) -> None:

        _fs_args = deepcopy(fs_args) or {}
        _fs_open_args_load = _fs_args.pop("open_args_load", {})
        _fs_open_args_save = _fs_args.pop("open_args_save", {})
        _credentials = deepcopy(credentials) or {}

        protocol, path = get_protocol_and_path(filepath, version)
        if protocol == "file":
            _fs_args.setdefault("auto_mkdir", True)

        self._protocol = protocol
        self._fs = fsspec.filesystem(self._protocol, **_credentials, **_fs_args)

        super().__init__(
            filepath=PurePosixPath(path),
            version=version,
            exists_function=self._fs.exists,
            glob_function=self._fs.glob,
        )

        self._save_args = deepcopy(self.DEFAULT_SAVE_ARGS)
        if save_args is not None:
            self._save_args.update(save_args)

        _fs_open_args_save.setdefault("mode", "wb")
        self._fs_open_args_load = _fs_open_args_load
        self._fs_open_args_save = _fs_open_args_save

    def _describe(self) -> Dict[str, Any]:
        return dict(
            filepath=self._filepath,
            protocol=self._protocol,
            save_args=self._save_args,
            version=self._version,
        )

    def _load(self) -> Map:
        load_path = get_filepath_str(self._get_load_path(), self._protocol)
        with self._fs.open(load_path, **self._fs_open_args_load) as fs_file:
            file = fits.open(fs_file).copy()
            image_hdu = file[1]
            image_hdu.verify("fix")
            smap = Map((image_hdu.data, image_hdu.header))
            smap.data[np.isnan(smap.data)] = 0
            return smap

    def _save(self, data: Map) -> None:
        save_path = get_filepath_str(self._get_save_path(), self._protocol)
        with self._fs.open(save_path, **self._fs_open_args_save) as fs_file:
            hdu = fits.ImageHDU()
            hdu.header = data.fits_header
            hdu.data = data.data
            hdu.writeto(fs_file, **self._save_args)
        self._invalidate_cache()

    def _exists(self) -> bool:
        try:
            load_path = get_filepath_str(self._get_load_path(), self._protocol)
        except DataSetError:
            return False
        return self._fs.exists(load_path)

    def _release(self) -> None:
        super()._release()
        self._invalidate_cache()

    def _invalidate_cache(self) -> None:
        """Invalidate underlying filesystem caches."""
        filepath = get_filepath_str(self._filepath, self._protocol)
        self._fs.invalidate_cache(filepath)
