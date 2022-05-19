# FlowIO

[![PyPI license](https://img.shields.io/pypi/l/flowio.svg?colorB=dodgerblue)](https://pypi.python.org/pypi/flowio/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/flowio.svg)](https://pypi.python.org/pypi/flowio/)
[![PyPI version](https://img.shields.io/pypi/v/flowio.svg?colorB=blue)](https://pypi.python.org/pypi/flowio/)
[![DOI](https://zenodo.org/badge/14634514.svg)](https://zenodo.org/badge/latestdoi/14634514)


[![Build & test (master)](https://github.com/whitews/FlowIO/actions/workflows/tests_master.yml/badge.svg)](https://github.com/whitews/FlowIO/actions/workflows/tests_master.yml)
[![Build & test (develop)](https://github.com/whitews/FlowIO/actions/workflows/tests_develop.yml/badge.svg)](https://github.com/whitews/FlowIO/actions/workflows/tests_develop.yml)
[![Coverage](https://codecov.io/gh/whitews/FlowIO/branch/master/graph/badge.svg)](https://codecov.io/gh/whitews/flowio)
[![Documentation Status](https://readthedocs.org/projects/flowio/badge/?version=latest)](https://flowio.readthedocs.io/en/latest/?badge=latest)

## Overview

FlowIO is a Python library for reading / writing Flow Cytometry Standard (FCS) 
files and has zero external dependencies. FlowIO is compatible with Python 3.6+ (FlowIO v0.9.9 was the last release supporting Python 2). 

For higher level interaction with flow cytometry data, including GatingML and FlowJo 10 support, 
see the related [FlowKit](https://github.com/whitews/FlowKit) project.

## Installation

The recommended way to install FlowIO is via the `pip` command:

```
pip install flowio
```

Or, if you prefer, you can install from the GitHub source:

```
git clone https://github.com/whitews/flowio
cd flowio
python setup.py install
```

## Usage

FlowIO retrieves event data exactly as it is encoded in the FCS file: as a 
1-dimensional list without separating the events into channels. However, all the metadata 
found within the FCS file is available as a dictionary via the 'text' attribute. Basic attributes
are also available for commonly accessed properties. For example, the channel count 
can be used to easily convert the event data to a multi-column NumPy array:

```
import flowio
import numpy

fcs_data = flowio.FlowData('example.fcs')
npy_data = numpy.reshape(fcs_data.events, (-1, fcs_data.channel_count))
```
