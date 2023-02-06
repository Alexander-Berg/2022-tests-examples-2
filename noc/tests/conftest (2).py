import os
import uuid
import contextlib
import tempfile
import pathlib
from unittest import mock

import aiohttp
import aiohttp.pytest_plugin
import pytest
import freezegun

from aiohttp_apispec import validation_middleware
from _pytest.fixtures import FixtureRequest

import checkist.api
import checkist.core
import checkist.ann.instance
import settings
import mongo_helpers
import snapshot_helpers


pytest_plugins = ['aiohttp.pytest_plugin']
del aiohttp.pytest_plugin.loop


@pytest.fixture
def loop(event_loop):
    return event_loop


@pytest.fixture
def core(checkist_settings):
    core = checkist.core.CheckistCore(checkist_settings)
    core.devices = mock.AsyncMock()
    yield core


@pytest.fixture
def checkist_settings(mongo_dbname, mongo_url):
    with contextlib.ExitStack() as stack:
        tmpdir = stack.enter_context(tempfile.TemporaryDirectory())
        ann_cache_path = stack.enter_context(tempfile.TemporaryDirectory())
        yield settings.Settings(
            tmpdir=tmpdir,
            http=settings.HTTPSettings(
                host="::1",
                port=0,
            ),
            mongo=settings.MongoSettings(
                host=mongo_url,
                db_name=mongo_dbname,
            ),
            robot=settings.RobotSettings(
                name="test-robot-name",
                token="test-robot-token",
            ),
            ck=settings.CKSettings(
                url="http://localhost/ck-url-settings",
                timeout=0.01,
            ),
            comocutor=settings.ComocutorSettings(
                login="test-comocutor-login",
                password="test-comocutor-password",
            ),
            blackbox=settings.BlackboxSettings(
                base_url="http://localhost/blackbox-url",
                oauth_scope="test:scope",
            ),
            tvm=settings.TVMSettings(
                client_id=0,
                secret="test-tvm-settings",
            ),
            invapi=settings.InvApiSettings(
                oauth_token="token",
            ),
            monitoring=settings.MonitoringSettings(
                solomon=settings.SolomonSettings(enabled=False),
                juggler=settings.JugglerSettings(enabled=False),
            ),
            annushka=settings.AnnushkaSettings(
                cache_path=ann_cache_path,
            )
        )


@pytest.fixture
async def app(core):
    web = mock.Mock()
    web.app = aiohttp.web.Application()
    web.app["core"] = core
    core.web = web
    core.solomon_client = mock.AsyncMock()
    middlewares = [validation_middleware]
    await checkist.api.init(core=core, prefix="", middlewares=middlewares)
    return web.app


@pytest.fixture
async def api_client(aiohttp_client, app):
    return await aiohttp_client(app)


@pytest.fixture
def ann_instance(checkist_settings):
    async def clone_patch(ann_instance, clone_dir, _pull_from):
        outdir = os.path.join(clone_dir, "out")
        os.makedirs(outdir)
        ann_instance._dirname = clone_dir
        ann_instance.outdir = pathlib.Path(outdir)
        ann_instance._commit_hash = ann_instance.git_commit_id
    ann_instance = checkist.ann.instance.AnnInstance(
        "e74ffe0939e4a4a8f3f04df2ad96d155d5aa55f6",
        checkist_settings,
    )
    with contextlib.ExitStack() as stack:
        stack.enter_context(mock.patch.object(checkist.ann.instance.AnnInstance, "clone", new=clone_patch))
        stack.enter_context(mock.patch.object(checkist.ann.instance.AnnInstance, "_check_readiness"))
        stack.enter_context(mock.patch.object(checkist.ann.instance.AnnInstance, "get_commit_hash", new=lambda x: x._commit_hash))
        yield ann_instance


@pytest.fixture
async def mongo_hostname():
    # mongodb.inc provides local mongodb
    return "localhost"


@pytest.fixture
async def mongo_dbname():
    uniq_db_name = str(uuid.uuid4())
    return uniq_db_name


@pytest.fixture
async def mongo_url(mongo_hostname, mongo_dbname):
    # mongodb.inc provides local mongodb
    port = int(os.getenv("RECIPE_MONGO_PORT"))
    return f"mongodb://{mongo_hostname}:{port}/{mongo_dbname}"


@pytest.fixture
async def snapshot(request: FixtureRequest, mongo_url):
    # NOTE: ObjectId должен быть воспроизводимым, чтобы снапшоты не отличались
    #       от запуска к запуску
    with mongo_helpers.predictable_object_id():
        # NOTE: в конце нужно удалить базу mongo, чтобы данные от предыдущих
        #       тестов не мешали снапшотам и чтобы не было
        #       DuplicateError-конфликтов по совпадающим ObjectId
        async with mongo_helpers.keep_db_clean_async(mongo_url):
            # NOTE: время должно быть фиксированным, чтобы снапшоты не
            #       отличались от запуска к запуску
            with freezegun.freeze_time("1980-01-01"):
                yield snapshot_helpers.snapshot(request)
