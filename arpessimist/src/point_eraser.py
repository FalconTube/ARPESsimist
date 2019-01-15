import math
import numpy as np


class PointEraser(object):
    """ Erases Scatter Points from both the figure and the array """

    def __init__(self, figure, axes, max_line, x, y):
        self._figure, self._axes, self.line = figure, axes, None
        self.hover_counter = 0
        self.current_object = -1
        self.x = x
        self.y = y
        self.scattercolors = ["#ff7f0e"] * len(self.x)

        self.max_line = max_line

        self._init_plot()

    def _init_plot(self):
        self.click_cid = self._figure.canvas.mpl_connect(
            "button_press_event", self._remove_point
        )
        self.hover_cid = self._figure.canvas.mpl_connect(
            "motion_notify_event", self._on_hover
        )

    def _on_hover(self, event):
        if event.inaxes == self._axes:
            cont, ind = self.max_line.contains(event)
            if cont:
                tmp_colors = self.scattercolors.copy()
                self.hover_counter = 1
                index_num = ind["ind"][0]
                self.current_object = index_num
                tmp_colors[index_num] = "red"
                self.max_line.set_edgecolors(tmp_colors)
                self._axes.draw_artist(self.max_line)
                self._figure.canvas.update()
            else:
                if self.hover_counter == 1:
                    self.max_line.set_edgecolors(self.scattercolors)
                    self._figure.canvas.draw()
                    self.hover_counter = 0
                    self.current_object = -1
                pass

    def _remove_point(self, event):
        if self.current_object != -1:
            try:
                self.max_line.remove()
                self.x = np.delete(self.x, self.current_object)
                self.y = np.delete(self.y, self.current_object)
                self.scattercolors = np.delete(self.scattercolors, self.current_object)
                self.max_line = self._axes.scatter(
                    self.x, self.y, s=50, facecolors="none", edgecolors=self.scattercolors
                )

                self._figure.canvas.draw()
            except:
                pass

    def disconnect(self):
        self._figure.canvas.mpl_disconnect(self.click_cid)
        self._figure.canvas.mpl_disconnect(self.hover_cid)

    def update_dataset(self, x, y):
        self.x = x
        self.y = y
        self._figure.canvas.draw()

    def get_data(self):
        return self.x, self.y
    
    def get_max_line(self):
        return self.max_line
