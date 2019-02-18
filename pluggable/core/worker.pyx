# distutils: define_macros=CYTHON_TRACE_NOGIL=1
# cython: linetrace=True
# cython: binding=True

from aioworker.worker cimport Worker

from .auth.data cimport CouchAuthData
from .auth.users cimport UserManager
from .auth.session cimport SessionManager
from .plugin cimport Plugin
from .managers.l10n cimport L10nManager


cdef class CoreWorkerPlugin(Plugin):

    @property
    def name(self):
        return 'core'

    cpdef add_hooks(self):
        self.app.hooks['auth.data'].register(CouchAuthData)
        self.app.hooks['auth.usermanager'].register(UserManager)
        self.app.hooks['auth.sessions'].register(SessionManager)
        self.app.hooks['tasks'].register(
            {'core.tasks': 'pluggable.core.tasks'})
        self.app.hooks['data'].register(self.data)
        self.app.hooks['managers'].register(self.managers)

    async def data(self, data):
        data["global/l10n"] = await self.app.couchdb.db('global/l10n')

    async def managers(self, managers):
        managers["l10n"] = L10nManager(self.app)
