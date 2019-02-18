# distutils: define_macros=CYTHON_TRACE_NOGIL=1
# cython: linetrace=True
# cython: binding=True

from typing import Callable, Union


cdef class Hook(object):

    def __cinit__(self, sync=True):
        self._sync = sync

    @property
    def cbs(self) -> list:
        if self._cbs is None:
            self._cbs = []
        return self._cbs

    cpdef register(self, cb: Callable):
        self.cbs.append(cb)

    def get(self, *args, **kwargs):
        return (
            self.cbs[0](*args, **kwargs)
            if self.cbs
            else None)

    cpdef gather(self, result=None):
        if not self._sync:
            return self.async_gather(result)
        else:
            out = {}
            for cb in self.cbs:
                (out.update(cb())
                 if callable(cb)
                 else out.update(cb))
            return out

    async def async_gather(self, result) -> None:
        for cb in self.cbs:
            await cb(result)
