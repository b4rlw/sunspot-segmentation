"""
This is a boilerplate pipeline 'region_extraction'
generated using Kedro 0.18.3
"""
from typing import Callable, Optional
import numpy as np
from scipy import ndimage
from sunpy.map import Map


def select_region(
    labels: np.ndarray, index: int, box_size: int, contour_size: Optional[int] = None
) -> tuple[int, int]:
    """
    Return the bottom left and top right corners of the
    bounding box of a labelled image region, optionally
    contouring around the box to "fuzzily" include
    features on the edge.

    Parameters
    ----------
    labels : np.ndarray
        The integer labelled mask (produced by e.g. scipy.ndimage.label).
    index : int
        The labelled region to extract.
    box_size : int
        The size of the boxes used to define the regions.
    contour_size : Optional[int]
        The size to add onto each side of the region when defining
        the bounding box. Default: boxSize // 2.

    Returns
    -------
    bottom_left, top_right : Tuple[int, int]
        The pixel coordinates of the corners of the selected region.
    """
    if contour_size is None:
        contour_size = box_size // 2

    coords = np.argwhere(labels == index)
    min_x = np.min(coords[:, 1])
    max_x = np.max(coords[:, 1])
    min_y = np.min(coords[:, 0])
    max_y = np.max(coords[:, 0])

    bottom_left = (
        (max_x + 1) * box_size + contour_size // 2,
        (max_y + 1) * box_size + contour_size // 2,
    )
    top_right = (
        min_x * box_size - contour_size // 2,
        min_y * box_size - contour_size // 2,
    )
    return bottom_left, top_right


def get_region_coords(dataset: dict[str, Callable], targets: np.ndarray, box_size):
    """
    Gets the coordinates for regions of contiguous targets for all maps in a dataset.
    """
    region_coords = {}
    for key, mask in zip(dataset.keys(), targets):
        region_coords[key] = []
        labeled_array, num_features = ndimage.label(mask)
        for index in range(1, num_features + 1):
            bounding_coords = select_region(labeled_array, index, box_size)
            region_coords[key].append(bounding_coords)
    return region_coords


def extract_region(
    smap: Map, bottom_left: tuple[int, int], top_right: tuple[int, int]
) -> Map:
    """
    Extract a submap from the provided pixel coordinates
    (obtained from select_region).

    Parameters
    ----------
    smap : sunpy.map.Map
        The HMI map.
    bottom_left : tuple[int, int]
        The bottom left pixel coordinate pair.
    top_right : tuple[int, int]
        The top right pixel coordinate pair.

    Returns
    -------
    submap : sunpy.map.Map
        The submap of the selected region.
    """
    bl = smap.wcs.pixel_to_world(*bottom_left)
    tr = smap.wcs.pixel_to_world(*top_right)
    return smap.submap(bottom_left=bl, top_right=tr)


def extract_regions(
    dataset: dict[str, Callable], region_coords: dict[str, list[tuple]]
):
    """
    Extracts submaps from provided pixel coordinates across all maps in a
    dataset.
    """
    extractions = {}
    for (key, smap), coords in zip(dataset.items(), list(region_coords.values())):
        for coord in coords:
            bottom_left, top_right = coord
            region_submap = extract_region(smap(), bottom_left, top_right)
            extractions[f"{key}_{bottom_left}_{top_right}"] = region_submap
    return extractions
