import collections
import functools
import inspect
import io
import json as std_json
import logging
import os
import pathlib

import pytest
import requests

try:
    import yatest.common  # noqa
    YATEST = True
except ImportError:
    YATEST = False

from taxi_buildagent.tools.vcs import git_repo


@pytest.fixture(name='search_path')
def _search_path(request):
    if YATEST:
        fullname = pathlib.Path(
            yatest.common.source_path(request.module.__file__),
        )
    else:
        fullname = str(request.fspath)
    test_module_dir = os.path.dirname(fullname)
    test_module_name = os.path.splitext(os.path.basename(fullname))[0]
    static_dir = os.path.join(test_module_dir, 'static')
    node_name = request.node.name
    local_path = [os.path.join(test_module_name, node_name)]
    if '[' in node_name:
        node_short_name = node_name[: node_name.index('[')]
        local_path.append(os.path.join(test_module_name, node_short_name))
    local_path.append(test_module_name)
    local_path.append('default')
    search_directories = [
        os.path.join(static_dir, subdir) for subdir in local_path
    ]

    def _search_path(filename, directory=False):
        if directory:
            path_check = os.path.isdir
        else:
            path_check = os.path.isfile
        for _dir in search_directories:
            abs_filename = os.path.join(_dir, filename)
            if path_check(abs_filename):
                yield abs_filename

    return _search_path


@pytest.fixture
def get_file_path(search_path):
    def _get_file_path(filename):
        for path in search_path(filename):
            return path
        raise FileNotFoundError('File %s was not found' % filename)

    return _get_file_path


@pytest.fixture
def get_directory_path(search_path):
    def _get_directory_path(filename):
        for path in search_path(filename, directory=True):
            return path
        raise FileNotFoundError('Directory %s was not found' % filename)

    return _get_directory_path


@pytest.fixture(name='open_file')
def _open_file(search_path):
    # better to rewrite signature of function in future
    # pylint: disable=keyword-arg-before-vararg
    def _open_file(filename, mode='r', encoding='utf-8', *args, **kwargs):
        for _filename in search_path(filename):
            return open(
                _filename, mode=mode, encoding=encoding, *args, **kwargs,
            )
        # Raise `ValueError`, not `IOError`, because file **must** exist
        # (or maybe you test writer has made an typo)
        raise FileNotFoundError('File %s wasn\'t found' % filename)

    return _open_file


@pytest.fixture(name='load')
def _load(open_file):
    """Load data from `tests-pytest/static` directory.

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

    def _load(filename, *args, **kwargs):
        with open_file(filename, *args, **kwargs) as fp:
            return fp.read()

    return _load


@pytest.fixture
def load_binary(load):
    """Load binary data from `tests-pytest/static` directory

    Usage:

        def test_something(load_binary):
            raw_data = load_binary('filename')
    """

    def _load_binary(filename):
        return load(filename, 'rb', encoding=None)

    return _load_binary


@pytest.fixture
def load_json(load, _session_context):
    """Load json doc from `tests-pytest/static directory

    Usage:

        def test_something(load_json):
            json_obj = load_json('filename')
    """

    def _load_json(filename, *args, **kwargs):
        return std_json.loads(load(filename), *args, **kwargs)

    return _load_json


@pytest.fixture(scope='session')
def _session_context():
    class SessionContext:
        pass

    return SessionContext()


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

    def func(**kw):
        return collections.namedtuple('Stub', kw.keys())(**kw)

    return func


class CallsInfoWrapper:
    """Function wrapper that adds information about function calls.

    Wrapped function `__dict__` is extend with two public attributes:

        `call`  - pops information about first call
        `calls` - pops all calls information

    """

    def __init__(self, func):
        self.__func = func
        self.__is_method = inspect.ismethod(func)
        self.__calls = []
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

    def __call__(self, *args, **kwargs):
        func_spec = inspect.getfullargspec(self.__func)
        func_args = func_spec.args
        if self.__is_method:
            func_args = func_args[1:]
        func_varargs = func_spec.varargs
        func_varkw = func_spec.varkw
        func_kwonlyargs = func_spec.kwonlyargs
        func_kwonlydefaults = func_spec.kwonlydefaults
        defaults = func_spec.defaults or ()
        func_defaults = dict(zip(func_args[-len(defaults) :], defaults))

        dct = dict(zip(func_args, args))
        for argname in func_args[len(args) :]:
            if argname in kwargs:
                dct[argname] = kwargs[argname]
            else:
                dct[argname] = func_defaults[argname]
        if func_varargs is not None:
            dct[func_varargs] = args[len(dct) :]
        for argname in func_kwonlyargs:
            if argname in kwargs:
                dct[argname] = kwargs[argname]
            else:
                dct[argname] = func_kwonlydefaults[argname]
        if func_varkw is not None:
            dct[func_varkw] = dict(
                (k, v) for (k, v) in kwargs.items() if k not in dct
            )

        self.__calls.append(dct)
        return self.__func(*args, **kwargs)


@pytest.fixture(name='mock')
def _mock():
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

    def wrapper(func):
        return functools.wraps(func)(CallsInfoWrapper(func))

    return wrapper


@pytest.fixture(name='patch')
def _patch(mock, monkeypatch):
    """Monkey patch helper.

    Usage:

        @patch('full.path.to.func')
        def foo(*args, **kwargs):
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


class RequestsMock:
    def __init__(self, _mock):
        self._mock = _mock
        self._handlers = {}
        self._errors = []

    def fake_request(self, method, url, **kwargs):
        for base_url, handler in self._handlers.items():
            if url.startswith(base_url):
                try:
                    return handler(method, url, **kwargs)
                except Exception as exc:
                    self._errors.append((method, url, exc))
                    raise

        exc_ = NotImplementedError('request %s not patched' % url)
        self._errors.append((method, url, exc_))
        raise exc_

    def __call__(self, base_url):
        def _mock(handler):
            mock_handler = self._mock(handler)
            self._handlers[base_url] = mock_handler
            return mock_handler

        return _mock

    # needed for mock
    # pylint: disable=redefined-outer-name
    @staticmethod
    def response(
            status_code=200, json=None, headers=None, content=None, text=None,
    ):
        return ResponseMock(status_code, json, headers, content, text)

    def raise_first_exception(self):
        if self._errors:
            raise Exception('RequestsMock %s %s error: %r' % self._errors[0])


class ResponseMock:
    def __init__(
            self,
            status_code=200,
            json=None,
            headers=None,
            content=None,
            text=None,
            raw=None,
    ):
        self.status_code = status_code
        self._json = json
        self._headers = headers or {}
        self._content = content
        self._text = text
        self._raw = raw

    @property
    def headers(self):
        return self._headers

    @property
    def content(self):
        return self._content

    def json(self):
        assert self._json is not None
        return self._json

    @property
    def text(self):
        assert self._text is not None
        return self._text

    @property
    def raw(self):
        assert self._content is not None
        if self._raw is None:
            return io.BytesIO(self._content)

        return self._raw

    @raw.setter
    def raw(self, value):
        self._raw = value

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError('error')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture(autouse=True)
def patch_requests(mock, patch):
    """Patch http requests

    Usage:

        @patch_requests('http://yandex.ru/')
        def func(method, url, **kwargs):
            return patch_requests.response(203, json={1: 2})

        response = requests.get('http://yandex.ru/asdf')
        assert response.status_code == 203
        assert response.json() == {1: 2}
        assert func.calls == [{
            'method': 'get',
            'url': 'http://yandex.ru/asdf',
            'kwargs': {'allow_redirects': True, 'params': None},
        }]

    """
    requests_mock = RequestsMock(mock)
    patch('requests.sessions.Session.request')(requests_mock.fake_request)
    yield requests_mock
    requests_mock.raise_first_exception()


@pytest.fixture
def chdir():
    """Change current directory

    Usage:

        chdir('/tmp')

    """
    curdir = os.path.curdir
    yield os.chdir
    os.chdir(curdir)


@pytest.fixture
def repos_dir(tmpdir, monkeypatch):
    path = pathlib.Path(tmpdir.mkdir('repos'))
    monkeypatch.setattr(git_repo, 'MIRROR_DIR', str(path))
    return path


@pytest.fixture(autouse=True)
def _remove_loggers(monkeypatch):
    monkeypatch.setenv('LOG_LEVEL', 'DEBUG')
    yield
    logger = logging.getLogger()
    logger.handlers = []


@pytest.fixture
def home_dir(tmpdir, monkeypatch):
    path = tmpdir.mkdir('home')
    monkeypatch.setenv('HOME', str(path))
    monkeypatch.setenv('XDG_CONFIG_HOME', str(path / '.config'))
    return path


@pytest.fixture(autouse=True)
def git_restrict_network(monkeypatch):
    monkeypatch.setenv('GIT_SSH_COMMAND', 'restricted-git')
    monkeypatch.setenv('ALL_PROXY', 'restricted-http')


@pytest.fixture(autouse=True)
def patch_sleep(patch):
    patch('time.sleep')(lambda _: None)
