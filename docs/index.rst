.. FlowIO documentation master file, created by
   sphinx-quickstart on Mon May 10 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

FlowUtils Documentation
=======================

.. image:: https://img.shields.io/pypi/v/flowio.svg?colorB=dodgerblue
    :target: https://pypi.org/project/flowio/

.. image:: https://img.shields.io/pypi/l/flowio.svg?colorB=green
    :target: https://pypi.python.org/pypi/flowio/

.. image:: https://img.shields.io/pypi/pyversions/flowio.svg
    :target: https://pypi.org/project/flowio/

FlowIO is a Python library for reading / writing Flow Cytometry Standard (FCS)
files and has zero external dependencies. FlowIO is compatible with Python 3 (FlowIO v0.9.9 was the last release supporting Python 2).

For higher level interaction with flow cytometry data, including GatingML and FlowJo 10 support,
see the related [FlowKit](https://github.com/whitews/FlowKit) project.

Installation
------------

The recommended way to install FlowIO is via the `pip` command:

.. code-block:: python

    pip install flowio


Or, if you prefer, you can install from the GitHub source:

.. code-block:: python

    git clone https://github.com/whitews/flowio
    cd flowio
    python setup.py install
----

API
---

* :ref:`genindex`

.. toctree::
   :maxdepth: 3

   api
