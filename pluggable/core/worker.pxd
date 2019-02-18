
from .plugin cimport Plugin


cdef class CoreWorkerPlugin(Plugin):
     cpdef add_hooks(self)
