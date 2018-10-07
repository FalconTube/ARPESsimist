import numpy as np
import kmaps


xd = np.linspace(0, 2, 6)
yd = np.linspace(0, 2, 6)
zd = np.linspace(0, 2, 6)

fq = np.zeros((6, 6, 6))
for n, x in enumerate(xd):
    for m, y in enumerate(yd):
        for l, z in enumerate(zd):
            piov2 = 2.0*np.arctan(1.0)
            fq[n, m, l] = 0.5*(y*np.exp(-x) + z*np.sin(piov2*y))
            # fq[n, m, l] = ((x + 2.0 * y + 3.0 * z) / 6.0)**2
# print(fq)
# l = int(3)
# kmaps.kmaps.printer(l)
print(type(fq))
# evalx, evaly, evalz = [0.1, 0.22, 0.33]
evalx = 0.5
evaly = 0.5
evalz = 0.5
outval = kmaps.kmaps.kslice(xd, zd, yd,  fq,
                            evalx, evaly, evalz)
# outval = kmaps.kmaps.kslice()
print(outval)
# print(out)
