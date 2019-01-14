import numpy as np
from PyQt5 import QtCore
from .basefile_spectra import Spectra


# class Calc_K_space(QtCore.QThread):
#     """ Runs k-space conversion in background """

#     def __init__(self, data, ranges, parent=None):
#         QtCore.QThread.__init__(self, parent)
#         self.DataHandler = HandleNielsSpectra(data, ranges)

#     def run(self):
#         self.data_stack_k, self.stack_range_k = self.DataHandler.convert_all_to_k()
#         self.k_space_generated = True

#     def get(self):
#         return self.data_stack_k, self.stack_range_k, self.k_space_generated


class HandleNielsSpectra(Spectra):
    """ Data handler that uses Niels Ehlens functions """

    def __init__(self):
        pass

    def convert_all_to_k(self, data_stack, data_ranges):
        data_ranges_k = []
        for n, i in enumerate(data_ranges):
            intens = data_stack[:, :, n]
            # Maxima and minima are always at fixed positons, regardless of
            # loaded file
            a_min, a_max = i[0], i[1]
            e_min, e_max = i[2], i[3]
            xlimits = [a_min, a_max]
            ylimits = [e_min, e_max]
            this_spec = Spectra(intens, xlimits, ylimits)
            this_spec.convertToKSpace()
            intens, extent = this_spec.get_current_space()
            if n == 0:
                data_stack_k = intens
                data_ranges_k.append(extent)
            else:
                data_stack_k = np.dstack((data_stack_k, intens))
                data_ranges_k.append(extent)
        return data_stack_k, data_ranges_k

    def convert_single_to_k(self, data, extent_in):
        data = np.asarray(data)
        a_min, a_max = extent_in[0], extent_in[1]
        e_min, e_max = extent_in[2], extent_in[3]
        xlimits = [a_min, a_max]
        ylimits = [e_min, e_max]
        this_spec = Spectra(data, xlimits, ylimits)
        this_spec.convertToKSpace()
        intens, extent = this_spec.get_current_space()
        return intens, extent
