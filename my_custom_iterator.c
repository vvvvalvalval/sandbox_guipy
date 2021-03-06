#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "structmember.h"

// https://docs.python.org/3/extending/extending.html

typedef struct {
    PyObject_HEAD
    int start;
    int end;
    int cursor;
    char content_hash;
} MyCustomIterator;

static void
Custom_dealloc(MyCustomIterator *self)
{
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject *
Custom_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    MyCustomIterator *self;
    self = (MyCustomIterator *) type->tp_alloc(type, 0);
    if (self != NULL) {
        self->start = 0;
        self->end = 0;
        self->cursor = 0;
        self->content_hash = (char) 0;
    }
    return (PyObject *) self;
}

static int
Custom_init(MyCustomIterator *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"start", "end", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|ii", kwlist,
                                     &self->start,
                                     &self->end))
        return -1;
    if(self->end < self->start)
        return -1;
    self->cursor = self->start;
    return 0;
}

static PyMemberDef Custom_members[] = {
    {"start", T_INT, offsetof(MyCustomIterator, start), 0,
     "Where the range starts, inclusive."},
    {"end", T_INT, offsetof(MyCustomIterator, end), 0,
     "Where the range ends, exclusive."},
    {"content_hash", T_INT, offsetof(MyCustomIterator, content_hash), 0,
     "A digest of the data supplied so far."},
    {NULL}  /* Sentinel */
};

static PyObject * Custom_addBytes(MyCustomIterator *self, PyObject *data){
  // https://docs.python.org/3/c-api/bytes.html
  if (!PyBytes_Check(data)){
    return NULL;
  }
  Py_ssize_t l =  PyBytes_Size(data);
  char * payload = PyBytes_AsString(data);
  char hash = self->content_hash;
  for(Py_ssize_t i = 0; i < l; i++){
    hash = hash ^ payload[i];
  }
  self->content_hash = hash;
  Py_RETURN_NONE
}

static PyObject *
Custom_hasNext(MyCustomIterator *self, PyObject *Py_UNUSED(ignored))
{
    if(self->cursor < self->end)
    { // https://docs.python.org/3/c-api/bool.html
      Py_RETURN_TRUE
    } else
    {
      Py_RETURN_FALSE
    }
}

static PyObject *
Custom_next(MyCustomIterator *self, PyObject *Py_UNUSED(ignored))
{
    if(self->cursor < self->end) {
      //PyObject * ret = PyLong_FromLong((long) self->cursor);

      Py_ssize_t l = 5;
      // PyList reference: https://docs.python.org/3.3/c-api/list.html?highlight=m
      PyObject * elems = PyList_New(l);
      for(Py_ssize_t i = 0; i < l; i++){
        PyObject * e = PyLong_FromLong((long) self->cursor);
        // https://stackoverflow.com/questions/10863669/lost-on-py-decref-incref-when-handling-pylist-append-in-python-c-extension
        PyList_SetItem(elems, i, e);
      }
      // https://docs.python.org/3/extending/extending.html#building-arbitrary-values
      PyObject * ret = Py_BuildValue("{s:s,s:O,s:i}", "event_type", "data_points", "elements", elems, "content_hash", self->content_hash);
      self->cursor++;
      return ret;
    } else {
      PyErr_SetString(PyExc_RuntimeError, "No more elements.");
      return NULL;
    }
}

static PyMethodDef Custom_methods[] = {
    {"add_bytes", (PyCFunction) Custom_addBytes, METH_O, // https://docs.python.org/3/c-api/structures.html
     "Add data that modifies the state of the iterator."
    },
    {"has_next", (PyCFunction) Custom_hasNext, METH_NOARGS,
     "Whether the iterator is exhausted."
    },
    {"next", (PyCFunction) Custom_next, METH_NOARGS,
     "Returns the next element and moves the cursor."
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject CustomType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "my_custom_iterator.MyRangeIterator",
    .tp_doc = "A basic stateful iterator",
    .tp_basicsize = sizeof(MyCustomIterator),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = Custom_new,
    .tp_init = (initproc) Custom_init,
    .tp_dealloc = (destructor) Custom_dealloc,
    .tp_members = Custom_members,
    .tp_methods = Custom_methods,
};

static PyModuleDef custommodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "my_custom_iterator",
    .m_doc = "Example module that creates an extension type.",
    .m_size = -1,
};

PyMODINIT_FUNC
PyInit_my_custom_iterator(void)
{
    PyObject *m;
    if (PyType_Ready(&CustomType) < 0)
        return NULL;

    m = PyModule_Create(&custommodule);
    if (m == NULL)
        return NULL;

    Py_INCREF(&CustomType);
    if (PyModule_AddObject(m, "MyRangeIterator", (PyObject *) &CustomType) < 0) {
        Py_DECREF(&CustomType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
