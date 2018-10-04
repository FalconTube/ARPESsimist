import numpy as np
import matplotlib.pyplot as plt
from mpl_canvas_class import MyMplCanvas


class TwoD_Plotter(MyMplCanvas):
    ''' Plots 2D images '''

    # def __init__(self, *args, **kwargs):
    def __init__(self, parent=None, width=5, height=10, dpi=100,
                 multifig=False):
        super().__init__(parent, width, height, dpi,
                         multifig)
        self.instance_counter = 0
        # self.axes = self.twod_ax
        print(self.axes)

    def update_2dplot(self, extent=None):
        if extent:
            x_range = abs(extent[1] - extent[0])
            e_range = abs(extent[3] - extent[2])
            aspectratio = x_range/e_range

        if self.instance_counter == 0:
            self.instance_counter += 1
            self.axes.cla()
            self.thisax = self.axes.imshow(self.twoD_data,
                                           extent=extent,
                                           aspect=aspectratio,
                                           zorder=0)
            self.toolbar.update()
            self.canvas.draw()
        else:
            self.thisax.set_data(self.twoD_data)
            self.toolbar.update()
            self.canvas.draw()

    def update_2d_data(self, data):
        self.twoD_data = data

    def compute_initial_figure(self):
        self.twoD_data = np.zeros((10, 10))
        self.axes.imshow(self.twoD_data)
