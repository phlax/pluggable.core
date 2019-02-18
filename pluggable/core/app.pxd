
from aioworker.app cimport App as BaseApp
from aioworker.worker cimport Worker

from pluggable.core.hooks cimport Hook


cdef class App(BaseApp):
    cdef public Worker worker
    cdef public dict config
    cdef public dict caches
    cdef public dict hooks
    cdef public dict plugins
    cdef public list _plugins
    cdef public signals
    cdef public loop
    cdef public sessions
    cdef public commands

    cpdef void create_config(self, dict config)
    cpdef import_plugins(self)
    cpdef setup_plugins(self)
    cpdef configure(self, dict config)
    cpdef Hook create_hook(self, dict kwargs=*)
    cpdef create_hooks(self)
    cpdef setup_loop(self)
