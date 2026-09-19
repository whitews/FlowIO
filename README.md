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

### Metadata probe and lazy DATA access

For channel / `$TOT` / datatype checks without loading events, open a file with
`FlowData(path, only_text=True)`. That parses HEADER + TEXT (and ANALYSIS) and
leaves `events` as `None`, while still exposing DATA offsets and related metadata.

For uniform IEEE float layouts (`$DATATYPE=F` or `D`), you can then memory-map or
subsample events without a full in-memory load:

```python
from flowio import FlowData

# Lightweight metadata probe
meta = FlowData("sample.fcs", only_text=True)
print(meta.pnn_labels, meta.event_count, meta.data_type)

# Read-only memmap shaped (event_count, channel_count); raw on-disk values
mm = meta.as_memmap()

# Selected 0-based event rows (preprocessed by default, like as_array())
rows = meta.read_events(indices=[0, 10, 100])

# Raw stored values without gain/log/time scaling
raw_rows = meta.read_events(indices=[0, 10, 100], preprocess=False)
```

ASCII and variable bit-width integer layouts raise `UnsupportedLazyDataError` from
these helpers; load those files normally (without `only_text=True`) and use
`read_events()` / `as_array()` on the in-memory events.
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

### Source builds and preprocessing extension

FlowIO now includes an optional C extension for event preprocessing. Normal
`pip install .` and editable `pip install -e .` builds will attempt to compile
the extension automatically when a supported compiler and the NumPy headers are
available. If the extension cannot be built, FlowIO remains usable and falls
back to the existing Python/NumPy preprocessing implementation.

The extension is compiled with conservative floating-point flags on supported
compilers to reduce environment-dependent differences in the preprocessing math.
For GCC/Clang builds this includes disabling floating-point contraction
(`-ffp-contract=off`) and avoiding fast-math reassociation; x86/x86_64 builds
also disable FMA code generation (`-mno-fma`). MSVC builds use `/fp:strict`.
These settings improve reproducibility for FlowIO's preprocessing path, but they
do **not** guarantee bit-identical transcendental `pow()` results across every
operating system, C library, CPU architecture, or compiler toolchain.

For release wheels, build and test platform-specific wheels with the intended
toolchain on each supported platform rather than assuming a source build on an
end-user machine will reproduce the exact same floating-point results.

## Documentation

The FlowIO API documentation is available [on ReadTheDocs here](https://flowio.readthedocs.io/en/latest/?badge=latest). If you have any questions about FlowIO or find any bugs [please submit an issue to the GitHub repository here](https://github.com/whitews/FlowIO/issues/new/).

### Changelogs

[Changelogs for versions are available here](https://github.com/whitews/FlowIO/releases)
