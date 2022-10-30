"""
This is a boilerplate pipeline 'data_ingestion'
generated using Kedro 0.18.3
"""
from typing import Generator, Callable
import cv2
import numpy as np
import pandas as pd
from sunpy.map import Map


def _chunk_image(
    smap: Map, box_size: int
) -> Generator[tuple[tuple[int, int], np.ndarray], None, None]:
    """
    Slices a SunPy Map into chunks of a specified box size.
    Generates the chunks with their coordinates in box units.
    """
    for i in range(box_size):
        for j in range(box_size):
            coord = (i, j)
            chunk = smap.data[
                i * box_size : (i + 1) * box_size, j * box_size : (j + 1) * box_size
            ].flatten()
            yield coord, chunk


def _fourier_transform(image: np.ndarray) -> np.ndarray:
    """
    Returns the real part of the Discrete Fourier Transform of a specified
    chunk.
    """
    dft = cv2.dft(np.float32(image), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    dft_complex = dft_shift[:, :, 0] + 1j * dft_shift[:, :, 1]
    dft_absolute = np.abs(dft_complex) + 1  # lie between 1 and 1e6
    dft_bounded = 20 * np.log(dft_absolute)
    dft_image = 255 * dft_bounded / np.max(dft_bounded)
    return dft_image.astype(np.uint8)


def _coord_radius(box_size: int, i: int, j: int) -> int:
    """
    Calculate radial distance from center of solar disk to specified box coord.
    """
    return np.sqrt((4096 / box_size / 2 - i) ** 2 + (4096 / box_size / 2 - j) ** 2)


def _compute_chunk_features(
    chunks: Generator, key: str, box_size: int
) -> Generator[dict, None, None]:
    """
    Generates a set of specified features for supplied chunks.
    """
    for coord, chunk in chunks:
        fourier_chunk = _fourier_transform(chunk)
        yield {
            "key": key,
            "coord": coord,
            "coord_radius": _coord_radius(box_size, coord[0], coord[1]),
            "mean": np.mean(chunk),
            "standard_deviation": np.std(chunk),
            "range": np.ptp(chunk),
            "fourier_mean": np.mean(fourier_chunk),
            "fourier_standard_deviation": np.std(fourier_chunk),
            "fourier_range": np.ptp(fourier_chunk),
        }


def generate_feature_table(data: dict[str, Callable], box_size: int) -> pd.DataFrame:
    """
    Returns pandas dataframe of features of all chunks across an entire dataset
    of SunPy maps.
    """
    chunk_features = []
    for key, value in data.items():
        smap = value()
        chunks = _chunk_image(smap, box_size)
        features = _compute_chunk_features(chunks, key, box_size)
        for record in features:
            chunk_features.append(record)
    return pd.DataFrame.from_records(chunk_features)
