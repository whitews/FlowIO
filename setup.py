from setuptools import setup

# read in version string
VERSION_FILE = 'flowio/_version.py'
__version__ = ''  # to avoid inspection warning and check if __version__ was loaded
exec(open(VERSION_FILE).read())

# empty strings evaluate as False in a boolean context
if not __version__:
    raise RuntimeError("__version__ string not found in file %s" % VERSION_FILE)

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='FlowIO',
    version=__version__,
    packages=['flowio'],
    package_data={'': []},
    description='FlowIO is a Python library for reading / writing Flow Cytometry Standard (FCS) files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Scott White',
    author_email='whitews@gmail.com',
    license='BSD',
    license_files=('LICENSE',),
    url='https://github.com/whitews/flowio',
    requires=[],
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.7'
    ]
)
