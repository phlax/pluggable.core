# distutils: define_macros=CYTHON_TRACE_NOGIL=1
# cython: linetrace=True
# cython: binding=True

import aioredis
import rapidjson as json

from .auth.session cimport SessionManager
from .plugin cimport Plugin
from .auth.users cimport UserManager

from .tasks import l10n, login, register


cdef class CoreSocketPlugin(Plugin):
    _manager = None
    session_manager = SessionManager

    @property
    def name(self):
        return 'core'

    cpdef add_hooks(self):
        self.app.hooks['auth.sessions'].register(self.session_manager)
        self.app.hooks['tasks.worker'].register(
            {'core.tasks': 'pluggable.core.tasks'})
        self.app.hooks['tasks.local'].register({
            "auth.login": self.login,
            "auth.logout": self.logout,
            "auth.register": self.register,
            "l10n": self.l10n})
        self.app.hooks['caches'].register(self.get_caches)

    async def get_caches(self, caches):
        # this needs to disconnect gracefully
        for k, v in self.app.config["caches"].items():
            caches[k] = await aioredis.create_connection(
                v,
                loop=self.loop)

    async def l10n(
            self,
            connection: int,
            uuid: str,
            language: str,
            filetype: str) -> Union[dict, bytes]:
        # this needs some logic to check if its a recognized lang
        cached = await self.app.caches['l10n'].execute(
            'get',
            ".".join([language, filetype]))
        return (
            cached if cached
            else dict(
                response=(
                    await self._l10n_worker(
                        language, filetype))))

    async def login(
            self,
            connection: int,
            uuid: str,
            session: str = None,
            username: str = None,
            password: str = None):
        user, sessionid = await self._login(session, username, password)
        if sessionid:
            self.app.signals.emit(
                'auth.session.create',
                connection=connection,
                session=sessionid)
        return (
            dict(response=user)
            if sessionid
            else dict(errors=['login.failed']))

    async def logout(self, connection, uuid):
        _connection = self.app.socket.connections[connection]
        await self.app.sessions.delete(_connection['session'])
        self.app.signals.emit(
            'auth.session.destroy',
            connection=connection)
        return dict(response='logged.out')

    async def register(self, connection, uuid, **kwargs):
        session = await register.call(**kwargs)
        if 'session' in session:
            data = dict(user=dict(username=kwargs['username']))
            return dict(
                response=dict(
                    data=data,
                    session=session['session']['_id'],
                    command='ui.auth.register.success'))
        else:
            return dict(errors=['register.failed'])

    async def _l10n_worker(
            self,
            language: str,
            filetype: str) -> dict:
        response = await self.app.worker.tasks["l10n"].call(
            language=language,
            filetype=filetype)
        await self.app.caches['l10n'].execute(
            'set',
            ".".join([language, filetype]),
            json.dumps(response))
        return response

    async def _login_session(self, sessionid: str):
        user = await self.app.sessions.get(sessionid)
        return (
            (None, None)
            if not user
            else (user, sessionid))

    async def _login_worker(self, username: str, password: str):
        user = await login.call(username=username, password=password)
        return (
            (None, None)
            if not user
            else (username, await self.app.sessions.create(username)))

    async def _login(
            self,
            session: str = None,
            username: str = None,
            password: str = None):
        username, sessionid = (
            await self._login_session(session)
            if session and not username
            else await (
                self._login_worker(
                    username,
                    password)))
        return (
            (None, None)
            if not sessionid
            else (
                dict(username=username,
                     _id=sessionid),
                sessionid))


class Py__CoreSocketPlugin(CoreSocketPlugin):
    pass
