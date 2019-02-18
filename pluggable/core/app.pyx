# distutils: define_macros=CYTHON_TRACE_NOGIL=1
# cython: linetrace=True
# cython: binding=True

import asyncio
from importlib import import_module

import uvloop

from aioworker.app cimport App as BaseApp
from aioworker.worker cimport Worker

from pluggable.core.hooks cimport Hook
from pluggable.core.signals cimport Signals


default_config = ()


cdef class App(BaseApp):

    @property
    def default_config(self):
        return default_config

    def __cinit__(self, Worker worker, dict config):
        self.worker = worker
        self.config = {}
        self.caches = {}
        self.hooks = {}
        self.plugins = {}
        self._plugins = []

    def __init__(self, Worker worker, dict config):
        self.configure(config)

    @property
    def loop_policy(self) -> asyncio.AbstractEventLoopPolicy:
        return uvloop.EventLoopPolicy

    cpdef configure(self, dict config):
        self.create_config(config)
        self.import_plugins()
        self.signals = Signals(self)
        self.setup_loop()
        self.create_hooks()
        self.setup_plugins()
        self.caches = {}

    cpdef Hook create_hook(self, dict kwargs={}):
        return Hook(**kwargs)

    cpdef create_hooks(self):
        pass

    cpdef void create_config(self, dict config):
        self.config.update(dict(self.default_config))
        self.config.update(config)

    cpdef import_plugins(self):
        for _plugin in self.config.get('plugins', []):
            parts = _plugin.split('.')
            klass = parts.pop()
            self._plugins.append(
                getattr(
                    import_module('.'.join(parts)),
                    klass))

    cpdef setup_loop(self):
        should_set_loop_policy = not isinstance(
            asyncio.get_event_loop_policy(),
            self.loop_policy)
        if should_set_loop_policy:
            asyncio.set_event_loop_policy(self.loop_policy())
        self.loop = asyncio.get_event_loop()

    cpdef setup_plugins(self):
        for plugin in self._plugins:
            p = plugin(self)
            self.plugins[p.name] = p


class Py__App(App):
    pass
