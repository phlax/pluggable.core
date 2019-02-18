

cdef class Signals:
    cdef public app
    cdef public dict _signals
    cpdef public listen(self, signal, cb)
    cpdef public unlisten(self, signal, cb)
