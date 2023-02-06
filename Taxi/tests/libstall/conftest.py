import asyncio
from contextlib import suppress
import glob
import inspect
import os.path
import re                   # pylint: disable=wrong-import-order
import urllib.parse
from uuid import uuid4

from aiohttp import hdrs, helpers
import easytaphttp
import pytest               # pylint: disable=wrong-import-order

from libstall import config
import libstall.json_pp
import libstall.pg.dbh
import libstall.util
import libstall.web


@pytest.fixture
async def now():
    def _now(*a, **k):
        return libstall.util.now(*a, **k)
    yield _now


@pytest.fixture
async def uuid():
    def _uuid():
        return uuid4().hex
    yield _uuid


@pytest.fixture
async def cfg():
    config.cfg.reload()
    yield config.cfg
    config.cfg.reload()


@pytest.fixture(scope='function')
async def at_loop_close(event_loop):  # pylint: disable=unused-argument
    _at_loop_close = []
    yield _at_loop_close
    for fn in _at_loop_close:
        await fn()


@pytest.fixture
# pylint: disable=unused-argument,redefined-outer-name
async def dbh(event_loop):
    yield libstall.pg.dbh.dbh
    if not event_loop.is_closed():
        await libstall.pg.dbh.dbh.close()


class AioHttpTestAgent(easytaphttp.WebTestAgent):
    mode = 'async'

    def __init__(self, tap, client):    # pylint: disable=redefined-outer-name
        self.client = client
        self.tap = tap

    async def request(self, method, url, headers, body, proto='1.0'):
        # pylint: disable=invalid-overridden-method
        url = urllib.parse.urlparse(url)
        url = '?'.join((url.path or '/', url.query))

        headers = {k: str(v) for k, v in headers.items()}
        response = await self.client.request(
            method.upper(),
            url,
            headers=headers,
            data=body,
        )
        ctype = response.headers.get(hdrs.CONTENT_TYPE, '').lower()
        mimetype = helpers.parse_mimetype(ctype)
        if mimetype.type in ['application', 'message', 'text']:
            content = await response.text()
        else:
            content = await response.read()

        headers = {}
        for n, v in response.headers.items():
            if n in headers:
                if isinstance(headers[n], tuple):
                    headers[n] = headers[n] + (v,)
                else:
                    headers[n] = (headers[n], v)
            else:
                headers[n] = v

        return {
            'status': response.status,
            'reason': response.reason,
            'headers': headers,
            'body': content,
        }


class AioHttpTestApp(easytaphttp.WebTest):
    # pylint: disable=too-many-branches
    _auth_user = None
    _auth_token = None

    # pylint: disable=redefined-outer-name
    def __init__(self, tap, client, **kw):
        agent = AioHttpTestAgent(tap, client)
        self.client = client
        kw.setdefault('json_encoder', libstall.json_pp.dumps)
        super().__init__(tap, agent, **kw)

    # pylint: disable=arguments-differ,arguments-renamed
    async def _arequest_ok(self, method, route,
                           desc=None, *, framelevel=2, **kw):
        try:
            url = None

            if isinstance(route, str):
                if route.startswith('/'):
                    url = route
                else:
                    lst = [self.client.app]
                    # pylint: disable=protected-access
                    lst += self.client.app._subapps
                    for subapp in lst:
                        if route in subapp.router:
                            url = subapp.router[route].url_for(
                                **kw.get('params_path', {}))
                            break
            elif isinstance(route, tuple):
                variable = {k: str(v) for k, v in route[1].items()}
                url = self.client.app.router[route[0]].url_for(**variable)
                if route[2]:
                    url = url.with_query(**route[2])
            else:
                url = route

            if not url:
                raise ValueError(f'Can`t resolve "{route}" as url')

        except KeyError as e:
            if not desc:
                desc = f'{method} { route }'
            self.tap.failed(desc, framelevel=None)
            self.tap.diag(f'Can not find URL: { e }')
            # pylint: disable=protected-access
            self.tap.diag(self.tap._frame(framelevel))
            return self

        url = str(url)

        if self._auth_token:
            headers = kw.get('headers', {})
            headers['Authorization'] = ('Bearer ' + str(self._auth_token))
            kw['headers'] = headers
        elif self._auth_user:
            headers = kw.get('headers', {})
            headers['Authorization'] = (
                'Bearer ' + self._auth_user.token(self._auth_user.device[0])
            )
            kw['headers'] = headers
        return await super()._arequest_ok(method, url, desc,
                                          framelevel=framelevel + 1, **kw)


@pytest.fixture
# pylint: disable=redefined-outer-name,unused-argument
async def http_api(aiohttp_client, tap):
    async def _creator(spec=None, cls=AioHttpTestApp, stack_depth=1):
        if spec and isinstance(spec, str):
            spec = [spec]
        if not spec:
            current = os.path.abspath('tests')
            test    = os.path.dirname(inspect.stack()[stack_depth].filename)
            spec_path = os.path.join(
                'doc', test.replace(current + '/', '', 1) + '.yaml'
            )
            if os.path.exists(spec_path):
                spec = [spec_path]
        if not spec:
            spec = glob.glob('doc/api/**/*.yaml', recursive=True)
            spec = list(filter(lambda x: not re.match(r'.*/models/', x), spec))

        app = libstall.web.ApplicationAuto(spec=spec)
        client = cls(tap, await aiohttp_client(app))
        client.app = app    # pylint: disable=attribute-defined-outside-init

        return client
    return _creator


@pytest.fixture
async def perfomance():
    """
    Проверка сорости выполнения.
    Получает короутину и сколько времени ее надо повторять.
    На выходе отдает количество повторений которое успело сделать и реальное
    время выполнения (на большом количестве всегда будет близко к заданному).
    """
    async def _test(coro, timeout: float):
        count = 0
        start = current = asyncio.get_event_loop().time()
        while current - start < timeout:
            await coro()
            count += 1
            current = asyncio.get_event_loop().time()

        return (count, current - start)

    async def _wrapper(coro, timeout: float = 2.0):
        with suppress(asyncio.TimeoutError):
            count, total_time = await asyncio.wait_for(
                _test(coro=coro, timeout=timeout),
                timeout=timeout,
            )

        return count, total_time

    return _wrapper

__all__ = ('dbh', 'cfg', 'uuid', 'http_api', 'AioHttpTestApp')
