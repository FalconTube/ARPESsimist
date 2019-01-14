import os
import glob
import sys

py_vers = sys.version
wheel_vers = 'py3' + str(py_vers.split('.')[1])
print(wheel_vers)
for file in glob.glob('dist/*.whl'):
    out = file.replace('cp3', wheel_vers)
    os.rename(file, out)
    print('Renamed {} to {}'.format(file, out))
