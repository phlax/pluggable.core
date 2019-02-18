# distutils: define_macros=CYTHON_TRACE_NOGIL=1
# cython: linetrace=True
# cython: binding=True
# cython: language_level=3


async def cy_async_fun(dict arg1, arg2: dict) -> str:
    pass


def cy_fun(dict arg1, arg2: dict) -> str:
    pass
