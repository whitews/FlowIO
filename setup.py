"""
Setup script for the FlowIO package
"""
from setuptools import setup

# read in version string
VERSION_FILE = 'src/flowio/_version.py'
__version__ = ''  # to avoid inspection warning and check if __version__ was loaded
exec(open(VERSION_FILE).read())

# empty strings evaluate as False in a boolean context
if not __version__:
    raise RuntimeError("__version__ string not found in file %s" % VERSION_FILE)

setup(
    packages=['flowio'],
    package_dir={'': "src"},
    package_data={'': []}
)
