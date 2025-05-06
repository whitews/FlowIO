.. FlowIO documentation master file, created by
   sphinx-quickstart on Mon May 10 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

FlowIO Documentation
====================

.. image:: https://img.shields.io/pypi/v/flowio.svg?colorB=dodgerblue
    :target: https://pypi.org/project/flowio/

.. image:: https://img.shields.io/pypi/l/flowio.svg?colorB=green
    :target: https://pypi.python.org/pypi/flowio/

.. image:: https://img.shields.io/pypi/pyversions/flowio.svg
    :target: https://pypi.org/project/flowio/

.. image:: https://img.shields.io/pypi/dm/flowio
   :alt: PyPI - Downloads

FlowIO is a Python library for reading / writing Flow Cytometry Standard (FCS)
files, with minimal dependencies and is compatible with Python 3.9+.

For higher level interaction with flow cytometry data, including GatingML and
FlowJo 10 support, see the related FlowKit_ project.

.. _FlowKit: https://github.com/whitews/FlowKit

Installation
------------

The recommended way to install FlowIO is via the `pip` command:

.. code-block::

    pip install flowio


Or, if you prefer, you can install from the GitHub source:

.. code-block::

    git clone https://github.com/whitews/flowio
    cd flowio
    pip install .

Changelogs
__________

`Changelogs for versions are available here <https://github.com/whitews/FlowIO/releases>`_

----

Tutorials
---------

`FlowIO Tutorial`_

.. _FlowIO Tutorial: notebooks/flowio_tutorial.ipynb

API
---

* :ref:`genindex`

.. toctree::
   :maxdepth: 2

   api
