"""
This is a boilerplate pipeline 'STARA'
generated using Kedro 0.18.3
"""
from typing import Callable
import astropy.units as u
import numpy as np
import pandas as pd
from scipy import ndimage
from skimage.measure import label, regionprops_table
from skimage.filters import median
from skimage.morphology import disk, square
from skimage.util import invert
import sunpy.map
from astropy.table import QTable
from astropy.time import Time
from numba import njit, prange, set_num_threads
from sunpy.map import Map


@njit(parallel=False)
def erode_core(image, pad_image, s_element):
    pad_width = s_element.shape[0] // 2
    out = np.zeros_like(image)
    if pad_width % 2 == 0:
        pad_width -= 1
    for y in prange(image.shape[0]):
        for x in range(image.shape[1]):
            xc = x + pad_width
            yc = y + pad_width
            min_val = pad_image[yc, xc]
            for yy in range(s_element.shape[0]):
                for xx in range(s_element.shape[1]):
                    if s_element[yy, xx]:
                        xxc = xx - pad_width
                        yyc = yy - pad_width
                        min_val = min(min_val, pad_image[yc + yyc, xc + xxc])
            out[y, x] = min_val
    return out


def erode(image, s_element):
    """
    Morphologically erode image with structure element.
    """
    pad_y, pad_x = [s % 2 == 0 for s in s_element.shape]
    pad_s_element = np.zeros(
        (s_element.shape[0] + int(pad_y), s_element.shape[1] + int(pad_x))
    )
    pad_s_element[pad_y:, pad_x:] = s_element
    pad_width = pad_s_element.shape[0] // 2
    pad_image = np.pad(image, pad_width, mode="reflect")
    return erode_core(image, pad_image, pad_s_element)


@njit(parallel=False)
def dilate_core(image, pad_image, s_element):
    pad_width = s_element.shape[0] // 2
    out = np.zeros_like(image)
    if pad_width % 2 == 0:
        pad_width -= 1
    for y in prange(image.shape[0]):
        for x in range(image.shape[1]):
            xc = x + pad_width
            yc = y + pad_width
            max_val = pad_image[yc, xc]
            for yy in range(s_element.shape[0]):
                for xx in range(s_element.shape[1]):
                    if s_element[yy, xx]:
                        xxc = xx - pad_width
                        yyc = yy - pad_width
                        max_val = max(max_val, pad_image[yc + yyc, xc + xxc])
            out[y, x] = max_val
    return out


def dilate(image, s_element):
    """
    Morphologically dilate image with structure element.
    """
    pad_y, pad_x = [s % 2 == 0 for s in s_element.shape]
    pad_element = np.zeros(
        (s_element.shape[0] + int(pad_y), s_element.shape[1] + int(pad_x))
    )
    pad_element[pad_y:, pad_x:] = s_element
    pad_width = pad_element.shape[0] // 2
    pad_image = np.pad(image, pad_width, mode="reflect")
    return dilate_core(image, pad_image, pad_element)


def opening(image: np.ndarray, s_element: np.ndarray):
    """
    Morphological opening.

    Parameters
    ----------
    image : np.ndarray
        The image to be filtered.
    s_element : np.ndarray
        The structure element to be used in the morphological opening.

    Returns
    -------
    result : np.ndarray
        The morphological opening of the image by the structure element.
    """
    return dilate(erode(image, s_element), s_element)


def white_tophat(image: np.ndarray, s_element: np.ndarray):
    """
    Morphological white tophat filter.

    Parameters
    ----------
    image : np.ndarray
        The image to be filtered.
    s_element : np.ndarray
        The structure element to be used in the morphological opening.

    Returns
    -------
    result : np.ndarray
        The white tophat filtered image, i.e. image - opening(image, s_element).
    """
    return image - opening(image, s_element)


@u.quantity_input
def stara(
    smap,
    circle_radius: u.deg = 100 * u.arcsec,
    median_box: u.deg = 10 * u.arcsec,
    threshold=6000,
    limb_filter: u.percent = None,
):
    """
    A method for automatically detecting sunspots in white-light data using
    morphological operations.

    Parameters
    ----------
    smap : `sunpy.map.GenericMap`
        The map to apply the algorithm to.
    circle_radius : `astropy.units.Quantity`, optional
        The angular size of the structuring element used in the
        `skimage.morphology.white_tophat`. This is the maximum radius of
        detected features.
    median_box : `astropy.units.Quantity`, optional
        The size of the structuring element for the median filter, features
        smaller than this will be averaged out.
    threshold : `int`, optional
        The threshold used for detection, this will be subject to detector
        degradation. The default is a reasonable value for HMI continuum images.
    limb_filter : `astropy.units.Quantity`, optional
        If set, ignore features close to the limb within a percentage of the
        radius of the disk. A value of 10% generally filters out false
        detections around the limb with HMI continuum images.
    """
    data = invert(smap.data)
    # Filter things that are close to limb to reduce false detections
    if limb_filter is not None:
        hpc_coords = sunpy.map.all_coordinates_from_map(smap)
        r = np.sqrt(hpc_coords.Tx**2 + hpc_coords.Ty**2) / (
            smap.rsun_obs - smap.rsun_obs * limb_filter
        )
        data[r > 1] = np.nan
    # Median filter to remove detections based on hot pixels
    m_pix = int((median_box / smap.scale[0]).to_value(u.pix))
    med = median(data, square(m_pix), behavior="ndimage")
    # Construct the pixel structuring element
    c_pix = int(np.round((circle_radius / smap.scale[0]).to_value(u.pix)))
    circle = disk(c_pix // 2)
    finite = white_tophat(med, circle)
    finite[np.isnan(finite)] = 0  # Filter out nans
    return finite > threshold


def get_regions(
    segmentation, smap, properties=("label", "centroid", "area", "min_intensity")
):
    labelled = label(segmentation)
    if labelled.max() == 0:
        return QTable()
    regions = regionprops_table(labelled, smap.data, properties=properties)
    regions["obstime"] = Time([smap.date] * regions["label"].size)
    regions["center_coord"] = smap.pixel_to_world(
        regions["centroid-0"] * u.pix, regions["centroid-1"] * u.pix
    ).heliographic_stonyhurst
    return QTable(regions)


def process_extraction(
    region_submap: Map, stara_params: dict
) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    circle_radius = stara_params["circle_radius"] * u.arcsec
    median_box = stara_params["median_box"] * u.arcsec
    threshold = stara_params["threshold"]
    limb_filter = stara_params["limb_filter"] * u.percent
    segmentation = stara(
        region_submap, circle_radius, median_box, threshold, limb_filter
    )
    segmentation_mask, _ = ndimage.label(segmentation)
    region_table = get_regions(
        segmentation,
        region_submap,
        properties=["label", "centroid", "area", "min_intensity"],
    )
    region_dataframe = region_table.to_pandas()
    return segmentation, segmentation_mask, region_dataframe


def process_extractions(region_submaps: dict[str, Callable], stara_params: dict):
    segmentations = {}
    segmentation_masks = {}
    region_dataframes = {}
    for key, value in region_submaps.items():
        region_submap = value()
        segmentation, segmentation_mask, region_dataframe = process_extraction(
            region_submap, stara_params
        )
        segmentations[f"{key}_segmentation"] = segmentation
        segmentation_masks[f"{key}_segmentation_mask"] = segmentation_mask
        region_dataframes[f"{key}_region_dataframe"] = region_dataframe
    return segmentations, segmentation_masks, region_dataframes


# set_num_threads(16)
