import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Qt5Agg")
from mpl_canvas_class import MyMplCanvas


class TwoD_Plotter(MyMplCanvas):
    ''' Plots 2D images '''

    # def __init__(self, *args, **kwargs):
    def __init__(self, parent=None, width=5, height=6, dpi=100,
                 multifig=True):
        super().__init__(parent, width, height, dpi,
                         multifig)
        self.instance_counter = 0

    def update_2dplot(self, extent=None):
        ''' Really slow at the moment, due to having three axis
        in here. Have to use blitting '''
        if extent:
            x_range = abs(extent[1] - extent[0])
            e_range = abs(extent[3] - extent[2])
            aspectratio = x_range/e_range
        # print('instance_counter {}'.format(self.instance_counter))
        if self.instance_counter == 0:
            print('zero instance')
            self.instance_counter += 1
            self.axes.cla()
            self.twoD_ax = self.axes.imshow(self.twoD_data,
                                            extent=extent,
                                            aspect=aspectratio,
                                            zorder=0)
            self.plt_backgrounds = \
                [ax.bbox for ax in self.fig.axes]
            # self.plt_backgrounds = \
            #     [self.axes.figure.canvas.copy_from_bbox(
            #         ax.bbox) for ax in self.fig.axes]
            self.toolbar.update()
            self.canvas.draw()
        else:
            ''' Really slow at the moment, due to having three axis
                in here. Have to use blitting '''
            self.twoD_ax.set_data(self.twoD_data)
            # self.axes.draw_artist(self.twoD_ax)
            for i in self.plt_backgrounds:
                self.axes.figure.canvas.blit(i)

            # self.axes.figure.canvas.blit(self.plt_backgrounds)
            # self.axes.figure.canvas.update()
            # self.axes.figure.canvas.flush_events()
            self.toolbar.update()

    def update_2d_data(self, data):
        self.twoD_data = data

    def compute_initial_figure(self):
        self.twoD_data = np.zeros((10, 10))
        self.axes.imshow(self.twoD_data)
