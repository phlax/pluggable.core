# distutils: define_macros=CYTHON_TRACE_NOGIL=1
# cython: linetrace=True
# cython: binding=True

from uuid import uuid4


cdef class SessionManager(object):

    def __cinit__(self, app):
        self.app = app

    async def create(self, str username) -> str:
        cdef str uuid = uuid4().hex
        await self.app.caches['session'].execute(
            'set',
            uuid,
            username.encode('utf8'))
        return uuid

    async def get(self, str uuid) -> str:
        return (
            await self.app.caches['session'].execute(
                'get', uuid)).decode('utf8')

    async def delete(self, str uuid):
        return await self.app.caches['session'].execute(
            'del', uuid)


class Py__SessionManager(SessionManager):
    pass
