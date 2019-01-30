from __future__ import division, absolute_import, print_function
import os, platform, subprocess
from setuptools import find_packages
from numpy.distutils.core import setup, Extension
from distutils.command.sdist import sdist
import sys
import glob

#extension_packages = {'arpessimist': ['src/*.so', 'src/images/*']}

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

REQUIRES_PYTHON = '>=3.5.0'

# build requirements
def build_objects_from_fortran(sources):
  objects = []
  path_base = os.path.join(
    'build',
    'temp.' + platform.system().lower() + '-'
    + platform.machine() + '-'
    + '.'.join(platform.python_version_tuple()[:2]))
  for source in sources:
    path_dir, name = source.rsplit(os.path.sep, 1)
    path_dir_object = os.path.join(path_base, path_dir)
    if not os.path.exists(path_dir_object):
      os.makedirs(path_dir_object)
    path_object = os.path.join(
      path_dir_object,
      os.path.splitext(name)[0] + '.o')
    objects.append(os.path.relpath(path_object))
    command_compile_fortran_mod = (
      'gfortran ' + ' -O3 -fPIC -c ' + source + ' -o ' + path_object)

    print(command_compile_fortran_mod)
    subprocess.check_output(command_compile_fortran_mod, shell=True)
  return objects

ext_folder = 'arpessimist/fortran_routines/'

object_sources = [ext_folder + 'bspline_kinds_module.f90',
    ext_folder + 'bspline_sub_module.f90',
    ext_folder + 'bspline_oo_module.f90',
    ext_folder + 'bspline_module.f90',
    ]
# build requirements
extra_objects = build_objects_from_fortran(object_sources)
# build kmap extension
ext_sources = [ext_folder + 'kmaps.f90']
extensions = Extension(
        name = 'kmaps',
        sources = ext_sources,
        extra_objects = extra_objects,
        )
# Get the long description from the README file

metadata = dict(
    name='arpessimist',  # Required
    version='0.1.10',  # Required
    description='ARPES evaluation software',  # Optional
    long_description=long_description,  # Optional
    url='https://github.com/FalconTube/ARPESsimist',  # Optional
    author='Yannic Falke',  # Optional
    author_email='yannic.falke@gmail.com',  # Optional
    python_requires=REQUIRES_PYTHON,
    platforms = ['Linux'],
    classifiers=[  # Optional
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
    ],
    package_dir={'arpessimist' : 'arpessimist'},
    packages=find_packages(
        exclude='logo'
        ),  # Required
    #package_data=extension_packages,
    entry_points={  # Optional
        'console_scripts': [
            # 'arpessimist=arpessimist/src:main_gui.py',
            'arpessimist=arpessimist:main_gui.run',
        ],
    },
    #include_package_data=True,
    install_requires=['setuptools',
                    'PyWavelets',
                    'h5py',
                    'matplotlib',
                    'numpy',
                    'scipy',
                    'natsort',
                    'PyQt5',
                    ],  # Optional
    zip_safe=False,
    ext_modules = [extensions],
    cmdclass={'sdist' : sdist},
)

setup(**metadata)
