"""Pytest conftest file.

Fixtures:

    `stub`     - create stub objects.
    `load`     - load static documents.
    `sleep`    - emulate sleeping to test scheduled events.
    `asyncenv` - show which environment is used in test.
    `mock`     - help to mock objects.
    `patch`    - help to patch functions.
    `response` - build responses.

Markers:

    `now`       - set current time (see `sleep` doc for details).
    `filldb`    - specify parameters for filling database.
    `asyncenv`  - specify which environment to test.
    `mocklevel` - specify what kind of functions to mock.

Extends `pytest` namespace with:

    `inline_callbacks` - allow to write tests with inline callbacks.

"""

import collections
import datetime
import sys

import decorator
import functools
import inspect
import itertools
import json
import os
import threading
import types
import urlparse
import uuid

from taxi.external import corp_clients
from taxi.external import experiments3

sys.path.insert(
    0, os.path.abspath(
        os.path.join(os.path.dirname(__file__),
                     os.pardir, 'submodules', 'stq'),
    )
)

from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet import task
import dateutil.parser
import freezegun
import pymongo
from pymongo.bulk import BulkWriteOperation
import pytest

from taxi import config
from taxi.conf import settings
from taxi.core import async
from taxi.core import arequests
from taxi.core import db
from taxi.core import mc
from taxi.core import scheduler
from taxi.core import threads
from taxi.core import translations
from taxi.core.db import classes as db_classes
from taxi.internal import archive
from taxi.internal import dbh
from taxi.internal import order_core
from taxi.internal import replication
from taxi.internal.promocode_kit import coupons_manager
from taxi.util import json_util
from taxi_maintenance.stuff import ensure_db_indexes

import helpers

TESTS_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(TESTS_DIR)
STATIC_DIR = os.path.join(TESTS_DIR, 'static')

# Time before forced terminating of `async_sleep`
ASYNC_WAITING_TERMINATION_TIMEOUT = 1

# pytest we are using is too old (< 2.7.0)
# pytest_plugins = 'hypothesis.extra.pytestplugin'


@pytest.fixture
def stub():
    """Stub fixture.

    Provides function that takes only keyword arguments `**kw` and
    creates stub object which attributes are `kw` keys.

    Usage:

        def test_something(stub):
            obj = stub(x=1, get_x=lambda: return 2)
            assert obj.x == 1
            assert obj.get_x() == 2

    :return: Function that creates stub objects.
    """
    return lambda **kw: collections.namedtuple('Stub', kw.keys())(**kw)


@pytest.fixture
def file_path(request):
    """Return absolute path of a file from `tests-pytest/static` directory.

    Usage:

        def test_something(file_path):
            with open(file_path('filename')) as fp:
                ...

    File search order is:

    1. `tests-pytest/static/test_something/filename`.
    2. `tests-pytest/static/default/filename`.

    If file doesn't exist `ValueError` exception is raised.

    :param request: `request` fixture.
    :return: Loader (function).
    """
    fullname = str(request.fspath)
    test_module_name = os.path.splitext(os.path.basename(fullname))[0]
    search_directories = [
        os.path.join(STATIC_DIR, subdir)
        for subdir in [test_module_name, 'default']
    ]

    def _file_path(filename):
        for directory in search_directories:
            abs_filename = os.path.join(directory, filename)
            if os.path.exists(abs_filename):
                return abs_filename
        # Raise `ValueError`, not `IOError`, because file **must** exist
        # (or maybe you test writer has made an typo)
        raise ValueError('File %s wasn\'t found' % filename)

    return _file_path


@pytest.fixture
def open_file(file_path):
    """Open file from `tests-pytest/static` directory.

    Usage:

        def test_something(open):
            with open('filename') as fp:
                ...

    File search order is:

    1. `tests-pytest/static/test_something/filename`.
    2. `tests-pytest/static/default/filename`.

    If file doesn't exist `ValueError` exception is raised.

    :param file_path: `file_path` fixture.
    :return: Loader (function).
    """
    def _open_file(filename, *args, **kwargs):
        return open(file_path(filename), *args, **kwargs)
        # Raise `ValueError`, not `IOError`, because file **must** exist
        # (or maybe you test writer has made an typo)
        raise ValueError('File %s wasn\'t found' % filename)

    return _open_file


@pytest.fixture
def load(open_file):
    """Load binary data from `tests-pytest/static` directory.

    Usage:

        def test_something(load):
            data = load('filename')

    File search order is:

    1. `tests-pytest/static/test_something/filename`.
    2. `tests-pytest/static/default/filename`.

    If file doesn't exist `ValueError` exception is raised.

    :param request: `request` fixture.
    :return: Loader (function).
    """
    def _load(filename):
        with open_file(filename) as f:
            return f.read()

    return _load


@pytest.yield_fixture(autouse=True)
def sleep(monkeypatch, request):
    """Set current time and emulate sleeping to test scheduled events.

    Current time is set with `freezegun`. Current time can be set via
    `now` marker. If not specified `datetime.datetime.utcnow()` is used:

        def test_something():
            utcnow = datetime.datetime.utcnow()
            assert isinstance(utcnow, freezegun.api.FakeDatetime)

        @pytest.mark.now('2014-12-30 10:00:00 +03')
        def test_another_thing():
            utcnow = datetime.datetime.utcnow()
            assert utcnow == datetime.datetime(2014, 12, 30, 7)
            now = datetime.datetime.now()
            assert now == datetime.datetime(2014, 12, 30, 10)

    You can walk through a time with `sleep` and test scheduled events:

        @pytest.inline_callbacks
        def test_time_walking(sleep):
            start = datetime.datetime.utcnow()
            yield sleep(10)
            now = datetime.datetime.utcnow()
            assert (now - start).seconds == 10

    Note, when you test some events that should occur in another cycle
    of event loop you should call `yield sleep(0)` to execute all such
    cycles. More than that, if you don't do this reator won't be clean
    when test is over:

        def foo():
            print 'foo is called'

        def bar():
            scheduler.call_later(0, foo)
            print 'bar is called'

        @pytest.inline_callbacks
        def test_foo_bar(sleep, capsys):
            foo()
            (out, err) = capsys.readouterr()
            assert out == 'foo is called\n'

            # Without this sleep reactor won't be clean as scheduled
            # event will be left when test is over
            yield sleep(0)
            (out, err) = capsys.readouterr()
            assert out == 'bar is called\n'

    """
    timestr = lambda now, offset: (
        now.strftime('%Y-%m-%dT%H:%M:%S') + '%+05d' % (offset * 100)
    )

    # Define offset and current time (depends on `now` marker)
    marker = request.node.get_marker('now')
    if marker:
        assert not marker.kwargs
        assert len(marker.args) == 1
        now = dateutil.parser.parse(marker.args[0])
        offset = now.tzinfo._offset.seconds / 3600.0 if now.tzinfo else 0
    else:
        now = datetime.datetime.now()
        utcnow = datetime.datetime.utcnow()
        delta = now - utcnow
        offset = round((delta.seconds + delta.days * 86400) / 3600.0, 2)

    old_update = db_classes.BaseCollectionWrapper.update

    def _adjust_dates(document):
        if isinstance(document, dict):
            current_date = document.get("$currentDate") or {}
            if document.get('$set') == {}:
                raise pymongo.errors.WriteError('"$set" is empty.')
            update_set = None
            if current_date:
                to_remove = []
                for (k, v) in current_date.items():
                    if isinstance(v, dict) and v["$type"] == "timestamp":
                        continue
                    update_set = update_set or document.setdefault('$set', {})
                    update_set[k] = now
                    to_remove.append(k)
                if len(to_remove) == len(current_date):
                    document.pop('$currentDate')
                else:
                    for k in to_remove:
                        current_date.pop(k)

    def update(self, spec, document, *args, **kwargs):
        _adjust_dates(document)
        return old_update(self, spec, document, *args, **kwargs)

    monkeypatch.setattr(db_classes.BaseCollectionWrapper, 'update', update)

    old_bulk_op_update = BulkWriteOperation.update

    def bulk_op_update(self, update):
        _adjust_dates(update)
        return old_bulk_op_update(self, update)

    monkeypatch.setattr(BulkWriteOperation, 'update', bulk_op_update)

    old_find_and_modify = db_classes.BaseCollectionWrapper.find_and_modify

    def find_and_modify(self, query={}, update=None, *args, **kwargs):
        _adjust_dates(update)
        return old_find_and_modify(self, query, update, *args, **kwargs)

    monkeypatch.setattr(
        db_classes.BaseCollectionWrapper, 'find_and_modify', find_and_modify
    )

    # Create freezer, remember current time and put it into a list
    # (mutable container) to have an opportunity to replace it later
    freezer = freezegun.freeze_time(timestr(now, offset), tz_offset=offset, ignore=[''])
    freezer.start()
    now = datetime.datetime.now()
    container = [(freezer, now)]

    clock = task.Clock()
    monkeypatch.setattr(scheduler, 'callLater', clock.callLater)

    @defer.inlineCallbacks
    def _sleep(seconds):
        # Add `seconds` to `now`
        if seconds:
            (old_freezer, now) = container.pop()
            now += datetime.timedelta(seconds=seconds)
            nowstr = timestr(now, offset)
            freezer = freezegun.freeze_time(nowstr, tz_offset=offset, ignore=[''])
            old_freezer.stop()
            freezer.start()
            container.append((freezer, now))

        clock.advance(seconds)

        # Force handling of all occured events
        while clock.calls and clock.calls[0].getTime() <= clock.seconds():
            yield async_sleep(0.001)
            clock.advance(0)

    yield _sleep

    # Stop freezing when test is over
    container[0][0].stop()


@pytest.fixture(autouse=True)
def asyncenv(request, monkeypatch):
    """Force code execution in blocking or asynchronous environment.

    By default, both both blocking and asynchronous environments code
    will be tested. If you want to execute test code in blocking or
    asynchronous environment only you must explicitly specify this via
    `asyncenv` marker:

        @pytest.mark.asyncenv('blocking')
        def test_only_sync_code():
            ...

        @pytest.mark.asyncenv('async')
        def test_only_async_code():
            ...

    You can see which environment is tested:

        def test_something(asyncenv):
            assert asyncenv in ['blocking', 'async']

    :param request: `request` fixture.
    :param monkeypatch: `monkeypatch` fixture.
    :return: Either `'blocking'` or `'async'`.
    """
    if not hasattr(request, 'param'):
        return
    if request.param == 'blocking':
        monkeypatch.setattr('taxi.core.async.reactor', None)
    return request.param


@pytest.fixture
def mock(monkeypatch):
    """Help to mock objects.

    Usage:

        def test_something(mock):
            @mock
            def foo(x, y=1, *a, **kw):
                return x + y + sum(a) + sum(kw.values())

            assert foo(1, 2) == 3
            assert foo(5) == 6
            assert foo(3, y=4) == 7
            assert foo(10, 20, 300, 400, plus=1000) == 1730

            # `call` pops information about first call
            assert foo.call == {'x': 1, 'y': 2, 'a': (), 'kw': {}}
            assert foo.call == {'x': 5, 'y': 1, 'a': (), 'kw': {}}

            # `calls` pops all calls information
            assert foo.calls == [
                {'x': 3, 'y': 4, 'a': (), 'kw': {}},
                {'x': 10, 'y': 20, 'a': (300, 400), 'kw': {'plus': 1000}},
            ]

            # When no information left...
            assert foo.call is None
            assert foo.calls == []

    """
    def mock_and_validate(func_or_str):
        if callable(func_or_str):
            # Direct decoration
            return functools.wraps(func_or_str)(CallsInfoWrapper(func_or_str))
        else:
            # Decorator expected
            assert func_or_str in _SIGNATURES

            def decorator(func):
                wrapper = functools.wraps(func)(
                    CallsInfoWrapper(func, validate=func_or_str)
                )
                monkeypatch.setattr(func_or_str, wrapper)
                return wrapper
            return decorator
    return mock_and_validate


@pytest.fixture
def patch(mock, monkeypatch):
    """Monkey patch helper.

    Usage:

        @patch('full.path.to.func')
        def func(*args, **kwargs):
            return (args, kwargs)

        assert foo(1, x=2) == ((1,), {'x': 2})
        assert foo.calls == [{'args': (1,), 'kwargs': {'x': 2}}]

    """
    def dec_generator(full_func_path):
        def dec(func):
            mocked = mock(func)
            monkeypatch.setattr(full_func_path, mocked)
            return mocked
        return dec
    return dec_generator


@pytest.fixture(autouse=True)
def api_admin_permissions_patch(patch):
    @patch('taxi.external.api_admin.get_permissions')
    @async.inline_callbacks
    def get_permissions(log_extra=None):
        yield async.return_value({'permissions': {}})


@pytest.fixture(autouse=True)
def arequests_disable(patch):
    @patch('taxi.core.arequests._api._request')
    def _request(*args, **kwargs):
        raise RuntimeError(
            'External URL access attempt detected args=%r kwargs=%r' % (
                args, kwargs
            )
        )


@pytest.fixture(autouse=True)
def yt_clients_disable(patch, monkeypatch):
    @patch('taxi.external.yt_wrapper.get_yt_replication_clients')
    @async.inline_callbacks
    def get_yt_replication_clients():
        yield
        async.return_value([_DummyYtClient()])

    @patch('taxi.external.yt_wrapper.get_yt_replication_runtime_clients')
    @async.inline_callbacks
    def get_yt_replication_runtime_clients():
        yield
        async.return_value([_DummyYtClient()])

    monkeypatch.setattr('taxi.external.yt_wrapper.hahn', _DummyYtClient())
    monkeypatch.setattr('taxi.external.yt_wrapper.hahn_fraud', _DummyYtClient())
    monkeypatch.setattr('taxi.external.yt_wrapper.freud', _DummyYtClient())
    monkeypatch.setattr('taxi.external.yt_wrapper.hahn_env', _DummyYtClient())
    monkeypatch.setattr(
        'taxi.external.yt_wrapper.hahn_dwh_env', _DummyYtClient())
    monkeypatch.setattr('taxi.external.yt_wrapper.locke_env', _DummyYtClient())
    monkeypatch.setattr('taxi.external.yt_wrapper.freud_env', _DummyYtClient())
    monkeypatch.setattr(
        'taxi.external.yt_wrapper._environments', {})
    monkeypatch.setattr(
        'taxi.external.yt_wrapper._dyntable_environments', {})


@pytest.fixture
def areq_request(asyncenv, patch, arequests_disable):
    """Decorator for `arequsts.request` function

    Usage:
        def test_something(areq_respone):
            @areq_request
            def aresponse(method, url, **kwargs):
                code = 200
                body = '<ok/>'
                headers = {}
                return (code, body, headers)
    """

    def _areq_request(func):

        @async.inline_callbacks
        def wrapper(method, url, **kwargs):
            yield
            res = func(method, url, **kwargs)
            if isinstance(res, tuple):
                res = res + (None,) * (4 - len(res))
                code, body, headers, cookies = res
            elif isinstance(res, dict):
                code = res.get('code')
                body = res.get('body')
                headers = res.get('headers')
                cookies = res.get('cookies')

            response = arequests.Response(code, headers, body, cookies)
            response.elapsed = 0
            async.return_value(response)
        return patch('taxi.core.arequests._api._request')(wrapper)

    _areq_request.response = (
        lambda code, body=None, headers=None, cookies=None: {
            'code': code, 'body': body, 'headers': headers, 'cookies': cookies
        }
    )

    return _areq_request


@pytest.fixture
def parse_url(stub):
    def _parse_url(url):
        result = urlparse.urlparse(url)
        query = urlparse.parse_qs(result.query)
        return stub(
            base_url='%s://%s' % (result.scheme, result.netloc),
            scheme=result.scheme,
            netloc=result.netloc,
            path=result.path,
            query=query
        )
    return _parse_url


@pytest.fixture(autouse=True)
def _mocklevel(request, mock):
    """Mock functions on specified level.

    Function uses `_MOCK_LEVELS` variable. Level is defined via
    `mocklevel` marker (`'core'` by default).

    :param request: `request` fixture.
    :param mock: `mock` fixture.
    :return: `None`.
    """
    marker = request.node.get_marker('mocklevel')
    args = marker and marker.args or ['core']
    level = args[0]
    assert len(args) == 1 and level in [None, 'core', 'external', 'internal']
    assert not marker or not marker.kwargs

    def default_function(*args, **kwargs):
        raise NotImplementedError(
            'function with args=%s kwargs=%s is called; mock it explicitly' % (
                repr(args), repr(kwargs)
            )
        )

    for funcpath in _MOCK_LEVELS.get(level, []):
        mock(funcpath)(default_function)


@pytest.fixture(autouse=True)
def immediate_deferToThread(monkeypatch):
    """Need to execute target in tests immediately.

    :param monkeypatch: `monkeypatch` fixture.
    :return: `None`.
    """
    @defer.inlineCallbacks
    def deferToThread(target, *args, **kwargs):
        result = yield target(*args, **kwargs)
        defer.returnValue(result)

    monkeypatch.setattr(
        threads.twisted_threads, 'deferToThread', deferToThread
    )


def pytest_addoption(parser):
    parser.addoption('--no-indexes', action='store_true',
                     help='Do not ensure db indexes')


def _fill_collection(collection, name, dbset, load, specified=True):
    collection.remove()

    if not specified:
        return

    # Fill collections with data
    filename = 'db_%s%s.json' % (name, '_%s' % dbset if dbset else '')
    try:
        text = load(filename)
    except ValueError:
        # There are no documents in collection by default. But
        # it is most likely an error when `dbset` is specified
        # and not found.
        if dbset:
            raise
        text = '[]'

    try:
        docs = json.loads(text, object_hook=json_util.object_hook)
    except ValueError as err:
        new_message = '%s file %s' % (err.args[0], filename)
        new_args = [new_message] + list(err.args[1:])
        err.args = tuple(new_args)
        raise

    for doc in docs:
        collection.save(doc)


class _CollectionInitializer(object):
    def __init__(self, ensure_indexes=True):
        self.indexes_ensured = set()
        self.db_settings = None
        self.ensure_indexes = ensure_indexes
        self.aliases = {}
        for collection_name in db.get_collections().keys():
            self.aliases[getattr(db, collection_name)] = collection_name
            self.aliases[
                getattr(db.secondary, collection_name)
            ] = collection_name

        self.lock = threading.Lock()
        self.reset()

        self._wrap(db.classes.CollectionWrapper)
        self._wrap(db.classes.SecondaryCollectionWrapper)

    def reset(self, dbsets=None, load=None):
        self.collection_filled = set()
        self.dbsets = dbsets or {}
        self.load = load

    def _fill_collection(self, collection, alias):
        with self.lock:
            if self.ensure_indexes and alias not in self.indexes_ensured:
                self._ensure_indexes(alias, collection)
            _fill_collection(
                collection,
                alias,
                self.dbsets.get(alias),
                self.load,
                specified=alias in self.dbsets,
            )
            self.collection_filled.add(alias)

    def _ensure_indexes(self, alias, collection):
        if self.db_settings is None:
            self.db_settings = db.load_db_settings()
        collection.drop_indexes()
        collection.remove()
        if alias in self.db_settings:
            ensure_db_indexes.ensure_index_for(
                collection, alias, self.db_settings[alias]
            )
        self.indexes_ensured.add(alias)

    def _wrap(self, klass):
        original_property = klass._connection

        @property
        def get_connection(collection):
            connection = original_property.__get__(collection)
            alias = self.aliases.get(collection)
            if alias not in self.collection_filled:
                self._fill_collection(
                    connection[collection._database_name][
                        collection._collection_name
                    ], alias)
            return connection
        klass._connection = get_connection


@pytest.fixture(scope='session')
def _collection_initializer(worker_id, pytestconfig):
    ensure_indexes = False
    xdist_plugin = pytestconfig.pluginmanager.getplugin('xdist')
    xdist_numproc = pytestconfig.getoption('numprocesses', None)
    if (not hasattr(pytestconfig, 'slaveinput') and
            (not xdist_plugin or not xdist_numproc)):
        if not pytestconfig.getoption('--no-indexes'):
            ensure_indexes = True
    return _CollectionInitializer(ensure_indexes=ensure_indexes)


@pytest.yield_fixture(autouse=True)
def _filldb(request, monkeypatch, load, sleep, _patch_db,
            _collection_initializer):
    """Create temporary database and fill it with data.

    Before filling each `_database_name` of collection is mocked to get
    an opportunity run tests in parallel. Then all collections are
    filled with data and indexes are created.

    You can specify which file with documents to use for each collection
    via `filldb` marker. For example:

        # Filename: `test_client30_launch.py`

        @pytest.mark.filldb(users='banned')
        def test_banned_users():
            # Here you can be sure database is filled as you specify,
            # otherwise ValueError exception would have been raised
            # (if no files have been found or some file is invalid).
            ...

        # Search order for `users` collection:
        # 1. tests-pytest/static/test_client30_launch/db_users_banned.json
        # 2. tests-pytest/static/default/db_users_banned.json

        # Search order for `orders` collection:
        # 1. tests-pytest/static/test_client30_launch/db_orders.json
        # 2. tests-pytest/static/default/db_orders.json

    You are able to skip database population (indexes wouldn't be created too).
    To skip filling database (and indexes creation):

        @pytest.mark.filldb(_fill=False)
        def test_something():
            # Database is mocked, but not filled and has no indexes
            ...

    In case when you want to populate only a subset of collections:

        @pytest.mark.filldb(_specified=True, users='default', orders='my')
        def test_something():
            # Database is mocked, only users and orders collections are filled
            ...

    :param request: `request` fixture.
    :param monkeypatch: `monkeypatch` fixture.
    :param load: `load` fixture.
    :param sleep: `sleep` fixture.
    :return: `None`.
    """
    # We need `sleep` to be sure freezegun has made its work

    collection_names = _get_collection_names()

    # Database sets are specified via kwargs, no arguments are expected.
    # All collections must be defined in `taxi.core.db` module
    fill_database = True
    throw_on_db_access = False
    dbsets = dict(zip(collection_names, itertools.repeat(None)))
    marker = request.node.get_marker('filldb')
    if marker:
        kwargs = marker.kwargs.copy()
        throw_on_db_access = kwargs.pop('_throw_on_db_access', False)
        fill_database = kwargs.pop('_fill', True)
        specified = kwargs.pop('_specified', False)
        if marker.args:
            raise ValueError(
                '`%s` is wrongly marked with `filldb`, see help' %
                request.function.__name__
            )
        for name in kwargs.iterkeys():
            if name not in collection_names:
                raise ValueError(
                    '`%s` collection is not in taxi.core.db, check spelling' %
                    name
                )
        if specified:
            dbsets = {}
        for (collection_name, setname) in kwargs.items():
            dbsets[collection_name] = setname

    if throw_on_db_access:
        fill_database = False

    if fill_database:
        _collection_initializer.reset(dbsets=dbsets, load=load)
    else:
        _collection_initializer.reset()

    if throw_on_db_access:
        class DbAccessIsRestricted(object):
            pass
        for name in collection_names:
            monkeypatch.setattr(
                'taxi.core.db.{}'.format(name), DbAccessIsRestricted()
            )
            monkeypatch.setattr(
                'taxi.core.db.secondary.{}'.format(name), DbAccessIsRestricted()
            )

    # Wait until test will be passed or failed
    yield


@pytest.fixture(autouse=True)
def _mc_key(monkeypatch):
    prefix = uuid.uuid4().hex
    monkeypatch.setattr(mc, '_KEY_PREFIX', prefix)


@pytest.fixture(autouse=True)
def _memstorage_key(monkeypatch):
    prefix = uuid.uuid4().hex
    monkeypatch.setattr('taxi.core.memstorage._KEY_PREFIX', prefix)


@pytest.fixture(autouse=True)
def _flush_memstorage(invalidate_cache):
    invalidate_cache()


@pytest.fixture
def invalidate_cache(monkeypatch):
    def _invalidate_cache():
        monkeypatch.setattr('taxi.core.memstorage._manager._cache', {})
        monkeypatch.setattr(
            'taxi.core.memstorage._manager._blocking_cache', {}
        )
    return _invalidate_cache


@decorator.decorator
def inline_callbacks(fun, *args, **kwargs):
    return async.inline_callbacks(fun)(*args, **kwargs)


def pytest_generate_tests(metafunc):
    if 'asyncenv' in metafunc.fixturenames:
        available_envs = ['blocking', 'async']
        if hasattr(metafunc.function, 'asyncenv'):
            marker = metafunc.function.asyncenv
            if (marker.kwargs or not marker.args or
                    not all(arg in available_envs for arg in marker.args)):
                raise ValueError(
                    '`%s` is wrongly marked with `asyncenv`, see help' %
                    metafunc.function.__name__
                )
            envs = list(marker.args)
        else:
            envs = available_envs
        if pytest.__version__.startswith('2.'):
            metafunc._arg2fixturedefs['asyncenv'][0].params = envs
        elif pytest.__version__.startswith('3.'):
            metafunc.parametrize('asyncenv', envs)


def pytest_namespace():
    return dict(inline_callbacks=inline_callbacks,
                FakeTranslations=FakeTranslations)


########################################################################
# Internal classes and functions

# We need this lambdas to be sure mocked functions called properly. So,
# lambdas **must have** the same signatures as mocked functions.
_SIGNATURES = {
    'requests.api.request': (
        lambda method, url, **kwargs: None
    ),
    'taxi.core.arequests._api.request': (
        lambda method, url, **kwargs: None
    ),
    'taxi.core.threads.defer_to_thread': (
        lambda target, *args, **kwargs: None
    ),
    'taxi.external.passport.get_info_by_token': (
        lambda token, user_ip, tvm_src_service, log_extra=None: None
    ),
    'taxi.external.passport.get_info_by_sid': (
        lambda sessionid, user_ip, log_extra=None: None
    ),
    'taxi.internal.auth.get_token_info': (
        lambda token, user_ip, log_extra=None: None
    ),
    'taxi.internal.park_manager.logger.debug': (
        lambda *args, **kwargs: None
    ),
    'twisted.web.xmlrpc.Proxy': (
        lambda url, user=None, password=None, allowNone=False,
        useDateTime=False, connectTimeout=30.0, reactor=None: None
    ),
}

_MOCK_LEVELS = {
    'core': [
        'taxi.core.arequests._api.request',
        'requests.api.request',
        'twisted.web.xmlrpc.Proxy',
    ],
    'external': [
        'taxi.external.passport.get_info_by_token',
    ],
    'internal': [
        'taxi.internal.auth.get_token_info',
    ]
}


class CallsInfoWrapper:
    """Function wrapper that adds information about function calls.

    Wrapped function `__dict__` is extende with two public attributes:

        `call`  - pops information about first call
        `calls` - pops all calls information

    """

    def __init__(self, func, validate=None):
        self.__func = func
        self.__calls = []
        self.__validate_lambda = _SIGNATURES.get(validate)
        self.__dict__.update(func.__dict__)

    @property
    def call(self):
        return self.__calls.pop(0) if self.__calls else None

    @property
    def calls(self):
        calls = self.__calls[:]
        while self.__calls:
            self.__calls.pop(0)
        return calls

    @property
    def func_name(self):
        return self.__func.__name__

    def __call__(self, *args, **kwargs):
        if self.__validate_lambda:
            self.__validate_lambda(*args, **kwargs)

        func_spec = inspect.getargspec(self.__func)
        func_args = func_spec.args
        func_varargs = func_spec.varargs
        func_keywords = func_spec.keywords
        defaults = func_spec.defaults or ()
        func_defaults = dict(
            zip(func_args[-len(defaults):], defaults)
        )

        dct = dict(zip(func_args, args))
        for argname in func_args[len(args):]:
            if argname in kwargs:
                dct[argname] = kwargs[argname]
            else:
                dct[argname] = func_defaults[argname]
        if func_varargs is not None:
            dct[func_varargs] = args[len(dct):]
        if func_keywords is not None:
            dct[func_keywords] = dict(
                (k, v) for (k, v) in kwargs.items()
                if k not in dct
            )
        self.__calls.append(dct)
        return self.__func(*args, **kwargs)


def async_sleep(seconds):
    """Sleep for a `seconds` in non-blocking and safe manner.

    Use `async_sleep` to wait for a `seconds` in functions wrapped in
    `inlineCallbacks`:

        @defer.inlineCallbacks
        def foo():
            before = datetime.datetime.utcnow()
            yield async_sleep(1)
            after = datetime.datetime.utcnow()
            assert (after - before).seconds >= 1

    :param seconds: Seconds to sleep for.
    :return: Twisted's `Deferred` which will be callbacked with `None`
        in a `seconds` second or will be errbacked in a
        `seconds + ASYNC_WAITING_TERMINATION_TIMEOUT` seconds if reactor
        is stopped.
    """

    def _check_called(deferred):
        if not deferred.called:
            deferred.errback(RuntimeError('reactor is stopped'))

    def _cancel_timer(result, timer):
        # `cancel()` method can be called multiple times, so no need to
        # check whether timer has called a function or not
        timer.cancel()
        return result

    deferred = defer.Deferred()
    reactor.callLater(seconds, deferred.callback, None)

    # Sometimes reactor is stopped before `deferred.callback` is called,
    # so we have to ensure that `deferred` will be fired and test will
    # be finished. For this purpose we run `threading.Timer` that will
    # errback uncalled `deferred`.
    #
    # Note! `deferred.errback()` will be called in a non-main thread.
    # Cross threading notification mechanisms like `eventfd` won't work
    # because at the moment of calling `_check_called` main event loop
    # is broken.

    timer = threading.Timer(
        seconds + ASYNC_WAITING_TERMINATION_TIMEOUT,
        _check_called, args=(deferred,)
    )

    # Cancel timer to avoid unnecessary call of `_check_called`
    deferred.addCallback(_cancel_timer, timer)

    return deferred


########################################################################
# Faking translations

class _FakeTranslationBlock(translations.TranslationBlock):
    def __init__(self, block_name):
        super(_FakeTranslationBlock, self).__init__(block_name)
        self._keys = {}
        self._block_name = block_name

    def set_string(self, key, language, value):
        self._keys[self.full_key(key, language)] = value

    def get_string(self, key, language, n=None):
        full_key = self.full_key(key, language)
        if full_key not in self._keys:
            raise translations.TranslationNotFoundError(
                self._block_name, key, language
            )
        return self._keys[full_key]

    @staticmethod
    def full_key(key, language):
        return '%s.%s' % (key, language)


class _FakeOverriddenTranslationBlock(translations.OverridedTranslationBlock):
    pass


class FakeTranslations(object):
    def __init__(self):
        super(FakeTranslations, self).__init__()
        self._blocks = {}
        self._override_map = {}

    def _set(self, block, key, language, value):
        if block not in self._blocks:
            self._blocks[block] = _FakeTranslationBlock(block)
        self._blocks[block].set_string(key, language, value)

    def get_block(self, block, application=None, major_version=None):
        if application and major_version:
            application = '{}:{}'.format(application, major_version)

        if application:
            overrides = self._override_map.get(application, {})
            if (block in overrides):
                override = overrides[block]
                if override != 'ignore':
                    return self._get_overrided_block(block, override)

        if block not in self._blocks:
            raise translations.BlockNotFoundError(block)
        return self._blocks[block]

    def _get_overrided_block(self, block, override):
        if block in self._blocks and override in self._blocks:
            return _FakeOverriddenTranslationBlock(
                self._blocks[block], self._blocks[override]
            )
        elif block not in self._blocks:
            raise translations.BlockNotFoundError(
                '\'%s\' not in %s' % (block, self._blocks.keys())
            )
        else:
            raise translations.BlockNotFoundError(
                'Override \'%s\' for block \'%s\' not found in %s' % (
                    override, block, self._blocks.keys()
                )
            )

    def __getattr__(self, block):
        return self.get_block(block)


@pytest.yield_fixture(autouse=True)
def _translations(request, monkeypatch):
    marker = request.node.get_marker('translations')
    if marker:
        translations_db = FakeTranslations()
        all_keysets = translations.translations._blocks.keys()
        for keyset in all_keysets:
            translations_db._blocks[keyset] = _FakeTranslationBlock(keyset)
        for (block, key, language, value) in marker.args[0]:
            translations_db._set(block, key, language, value)
        config_marker = request.node.get_marker('config')
        if config_marker:
            app_map = config_marker.kwargs.get('APPLICATION_MAP_TRANSLATIONS')
            if app_map:
                translations_db._override_map = app_map
        monkeypatch.setattr('taxi.core.translations.translations',
                            translations_db)
    else:
        for block in translations.translations._blocks.itervalues():
            block._initialized = False

    yield


@pytest.yield_fixture(autouse=True)
def _config(request, monkeypatch):
    marker = request.node.get_marker('filldb')
    fill_database = True
    throw_on_db_access = False
    if marker:
        kwargs = marker.kwargs.copy()
        fill_database = kwargs.pop('_fill', True)
        throw_on_db_access = kwargs.pop('_throw_on_db_access', False)

    if not fill_database or throw_on_db_access:
        @async.inline_callbacks
        def param__get_fresh(self):
            yield
            async.return_value(self.default)

        @async.inline_callbacks
        def param__save(self, value):
            yield
            raise Exception(
                "You are saving config from _fill=False test. "
                "Use @pytest.mark.config(KEY1=value1, ...) to override values."
            )

        monkeypatch.setattr(
            'taxi.config.params.Param.get_fresh', types.MethodType(
                param__get_fresh, None, config.params.Param
            )
        )
        monkeypatch.setattr(
            'taxi.config.params.Param.save', types.MethodType(
                param__save, None, config.params.Param
            )
        )

    marker = request.node.get_marker('config')
    if marker:
        for config_key, value in marker.kwargs.iteritems():
            monkeypatch.setattr(
                'taxi.config.{}.get_fresh'.format(config_key),
                types.MethodType(
                    lambda self, val=value: val, getattr(config, config_key),
                    config.lazy_param.LazyParam
                )
            )
            monkeypatch.setattr(
                'taxi.config.{}.get'.format(config_key),
                types.MethodType(
                    lambda self, val=value: val, getattr(config, config_key),
                    config.lazy_param.LazyParam
                )
            )

            monkeypatch.setattr(
                'taxi.config.{}.get_fresh'.format(config_key),
                types.MethodType(
                    lambda self, val=value: val, getattr(config, config_key),
                    config.params.Param
                )
            )
    yield


class _DummyYtClient(object):
    _config_keys = ['operation_tracker']

    def __init__(self):
        self.config = {key: dict() for key in self._config_keys}


def _get_collection_names():
    return db.get_collections().keys()


def _check_collection_classes():
    for collection_class in dbh._AVAILABLE_CLASSES:
        name_map = object.__getattribute__(collection_class, '_name_map')
        reverse_name_map = collections.defaultdict(list)
        for name in name_map.mapped():
            short_name = name_map[name]
            reverse_name_map[short_name].append(name)
        errors = {}
        for short_name, names in reverse_name_map.items():
            if len(names) > 1:
                errors[short_name] = names
        if errors:
            raise TypeError(
                'short names in %s.%s are used for more than one field: %r' % (
                    collection_class.__module__,
                    collection_class.__name__,
                    errors,
                )
            )


def _patch_db_names(collection_names, worker_id):
    db_name_ending = '_pytest_%s' % worker_id
    for name in collection_names:
        wrapped_collection = getattr(db, name)
        _patch_wrapped_collection(wrapped_collection, db_name_ending)

        wrapped_collection_sec = getattr(db.secondary, name)
        _patch_wrapped_collection(wrapped_collection_sec, db_name_ending)


def _patch_wrapped_collection(wrapped_collection, name_ending):
    origin_name = getattr(wrapped_collection, '_origin_db_name', None)
    base_name = origin_name or wrapped_collection._database_name
    wrapped_collection._database_name = base_name + name_ending
    if not origin_name:
        setattr(wrapped_collection, '_origin_db_name', base_name)


@pytest.mark.optionalhook
def pytest_testnodeready(node):
    config = node.config
    if config.getoption('--no-indexes'):
        return

    _create_indexes(node.slaveinput['slaveid'])


def _create_indexes(worker_id='master'):
    _check_collection_classes()
    collection_names = _get_collection_names()
    _patch_db_names(collection_names, worker_id)
    _patch_ensure_index()

    for name in collection_names:
        collection = getattr(db, name)._collection
        collection.drop_indexes()
        collection.remove()
    ensure_db_indexes.do_stuff()


@pytest.fixture(scope='session')
def worker_id(request):
    if hasattr(request.config, 'slaveinput'):
        return request.config.slaveinput['slaveid']
    else:
        return 'master'


@pytest.fixture(scope='session')
def _patch_db(worker_id):
    collection_names = _get_collection_names()
    _patch_db_names(collection_names, worker_id)


def _patch_ensure_index():
    ensure_index = pymongo.collection.Collection.ensure_index

    def patched_ensure_index(*args, **kwargs):
        kwargs.pop('expireAfterSeconds', None)
        return ensure_index(*args, **kwargs)

    pymongo.collection.Collection.ensure_index = patched_ensure_index


class Response:
    def __init__(self, status_code, json):
        self.status_code = status_code
        self.content = ''
        self._json = json

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise arequests._exceptions.HTTPError


@pytest.fixture
def load_external_service_data(request, load):
    def _get_data(prefix):
        marker = request.node.get_marker('load_data')
        if marker and marker.kwargs.get('_load') is False:
            return []
        is_marked = marker and prefix in marker.kwargs
        if is_marked:
            filename = '{}_data_{}.json'.format(
                prefix, marker.kwargs[prefix],
            )
        else:
            filename = '{}_data.json'.format(prefix)
        try:
            data = load(filename)
        except ValueError as exc:
            if is_marked:
                raise exc
            data = None
        return json.loads(data) if data else []

    return _get_data


@pytest.fixture
def userapi_get_user_phone_mock(patch):
    @patch('taxi.external.userapi.get_user_phone')
    def get_user_phone(*args, **kwargs):
        return helpers.get_user_api_response()


@pytest.fixture
def personal_retrieve_mock(patch, load):
    @patch('taxi.internal.personal.retrieve')
    def retrieve(data_type, request_id, **kwargs):
        data = json.loads(load('personal_retrieve.json'))
        return {'phone': data[data_type][request_id]}


@pytest.fixture(autouse=True)
def territories_api_mock(request, monkeypatch, patch,
                         load_external_service_data):
    if 'disable_territories_api_mock' in request.keywords:
        return
    data = load_external_service_data('countries')

    @patch('taxi.external.territories._perform_post')
    def _perform_post(location, payload, *args, **kwargs):
        if 'list' in location:
            return Response(200, {'countries': data if data else []})
        else:
            countries_by_id = {country['_id']: country for country in data}
            country_id = location.split('id=')[1]
            update_set = payload.get('set')
            fields_to_unset = payload.get('unset')
            country = countries_by_id.get(country_id, {})
            if update_set:
                country.update(update_set)
            for field in fields_to_unset:
                country.pop(field, None)
            if country_id not in countries_by_id:
                country['_id'] = country_id
                data.append(country)
            return Response(200, {})


@async.inline_callbacks
def make(order_id, use_passenger_feedback):
    order_proc = yield archive.get_order_proc_by_id(order_id)
    feedback = order_proc.get('order', {}).get('feedback', {})
    new_style_feedback = {}
    if 'c' in feedback:
        new_style_feedback['call_me'] = feedback['c']
    if 'msg' in feedback:
        new_style_feedback['msg'] = feedback['msg']
    if 'app_comment' in feedback:
        new_style_feedback['app_comment'] = feedback['app_comment']
    if 'rating' in feedback:
        new_style_feedback['rating'] = feedback['rating']
    if 'choices' in feedback:
        choices = []
        if use_passenger_feedback:
            new_style_feedback['choices'] = feedback['choices']
        else:
            for reason_type, values in feedback['choices'].iteritems():
                for value in values:
                    choices.append(
                        {'type': reason_type, 'value': value}
                    )
            new_style_feedback['choices'] = choices

    if 'iac' in feedback:
        new_style_feedback['is_after_complete'] = feedback['iac']
    async.return_value(new_style_feedback)


@pytest.fixture
def feedback_retrieve_from_proc(patch):
    @patch('taxi.external.feedback.retrieve')
    @async.inline_callbacks
    def retrieve(order_id, **kwargs):
        feedback = yield make(order_id, use_passenger_feedback=False)
        async.return_value(feedback)


@pytest.fixture
def passenger_feedback_retrieve_from_proc(patch):
    @patch('taxi.external.passenger_feedback.retrieve')
    @async.inline_callbacks
    def retrieve(order_id, **kwargs):
        feedback = yield make(order_id, use_passenger_feedback=True)
        async.return_value(feedback)


@pytest.fixture
def replication_map_data(patch, load):
    def patcher(doc_id):
        data = json.loads(
            load('mapped_data-{}.json'.format(doc_id))
        )

        @patch('taxi.external.replication.map_data')
        @async.inline_callbacks
        def map_data(request, tvm_src_service, log_extra=None):
            response = []
            for item in request['items']:
                target_name = item['target_name']
                mapped_data = data[target_name]
                response.append({
                    'id': item['id'],
                    'target_name': target_name,
                    'mapped_data': [replication._dump_json(mapped_data)],
                })
            async.return_value({'items': response})
            yield

        return map_data

    return patcher


@pytest.fixture
def replication_yt_target_info(patch):
    default = {
        'table_path': '//home/yt_table',
        'clients_delays': [
            {
                'current_delay': 0,
                'client_name': 'hahn',
            },
        ],
    }
    responses = {}

    @patch('taxi.external.replication.get_yt_target_info')
    @async.inline_callbacks
    def get_yt_target_info(target_name, **kwargs):
        async.return_value(responses.get(target_name, default))
        yield

    def set_responses(info=None):
        if info:
            responses.update(info)
        return get_yt_target_info

    return set_responses


@pytest.fixture(autouse=True)
def mock_client_put(request, patch):
    if 'noputmock' in request.keywords:
        return

    @patch('taxi_stq._client.put')
    @async.inline_callbacks
    def put(queue, eta=None, task_id=None, args=None, kwargs=None):
        yield


@pytest.fixture
def inject_user_api_token(monkeypatch):
    monkeypatch.setattr(
        settings,
        'CLIENT_APIKEYS',
        {'user_api': {'user_api': 'user_api_token'}},
    )


@pytest.fixture
def patch_user_factory(patch, inject_user_api_token):
    @patch('taxi.external.userapi.create_user_phone_by_personal_phone_id')
    @async.inline_callbacks
    def mock_user_phones(personal_phone_id, phone_type, *args, **kwargs):
        phone_doc = yield db.user_phones.find_and_modify(
            {
                'personal_phone_id': personal_phone_id,
                'type': phone_type,
            },
            {
                '$set': {
                    'personal_phone_id': personal_phone_id,
                    'type': phone_type,
                    'phone': '+79999999999'
                }
            }, upsert=True, new=True,
        )
        response = {
            'id': phone_doc['_id'],
            'phone': phone_doc['phone'],
            'type': phone_type,
            'personal_phone_id': personal_phone_id,
            'created': '2017-02-01T13:00:00+0000',
            'updated': '2017-09-10T10:00:00+0000',
            'stat': {
                'big_first_discounts': 0,
                'complete': 0,
                'complete_card': 0,
                'complete_apple': 0,
                'complete_google': 0
            },
            'is_loyal': False,
            'is_yandex_staff': False,
            'is_taxi_staff': False,
        }
        async.return_value(response)


@pytest.fixture(autouse=True)
def parks_activation_api_mock(patch):
    @patch('taxi.external.parks_activation._request')
    @async.inline_callbacks
    def _request(*args, **kwargs):
        yield
        async.return_value({'parks_activation': []})


@pytest.fixture
def patch_bulk_retrieve_phones_by_personal(patch, inject_user_api_token):
    @patch('taxi.external.userapi.get_user_phones_by_personal_and_type')
    @async.inline_callbacks
    def mock_user_phones_by_personal(
            personal_phone_ids_and_types, *args, **kwargs):
        query = {'$or': []}
        for personal_and_type in personal_phone_ids_and_types:
            query['$or'].append({'personal_phone_id': personal_and_type.personal,
                                 'type': personal_and_type.type})

        phone_docs = yield db.user_phones.find(query).run()
        response = {'items': [{'id': phone_doc['_id']} for phone_doc in phone_docs]}

        async.return_value(response)


@pytest.fixture
def mock_processing_antifraud(patch):
    @patch('taxi.external.processing_antifraud._request')
    @async.inline_callbacks
    def mock_request(*args, **kwargs):
        yield
        async.return_value({})


@pytest.fixture
def mock_taximeter_notify(patch):
    class NotifyInfo:
        notify_count = 0
        last_payment_type = None

    notify_info = NotifyInfo()

    @patch('taxi.internal.notifications.taximeter.notify')
    @async.inline_callbacks
    def _notify(order_state, payment_type, **kwargs):
        yield
        notify_info.notify_count += 1
        notify_info.last_payment_type = payment_type

    return notify_info


@pytest.fixture
def mock_fix_change_payment_in_py2_config(patch):
    def _mock(is_enabled):
        @patch('taxi.config.FIX_CHANGE_PAYMENT_IN_PY2.get')
        @pytest.inline_callbacks
        def _get_value():
            if is_enabled:
                async.return_value(
                    {
                        'enable': True,
                        'order_groups': [
                            {
                                'percent': 100,
                                'salt': 'salt',
                                'start_time': '1990-01-02T18:05:00Z',
                            },
                        ],
                    }
                )
            async.return_value({'enable': False, 'order_groups': []})
            yield

    return _mock


@pytest.fixture
def corp_clients_get_client_by_client_id_mock(patch, load):
    @patch('taxi.external.corp_clients.get_client_by_client_id')
    def get_client_by_client_id(client_id, fields=None, log_extra=None, **kwargs):
        data = json.loads(load('corp_clients.json'))
        items = [item for item in data if item['_id'] == client_id]
        if not items:
            raise corp_clients.NotFoundError
        item = items[0]
        item['id'] = item['_id']
        if fields:
            fields.append('id')
            return {field: item.get(field) for field in fields}
        else:
            return item


@pytest.fixture
def mock_send_event(patch):
    @patch('taxi.external.order_core.send_event')
    @async.inline_callbacks
    def _send_event_legacy(
            order_id, event_key, idempotency_key, event_arg=None,
            event_extra_payload=None, filter=None, extra_update=None,
            processing_version=None, eta=None, fields=None,
            log_extra=None
    ):
        from taxi.internal import dbh
        Proc = dbh.order_proc.Doc
        status_updates = Proc.order_info.statistics.status_updates

        event = {
            status_updates.created.key: datetime.datetime.utcnow(),
            status_updates.need_handling.key: True,
            'x-idempotency-token': idempotency_key,
        }
        if event_key is not None:
            event[status_updates.reason_code.key] = event_key
        if event_arg is not None:
            event[status_updates.reason_arg.key] = event_arg
        if event_extra_payload is not None:
            event.update(event_extra_payload)

        update = {}
        if extra_update is not None:
            update.update(extra_update)
        dbh._helpers.Query.add_modifiers(
            update, '$set', '$push', '$currentDate', '$inc')
        update['$set'].update({
            Proc.processing.need_start: True,
        })
        update['$push'][status_updates] = event
        update['$currentDate'][Proc.updated] = True
        update['$inc'][Proc.processing.version] = 1
        update['$inc'][Proc.order.version] = 1

        query = {'_id': order_id}
        if filter is not None:
            query.update(filter)
        if processing_version is not None:
            query[Proc.processing.version] = processing_version

        if fields is not None and Proc.order_link not in fields:
            fields.append(Proc.order_link)
        result = yield db.order_proc.find_and_modify(
            query, update, new=True, fields=fields)
        if not result:
            raise order_core.BaseError(
                'find_and_modify returned empty object for query %r' % query
            )
        async.return_value(result)

    return _send_event_legacy


@pytest.fixture
def use_coupons_exp3(patch):
    consumer_experiment = \
        coupons_manager.EXPEROMENT_CONSUMER_PROMOCODES
    name_experiment = \
        coupons_manager.ACCESS_DB_PROMOCODES_IN_COUPONS_EXP

    def use_coupons(coupons_enabled):
        @patch('taxi.external.experiments3.get_values')
        @async.inline_callbacks
        def _dummy_get_values(consumer, args, **kwargs):
            yield
            assert consumer == consumer_experiment
            async.return_value([
                experiments3.ExperimentsValue(
                    name_experiment,
                    {'enabled': coupons_enabled},
                ),
            ])

    return use_coupons


@pytest.fixture
def coupons_find_one(patch):
    @patch('taxi.external.coupons.promocodes_find_one')
    @async.inline_callbacks
    def find_one(
        filters,
        use_primary=None,
        projection=None,
        tvm_src_service=None,
        log_extra=None
    ):
        result = yield db.promocodes.find_one(filters, projection)
        response = {}
        if result:
            response = {
                "document": json.dumps(result)
            }
        async.return_value(response)


@pytest.fixture
def coupons_count(patch):
    @patch('taxi.external.coupons.promocodes_count')
    @async.inline_callbacks
    def count(
        filters,
        use_primary=None,
        tvm_src_service=None,
        log_extra=None
    ):
        result = yield db.promocodes.find(filters, ["series_id"]).count()
        response = {
            "count": result
        }
        async.return_value(response)


@pytest.fixture
def coupons_insert(patch):
    @patch('taxi.external.coupons.promocodes_insert')
    @async.inline_callbacks
    def insert(doc, tvm_src_service, log_extra=None):
        doc_dict = doc.decode()
        yield db.promocodes.insert(doc_dict)
