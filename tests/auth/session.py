
from unittest.mock import patch, MagicMock

import pytest

from pluggable.core.auth.session import (
    Py__SessionManager as SessionManager)

from ..base import AsyncMock


def test_core_session_manager_signature():

    with pytest.raises(TypeError):
        SessionManager()


def test_core_session_manager(mocker):
    app = mocker.MagicMock()
    manager = SessionManager(app)
    assert manager.app is app


@pytest.mark.asyncio
async def test_core_session_manager_create(mocker):
    app = mocker.MagicMock()
    manager = SessionManager(app)
    assert manager.app is app

    with patch("pluggable.core.auth.session.uuid4") as uuid_m:
        uuid_m.return_value.hex = "UUID"
        username = 'fasldkkfnalsdfo☠asdfasdf'
        app.caches.__getitem__.return_value.execute = AsyncMock()
        result = await manager.create(username)
        assert result == uuid_m.return_value.hex
        assert (
            [c[0] for c
             in app.caches.__getitem__.return_value.execute.call_args_list]
            == [('set', uuid_m.return_value.hex, username.encode("utf8"))])
        assert (
            [c[0] for c in app.caches.__getitem__.call_args_list]
            == [('session',)])


@pytest.mark.asyncio
async def test_core_session_manager_get(mocker):
    app = mocker.MagicMock()
    manager = SessionManager(app)
    assert manager.app is app
    app.caches.__getitem__.return_value.execute = AsyncMock()
    app.caches.__getitem__.return_value.execute.return_value.decode = (
        MagicMock(return_value="23"))
    result = await manager.get("UUID")
    cache_dict = app.caches.__getitem__
    assert (
        [c[0] for c in cache_dict.return_value.execute.call_args_list]
        == [('get', 'UUID')])
    assert (
        [c[0] for c
         in cache_dict.return_value.execute.return_value.decode.call_args_list]
        == [('utf8',)])
    assert (
        [c[0] for c in cache_dict.call_args_list]
        == [('session',)])
    assert result == "23"


@pytest.mark.asyncio
async def test_core_session_manager_delete(mocker):
    app = mocker.MagicMock()
    manager = SessionManager(app)
    assert manager.app is app
    app.caches.__getitem__.return_value.execute = AsyncMock()
    await manager.delete("UUID")
    assert (
        [c[0] for c
         in app.caches.__getitem__.return_value.execute.call_args_list]
        == [('del', 'UUID')])
    assert (
        [c[0] for c in app.caches.__getitem__.call_args_list]
        == [('session',)])
