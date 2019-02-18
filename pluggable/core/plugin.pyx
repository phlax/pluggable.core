# distutils: define_macros=CYTHON_TRACE_NOGIL=1
# cython: linetrace=True


cdef class Plugin(object):

    def __init__(self, app):
        self.app = app
        self.add_hooks()
        self.add_listeners()

    def add_hooks(self):
        pass

    def add_listeners(self):
        pass

    def incoming(self):
        pass
