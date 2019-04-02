import sys
import glob
import os
import numpy as np
import time
from natsort import natsorted
import multiprocessing
import h5py as h5

# import scipy.interpolate as itpt
from scipy.interpolate import interp2d


# from PyQt5.QtCore import QThread
from PyQt5 import QtCore
from PyQt5.QtWidgets import QProgressBar, QWidget, QApplication, QMessageBox, QFileDialog


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
                    rawdata.append(np.uint32(stripline))
                if data_set_count == 1:
                    if not both_sets:
                        break
                    rawdata1.append(np.uint32(stripline))

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

    def read_multiple_sp2(self, filenames, both_sets=False, natsort=True):
        """ Only reads defined sp2 files """
        if len(filenames) == 1:
            self.multi_file_mode = False

        starttime = time.time()
        if natsort:
            iterate_list = natsorted(filenames)
        else:
            iterate_list = filenames
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
                    interpolated, is_data = self.interpolate_data(
                        out_arr, data, this_dict
                    )
                    if is_data:
                        data = interpolated
                    else:
                        if len(out_arr.shape) == 3:
                            out_arr[:, :, -1] = interpolated
                        else:
                            out_arr = interpolated
                    out_arr = np.dstack((out_arr, data))
        if not self.multi_file_mode:
            thisshape = out_arr.shape
            out_arr = out_arr.reshape(thisshape[0], thisshape[1], 1)
        print(out_arr)
        return np.array(out_arr), ranges_dict

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

    def read_with_gui(self, is_sp2=True, location_settings=None, sort=True):
        settings = location_settings
        if is_sp2:
            # Choose Data
            LastDir = "."
            if not settings.value("LastDir") == None:
                LastDir = settings.value("LastDir")
            try:
                many_files = QFileDialog.getOpenFileNames(
                    self.parent, "Select one or more files to open", LastDir
                )
                QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

                LastDir = os.path.dirname(many_files[0][0])
                settings.setValue("LastDir", LastDir)
                # Start loading Data
                sp2 = Sp2_loader()
                # loaded_filenames = sp2.tidy_up_list(many_files[0])
                loaded_filenames = many_files[0]
                fignum = len(loaded_filenames)
                figs_data, figs_extents = sp2.read_multiple_sp2(
                    loaded_filenames, natsort=False
                )
                QApplication.restoreOverrideCursor()
                return figs_data, figs_extents, settings
            except ValueError:
                return

        else:
            LastDir = "."
            if not settings.value("LastDir") == None:
                LastDir = settings.value("LastDir")
            self.statusBar().showMessage("Loading Data...", 2000)
            location = QFileDialog.getOpenFileNames(
                self.parent, "Select one NXS file to open", directory=LastDir, filter='*.nxs')
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            LastDir = os.path.dirname(location[0][0])
            settings.setValue("LastDir", LastDir)

            location = str(location[0][0])
            self.hd5mode = True
            H5loader = LoadHDF5(location)
            angle_data, angle_extent, p_min, p_max = (
                H5loader.return_data()
            )
            QApplication.restoreOverrideCursor()
            return angle_data, angle_extent, p_min, p_max, settings

    def interpolate_data(self, out_arr, data, extent):
        out_data = True
        if len(out_arr.shape) == 3:
            last_set = out_arr[:, :, -1]
        else:
            last_set = out_arr
        if last_set.shape == data.shape:
            return data, out_data
        if last_set.shape < data.shape:
            smaller = last_set
            larger = data
            out_data = False
        else:
            smaller = np.array(data, dtype=np.uint32)
            larger = np.array(last_set, dtype=np.uint32)

        x = np.linspace(extent[0], extent[1], smaller.shape[1])
        y = np.linspace(extent[2], extent[3], smaller.shape[0])

        f = interp2d(x, y, smaller)
        xl = np.linspace(extent[0], extent[1], larger.shape[1])
        yl = np.linspace(extent[2], extent[3], larger.shape[0])

        enlarged = f(xl, yl)
        return np.array(enlarged, dtype=np.uint32), np.array(out_data, dtype=np.uint32)


class LoadHDF5(object):
    def __init__(self, location):
        self._filelocation = location
        self.load()


    def load(self):
        self.f = h5.File(self._filelocation, "r")
        self.fkeys = list(self.f.keys())
        if 'entry1' in self.fkeys:
            self.load_old_nxs()
            self.data_stack = np.asarray(self._data)
            self.data_stack = np.swapaxes(self.data_stack, 0, 2)
            self.data_stack = self.data_stack[::-1, :, :]
            self.extent = [self._dmin, self._dmax, self._Emin, self._Emax]
            self.extent_stack = [list(self.extent)] * self.data_stack.shape[-1]
        if 'Defl' in self.fkeys[0]:
            self.load_deflection_map()
        else:
            self.load_new_nxs()

    def load_deflection_map(self):
        ''' This is just a temporary solution, but we can get latesst dataset
        with a loop and parameters easy, if always fixes'''
        first = self.f[self.fkeys[0]]
        data =np.array(first['scan_data/data_09'])
        print(data.shape)
        # data  = np.swapaxes(data, 0, 2)
        data = data[::-1, ::-1]
        print('Defl Map')
        # data  = np.swapaxes(data, 1, 2)
        print(data.shape)
        extent_stack = []
        for i in range(data.shape[-1]):
            extent = [-13, 12, 34, 35]
            extent_stack.append(extent)
        print(len(extent_stack))

        self.data_stack = data
        self.extent_stack = extent_stack

    def load_old_nxs(self):
        ''' Load HDF5 files before 05/2018 '''
        entry = 'entry1'
        data = self.f["entry1/analyser/data".format(entry)]
        d = self.f["{}/analyser/angles".format(entry)]
        E = self.f["{}/analyser/energies".format(entry)]
        p = self.f["{}/analyser/sapolar".format(entry)]
        self._pmin = p[0]
        self._pmax = p[-1]
        self._dmin = d[0]
        self._dmax = d[-1]
        self._Emin = E[0]
        self._Emax = E[-1]
        self._data = data

    def load_new_nxs(self):
        ''' Load HDF5 files after 05/2018 '''
        found_folder = None
        phi_count  = 0
        out_arr = None
        extent_stack = []
        for basefolder in self.fkeys:
            subfolder = self.f[basefolder]
            subfkeys = list(subfolder.keys())
            for lower_folders in natsorted(subfkeys):
                if not 'MBS_' in lower_folders:
                    continue
                # Here we found all data folders
                datafolder = self.f[basefolder + '/' + lower_folders]
                data = np.array(datafolder['Image32_1'], dtype=np.uint32)\
                        .T[::-1, ::-1]
                if out_arr is None:
                    out_arr = data
                else:
                    out_arr = np.dstack((out_arr, data))
                a_min = float(datafolder['XScaleMin_1'][0])
                a_max = float(datafolder['XScaleMax_1'][0])
                e_min = float(datafolder['EScaleMin_1'][0])
                e_max = float(datafolder['EScaleMax_1'][0])
                if phi_count == 0:
                    self._pmin = float(datafolder['Phi'][0])
                    phi_count += 1
                else:
                    self._pmax = float(datafolder['Phi'][0])

                extent = [a_min, a_max, e_min, e_max]
                extent_stack.append(extent)

        # Found all data, make exportable
        # self.data_stack = np.swapaxes(out_arr, 0, 1)
        self.data_stack = out_arr
        self.extent_stack = extent_stack


    def return_data(self):
        try:
            return self.data_stack, self.extent_stack, self._pmin, self._pmax
        except:
            return self.data_stack, self.extent_stack, None, None

class GUI_Loader(object):
    def __init__(self, parent=None):
        self.parent = parent

    def read_with_gui(self, is_sp2=True, location_settings=None, sort=True):
        settings = location_settings
        if is_sp2:
            # Choose Data
            LastDir = "."
            if not settings.value("LastDir") == None:
                LastDir = settings.value("LastDir")
            try:
                many_files = QFileDialog.getOpenFileNames(
                    self.parent, "Select one or more files to open", LastDir,
                    filter='*.sp2')
                QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

                LastDir = os.path.dirname(many_files[0][0])
                settings.setValue("LastDir", LastDir)
                # Start loading Data
                sp2 = Sp2_loader()
                # loaded_filenames = sp2.tidy_up_list(many_files[0])
                loaded_filenames = many_files[0]
                fignum = len(loaded_filenames)
                figs_data, figs_extents = sp2.read_multiple_sp2(
                    loaded_filenames, natsort=False
                )
                QApplication.restoreOverrideCursor()
                return figs_data, figs_extents, settings
            except ValueError:
                return

        else:
            LastDir = "."
            if not settings.value("LastDir") == None:
                LastDir = settings.value("LastDir")
            self.statusBar().showMessage("Loading Data...", 2000)
            location = QFileDialog.getOpenFileNames(
                self.parent, "Select one NXS file to open", directory=LastDir,
                filter='*.nxs')
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            LastDir = os.path.dirname(location[0][0])
            settings.setValue("LastDir", LastDir)

            location = str(location[0][0])
            self.hd5mode = True
            H5loader = LoadHDF5(location)
            angle_data, angle_extent, p_min, p_max = (
                H5loader.return_data()
            )
            QApplication.restoreOverrideCursor()
            return angle_data, angle_extent, p_min, p_max, settings
