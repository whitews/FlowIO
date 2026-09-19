#define PY_SSIZE_T_CLEAN
#define NPY_NO_DEPRECATED_API NPY_1_19_API_VERSION

#include <Python.h>
#include <numpy/arrayobject.h>
#include <math.h>


static int
validate_channels(PyArrayObject *events,
                  PyArrayObject *decades,
                  PyArrayObject *log0,
                  PyArrayObject *ranges,
                  PyArrayObject *gains)
{
    npy_intp channel_count;
    PyArrayObject *arrays[4] = {decades, log0, ranges, gains};
    const char *names[4] = {"decades", "log0", "ranges", "gains"};
    int idx;

    if (PyArray_NDIM(events) != 2) {
        PyErr_SetString(PyExc_ValueError, "events must be a 2-D float64 NumPy array");
        return 0;
    }

    channel_count = PyArray_DIM(events, 1);

    for (idx = 0; idx < 4; idx++) {
        if (PyArray_NDIM(arrays[idx]) != 1) {
            PyErr_Format(
                PyExc_ValueError,
                "%s must be a 1-D float64 NumPy array",
                names[idx]
            );
            return 0;
        }

        if (PyArray_DIM(arrays[idx], 0) != channel_count) {
            PyErr_Format(
                PyExc_ValueError,
                "%s must contain one value per channel (%zd != %zd)",
                names[idx],
                (Py_ssize_t) PyArray_DIM(arrays[idx], 0),
                (Py_ssize_t) channel_count
            );
            return 0;
        }
    }

    return 1;
}


static PyObject *
apply_preprocessing(PyObject *self, PyObject *args)
{
    PyObject *events_obj;
    PyObject *decades_obj;
    PyObject *log0_obj;
    PyObject *ranges_obj;
    PyObject *gains_obj;
    PyArrayObject *events = NULL;
    PyArrayObject *decades = NULL;
    PyArrayObject *log0 = NULL;
    PyArrayObject *ranges = NULL;
    PyArrayObject *gains = NULL;
    npy_intp row;
    npy_intp col;
    npy_intp row_count;
    npy_intp channel_count;
    double *events_data;
    double *decades_data;
    double *log0_data;
    double *ranges_data;
    double *gains_data;

    if (!PyArg_ParseTuple(
        args,
        "OOOOO:apply_preprocessing",
        &events_obj,
        &decades_obj,
        &log0_obj,
        &ranges_obj,
        &gains_obj
    )) {
        return NULL;
    }

    events = (PyArrayObject *) PyArray_FROM_OTF(
        events_obj,
        NPY_FLOAT64,
        NPY_ARRAY_INOUT_ARRAY2
    );
    if (events == NULL) {
        goto error;
    }

    decades = (PyArrayObject *) PyArray_FROM_OTF(
        decades_obj,
        NPY_FLOAT64,
        NPY_ARRAY_IN_ARRAY
    );
    log0 = (PyArrayObject *) PyArray_FROM_OTF(
        log0_obj,
        NPY_FLOAT64,
        NPY_ARRAY_IN_ARRAY
    );
    ranges = (PyArrayObject *) PyArray_FROM_OTF(
        ranges_obj,
        NPY_FLOAT64,
        NPY_ARRAY_IN_ARRAY
    );
    gains = (PyArrayObject *) PyArray_FROM_OTF(
        gains_obj,
        NPY_FLOAT64,
        NPY_ARRAY_IN_ARRAY
    );

    if (
        decades == NULL ||
        log0 == NULL ||
        ranges == NULL ||
        gains == NULL
    ) {
        goto error;
    }

    if (!validate_channels(events, decades, log0, ranges, gains)) {
        goto error;
    }

    row_count = PyArray_DIM(events, 0);
    channel_count = PyArray_DIM(events, 1);
    events_data = (double *) PyArray_DATA(events);
    decades_data = (double *) PyArray_DATA(decades);
    log0_data = (double *) PyArray_DATA(log0);
    ranges_data = (double *) PyArray_DATA(ranges);
    gains_data = (double *) PyArray_DATA(gains);

    for (row = 0; row < row_count; row++) {
        npy_intp row_offset = row * channel_count;

        for (col = 0; col < channel_count; col++) {
            double value = events_data[row_offset + col];

            if (decades_data[col] > 0.0) {
                value = pow(
                    10.0,
                    decades_data[col] * value / ranges_data[col]
                ) * log0_data[col];
            }

            if (gains_data[col] != 1.0 && gains_data[col] != 0.0) {
                value = value / gains_data[col];
            }

            events_data[row_offset + col] = value;
        }
    }

    PyArray_ResolveWritebackIfCopy(events);
    Py_DECREF(decades);
    Py_DECREF(log0);
    Py_DECREF(ranges);
    Py_DECREF(gains);

    return (PyObject *) events;

error:
    PyArray_DiscardWritebackIfCopy(events);
    Py_XDECREF(events);
    Py_XDECREF(decades);
    Py_XDECREF(log0);
    Py_XDECREF(ranges);
    Py_XDECREF(gains);
    return NULL;
}


static PyMethodDef module_methods[] = {
    {
        "apply_preprocessing",
        apply_preprocessing,
        METH_VARARGS,
        "Apply FlowIO preprocessing to a float64 2-D event array."
    },
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef module_definition = {
    PyModuleDef_HEAD_INIT,
    "_preprocessing_ext",
    NULL,
    -1,
    module_methods
};


PyMODINIT_FUNC
PyInit__preprocessing_ext(void)
{
    import_array();
    return PyModule_Create(&module_definition);
}
