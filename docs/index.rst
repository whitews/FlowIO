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

FlowIO is a Python library for reading / writing Flow Cytometry Standard (FCS)
files and has zero external dependencies. FlowIO is compatible with Python 3.7+
(FlowIO v0.9.9 was the last release supporting Python 2).

FlowIO retrieves event data exactly as it is encoded in the FCS file: as a
1-dimensional list without separating the events into channels or performing
any preprocessing (e.g. applying gain). However, all the metadata stored in the
FCS file is available as a dictionary via the 'text' attribute. Basic attributes
are also available for commonly accessed properties. For example, the channel
count can be used to easily convert the event data to a multi-column NumPy array:

.. code-block:: python

    import flowio
    import numpy

    fcs_data = flowio.FlowData('example.fcs')
    npy_data = numpy.reshape(fcs_data.events, (-1, fcs_data.channel_count))

For higher level interaction with flow cytometry data, including GatingML and
FlowJo 10 support, see the related FlowKit_ project.

.. _FlowKit: https://github.com/whitews/FlowKit

Changelogs
__________

`Changelogs for versions are available here <https://github.com/whitews/FlowIO/releases>`_

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
