# distutils: define_macros=CYTHON_TRACE_NOGIL=1
# cython: linetrace=True
# cython: binding=True

import binascii
import hashlib
import os

from cpython cimport bool

from pluggable.core.exceptions cimport DoesNotExist


class HttpListener(object):

    def listen(self, url, callback):
        pass


class EmailQueue(object):

    def send(self, email):
        pass


cdef class UserManager(object):
    min_username_length = 5
    max_username_length = 25
    min_password_length = 5
    max_password_length = 25

    def __cinit__(self, app):
        self.app = app

    def __init__(self, app):
        self.http = HttpListener()
        self.email_queue = EmailQueue()

    async def get_users(self, **kwargs):
        return await self.app.authdata.get_users(**kwargs)

    async def get_groups(self, **kwargs):
        return await self.app.authdata.get_groups(**kwargs)

    async def get_group_permissions(self, **kwargs):
        return await self.app.authdata.get_group_permissions(**kwargs)

    async def get_permissions(self, **kwargs):
        return await self.app.authdata.get_permissions(**kwargs)

    async def get_sessions(self, **kwargs):
        return await self.app.authdata.get_sessions(**kwargs)

    async def remove_session(self, sessionid):
        return await self.app.authdata.remove_session(sessionid)

    async def session_delete(self, sessions):
        return await self.app.authdata.session_delete(sessions)

    async def group_delete(self, groups):
        return await self.app.authdata.group_delete(groups)

    async def group_create(self, **kwargs):
        return await self.app.authdata.group_create(**kwargs)

    async def create_permission(self, **kwargs):
        return await self.app.authdata.create_permission(**kwargs)

    async def authenticate(self, username: str, password: str) -> bool:
        try:
            user = await self.app.authdata.get_user(username)
        except DoesNotExist:
            return
        return self.verify_password(
            user['password'],
            password)

    async def ensure_unique(self, username: str) -> bool:
        try:
            await self.app.authdata.get_user(username)
        except DoesNotExist:
            return True

    def _username_regex(self, username):
        return True

    def _password_regex(self, password):
        return True

    async def validate_email(self, password):
        return True

    async def validate_password(self, password: str) -> bool:
        return (
            len(password) < self.max_password_length
            and len(password) > self.min_password_length
            and self._password_regex(password))

    async def validate_username(self, username) -> bool:
        return (
            len(username) < self.max_username_length
            and len(username) > self.min_username_length
            and self._username_regex(username))

    cpdef str hash_password(self, str password):
        """Hash a password for storing."""
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac(
            'sha512',
            password.encode('utf-8'),
            salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')

    cpdef public bool verify_password(
            self,
            str stored_password,
            str provided_password):
        """Verify a stored password against one provided by user"""
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwdhash = hashlib.pbkdf2_hmac(
            'sha512',
            provided_password.encode('utf-8'),
            salt.encode('ascii'),
            100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == stored_password

    # return user ?
    async def create_user(
            self,
            username: str,
            password: str,
            email: str) -> None:
        await self.app.authdata.create_user(
            dict(username=username,
                 password=password,
                 email=email))

    async def generate_verification_url(self) -> str:
        import random
        return str(random.random())

    async def verify_user(self, verfification_url):
        pass

    async def listen_on_url(self, verification_url):
        self.http.listen(verification_url, self.verify_user)

    async def generate_verification_email(self, username, verification_url):
        pass

    async def send_verification_email(self, username, verification_url):
        self.email_queue.send(
            await self.generate_verification_email(
                username, verification_url))

    # remove ?
    async def create_session(self, username):
        return await self.app.sessions.create(username)

    async def register(self, **kwargs):
        # check the username/email isnt taken
        await self.ensure_unique(kwargs['username'])

        # validate the username
        await self.validate_username(kwargs['username'])

        # validate the email
        await self.validate_email(kwargs['email'])

        # validate the password
        await self.validate_password(kwargs['password'])

        # encrypt the password
        hashed = self.hash_password(kwargs['password'])

        # create the user
        await self.create_user(
            username=kwargs['username'],
            password=hashed,
            email=kwargs['email'])

        # create a timed hash for url callback in email
        verification_url = await self.generate_verification_url()

        # make that url available
        await self.listen_on_url(verification_url)

        # send an email
        await self.send_verification_email(
            kwargs['username'],
            verification_url)

        # create a session for unvalidated user
        session = await self.create_session(kwargs['username'])
        return session

    async def user_delete(self, users):
        return await self.app.authdata.user_delete(users)

    async def user_create(self, **kwargs):
        return await self.app.authdata.user_create(**kwargs)
