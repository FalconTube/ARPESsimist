"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path
# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='arpessimist',  # Required
    version='0.1.0',  # Required
    description='ARPES evaluation software',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/FalconTube/ARPESsimist',  # Optional
    author='Yannic Falke',  # Optional
    author_email='yannic.falke@gmail.com',  # Optional
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        # 'Intended Audience :: SCIENCE/RESEARCH',
        # 'Topic :: Data Evaluation :: ARPES',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    # packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    # packages=['arpessimist', 'arpessimist/src'],  # Required
    packages=find_packages(),  # Required
    # package_dir={'' : 'arpessimisst'},
    include_package_data=True,
    install_requires=['setuptools>=39.0.1',
                    'PyWavelets>=1.0.1',
                    'h5py>=2.8.0',
                    'matplotlib>=3.0.1',
                    'numpy>=1.13.3',
                    'scipy>=1.1.0',
                    'natsort>=5.4.1',
                    'PyQt5>=5.11.3',
                    'pywt>=1.0.6',
                    ],  # Optional
    package_data={  # Optional
        'arpessimist': ['src/*.so'],
    },
    entry_points={  # Optional
        'console_scripts': [
            # 'arpessimist=arpessimist/src:main_gui.py',
            'arpessimist=arpessimist:main_gui.run',
        ],
    },
)
