
from collections import OrderedDict
from unittest.mock import patch

import pytest

from pluggable.core.socket import (
    Py__CoreSocketPlugin as CoreSocketPlugin)

from .base import AsyncMock


def test_core_plugin_socket_signature():

    with pytest.raises(TypeError):
        CoreSocketPlugin()


def test_core_plugin_socket(mocker):
    app = mocker.MagicMock()
    plugin = CoreSocketPlugin(app)
    assert plugin.name == "core"


def test_core_plugin_socket_add_hooks(mocker):
    app = mocker.MagicMock()
    plugin = CoreSocketPlugin(app)
    app.reset_mock()
    plugin.add_hooks()
    assert (
        [c[0] for c in app.hooks.__getitem__.call_args_list]
        == [('auth.sessions',),
            ('tasks.worker',),
            ('tasks.local',),
            ('caches',)])
    assert (
        [c[0] for c
         in app.hooks.__getitem__.return_value.register.call_args_list]
        == [(plugin.session_manager,),
            ({'core.tasks': 'pluggable.core.tasks'},),
            ({'auth.logout': plugin.logout,
              'auth.login': plugin.login,
              'l10n': plugin.l10n,
              'auth.register': plugin.register}, ),
            (plugin.get_caches, )])


@pytest.mark.asyncio
async def test_core_plugin_socket_get_caches(mocker):
    app = mocker.MagicMock()
    plugin = CoreSocketPlugin(app)
    app.config = dict(
        caches=OrderedDict((
            ("foo", 17),
            ("bar", 7),
            ("baz", 23))))
    plugin.loop = "LOOP"
    with patch("pluggable.core.socket.aioredis") as redis_m:
        redis_m.create_connection = AsyncMock()
        caches = {}
        await plugin.get_caches(caches)
        assert (
            [c[0] for c in redis_m.create_connection.call_args_list]
            == [(17,), (7,), (23,)])
        assert (
            [c[1] for c in redis_m.create_connection.call_args_list]
            == [{'loop': "LOOP"}, {'loop': "LOOP"}, {'loop': "LOOP"}])
        assert (
            caches
            == {'bar': redis_m.create_connection.return_value,
                'foo': redis_m.create_connection.return_value,
                'baz': redis_m.create_connection.return_value})


@pytest.mark.asyncio
async def test_core_plugin_socket_login_session(mocker):
    app = mocker.MagicMock()
    app.sessions.get = AsyncMock(return_value="USER")
    plugin = CoreSocketPlugin(app)
    result = await plugin._login_session("SESSIONID")
    assert result == ('USER', 'SESSIONID')
    assert (
        [c[0] for c in plugin.app.sessions.get.call_args_list]
        == [('SESSIONID', )])

    app.sessions.get.return_value = None
    result = await plugin._login_session("SESSIONID")
    assert result == (None, None)
    assert (
        [c[0] for c in plugin.app.sessions.get.call_args_list]
        == [('SESSIONID', )] * 2)


@pytest.mark.asyncio
async def test_core_plugin_socket_login_worker(mocker):
    app = mocker.MagicMock()
    app.sessions.create = AsyncMock(return_value="SESSION")
    plugin = CoreSocketPlugin(app)
    _patch = patch(
        "pluggable.core.socket.login",
        new_callable=AsyncMock)
    with _patch as login_m:
        login_m.call.return_value = "BOOM"
        result = await plugin._login_worker("USERNAME", "PASSWORD")
        assert (
            [c[1] for c in login_m.call.call_args_list]
            == [{'password': 'PASSWORD', 'username': 'USERNAME'}])
        assert (
            [c[0] for c in app.sessions.create.call_args_list]
            == [('USERNAME', )])
        assert result == ('USERNAME', 'SESSION')

        login_m.call.return_value = None
        result = await plugin._login_worker("USERNAME", "PASSWORD")
        assert result == (None, None)
        assert (
            [c[1] for c in login_m.call.call_args_list]
            == [{'password': 'PASSWORD', 'username': 'USERNAME'}] * 2)
        # not called again
        assert (
            [c[0] for c in app.sessions.create.call_args_list]
            == [('USERNAME', )])


@pytest.mark.asyncio
async def test_core_plugin_socket_login_actual(mocker):
    app = mocker.MagicMock()
    plugin = CoreSocketPlugin(app)
    _patch = patch(
        "pluggable.core.socket.Py__CoreSocketPlugin._login_worker",
        new_callable=AsyncMock)
    _session_patch = patch(
        "pluggable.core.socket.Py__CoreSocketPlugin._login_session",
        new_callable=AsyncMock)
    with _patch as worker_m:
        with _session_patch as session_m:
            session_m.return_value = ("USERNAME", "SESSIONID")
            result = await plugin._login(session="SESSION")
            assert (
                [c[0] for c in session_m.call_args_list]
                == [('SESSION', )])
            assert (
                result
                == ({'username': 'USERNAME', '_id': 'SESSIONID'},
                    'SESSIONID'))
            assert worker_m.call_args_list == []

            session_m.reset_mock()
            session_m.return_value = (None, None)
            result = await plugin._login(session="SESSION")
            assert result == (None, None)
            assert (
                [c[0] for c in session_m.call_args_list]
                == [('SESSION', )])
            assert worker_m.call_args_list == []

            session_m.reset_mock()
            worker_m.return_value = ("USERNAME", "SESSIONID")
            result = await plugin._login(username="FOO", password="BAR")
            assert session_m.call_args_list == []
            assert (
                [c[0] for c in worker_m.call_args_list]
                == [('FOO', 'BAR')])
            assert (
                result
                == ({'username': 'USERNAME', '_id': 'SESSIONID'},
                    'SESSIONID'))

            worker_m.reset_mock()
            worker_m.return_value = (None, None)
            result = await plugin._login(username="FOO", password="BAR")
            assert result == (None, None)
            assert session_m.call_args_list == []
            assert (
                [c[0] for c in worker_m.call_args_list]
                == [('FOO', 'BAR')])


@pytest.mark.asyncio
async def test_core_plugin_socket_login(mocker):
    app = mocker.MagicMock()
    plugin = CoreSocketPlugin(app)
    _patch = patch(
        "pluggable.core.socket.Py__CoreSocketPlugin._login",
        new_callable=AsyncMock)
    with _patch as login_m:
        login_m.return_value = (
            {'username': 'USERNAME',
             '_id': 'SESSIONID'},
            'SESSIONID')
        result = await plugin.login(
            "CONNECTION", "UUID",
            username="FOO", password="BAR",
            session="BAZ")
        assert (
            [c[0] for c in login_m.call_args_list]
            == [("BAZ", "FOO", "BAR")])
        assert (
            result
            == {'response': {'_id': 'SESSIONID', 'username': 'USERNAME'}})
        assert (
            [c[0] for c in app.signals.emit.call_args_list]
            == [('auth.session.create',)])
        assert (
            [c[1] for c in app.signals.emit.call_args_list]
            == [{'session': 'SESSIONID', 'connection': 'CONNECTION'}])

        login_m.reset_mock()
        app.signals.emit.reset_mock()

        login_m.return_value = (None, None)
        result = await plugin.login(
            "CONNECTION", "UUID",
            username="FOO", password="BAR",
            session="BAZ")
        assert result == {'errors': ['login.failed']}
        assert (
            [c[0] for c in login_m.call_args_list]
            == [("BAZ", "FOO", "BAR")])
        assert app.signals.emit.call_args_list == []


@pytest.mark.asyncio
async def test_core_plugin_socket_logout(mocker):
    app = mocker.MagicMock()
    plugin = CoreSocketPlugin(app)
    app.socket.connnections.__getitem__ = AsyncMock()
    app.sessions.delete = AsyncMock()
    response = await plugin.logout("CONNECTION", "UUID")
    connection_dict = app.socket.connections.__getitem__
    assert (
        [c[0] for c in connection_dict.call_args_list]
        == [('CONNECTION', )])
    assert (
        [c[0] for c
         in connection_dict.return_value.__getitem__.call_args_list]
        == [('session',)])
    assert (
        [c[0] for c in app.sessions.delete.call_args_list]
        == [(connection_dict.return_value.__getitem__.return_value,)])
    assert (
        [c[0] for c in app.signals.emit.call_args_list]
        == [('auth.session.destroy',)])
    assert (
        [c[1] for c in app.signals.emit.call_args_list]
        == [{'connection': 'CONNECTION'}])
    assert response == {'response': 'logged.out'}


@pytest.mark.asyncio
async def test_core_plugin_socket_l10n(mocker):
    app = mocker.MagicMock()
    plugin = CoreSocketPlugin(app)
    _patch = patch(
        "pluggable.core.socket.Py__CoreSocketPlugin._l10n_worker",
        new_callable=AsyncMock)
    with _patch as worker_m:
        app.caches.__getitem__.return_value.execute = AsyncMock(
            return_value="CACHED_L10N")
        response = await plugin.l10n(12345, "UUID", "LANGUAGE", "FILETYPE")
        assert response == "CACHED_L10N"
        assert not worker_m.called
        assert (
            [c[0] for c in app.caches.__getitem__.call_args_list]
            == [('l10n',)])
        assert (
            [c[0] for c
             in app.caches.__getitem__.return_value.execute.call_args_list]
            == [('get', 'LANGUAGE.FILETYPE')])

        app.caches.__getitem__.reset_mock()
        app.caches.__getitem__.return_value.execute.reset_mock()
        app.caches.__getitem__.return_value.execute.return_value = None
        response = await plugin.l10n(12345, "UUID", "LANGUAGE", "FILETYPE")
        assert (
            response
            == {'response': worker_m.return_value})
        assert (
            [c[0] for c in worker_m.call_args_list]
            == [('LANGUAGE', 'FILETYPE')])
        assert (
            [c[0] for c in app.caches.__getitem__.call_args_list]
            == [('l10n',)])


@pytest.mark.asyncio
async def test_core_plugin_socket_l10n_worker(mocker):
    app = mocker.MagicMock()
    plugin = CoreSocketPlugin(app)
    app.worker.tasks.__getitem__.return_value.call = AsyncMock(
        return_value="STORED_L10N")
    app.caches.__getitem__.return_value.execute = AsyncMock()

    with patch("pluggable.core.socket.json") as json_m:
        response = await plugin._l10n_worker("LANGUAGE", "FILETYPE")
        assert response == "STORED_L10N"
        assert (
            [c[0] for c in app.caches.__getitem__.call_args_list]
            == [('l10n',)])
        assert (
            [c[0] for c
             in app.caches.__getitem__.return_value.execute.call_args_list]
            == [('set', 'LANGUAGE.FILETYPE', json_m.dumps.return_value)])
        assert (
            [c[0] for c in json_m.dumps.call_args_list]
            == [('STORED_L10N',)])
