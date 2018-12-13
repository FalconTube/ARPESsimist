import math

import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent


class DraggablePlotExample(object):
    """ An example of plot with draggable markers """

    def __init__(self, figure, axes):
        self._figure, self._axes, self.line = figure, axes, None
        self._dragging_point = None
        self._points = {}
        self.xy1 = ()
        self.xy2 = ()

        self._init_plot()

    def _init_plot(self):
        self.click_cid = self._figure.canvas.mpl_connect(
            "button_press_event", self._on_click
        )
        self.release_cid = self._figure.canvas.mpl_connect(
            "button_release_event", self._on_release
        )
        self.motion_cid = self._figure.canvas.mpl_connect(
            "motion_notify_event", self._on_motion
        )

    def _update_plot(self):
        if not self._points:
            return
        x, y = zip(*sorted(self._points.items()))
        self.xy1 = (x[0], y[0])
        try:
            self.xy2 = (x[1], y[1])
        except:
            pass
        # Add new plot
        if not self.line:
            self.line, = self._axes.plot(
                x, y, marker="o", linestyle="-", color="#ff7f0e", markersize=5
            )
            self._figure.canvas.draw()
        # Update current plot
        else:
            self.line.set_data(x, y)
            self._figure.canvas.draw()

    def _add_point(self, x, y=None):
        if len(self._points) >= 2:
            return
        if isinstance(x, MouseEvent):
            x, y = float(x.xdata), float(x.ydata)
        self._points[x] = y
        return x, y

    def _remove_point(self, x, _):
        if x in self._points:
            self._points.pop(x)

    def _find_neighbor_point(self, event):
        """ Find point around mouse position
        :rtype: ((int, int)|None)
        :return: (x, y) if there are any point around mouse else None
        """
        # TODO: Do this dynamically
        distance_threshold = 3
        nearest_point = None
        # min_distance = math.sqrt(2 * (100 ** 2))
        min_distance = 1
        for x, y in self._points.items():
            distance = math.hypot(abs(event.xdata - x), abs(event.ydata - y))
            if distance < min_distance:
                min_distance = distance
                nearest_point = (x, y)
        if min_distance < distance_threshold:
            return nearest_point
        return None

    def _on_click(self, event):
        """ callback method for mouse click event
        :type event: MouseEvent
        """
        # right click
        if event.button == 3 and event.inaxes in [self._axes]:
            point = self._find_neighbor_point(event)
            if point:
                self._dragging_point = point
                self._remove_point(*point)
            else:
                self._add_point(event)
            self._update_plot()

    def _on_release(self, event):
        """ callback method for mouse release event
        :type event: MouseEvent
        """
        if event.button == 3 and event.inaxes in [self._axes] and self._dragging_point:
            self._add_point(event)
            self._dragging_point = None
            self._update_plot()

    def _on_motion(self, event):
        """ callback method for mouse motion event
        :type event: MouseEvent
        """
        if not self._dragging_point:
            return
        self._remove_point(*self._dragging_point)
        self._dragging_point = self._add_point(event)
        self._update_plot()

    def disconnect(self):
        self._figure.canvas.mpl_disconnect(self.click_cid)
        self._figure.canvas.mpl_disconnect(self.release_cid)
        self._figure.canvas.mpl_disconnect(self.motion_cid)

    def get_data(self):
        return self.xy1, self.xy2

    def clear_line(self):
        try:
            self.line.remove()
        except:
            pass


if __name__ == "__main__":

    fig, ax = plt.subplots()
    plot = DraggablePlotExample(fig, ax)
    plt.show()
