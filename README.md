# FlowIO

[![PyPI license](https://img.shields.io/pypi/l/flowio.svg?colorB=dodgerblue)](https://pypi.python.org/pypi/flowio/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/flowio.svg)](https://pypi.python.org/pypi/flowio/)
[![PyPI version](https://img.shields.io/pypi/v/flowio.svg?colorB=blue)](https://pypi.python.org/pypi/flowio/)
[![DOI](https://zenodo.org/badge/14634514.svg)](https://zenodo.org/badge/latestdoi/14634514)


[![Test (master)](https://github.com/whitews/FlowIO/actions/workflows/tests_master.yml/badge.svg)](https://github.com/whitews/FlowIO/actions/workflows/tests_master.yml)
[![Test (develop)](https://github.com/whitews/FlowIO/actions/workflows/tests_develop.yml/badge.svg)](https://github.com/whitews/FlowIO/actions/workflows/tests_develop.yml)
[![Coverage](https://codecov.io/gh/whitews/FlowIO/branch/master/graph/badge.svg)](https://codecov.io/gh/whitews/flowio)
[![Documentation Status](https://readthedocs.org/projects/flowio/badge/?version=latest)](https://flowio.readthedocs.io/en/latest/?badge=latest)
![PyPI - Downloads](https://img.shields.io/pypi/dm/flowio)

## Overview

FlowIO is a Python library for reading and writing Flow Cytometry Standard (FCS)
files, with minimal dependencies and is compatible with Python 3.9+. It is intended 
as a lightweight library, suitable for parsing FCS data sets (e.g. as a web server 
backend, for simple metadata extraction, etc.). It is **highly recommended** that 
one be familiar with the various FCS file standards (2.0, 3.0, 3,1) before using 
FlowIO for downstream analysis. For higher level cytometry analysis, please see the 
related [FlowKit](https://github.com/whitews/FlowKit) library which offers a much 
wider set of analysis options such as compensation, transformation, and gating 
support (including support for importing FlowJo 10 workspaces).

If you have any questions about FlowIO, find any bugs, or feel something is missing 
from the documentation [please submit an issue to the GitHub repository here](https://github.com/whitews/FlowIO/issues/new/).

## Installation

The recommended way to install FlowIO is via the `pip` command:

```
pip install flowio
```

Or, if you prefer, you can install from the GitHub source:

```
git clone https://github.com/whitews/flowio
cd flowio
pip install .
```

## Documentation

The FlowIO API documentation is available [on ReadTheDocs here](https://flowio.readthedocs.io/en/latest/?badge=latest). If you have any questions about FlowIO or find any bugs [please submit an issue to the GitHub repository here](https://github.com/whitews/FlowIO/issues/new/).

### Changelogs

[Changelogs for versions are available here](https://github.com/whitews/FlowIO/releases)

