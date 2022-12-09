"""
This is a boilerplate pipeline 'label_extraction'
generated using Kedro 0.18.3
"""
from typing import Generator
import pandas as pd
from sunspots.extras.utils.sunspot_selector import SunspotSelector


def _extract_labels(
    label_dict: dict[str, list[tuple[int, int]]], box_size: int
) -> Generator[dict, None, None]:
    """
    Generator which extracts dictionaries of labels for assembly in a pandas
    dataframe.
    """
    for key, _list in label_dict.items():
        for j in range(box_size):
            for i in range(box_size):
                coord = (i, j)
                label = coord in _list
                yield {
                    "key": key,
                    "coord": coord,
                    "label": label,
                }


def generate_label_table(selector: SunspotSelector, box_size: int) -> pd.DataFrame:
    """
    Returns a pandas dataframe of patch labels across an entire dataset of SunPy
    maps.
    """
    label_dict = dict(zip(selector.keys, selector.box_coords_all))
    patch_labels = list(_extract_labels(label_dict, box_size))
    label_df = pd.DataFrame.from_records(patch_labels)
    label_df["label"] = label_df["label"].astype(int)
    return label_df
