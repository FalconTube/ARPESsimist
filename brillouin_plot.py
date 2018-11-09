import numpy as np


def calc_brillouin(a):
    """ Calculates hexagonal brillouin zone points, returns points """

    def rotmat(theta):
        """ 2D Rotation matrix """
        rotated = [
            [np.cos(theta * np.pi / 180.0), -np.sin(theta * np.pi / 180.0)],
            [np.sin(theta * np.pi / 180.0), np.cos(theta * np.pi / 180.0)],
        ]
        return np.asarray(rotated)

    # a = 3.356  # http://www.rsc.org/suppdata/c6/cp/c6cp06732h/c6cp06732h1.pdf

    K0 = [
        np.cos(30.0 * np.pi / 180.0) * 2 * np.pi / (np.sqrt(3) * a),
        np.sin(30.0 * np.pi / 180.0) * 2 * np.pi / (np.sqrt(3) * a),
    ]
    Kx = []
    Ky = []

    for i in range(6):
        rotval = 60 * i + 60
        if i == 0:  # Append first point for full heaxgon
            Kx.append(K0[0])
            Ky.append(K0[1])

        k = np.dot(rotmat(rotval), K0)
        Kx.append(k[0])
        Ky.append(k[1])
    return Kx, Ky
