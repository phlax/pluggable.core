
from typing import Callable


cdef class Hook:
    cdef _sync
    cdef public list _cbs
    cpdef register(self, cb: Callable)
    cpdef gather(self, result=*)    
