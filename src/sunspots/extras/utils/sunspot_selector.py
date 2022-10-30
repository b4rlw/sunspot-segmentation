"""
Module housing the SunspotSelector class used for labelling SunPy Map chunks.
"""
from IPython import display
import matplotlib.pyplot as plt
from matplotlib import patches
from ipywidgets import widgets


class SunspotSelector:
    """
    Class for selecting rectangular regions of an image sequence.
    Designed to be used in a notebook with the matplotlib widget backend.
    Reworked for Kedro compatibility, dataset dict should be output from Kedro
    catalog load.
    Can specify a local or remote dataset as determined by catalog entry specs.
    """

    def __init__(
        self, dataset: dict, dataset_name: str, pixels_per_cell: tuple[int, int]
    ) -> None:
        self.dataset = dataset
        self.dataset_name = dataset_name
        self.keys = list(self.dataset.keys())
        self.pixels_per_cell = pixels_per_cell
        self.hmi_coords_all = [[] for _ in self.keys]
        self.box_coords_all = [[] for _ in self.keys]

        self.index = 0
        image = self.dataset[self.keys[self.index]]()
        self.fig = plt.figure()
        self.axes = plt.subplot(projection=image)
        self.setup_buttons()
        self.setup_image(self.index)

    def setup_buttons(self, starting_slider: int = 0) -> None:
        """Sets up buttons for the selector widget."""
        self.receiver = self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        self.slider = widgets.IntSlider(
            starting_slider, 0, len(self.keys) - 1, description="File Number"
        )
        display.display(self.slider)
        self.slider.observe(self.change_image, names="value")
        self.clear_button = widgets.Button(description="Clear Image")
        display.display(self.clear_button)
        self.clear_button.on_click(self.clear)

    def setup_image(self, index: int) -> None:
        """Plots image of a specified index from the dataset."""
        self.index = index
        for patch_index in range(len(self.axes.patches) - 1, -1, -1):
            self.axes.patches[patch_index].remove()
        self.fig.canvas.flush_events()
        self.image = self.dataset[self.keys[index]]()
        self.image.plot(axes=self.axes)
        self.hmi_coords = self.hmi_coords_all[index]
        self.box_coords = self.box_coords_all[index]

        for coord in self.box_coords:
            box_x = self.pixels_per_cell[0]
            box_y = self.pixels_per_cell[1]
            box_anchor = (coord[0] * box_x - 0.5, coord[1] * box_y - 0.5)
            new_rect = patches.Rectangle(
                box_anchor, box_x, box_y, linewidth=1, edgecolor="r", facecolor="none"
            )
            self.axes.add_patch(new_rect)
        self.axes.autoscale_view()

    def change_image(self, event: dict) -> None:
        """Changes index of image setup function."""
        self.setup_image(event["new"])

    def on_click(self, event: dict) -> None:
        """
        Determines the behaviour of clicking on the selector widget.
        If wrong mode is selected, the clicking will do nothing.
        If clicking on an existing box, the box will be removed.
        If clicking on blank space, a new box will be added.
        """
        if self.fig.canvas.manager.toolbar.mode != "":
            return

        box_x = self.pixels_per_cell[0]
        box_y = self.pixels_per_cell[1]
        box_coord = (
            int((event.xdata + 0.5) // box_x),
            int((event.ydata + 0.5) // box_y),
        )
        box_anchor = (box_coord[0] * box_x - 0.5, box_coord[1] * box_y - 0.5)
        if box_coord in self.box_coords:
            for patch in self.axes.patches:
                if patch.get_xy() == box_anchor:
                    patch.remove()

            index = self.box_coords.index(box_coord)
            del self.box_coords[index]
            del self.hmi_coords[index]
        else:
            self.hmi_coords.append((event.xdata, event.ydata))
            self.box_coords.append(box_coord)
            new_rect = patches.Rectangle(
                box_anchor, box_x, box_y, linewidth=1, edgecolor="r", facecolor="none"
            )
            self.axes.add_patch(new_rect)

    def disconnect_matplotlib(self, _) -> None:
        """Disconnect the receiver's callback id."""
        self.fig.canvas.mpl_disconnect(self.receiver)

    def clear(self, _) -> None:
        """Clears all boxes from the widget's current selected image."""
        self.hmi_coords[:] = []
        self.box_coords[:] = []
        for patch_index in range(len(self.axes.patches) - 1, -1, -1):
            self.axes.patches[patch_index].remove()
        self.fig.canvas.flush_events()
        self.fig.canvas.flush_events()

    def display_widget(self, dataset: dict) -> None:
        """
        Image widget initialiser for post-Pickle reload. Required because
        dataset dict of callables cannot be pickled to cloud. For cases where
        only the box coords and hmi data are required, this function need not be
        called.
        """
        self.dataset = dataset
        self.fig = plt.figure()
        image = self.dataset[self.keys[0]]()
        self.axes = plt.subplot(projection=image)
        self.axes = self.fig.gca()
        self.setup_buttons(starting_slider=self.index)
        self.setup_image(self.index)
        self.slider.send_state({"value": self.index})

    def __getstate__(self) -> dict:
        state = {
            "index": self.index,
            "dataset_name": self.dataset_name,
            "keys": self.keys,
            "pixels_per_cell": self.pixels_per_cell,
            "hmi_coords_all": self.hmi_coords_all,
            "box_coords_all": self.box_coords_all,
        }
        return state

    def __setstate__(self, state: dict) -> None:
        self.index = state["index"]
        self.dataset_name = state["dataset_name"]
        self.keys = state["keys"]
        self.pixels_per_cell = state["pixels_per_cell"]
        self.hmi_coords_all = state["hmi_coords_all"]
        self.box_coords_all = state["box_coords_all"]
