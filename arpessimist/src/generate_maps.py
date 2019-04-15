import numpy as np
import os
import scipy.interpolate as itpt
from PyQt5.QtCore import QThread

# import mayavi.mlab as mlb
# import h5py as h5
import time
from ..kmaps import kmaps
from .new_k_window import K_Window

me = 9.11e-31
m_e = 9.11e-31
hbar = 1.054e-34
deg = np.pi / 180
rad = 180 / np.pi


class VerticalSlitPolarScan(object):
    """ Calculate K-Map with Vertical Slits """

    def __init__(
        self,
        data_stack,
        ranges_stack,
        map_start,
        map_end,
        angle_offset,
        p_offset,
        kxmin,
        kxmax,
        kymin,
        kymax,
    ):
        # self.data = np.swapaxes(data_stack, 0, 2)
        self.data = data_stack
        ranges_stack = ranges_stack[0]
        self.dmin, self.dmax = ranges_stack[0], ranges_stack[1]
        self.Emin, self.Emax = ranges_stack[2], ranges_stack[3]
        self.pmin = map_start
        self.pmax = map_end  # map_start + dmap * \
        self.angle_offset = angle_offset  # Offset in Angle
        self.p_offset = p_offset  # Offset in Polar or Azimuth
        self.kxmin = kxmin
        self.kxmax = kxmax
        self.kymin = kymin
        self.kymax = kymax
        self.kmap_out = 0

        # self._f = self.interpolatePointCloud(self.data)

    def convertAngleToK(self, a, E):
        ev_to_j = 1.6e-19
        return np.sqrt(2 * m_e * E * ev_to_j) * np.sin(a * np.pi / 180.0) * 1e-10 / hbar

    def get_kmap(self):
        return self.kmap_out

    def interpolatePointCloud(self, array):
        """ Generate interpolator for 3D space """
        y = np.linspace(
            self.dmin + self.angle_offset,
            self.dmax + self.angle_offset,
            self.data.shape[1],
        )
        z = np.linspace(self.Emin, self.Emax, self.data.shape[2])
        x = np.linspace(self.pmin, self.pmax, self.data.shape[0])

        f = itpt.RegularGridInterpolator(
            (x, y, z), array, bounds_error=False, fill_value=0.0
        )

        return f

    def getkVals(self, kstart, theta, N):
        k = np.linspace(0, 1.0, int(N))
        kx = k * np.cos(theta * np.pi / 180) + kstart[0]
        ky = k * np.sin(theta * np.pi / 180) + kstart[1]
        return kx, ky

    def calc_k(self, E, kpar, kperp):
        """ Calculate K value depending on E, kpar, kperp """
        inner_sqrt_term = np.sqrt(kpar ** 2 + kperp ** 2) * 0.512317 ** (-2)
        return 0.512317 * np.sqrt(E + inner_sqrt_term), inner_sqrt_term

    def a_tilt(self, kx, ky, kz, az, tlt):
        atilt = np.arcsin(
            (kx * np.sin(az) + ky * np.cos(az)) * np.cos(tlt) - kz * np.sin(tlt)
        )
        return atilt

    def cos_pol(self, kz, tlt, atilt):
        cospol = (kz - np.sin(tlt) * np.sin(atilt)) / (np.cos(tlt) * np.cos(atilt))
        return cospol

    def pol(self, atilt, az, tlt, kx, cospol):
        pol = np.arcsin(
            (
                np.sin(atilt) * np.sin(az) * np.cos(tlt)
                - kx
                + np.cos(atilt) * cospol * np.sin(az) * np.sin(tlt)
            )
            / (np.cos(atilt) * np.cos(az))
        )
        return pol

    def EDC(self, _kx, _ky, Estart, Estop, azi, tilt, NE=120):
        EDC = np.zeros(NE)
        # a1 = _kx
        # a2 = _ky
        erange = np.linspace(Estart, Estop, NE)
        for countE, E in enumerate(erange):
            for i in np.linspace(-0.01, 0.01, 10):
                for j in np.linspace(-0.01, 0.01, 10):
                    a1 = _kx + i
                    a2 = _ky + j
                    k, inner_sqrt_term = self.calc_k(E, a1, a2)
                    kx = a1 / k
                    ky = a2 / k
                    kz = np.sqrt(1.0 - kx ** 2 - ky ** 2)

                    tlt = tilt * deg
                    az = -azi * deg
                    # Perform euler transformations
                    atilt = self.a_tilt(kx, ky, kz, az, tlt)
                    cospol = self.cos_pol(kz, tlt, atilt)
                    pol = self.pol(atilt, az, tlt, kx, cospol)
                    # Add results
                    arr_x = -pol * rad
                    arr_y = atilt * rad
                    arr_z = E  # +np.interp(inner_sqrt_term,
                    #           self._offsetsX, self._offsets)
                    EDC[countE] += self._f((arr_x, arr_y, arr_z))
        return EDC

    def SliceE(self, kstart, theta, Estart, Estop, azi, tilt, NK=50, NE=120):
        ESlice = np.zeros((NK, NE))
        kx, ky = self.getkVals(kstart, theta, NK)
        erange = np.linspace(Estart, Estop, NE)
        for countK, (a1, a2) in enumerate(zip(kx, ky)):
            for countE, E in enumerate(erange):
                k, inner_sqrt_term = self.calc_k(E, a1, a2)
                kx = a1 / k
                ky = a2 / k
                kz = np.sqrt(1.0 - kx ** 2 - ky ** 2)

                tlt = tilt * deg
                az = -azi * deg
                atilt = self.a_tilt(kx, ky, kz, az, tlt)
                cospol = self.cos_pol(kz, tlt, atilt)
                pol = self.pol(atilt, az, tlt, kx, cospol)
                arr_x = -pol * rad
                arr_y = atilt * rad
                arr_z = E  # +np.interp(inner_sqrt_term,
                #         self._offsetsX, self._offsets)

                ESlice[countK, countE] += self._f(
                    (arr_x, arr_y, arr_z), inner_sqrt_term
                )
        return ESlice.T[::-1, :]

    def SliceK(self, E, dk, azi, tilt, kxmax=0.5, kxmin=-0.5, kymax=0.5, kymin=-0.5):
        # azi=0.
        kx_range = int((kxmax - kxmin) / dk)
        ky_range = int((kymax - kymin) / dk)
        kSlice = np.zeros((kx_range, ky_range))
        print("python slice, ", kx_range, ky_range)
        for i in range(0, int(kx_range)):
            a1 = kxmin + i * dk
            for j in range(0, int(ky_range)):
                a2 = kymin + j * dk
                k, inner_sqrt_term = self.calc_k(E, a1, a2)
                # ky = a1/k
                # kx = a2/k
                kx = a1 / k
                ky = a2 / k
                kz = np.sqrt(1.0 - kx ** 2 - ky ** 2)
                # print(kx, ky, kz)
                tlt = tilt * deg
                az = -azi * deg
                atilt = self.a_tilt(kx, ky, kz, az, tlt)
                cospol = self.cos_pol(kz, tlt, atilt)
                pol = self.pol(atilt, az, tlt, kx, cospol)
                # print(atilt, cospol, pol)
                arr_x = -pol * rad
                arr_y = atilt * rad
                arr_z = E
                kSlice[i, j] += self._f((arr_x, arr_y, arr_z))

        return kSlice.T

    def slice_K_fortran(self, dk, dE, azi, tilt, useazi=False, single_slice=False):
        print('poff {}'.format(self.p_offset))
        """ Performs K Slice in fortran routine """
        # self.data = self.data[:, ::2, ::2]
        if single_slice == False:
            Ecutmin = self.Emin
            Ecutmax = self.Emax
            print(self.convertAngleToK(self.dmin + self.angle_offset, self.Emin))
            print(self.convertAngleToK(self.dmax + self.angle_offset, self.Emax))
            Ecut_range = np.arange(Ecutmin, Ecutmax, dE)
        else:
            Ecut_range = np.array([single_slice])
        kx_range = np.arange(self.kxmin, self.kxmax+dk, dk)
        ky_range = np.arange(self.kymin, self.kymax+dk, dk)
        prefac = self.kymax + self.kymin # Somehow there is a stange offset,
        # This prefac is correcting it

        if useazi:
            self.data = np.swapaxes(self.data, 0, 1)
            # Azimuthal range
            indata_z = (
                np.linspace(self.pmin, self.pmax, self.data.shape[2]) + self.p_offset
            )  # Azimuth
            indata_x = (
                np.linspace(self.dmin, self.dmax, self.data.shape[0])
                + self.angle_offset
            )  # Angle
            indata_y = np.linspace(self.Emin, self.Emax, self.data.shape[1])  # Energy
            kSlice = kmaps.kslice_spline_horizontal(
                indata_x,
                indata_y,
                indata_z,
                self.data,
                kx_range,
                ky_range-prefac,
                Ecut_range,
                tilt,
                azi,
            )
        else:
            self.data = np.swapaxes(self.data, 0, 2)
            # Polar range
            indata_x = (
                np.linspace(self.pmin, self.pmax, self.data.shape[0]) + self.p_offset
            )  # Azimuth
            indata_y = (
                np.linspace(self.dmin, self.dmax, self.data.shape[1])
                + self.angle_offset
            )  # Angle
            indata_z = np.linspace(self.Emin, self.Emax, self.data.shape[2])  # Energy
            kSlice = kmaps.kslice_spline(
                indata_x,
                indata_y,
                indata_z,
                self.data,
                kx_range,
                ky_range,
                Ecut_range,
                tilt,
                azi,
            )
        outx = np.swapaxes(kSlice, 0, 1)
        outy = np.swapaxes(kSlice, 0, 2)
        outE = np.swapaxes(kSlice, 1, 2)
        outE = np.swapaxes(outE, 0, 1)

        return (
            outx,
            outy,
            outE,
            self.kxmin,
            self.kxmax,
            self.kymin,
            self.kymax,
            kx_range,
            ky_range,
            Ecut_range,
        )

    # def SliceK_horizontal(self, dk, dE, azi, tilt):
    #     k = 0.512317*np.sqrt(E)
    #     kSlice = np.zeros(((kxmax-kxmin)/dk, (kymax-kymin)/dk))
    #     for i in xrange(0, int((kxmax-kxmin)/dk)):
    #         a1 = kxmin + i*dk
    #         kx = a1/k
    #         for j in xrange(0, int((kymax-kymin)/dk)):
    #             a2 = kymin + j*dk
    #             ky = a2/k
    #             kz = np.sqrt(1-kx**2-ky**2)

    #             tlt = tilt*deg
    #             az = np.arcsin((np.abs(kx)*kz*np.tan(tlt)-np.abs(ky)
    #                             * np.sqrt(1-kz**2 / np.cos(tlt)**2))/(1-kz**2))
    #             pol = np.arcsin(np.abs(ky)*np.sin(az)-np.abs(kx)*np.cos(az))
    #             kSlice[i, j] = self._f((-pol*180/np.pi, E, -az*180/np.pi))
    #     kSlice = np.nan_to_num(kSlice)
    #     # kSlice[np.isneginf(kSlice)] = 0.
    #     # kSlice[np.isposinf(kSlice)] = 0.
    #     # kSlice += np.zeros(kSlice.shape)
    #     return kSlice

    # def SliceK_E_range(self, Ecutmin, Ecutmax, dk, azi, tilt, kxmax=0.5, kxmin=-0.5,
    #                    kymax=0.5, kymin=-0.5):
    #     # azi=0.
    #     kx_range = int((kxmax-kxmin)/dk)
    #     ky_range = int((kymax-kymin)/dk)

    #     print('python slice, ', kx_range, ky_range)
    #     Ecut_range = np.linspace(Ecutmin, Ecutmax, self.data.shape[0])
    #     kSlice = np.zeros((kx_range, ky_range, self.data.shape[0]))
    #     for h, E in enumerate(Ecut_range):
    #         for i in range(0, int(kx_range)):
    #             a1 = kxmin + i*dk
    #             for j in range(0, int(ky_range)):
    #                 a2 = kymin + j*dk
    #                 k, inner_sqrt_term = self.calc_k(E, a1, a2)
    #                 # ky = a1/k
    #                 # kx = a2/k
    #                 kx = a1/k
    #                 ky = a2/k
    #                 kz = np.sqrt(1.-kx**2-ky**2)
    #                 # print(kx, ky, kz)
    #                 tlt = tilt*deg
    #                 az = -azi*deg
    #                 atilt = self.a_tilt(kx, ky, kz, az, tlt)
    #                 cospol = self.cos_pol(kz, tlt, atilt)
    #                 pol = self.pol(atilt, az, tlt, kx, cospol)
    #                 # print(atilt, cospol, pol)
    #                 arr_x = -pol*rad
    #                 arr_y = atilt*rad
    #                 arr_z = E

    #                 kSlice[i, j, h] += self._f((arr_x, arr_y, arr_z))

    #     return kSlice.T


class PointCloudHorizontalSlitAziScan(object):
    """
    This class is responsible for plotting an azimuthal scan of ARPES maps done with a horizontal slit.
    Give it a SpecsFiles class that holds the corresponding map data, the angle-delta between each measurement, the angle offset,
    as well as an offset in the polar axis.
    The class generates a PointCloud by importing all files into a 3D array and linearly interpolates said data. You can then use
    SliceK to calculate the map at a given energy for fixed tilt. Use SliceAngle to get a Slice of the 3D array at a given energy.
    """

    def __init__(self, files, deltaTheta, theta0, d0):
        self._folder = files._folder
        self._dT = deltaTheta  # delta Theta Azimut between each measurement
        self._theta0 = theta0  # Azimut offset
        self.angle_offset = d0  # shift the middle
        self.data = files
        # self.load()
        self._I = self.generatePointCloud()
        self._f = self.interpolatePointCloud(self._I)
        # self.data.load_files()

    def load(self):
        self.data.load_files()

    def generatePointCloud(self, reverse=False):
        """
        generates the Point Cloud, put reverse=True if you would like to see the other direction
        """
        count = 0
        I = np.empty((480, 640, 0))
        for sf in self.data._files:
            if count % 10 == 0:
                pass
            if reverse:
                I = np.dstack((I, sf._data.T[::-1, :]))
            else:
                I = np.dstack((I, sf._data.T))
            count += 1
        return I

    def interpolatePointCloud(self, I):
        count = len(self.data._files)
        x = np.linspace(
            self.data._files[0]._dmin + self.angle_offset,
            self.data._files[0]._dmax + self.angle_offset,
            self.data._files[0]._data.shape[1],
        )
        y = np.linspace(
            self.data._files[0]._Emin,
            self.data._files[0]._Emax,
            self.data._files[0]._data.shape[0],
        )
        z = np.linspace(self._theta0, self._theta0 + count * self._dT, count)
        f = itpt.RegularGridInterpolator(
            (x, y, z), I, bounds_error=False, fill_value=0.0
        )
        return f

    def SliceK(self, E, dk, tilt, kxmax=0.5, kxmin=-0.5, kymax=0.5, kymin=-0.5):
        k = 0.512317 * np.sqrt(E)
        kSlice = np.zeros(((kxmax - kxmin) / dk, (kymax - kymin) / dk))
        for i in range(0, int((kxmax - kxmin) / dk)):
            a1 = kxmin + i * dk
            kx = a1 / k
            for j in range(0, int((kymax - kymin) / dk)):
                a2 = kymin + j * dk
                ky = a2 / k
                kz = np.sqrt(1 - kx ** 2 - ky ** 2)

                tlt = tilt * deg
                az = np.arcsin(
                    (
                        np.abs(kx) * kz * np.tan(tlt)
                        - np.abs(ky) * np.sqrt(1 - kz ** 2 / np.cos(tlt) ** 2)
                    )
                    / (1 - kz ** 2)
                )
                pol = np.arcsin(np.abs(ky) * np.sin(az) - np.abs(kx) * np.cos(az))
                kSlice[i, j] = self._f((-pol * 180 / np.pi, E, -az * 180 / np.pi))
        kSlice = np.nan_to_num(kSlice)
        # kSlice[np.isneginf(kSlice)] = 0.
        # kSlice[np.isposinf(kSlice)] = 0.
        # kSlice += np.zeros(kSlice.shape)
        return kSlice

    def SliceAngle(self, E):
        return np.array(
            [
                [
                    self._f((x, E, z))
                    for x in np.linspace(
                        -15 + self.angle_offset, 15 + self.angle_offset, 100
                    )
                ]
                for z in np.linspace(
                    self._theta0,
                    self._theta0 + len(self.data._files) * self._dT,
                    len(self.data._files),
                )
            ]
        )
