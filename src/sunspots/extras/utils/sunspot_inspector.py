from typing import Optional
from IPython import display
import matplotlib.pyplot as plt
from matplotlib import patches
from ipywidgets import widgets
import numpy as np
from scipy import ndimage


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


def overplot_rect_from_coords(
    axes: plt.Axes, bottom_left: tuple[int, int], top_right: tuple[int, int]
) -> None:
    """
    Overplot green rectangle from the provided corners on the axes.

    Parameters
    ----------
    axes : Matplotlib axes
        The axes to plot on.
    bottom_left : tuple[int, int]
        The bottom left corner (pixel coordinates) of the region.
    top_right : tuple[int, int]
        The top right corner (pixel coordinates) of the region.
    """
    box_x = top_right[0] - bottom_left[0]
    box_y = top_right[1] - bottom_left[1]
    box_anchor = (bottom_left[0] - 0.5, bottom_left[1] - 0.5)
    new_rect = patches.Rectangle(
        box_anchor, box_x, box_y, linewidth=1, edgecolor="g", facecolor="none"
    )
    axes.add_patch(new_rect)


def overplot_spots_from_mask(
    axes: plt.Axes, mask: np.ndarray, box_size: Optional[int] = 64
) -> None:
    """
    Plot the mask onto a given set of axes, drawing the selected regions in
    red.

    Parameters
    ----------
    axes : Matplotlib axes
        The axes to which to add the boxes from the mask.
    mask : np.ndarray
        The mask indicating the regions to draw.
    box_size : int
        The size each block in the mask represents on the image.
    """
    boxCoords = zip(*np.unravel_index(mask.reshape(-1).nonzero()[0], mask.shape))
    for c in boxCoords:
        boxX = box_size
        boxY = box_size
        box_anchor = (c[1] * boxX - 0.5, c[0] * boxY - 0.5)
        new_rect = patches.Rectangle(
            box_anchor, boxX, boxY, linewidth=1, edgecolor="r", facecolor="none"
        )
        axes.add_patch(new_rect)


class SunspotInspector:
    """
    Class for plotting label predictions or contiguous regions over their
    corresponding sunmap(s).
    Designed to be used in a notebook with the matplotlib widget backend.

    Parameters
    ----------
    dataset : dict[str]
        Kedro PartitionedDataSet.
    predictions: np.ndarray[np.ndarray]
        Image stack of binary mask predictions, shape
        (len(dataset), box_size, box_size)
    box_size : Optional[int]
        The size of the boxes used to define the regions.
    """

    def __init__(
        self,
        dataset: dict,
        predictions: np.ndarray,
        plot_regions: Optional[bool] = False,
        box_size: Optional[int] = 64,
    ) -> None:
        self.dataset = dataset
        self.keys = list(self.dataset.keys())
        self.predictions = predictions
        self.plot_regions = plot_regions
        self.box_size = box_size
        if self.plot_regions is True:
            self.get_regions()

        self.index = 0
        image = self.dataset[self.keys[self.index]]()
        self.fig = plt.figure()
        self.axes = plt.subplot(projection=image)
        self.setup_buttons()
        self.setup_image(self.index)

    def get_regions(self) -> None:
        self.regions = {}
        for index, prediction in enumerate(self.predictions):
            self.regions[index] = []
            labeled_array, num_features = ndimage.label(prediction)
            for idx in range(1, num_features + 1):
                self.regions[index].append(
                    select_region(labeled_array, idx, box_size=self.box_size)
                )

    def setup_buttons(self, starting_slider: int = 0) -> None:
        """Sets up buttons for the selector widget."""
        self.slider = widgets.IntSlider(
            starting_slider, 0, len(self.keys) - 1, description="File Number"
        )
        display.display(self.slider)
        self.slider.observe(self.change_image, names="value")

    def setup_image(self, index: int) -> None:
        """Plots image of a specified index from the dataset."""
        self.index = index
        for patch_index in range(len(self.axes.patches) - 1, -1, -1):
            self.axes.patches[patch_index].remove()
        self.fig.canvas.flush_events()
        self.image = self.dataset[self.keys[index]]()
        self.image.plot(axes=self.axes)
        if self.plot_regions is True:
            self.region = self.regions[index]
            for corner in self.region:
                overplot_rect_from_coords(self.axes, corner[0], corner[1])
        else:
            self.mask = self.predictions[index]
            overplot_spots_from_mask(self.axes, self.mask, box_size=self.box_size)

    def change_image(self, event: dict) -> None:
        """Changes index of image setup function."""
        self.setup_image(event["new"])

    def __getstate__(self) -> dict:
        state = {
            "index": self.index,
            "dataset": self.dataset,
            "predictions": self.predictions,
            "plot_regions": self.plot_regions,
            "regions": self.regions,
            "box_size": self.box_size,
        }
        return state

    def __setstate__(self, state: dict) -> None:
        self.index = state["index"]
        self.dataset = state["dataset"]
        self.predictions = state["predictions"]
        self.plot_regions = state["plot_regions"]
        self.regions = state["regions"]
        self.box_size = state["box_size"]
