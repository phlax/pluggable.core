# distutils: define_macros=CYTHON_TRACE_NOGIL=1
# cython: linetrace=True


class User(object):
    verified = False

    def __init__(self, **kwargs):
        self.kwargs = kwargs
