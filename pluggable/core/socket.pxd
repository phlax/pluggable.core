
from .plugin cimport Plugin


cdef class CoreSocketPlugin(Plugin):
     cpdef add_hooks(self)
     cpdef public loop
