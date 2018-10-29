import glob
import os
import numpy as np
import matplotlib.pyplot as plt
import time
from natsort import natsorted
import multiprocessing
import h5py as h5


from PyQt5.QtWidgets import QProgressBar, QWidget, QApplication, QMessageBox
from progbar import ProgressBar


class Sp2_loader:
    """ Class able to load single or multiple SP2 files. """

    def __init__(self, parent=None):
        self.multi_file_mode = False
        self.parent = parent
        self.multi_file_mode = True
        self.measurement_ranges = []

    def init_prog_bar(self):
        self.prog_widget = QWidget(self.parent)

    def read_sp2(self, filename, both_sets=False):
        """ Reads a single SP2 file. """
        with open(filename, "r") as f:
            comments = []
            ranges_dict = {}
            rawdata = []
            rawdata1 = []
            data_set_count = -1
            for line in f:
                stripline = line.strip()
                if str(stripline) == "P2":
                    continue
                if line.startswith("#"):
                    comments.append(str(line).strip())
                    continue
                if len(line.split()) > 1:
                    # A new data set starts
                    data_set_count += 1
                    # Return all dimensions as ints
                    xdim, ydim, total_counts = [int(i) for i in line.split()]
                    continue
                if data_set_count == 0:
                    rawdata.append(float(stripline))
                if data_set_count == 1:
                    if not both_sets:
                        break
                    rawdata1.append(float(stripline))

        # Get E range and angle range
        if not self.measurement_ranges:
            for i in comments:
                thisline = i.split()
                if "ERange" in i:
                    ranges_dict.update(
                        {"E_min": float(thisline[3]), "E_max": float(thisline[4])}
                    )
                if "aRange" in i:
                    ranges_dict.update(
                        {"a_min": float(thisline[3]), "a_max": float(thisline[4])}
                    )
        # Reformat data
        data = self.reshape_data(rawdata, ydim)
        extent = [
            ranges_dict["a_min"],
            ranges_dict["a_max"],
            ranges_dict["E_min"],
            ranges_dict["E_max"],
        ]

        if both_sets:
            data1 = self.reshape_data(rawdata1, ydim)
            return np.array(data), np.array(data1)

        return np.array(data), extent

    def read_multiple_sp2(self, filenames, both_sets=False):
        """ Only reads defined sp2 files """
        if len(filenames) == 1:
            self.multi_file_mode = False

        starttime = time.time()
        iterate_list = natsorted(filenames)
        with multiprocessing.Pool() as p:
            out = p.map(self.read_sp2, iterate_list)

            # Can be optimized by removing loop and putting it in self.read_sp2
            ranges_dict = []
            for n, results in enumerate(out):
                data, this_dict = results[0], results[1]
                ranges_dict.append(this_dict)
                if n == 0:
                    out_arr = data
                else:
                    out_arr = np.dstack((out_arr, data))
        print(
            "Loading {} took {:.1f} seconds".format(
                len(filenames), time.time() - starttime
            )
        )
        return out_arr, ranges_dict

    def single_thread_sp2(self, filenames, both_sets=False):
        starttime = time.time()
        pb = ProgressBar()
        files_max_count = len(filenames)
        for n, filename in enumerate(natsorted(filenames)):
            data = self.read_sp2(filename, both_sets)
            if n == 0:
                out_arr = data
            else:
                out_arr = np.dstack((out_arr, data))
            progress = round(n / files_max_count * 100, 0)
            pb.setValue(progress)
            QApplication.processEvents()

        pb.close()
        print("Time_elaped = {}".format(time.time() - starttime))
        return out_arr

    def tidy_up_list(self, inlist):
        """ Remove all files that are not .sp2 """
        outlist = []
        for i in inlist:
            if i.endswith(".sp2"):
                outlist.append(i)
        return outlist

    def reshape_data(self, indata: list, ydim: int):
        """ Turns 1D array into proper 2D array """
        indata = np.array(indata)
        indata = np.array(indata)
        indata = np.reshape(indata, (ydim, -1))
        data = np.swapaxes(indata, 0, 1)[::-1]
        return data


class LoadHDF5(object):
    def __init__(self, location):
        self._filelocation = location
        pmin, pmax, dmin, dmax, Emin, Emax, data = self.load()
        self._pmin = pmin
        self._pmax = pmax
        self._dmin = dmin
        self._dmax = dmax
        self._Emin = Emin
        self._Emax = Emax

        self.data_stack = np.asarray(data)
        self.data_stack = np.swapaxes(self.data_stack, 0, 2)
        self.data_stack = self.data_stack[::-1, :, :]
        self.extent = [self._dmin, self._dmax, self._Emin, self._Emax]
        self.extent_stack = [list(self.extent)] * self.data_stack.shape[-1]

    def load(self):
        f = h5.File(self._filelocation, "r")
        data = f["entry1/analyser/data"]
        d = f["entry1/analyser/angles"]
        E = f["entry1/analyser/energies"]
        p = f["entry1/analyser/sapolar"]
        return p[0], p[-1], d[0], d[-1], E[0], E[-1], data

    def return_data(self):
        return self.data_stack, self.extent_stack, self._pmin, self._pmax


if __name__ == "__main__":
    sp2 = Sp2_loader()
    out_data = sp2.read_sp2("mos2_2_015.sp2")
    plt.imshow(out_data)
    plt.show()
