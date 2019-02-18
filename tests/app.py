# -*- coding: utf-8 -*-

from unittest.mock import patch, MagicMock, PropertyMock

import pytest

import uvloop

from aioworker.worker import Worker

from pluggable.core.hooks import Hook
from pluggable.core.app import (
    default_config,
    Py__App as App)


class _MockWorker(Worker):
    pass


def MockWorker():
    return _MockWorker("BROKER")


def test_app_signature():
    with pytest.raises(TypeError):
        App()


@patch('pluggable.core.app.Py__App.configure')
def test_app(configure_m):
    worker = MockWorker()
    app = App(worker, {})
    assert (
        [c[0] for c in configure_m.call_args_list]
        == [({},)])
    assert app.config == {}
    assert app.caches == {}
    assert app.hooks == {}
    assert app.plugins == {}
    assert app._plugins == []


@patch('pluggable.core.app.Py__App.configure')
def test_app_loop_policy(configure_m):
    worker = MockWorker()
    app = App(worker, {})
    assert app.loop_policy is uvloop.EventLoopPolicy


@patch('pluggable.core.app.Py__App.setup_plugins')
@patch('pluggable.core.app.Py__App.create_hooks')
@patch('pluggable.core.app.Py__App.setup_loop')
@patch('pluggable.core.app.Py__App.import_plugins')
@patch('pluggable.core.app.Py__App.create_config')
def test_app_configure(config_m, plugins_m, loop_m, hooks_m, setup_m, mocker):
    worker = MockWorker()

    class MockApp(App):

        def __init__(self, *args, **kwargs):
            pass

    app = MockApp(worker, {})
    app.hooks["worker"] = mocker.MagicMock()
    app.configure(dict(foo=7, bar=23))
    assert (
        [c[0] for c in config_m.call_args_list]
        == [({'foo': 7, 'bar': 23},)])
    assert (
        [c[0] for c in plugins_m.call_args_list]
        == [()])
    assert (
        [c[0] for c in loop_m.call_args_list]
        == [()])
    assert (
        [c[0] for c in hooks_m.call_args_list]
        == [()])
    assert (
        [c[0] for c in setup_m.call_args_list]
        == [()])


@patch('pluggable.core.app.Py__App.configure')
def test_app_create_config(configure_m, mocker):
    worker = MockWorker()
    app = App(worker, {})
    app.create_config({"foo": 7, "bar": 23})
    config = dict(default_config)
    config.update({"foo": 7, "bar": 23})
    assert app.config == config


@patch('pluggable.core.app.Py__App.create_hook')
@patch('pluggable.core.app.Py__App.configure')
def test_app_create_hooks(configure_m, hook_m):
    worker = MockWorker()
    hook_m.return_value = Hook()
    app = App(worker, {})
    app.create_hooks()
    assert hook_m.call_args_list == []
    assert app.hooks == {}


@patch('pluggable.core.app.import_module')
@patch('pluggable.core.app.Py__App.configure')
def test_app_import_plugins(configure_m, import_m):
    worker = MockWorker()
    app = App(worker, {})
    app.config['plugins'] = ['foo.Foo', 'bar.Bar', 'foo.bar.baz.Baz']
    app.import_plugins()
    assert (
        [c[0] for c in import_m.call_args_list]
        == [('foo',), ('bar',), ('foo.bar.baz',)])
    assert (
        app._plugins
        == [getattr(import_m(), m) for m in ['Foo', 'Bar', 'Baz']])


@patch('pluggable.core.app.Py__App.configure')
def test_app_setup_plugins(config_m, mocker):
    worker = MockWorker()
    app = App(worker, {})
    app.setup_plugins()
    assert app.plugins == {}

    app._plugins = [mocker.MagicMock(), mocker.MagicMock()]
    app.setup_plugins()

    for plugin in app._plugins:
        assert (
            [c[0] for c in plugin.call_args_list]
            == [(app,)])
    assert (
        app.plugins
        == {plugin.return_value.name: plugin.return_value
            for plugin
            in app._plugins})


@patch('pluggable.core.app.asyncio')
@patch('pluggable.core.app.Py__App.loop_policy', new_callable=PropertyMock)
@patch('pluggable.core.app.Py__App.configure')
def test_app_setup_loop(configure_m, policy_m, aio_m):
    worker = MockWorker()
    app = App(worker, {})

    class FooPolicy:
        pass

    policy_m.return_value = FooPolicy
    aio_m.get_event_loop_policy.return_value = FooPolicy()
    FooPolicy.__init__ = MagicMock(return_value=None)

    app.setup_loop()
    assert (
        [c[0] for c in policy_m.call_args_list]
        == [()])
    assert (
        [c[0] for c in aio_m.get_event_loop_policy.call_args_list]
        == [()])
    assert not FooPolicy.__init__.called
    assert not aio_m.set_event_loop_policy.called
    assert app.loop == aio_m.get_event_loop.return_value

    aio_m.get_event_loop_policy.return_value = 23
    aio_m.get_event_loop.return_value = 17
    app.setup_loop()
    assert (
        [c[0] for c in policy_m.call_args_list]
        == [(), (), ()])
    assert (
        [c[0] for c in aio_m.get_event_loop_policy.call_args_list]
        == [(), ()])
    assert (
        [c[0] for c in FooPolicy.__init__.call_args_list]
        == [()])
    assert isinstance(
        aio_m.set_event_loop_policy.call_args_list[0][0][0],
        FooPolicy)
    assert app.loop == aio_m.get_event_loop.return_value
