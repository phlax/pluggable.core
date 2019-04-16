# distutils: define_macros=CYTHON_TRACE_NOGIL=1
# cython: linetrace=True
# cython: binding=True
# cython: language_level=3

import asyncio

from aioworker.request import JobRequest
from aioworker import task


BACKENDS = [
    'social_core.backends.open_id.OpenIdAuth',
    'social_core.backends.google.GoogleOpenId',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.google.GoogleOAuth',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.yahoo.YahooOpenId']


# @manager.subscribe("my_topic")
# async def sub_01(topic, data):
#    print("Task subscribe task_01 - ({}): {}".format(topic, data))
#    return 23

_type = type


@task
async def log(request: JobRequest, type: str, msg: str) -> str:
    request.app.loop.create_task(
        request.app.logs.log(type, msg))


@task(returns=object)
async def login(request: JobRequest, username: str, password: str) -> object:
    return await request.app.usermanager.authenticate(
        username=username,
        password=password)


@task(returns=dict)
async def l10n(request: JobRequest, language: str, filetype: str) -> dict:
    return await request.app.managers["l10n"].get_l10n(language, filetype)


@task('auth.social.request')
async def social_request(request, **kwargs):
    # not quite sure how to handle this yet
    from social_core.actions import do_auth
    # from social_core.backends.utils import user_backends_data
    # from social_core.utils import setting_name, module_member, get_strategy
    from social_core.utils import get_strategy

    class User(object):
        pass
    # user = User()
    # from .social_auth import PluggableStorage
    # , PluggableStrategy
    from social_core.backends.utils import get_backend

    # backends = user_backends_data(user, BACKENDS, PluggableStorage)
    backend = get_backend(BACKENDS, 'twitter')
    strategy = get_strategy(
        'ws.core.social_auth.PluggableStrategy',
        'ws.core.social_auth.PluggableStorage')
    _backend = backend(strategy, 'http://localhost:3002')
    return await asyncio.get_event_loop().run_in_executor(
        None, do_auth, _backend)


@task
async def l10n_push(request, **kwargs) -> str:
    l10ndb = await request.app.couchdb.db('global/l10n')
    # await l10ndb.create()
    await l10ndb.bulk_docs(kwargs['params'].values())
    return 'done'


@task
async def logs(request, **kwargs) -> list:
    return await request.app.logs.of(
        'server',
        kwargs.get('limit'))


@task
async def register(request, **kwargs):
    return await request.app.usermanager.register(**kwargs)


@task
async def motd(request, **kwargs):
    # this kinda implies replacing app with request
    msg = 'The road to good intention is paved with hell'
    if kwargs.get('writer') is True:
        for i, char in enumerate(msg):
            if i == len(msg) - 1:
                request.send(char)
    else:
        return msg
