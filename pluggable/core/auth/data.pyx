# distutils: define_macros=CYTHON_TRACE_NOGIL=1
# cython: linetrace=True

from datetime import datetime

from pluggable.core.exceptions import DoesNotExist


cdef class BaseAuthData(object):
    _users = {}
    _sessions = {}
    _groups = {}
    _permissions = {}

    def __init__(self, app):
        self.app = app

    async def get_group(self, groupname):
        try:
            return self._groups[groupname]
        except KeyError:
            raise DoesNotExist('Group does not exist: %s' % groupname)

    async def get_groups(self, **kwargs):
        return self._groups

    async def get_sessions(self, **kwargs):
        return self._sessions

    async def create_group(self, data):
        self._groups[data['groupname']] = data

    async def remove_group(self, groupname):
        del self._groups[groupname]

    async def get_user(self, username):
        try:
            return self._users[username]
        except KeyError:
            raise DoesNotExist('User does not exist: %s' % username)

    async def get_users(self, **kwargs):
        return self._users

    async def create_user(self, data):
        self._users[data['username']] = data

    async def remove_user(self, username):
        del self._users[username]

    async def update_user(self, data):
        await self.create_user(data)

    async def get_permissions(self, username):
        try:
            return self._permissions[username]
        except KeyError:
            raise DoesNotExist('User does not exist: %s' % username)

    async def create_permissions(self, username, permissions):
        if username not in self._permissions:
            self._permissions[username] = []
        for permission in permissions:
            if permission not in self._permissions[username]:
                self._permissions[username].append(permission)

    async def remove_permissions(self, username, permissions):
        # permission_exists = (
        #    username in self._permissions
        #    and permission in self._permissions[username])
        for permission in permissions:
            self._permissions[username] = (
                self._permissions[username].remove(permission))

    async def get_session(self, uuid):
        try:
            return self._sessions[uuid]
        except KeyError:
            raise DoesNotExist('Session does not exist: %s' % uuid)

    async def create_session(self, uuid, username):
        session = dict(session=uuid, username=username)
        self._sessions[uuid] = session
        return session


cdef class CouchAuthData(BaseAuthData):
    # on methods with requests, raise if not status==200 ?

    async def get_group_db(self):
        return await self.app.couchdb.db('global/group')

    async def get_user_db(self):
        return await self.app.couchdb.db('global/user')

    async def get_permission_db(self):
        return await self.app.couchdb.db('global/permission')

    async def get_group_permission_db(self):
        return await self.app.couchdb.db('global/group/permission')

    async def create_user(self, data):
        tstamp = datetime.now().timestamp()
        db = await self.get_user_db()
        # await db.create()
        user = dict(
            _id=data['username'],
            email=data['email'],
            created=tstamp,
            modified=tstamp,
            password=data['password'])
        await db.put(user)
        return user

    async def get_users(self, **kwargs):
        db = await self.get_user_db()
        _users = await db.all_docs(include_docs='true', **kwargs)
        users = []

        while True:
            user = await _users.next()
            if user is None:
                break
            users.append(user['doc'])
        return dict(
            data=users,
            total_rows=_users.total_rows)

    async def get_user(self, userid):
        db = await self.get_user_db()
        _user = await db.doc(userid)
        return await _user.get()

    async def get_groups(self, **kwargs):
        db = await self.get_group_db()
        _groups = await db.all_docs(include_docs='true', **kwargs)
        groups = []

        while True:
            group = await _groups.next()
            if group is None:
                break
            groups.append(group['doc'])
        return dict(
            data=groups,
            total_rows=_groups.total_rows)

    async def get_group_permissions(self, **kwargs):
        db = await self.get_group_permission_db()
        await db.create()
        _permissions = await db.all_docs(include_docs='true', **kwargs)
        permissions = []

        while True:
            permission = await _permissions.next()
            if permission is None:
                break
            permissions.append(permission['doc'])
        return dict(
            data=permissions,
            total_rows=_permissions.total_rows)

    async def group_create(self, **kwargs):
        name = kwargs['name']
        tstamp = datetime.now().timestamp()
        db = await self.get_group_db()
        return await db.put(
            dict(_id=name,
                 created=tstamp,
                 modified=tstamp))

    async def group_delete(self, groups):
        if not isinstance(groups, list):
            groups = [groups]
        db = await self.get_group_db()
        for group in groups:
            await db.delete(group)

    async def get_permissions(self, **kwargs):
        db = await self.get_permission_db()
        _permissions = await db.all_docs(include_docs='true', **kwargs)
        permissions = []

        while True:
            permission = await _permissions.next()
            if permission is None:
                break
            permissions.append(permission['doc'])
        return dict(
            data=permissions,
            total_rows=_permissions.total_rows)

    async def create_permission(self, **kwargs):
        name = kwargs['name']
        tstamp = datetime.now().timestamp()
        db = await self.get_permission_db()
        return await db.put(
            dict(_id=name,
                 created=tstamp,
                 modified=tstamp))

    async def user_create(self, **kwargs):
        name = kwargs['name']
        tstamp = datetime.now().timestamp()
        db = await self.get_user_db()
        return await db.put(
            dict(_id=name,
                 created=tstamp,
                 modified=tstamp))

    async def user_delete(self, users):
        if not isinstance(users, list):
            users = [users]
        db = await self.get_user_db()
        for user in users:
            await db.delete(user)

    async def get_session_db(self):
        return await self.app.couchdb.db('global/session')

    async def remove_session(self, sessionid):
        db = await self.get_session_db()
        await db.delete(sessionid)

    async def session_delete(self, sessions):
        if not isinstance(sessions, list):
            sessions = [sessions]
        db = await self.get_session_db()
        for session in sessions:
            await db.delete(session)

    async def get_session(self, uuid):
        db = await self.get_session_db()
        _session = await db.get(uuid)
        if _session.status != 200:
            raise DoesNotExist('Session does not exist: %s' % uuid)
        session = await _session.json()
        return dict(session=uuid, user=session)

    async def get_sessions(self, **kwargs):
        db = await self.get_session_db()
        _sessions = await db.all_docs(include_docs='true', **kwargs)
        sessions = []

        while True:
            session = await _sessions.next()
            if session is None:
                break
            sessions.append(session['doc'])
        return dict(
            data=sessions,
            total_rows=_sessions.total_rows)

    async def create_session(self, uuid, username):
        tstamp = datetime.now().timestamp()
        db = await self.get_session_db()
        session = dict(
            _id=uuid,
            username=username,
            created=tstamp)
        await db.put(session)
        return session
