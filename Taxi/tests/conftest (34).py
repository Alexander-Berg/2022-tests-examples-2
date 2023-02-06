# pylint: skip-file

import asyncio
import csv
import glob
import importlib
import inspect
import io
import logging
import os
import pkgutil
import random
import re
import shutil
import string
import sys
import tempfile
import typing
from collections import defaultdict
from copy import deepcopy
from datetime import timedelta
from logging.handlers import BufferingHandler
from random import randint

import aiohttp
import chardet
import pytest
from aiohttp import web
from botocore.stub import Stubber
from dateutil.tz import tzlocal
from kikimr.public.sdk.python.client.resolver import DiscoveryResult
from mouse.validate.enum import plugin as enum_plugin

import libstall.config
import libstall.pg.dbh
import libstall.util
import stall.job
import stall.lp
import stall.model.analytics.event_cache
import stall.model.event_cache
import stall.mongo
import stall.queue
import tests.dataset
from libstall import json_pp
from libstall.log import metrics_log
from libstall.model.storable.pg_debug import pg_debug
from libstall.web import ApplicationAuto
from stall import keyword, log
from stall.client import httpx
from stall.client.clickhouse import ClickHouseClient
from stall.client.s3 import client as s3_client
from stall.logbroker import LogbrokerReader
from stall.model.event_cache import EventQueue
from tests.libstall.conftest import *  # noqa
from tests.model.clickhouse.base_model import TopicModel


@pytest.fixture(scope='function', autouse=True)
def debug_sql_explain():
    """Выводит статистику собранную pg_debug из EXPLAIN ANALYZE запросов"""
    yield

    # pylint: disable=too-many-nested-blocks

    if not pg_debug:
        return
    if 'DEBUG_EXPLAIN' in os.environ and not os.environ.get('DEBUG_EXPLAIN'):
        return

    # Словарь с ошибками планировки
    rules: dict = {
        r'Seq Scan': None,          # перебор без индекса
        r'Sort Key:': None,         # индекс не подходит под сортировку
        r'Sort Method:': None,      # индекс не подходит под сортировку

        # Фильтрация выборки без использования индекса.
        # TODO: В будущем надо перевести в error
        r'Rows Removed by Filter:\s*(\d+)': libstall.config.cfg('cursor.limit'),
        r'Bitmap Heap Scan': None,  # мерж нескольких индексов
    }

    for i, query in enumerate(pg_debug.analyze()):
        # Проверим есть ли проблема
        problem = False
        for row in query.explain:
            plan = row['QUERY PLAN']

            for rule, value in rules.items():
                result = re.search(rule, plan)
                if result:
                    if value is not None:
                        if int(result.group(1)) > value:
                            problem = True
                    else:
                        problem = True
                if problem:
                    break
            if problem:
                break

        if not problem and not os.environ.get('DEBUG_EXPLAIN'):
            continue

        # Вывод ошибки
        print(
            f'\n\n=== Query {i+1} warning EXPLAIN ANALYZE {("=") * (80 - 36)}',
            query.query.strip(),
            '\n',
            '\n'.join([x['QUERY PLAN'] for x in query.explain]),
            ('=') * 80,
            sep='\n',
            file=sys.stderr
        )


@pytest.fixture
async def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    await libstall.pg.dbh.dbh.close()


def _order_by_path(path):
    if not hasattr(_order_by_path, 'cache'):
        _order_by_path.cache = {}

    directory = os.path.dirname(path)

    if directory not in _order_by_path.cache:
        if directory == '/':
            _order_by_path.cache[directory] = 0xFFFFFFFF
            return _order_by_path.cache[directory]

        base_dir = os.path.basename(directory)
        if base_dir == 'tests':
            _order_by_path.cache[directory] = 0xFFFFFFFF
            return _order_by_path.cache[directory]

        ofile = os.path.join(directory, '.order')
        try:
            with open(ofile, 'r') as fh:
                order = int(fh.readline().strip(), base=10)
                _order_by_path.cache[directory] = order
        except Exception:
            _order_by_path.cache[directory] = _order_by_path(directory)

    return _order_by_path.cache[directory]


def pytest_collection_modifyitems(items):
    for item in items:
        #         print(item, inspect.iscoroutinefunction(item.function))
        # полная жопень, пока не разобрались.
        # фикстура api конфликтует с pytest.mark.asyncio
        if 'tests/api/' in str(item.fspath):
            continue

        if inspect.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)

    items.sort(key=lambda x: (_order_by_path(x.fspath), x.fspath))


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report):
    when = getattr(report, 'when', '')
    outcome = getattr(report, 'outcome', '')
    if when == 'setup' and outcome == 'passed':
        # Не выводим соббщения с переносом строки
        report.sections = []

    if when == 'teardown' and outcome == 'failed':
        # Не выводим ошибку для teardown
        report.when = 'skip_teardown'


class HttpClient(AioHttpTestApp):
    def set_user(self, user):
        if not user.device:
            raise RuntimeError('нет секции device у пользователя')
        self._auth_user = user

    async def set_role(self, role, force_role=None):
        if role in ('barcode_executer',):
            user = await tests.dataset.user(role='executer')
            user.force_role = role
        else:
            user = await tests.dataset.user(role=role)

        if force_role:
            force_role = user.role.__class__(force_role)
            user.force_role = force_role
        self.set_user(user)

    def set_token(self, token):
        self._auth_token = token


@pytest.fixture
# pylint: disable=redefined-outer-name,unused-argument
async def api(http_api, mongo, dbh):
    async def _creator(spec=None,
                       role=None,
                       force_role=None,
                       cls=HttpClient,
                       user=None,
                       token=None):
        client = await http_api(spec=spec, cls=cls, stack_depth=2)
        if token:
            client.set_token(token)
        elif role:
            if role.startswith('token:'):
                client.set_token(libstall.config.cfg(role[6:]))
            else:
                await client.set_role(role, force_role)
        if user:
            client.set_user(user)
        return client

    yield _creator
    mongo.close()
    await dbh.close()


@pytest.fixture(scope='function')
# pylint: disable=redefined-outer-name
async def server(aiohttp_server, mongo, event_loop):
    servers = []

    async def _creator(spec=None):
        if not spec:
            spec = [x for x in glob.glob('doc/api/**/*.yaml', recursive=True)
                    if x.find('/models/') == -1]
        elif isinstance(spec, str):
            spec = [spec]

        app = ApplicationAuto(spec=spec)
        server = await aiohttp_server(app)
        loop = asyncio.get_event_loop()
        servers.append((loop, server))
        return server

    yield _creator
    for l, s in servers:
        if id(l) == id(event_loop):
            await s.close()
    mongo.close()


@pytest.fixture
async def mongo():
    yield stall.mongo.mongo
    stall.mongo.mongo.close()


@pytest.fixture
async def lp():
    yield stall.lp
    stall.lp.pytest_cache = []


@pytest.fixture
async def queue():
    yield stall.queue.queue
    await asyncio.wait({stall.queue.queue.close()})


@pytest.fixture
async def job():  # pylint: disable=redefined-outer-name
    # Каждый тест на своей очереди, для параллельности
    stall.job.job.name = f'job-test-{libstall.util.uuid()}'
    # UGLY HACK чтобы новой тестовой очередью можно было воспользоваться
    old_enum = EventQueue.tube.plugins['enum']
    old_validator = EventQueue.tube.validators['enum']
    EventQueue.tube.plugins['enum'] = old_enum + (stall.job.job.name,)
    EventQueue.tube.validators['enum'] = enum_plugin(
        EventQueue.tube.plugins['enum'])
    yield stall.job.job
    await asyncio.wait({stall.job.job.stop()})
    EventQueue.tube.plugins['enum'] = old_enum
    EventQueue.tube.validators['enum'] = old_validator


@pytest.fixture
async def push_events_cache(monkeypatch, job):
    # pylint: disable=unused-argument,redefined-outer-name

    modules = [
        stall.model.event_cache,
        stall.model.analytics.event_cache,
    ]

    models = {
        module.EventCache.database: module.EventCache
        for module in modules
    }

    async def _wrapper(
            obj,
            job_method: typing.Union[list, str] = None,
            event_type: 'lp,queue' = 'queue',
            database: 'main|analytics' = 'main',
    ):

        base_model = models[database]

        class EventCacheMock(base_model):
            @classmethod
            async def top_candidates(cls, *args, **kwargs):
                nonlocal job_method
                records = await super().top_candidates(*args, **kwargs)
                job_methods = job_method
                if isinstance(job_method, str):
                    job_methods = [job_method]

                # Отфильтруем ивенты по колбекам
                _records = []
                for record in records:
                    _events = []
                    for e in record.events:
                        if event_type == 'queue' and job_methods:
                            callback = e['data'].get('callback', '')
                            if not any(j for j in job_methods if j in callback):
                                continue

                        _events.append(e)

                    if _events:
                        record.events = _events
                        _records.append(record)

                return _records

        async def put(callback, *, opts=None, tube=None, **kwargs):
            attrs = {
                'caller': inspect.stack()[1],
                'callback': job.serialize(callback),
            }
            attrs.update(opts or {})

            # добавляем в очередь только по имени
            return await job.queue.put(job.name, attrs, **kwargs)

        setattr(EventCacheMock, '__name__', base_model.__name__)
        monkeypatch.setattr(job, job.put.__name__, put)

        obj = obj if isinstance(obj, list) else [obj]
        table = type(obj[0]).meta.table
        pk_name = table.primary_key
        pk_values = [getattr(o, pk_name) for o in obj]
        await asyncio.gather(*[
            EventCacheMock.daemon_cycle(
                shard,
                ev_type=event_type,
                conditions=[
                    ('tbl', table.name),
                    ('pk', pk_values),
                ],
                lock_name=f'event_push-{job.name}-{shard}-{event_type}',
                lock_kwargs={'rm': True},
            )
            for shard in range(EventCacheMock.nshards())
        ])

    yield _wrapper


@pytest.fixture
async def tmpdir():
    dirname = tempfile.mkdtemp()
    yield dirname
    shutil.rmtree(dirname)


@pytest.fixture
# pylint: disable=redefined-outer-name
def unique_int(now):
    """Помогает создавать уникальные целые числа"""
    def _wrapper():
        return int(
            str(int(now().timestamp() * 1000000)) +
            str(int(randint(1000, 9999)))
        )

    return _wrapper


@pytest.fixture
def unique_email(uuid):
    """Помогает создавать уникальные почтовые адреса"""
    def _wrapper():
        return f'{uuid()}@yandex-team.ru'
    return _wrapper


@pytest.fixture
def unique_phone(unique_int):
    """Помогает создавать уникальные телефоны"""
    def _wrapper():
        return f'+7{unique_int()}'
    return _wrapper


@pytest.fixture
# pylint: disable=unused-argument,redefined-outer-name
async def dataset(dbh, mongo):
    yield tests.dataset


@pytest.fixture
def now():  # pylint: disable=function-redefined
    # NOTE: почему то функция испортирующаяся из libstall не работает
    #       поэтому оставил здесь новую
    def _now(*args, **kwargs):
        return libstall.util.now(*args, **kwargs)

    return _now


@pytest.fixture
def tzone():  # pylint: disable=function-redefined
    def _tzone(value):
        return libstall.util.tzone(value)

    return _tzone


@pytest.fixture
def time2time():  # pylint: disable=function-redefined
    def _time2time(value, tz=None):
        return libstall.util.time2time(value, tz)

    return _time2time


@pytest.fixture
def time2iso():  # pylint: disable=function-redefined
    def _time2iso(value, tz=None):
        return libstall.util.time2iso(value, tz)

    return _time2iso


@pytest.fixture
def time2iso_utc():  # pylint: disable=function-redefined
    def _time2iso_utc(value):
        return libstall.util.time2iso_utc(value)

    return _time2iso_utc


@pytest.fixture
def load_json():
    def _wrapper(file_name):
        if os.path.isabs(file_name):
            path = file_name
        else:
            current_dir = os.path.dirname(inspect.stack()[1].filename)
            path = os.path.join(current_dir, file_name)

        with open(path, 'r') as fh:
            json_body = fh.read()

        return json_pp.loads(json_body)

    return _wrapper


@pytest.fixture
def load_file():
    """Загружает файл с автоматической конвертацией в utf-8"""

    def _wrapper(file_name):
        if os.path.isabs(file_name):
            path = file_name
        else:
            current_dir = os.path.dirname(inspect.stack()[1].filename)
            path = os.path.join(current_dir, file_name)

        with open(path, 'rb') as fh:
            body = fh.read()

        if not body:
            return ''

        encoding = chardet.detect(body)
        body = body.decode(encoding['encoding'])

        return body

    return _wrapper


@pytest.fixture
def load_bytes():
    """Загружает файл в бинарном виде"""

    def _wrapper(file_name):
        if os.path.isabs(file_name):
            path = file_name
        else:
            current_dir = os.path.dirname(inspect.stack()[1].filename)
            path = os.path.join(current_dir, file_name)

        with open(path, 'rb') as fh:
            body = fh.read()

        return body

    return _wrapper


# pylint: disable=redefined-outer-name
@pytest.fixture
async def wait_order_status(tap, dataset):
    tap_save = tap

    async def _wait_order_status(
            order,
            fstatus,
            *,
            user_done=None,
            tap=None,
    ):
        if tap is None:
            tap = tap_save
        return await dataset.wait_order_status(order, fstatus,
                                               user_done=user_done, tap=tap)

    yield _wait_order_status


@pytest.fixture
def make_csv_str():
    def _wrapper(fieldnames, rows):
        with io.StringIO() as buff:
            wr = csv.DictWriter(buff, fieldnames=fieldnames)
            wr.writeheader()
            for row in rows:
                wr.writerow(row)
            buff.seek(0)
            return buff.read()

    return _wrapper


@pytest.fixture
async def ext_api(aiohttp_server, tvm_ticket, monkeypatch):
    # pylint: disable=unused-argument

    async def _creator(
            client, handler: typing.Callable,
            attributes=None, middlewares=None,
    ):
        if not middlewares:
            # pylint: disable=import-outside-toplevel
            # Можно отвечать простыми объектами как в наших ручках
            from stall.middlewares.faa_application_json import middleware
            middlewares = [middleware]

        if isinstance(client, str):
            # Можно писать просто название модуля, не импортируя его в тесте
            module = importlib.import_module(f'stall.client.{client}')
            assert module, f'Модуль клиента {client} не найден'
            client = getattr(module, 'client')
            assert client, f'Объект клиента {client} не найден'

        app = web.Application()
        app.router.add_route(method='*', path='/{tail:.*}', handler=handler)
        for middleware in (middlewares or []):
            app.middlewares.append(middleware)

        _server = await aiohttp_server(app)

        monkeypatch.setattr(
            client, 'base_url',
            f'{_server.scheme}://{_server.host}:{_server.port}/'
        )

        if attributes:
            for key, value in attributes.items():
                monkeypatch.setattr(
                    client, key, value
                )

        return client

    yield _creator


# pylint: disable=redefined-outer-name
@pytest.fixture
async def tvm_ticket(monkeypatch, uuid):
    _tickets = {}

    def fake_ticket_getter(tvm_id):
        return _tickets.setdefault(tvm_id, uuid())

    monkeypatch.setattr(
        httpx.tvm,
        httpx.tvm.get_service_ticket.__name__,
        fake_ticket_getter
    )


@pytest.fixture
async def caplog(caplog, cfg):
    class PropagateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger('root').handle(record)

    handler = PropagateHandler()
    log.addHandler(handler)
    yield caplog
    log.removeHandler(handler)
    log.setLevel(cfg('log.level'))


@pytest.fixture
def time_mock(monkeypatch):
    class FakeTime:
        def __init__(self):
            self._value = libstall.util.now()
            self._in_mock = True

        def now(self, tz=None):
            assert self._in_mock, "time_mock leaked"

            value = self._value.replace(microsecond=0)
            if tz is not None:
                value = value.astimezone(libstall.util.tzone(tz))
            return value

        def sleep(self, **kwargs):
            self._value += timedelta(**kwargs)

        def set(self, value):
            self._value = libstall.util.time2time(value)

    fake_time = FakeTime()

    monkeypatch.setattr(
        libstall.util, libstall.util._now.__name__,
        fake_time.now
    )

    yield fake_time

    fake_time._in_mock = False


@pytest.fixture
def metrics_log_mock():
    handler = BufferingHandler(100)
    current_level = metrics_log.level
    metrics_log.setLevel(logging.INFO)
    metrics_log.addHandler(handler)
    yield handler.buffer
    metrics_log.removeHandler(handler)
    metrics_log.setLevel(current_level)


@pytest.fixture
def replace_csv_column():
    """
    Заменяет 1 столбец у всех записей в CSV данных.
    """

    def _wrapper(
            csv_str: str,
            column: str,
            value: typing.Union[str, tuple, list],
    ) -> str:
        headers, body = csv_str.strip().split('\n', maxsplit=1)
        columns = headers.rstrip(';').split(';')
        column_id = columns.index(column)

        modified_csv = [f'{headers}']
        i = 0
        for line in body.split('\n'):
            line = line.strip()
            if line == '':
                modified_csv.append(line)
                continue

            fields = line.split(';')

            fields[column_id] = value if isinstance(value, str) else value[i]
            modified_csv.append(f'{";".join(fields[:len(columns)])}')
            i += 1

        return '\n'.join(modified_csv)

    return _wrapper


@pytest.fixture
def replace_csv_data(replace_csv_column):
    def _wrapper(csv_str: str, *items: typing.Union[tuple, list]) -> str:
        for column, value in items:
            csv_str = replace_csv_column(csv_str, column, value)
        return csv_str

    return _wrapper


class MockResponse:
    def __init__(self, status, text, headers):
        self.status = status
        self._text = text
        self.headers = headers or {}

    async def text(self):
        return self._text

    async def read(self):
        pass

    @property
    def ok(self) -> bool:
        return self.status < 400

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self

    async def json(self):
        return json_pp.loads(self._text)

    def __repr__(self):
        return (
            f'{self.__class__}: '
            f'ok={self.ok} '
            f'status={self.status} '
            f'text={self._text}'
        )


@pytest.fixture(scope='function')
def mock_client_response(monkeypatch, tvm_ticket):
    # pylint: disable=unused-argument,no-self-use
    """Отдаёт фейковый ответ внешнего сервиса"""

    async def _ensure_auth(self, *args, **kwargs):
        self.auth['X-Ya-Service-Ticket'] = tvm_ticket(12345)

    def _mock_client_response(status, text=None, json=None, headers=None):
        class MockClientSession:
            def __init__(self, *args, **kwargs):
                pass

            def request(self, *args, **kwargs):
                return MockResponse(
                    status=status,
                    text=text or json_pp.dumps(json),
                    headers=headers,
                )

            async def close(self):
                pass

        monkeypatch.setattr(
            'stall.client.httpx.base.aiohttp.ClientSession',
            MockClientSession
        )
        monkeypatch.setattr(
            'stall.client.httpx.base.BaseClient.ensure_auth',
            _ensure_auth
        )

    return _mock_client_response


@pytest.fixture
def mock_client_result(monkeypatch):
    # pylint: disable=unused-argument
    """Отдаёт фейковый результат метода клиента"""

    def _mock_client_result(client, method, result=None, **kw):
        async def _mock_method(*args, **kwargs):
            if kw:
                return MockResponse(
                    status=kw.get('status'),
                    text=kw.get('text') or json_pp.dumps(kw.get('json')),
                    headers=kw.get('headers'),
                )

            return result

        module = importlib.import_module(f'stall.client.{client}')
        if not module:
            raise KeyError(f'Клиент {client} не найден')

        name = None
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                if getattr(obj, method):
                    break
        else:
            raise KeyError(f'У клиента {client} нет метода {method}')

        if not name:
            raise KeyError(f'У клиента {client} нет класса с методом {method}')

        monkeypatch.setattr(f'{module.__name__}.{name}.{method}', _mock_method)

    return _mock_client_result


@pytest.fixture
def random_secret_key():
    def rnd(x):
        return "".join(random.choices(
            string.ascii_uppercase + string.digits, k=x))

    return f'{rnd(4)}-{rnd(4)}'


@pytest.fixture
def random_title():
    return keyword.noun()


class AutoCloseGenerator:
    # Закроем генератор, если не было новых данных

    def __init__(self, generator, timeout=0.5) -> None:
        self.generator = generator
        self.timeout = timedelta(seconds=timeout)
        self.is_processing = False
        self.last_update = libstall.util.now()

    async def __aiter__(self):
        self.last_update = libstall.util.now()
        asyncio.create_task(self.kill_generator())

        try:
            async for it in self.generator:
                self.is_processing = True
                yield it
                self.last_update = libstall.util.now()
                self.is_processing = False
        except GeneratorExit:
            pass

    async def __anext__(self):
        return await self.generator.__anext__()

    async def kill_generator(self):
        while True:
            await asyncio.sleep(0.1)
            if self.is_processing:
                continue
            if libstall.util.now() - self.last_update > self.timeout:
                break
        await self.generator.aclose()

    async def athrow(self, e):
        return await self.generator.athrow(e)


@pytest.fixture
def logbroker_balancer(cfg):
    installation = cfg('logbroker.test.installation')
    address = cfg(f'logbroker-installations.{installation}.endpoint')
    port = cfg(f'logbroker-installations.{installation}.port')

    from_response_backup = DiscoveryResult.from_response

    def from_response(rpc_state, response):
        # Логброкер (в роли балансера) перекидывает
        # изначальный коннект на другой хост
        # Другой хост - это hostname контейнера,
        # который не доступен с хостовой машины
        discovery_result = from_response_backup(rpc_state, response)
        for endpoint in discovery_result.endpoints:
            endpoint.address = address
            endpoint.port = port
            endpoint.endpoint = f'{address}:{port}'
        return discovery_result

    DiscoveryResult.from_response = from_response

    yield DiscoveryResult

    DiscoveryResult.from_response = from_response_backup


@pytest.fixture
def logbroker_read(logbroker_balancer):
    # pylint: disable=unused-argument
    async def read_messages(target, **kwargs):
        reader = LogbrokerReader(target, **kwargs)
        reader_gen = AutoCloseGenerator(reader.reading_generator)
        read = []
        async for messages in reader_gen:
            read += messages
        return read
    return read_messages


@pytest.fixture
def setup_topic(logbroker_read, uuid, cfg):
    # pylint: disable=protected-access
    # Автоматическая генерация топиков не поддерживается
    # Топики создаются через environment контейнера LOGBROKER_CREATE_TOPICS
    async def setup_topic_func(topic):
        target = uuid()

        cfg._db.o['logbroker'][target] = deepcopy(cfg('logbroker.test'))
        cfg.set(f'logbroker.{target}.topic', topic)
        cfg.set(f'logbroker.{target}.topics', [topic])
        # Вычитаем сообщения, чтобы убедится, что топик пустой
        await logbroker_read(target)
        return target
    return setup_topic_func


@pytest.fixture
async def autoclose_clickhouse_client():
    def close_session(function):
        async def wrapper(self, *args, **kwargs):
            result = await function(self, *args, **kwargs)
            await self.close()
            return result
        return wrapper

    backup_req = ClickHouseClient.req
    ClickHouseClient.req = close_session(ClickHouseClient.req)

    # Каждый тест запускается в отдельном event loop
    # Будем закрывать сессию после каждого запроса
    yield ClickHouseClient

    ClickHouseClient.req = backup_req


def find_modules(source_pkg_path):
    modules = defaultdict(set)
    work = [source_pkg_path]
    while work:
        path = work.pop()
        db_name = path.split('.')[-1]
        slash_path = path.replace('.', '/')
        for module_info in pkgutil.iter_modules([slash_path]):
            next_path = f'{path}.{module_info.name}'
            if module_info.ispkg:
                work.append(next_path)
            if module_info.name.startswith('test_'):
                # Пропускаем файлы с тестами
                continue
            module = importlib.import_module(next_path)
            modules[db_name].add(module)
    return modules


CH_TOPIC_MODELS: typing.Dict[str, typing.Set[TopicModel]] = defaultdict(set)


async def create_ch_models():
    if CH_TOPIC_MODELS:
        return
    pkg_path = '.'.join(TopicModel.__module__.split('.')[:-1])
    # Модели необходимо положить в папку с именем конфига кликхауса
    # Пример: tests/model/clickhouse/grocery/grocery_order_created.py
    # grocery - имя конфига
    # grocery_order_created.py - файл с моделью
    for db_name, modules in find_modules(pkg_path).items():
        for module in modules:
            for value in module.__dict__.values():
                if (
                    hasattr(value, '__bases__')
                    and issubclass(value, TopicModel)
                    and TopicModel != value
                ):
                    CH_TOPIC_MODELS[db_name].add(value)

    # Создадим таблицы по моделям
    for db_name, models in CH_TOPIC_MODELS.items():
        client = ClickHouseClient(db_name)
        for model in models:
            await client.request_query(
                query=model.create_query(),
                response_format=None,
            )


@pytest.fixture
async def clickhouse_client(autoclose_clickhouse_client):
    # pylint: disable=unused-argument, too-many-nested-blocks
    await create_ch_models()
    yield ClickHouseClient


@pytest.fixture
async def s3_stubber(monkeypatch):
    class CustomStubber(Stubber):
        def for_get_object_ok(
            self, bucket: str, key: str, data: bytes,
        ):
            self.add_response(
                'get_object',
                service_response={
                    'AcceptRanges': 'bytes',
                    'ContentLength': len(data),
                    'Body': io.BytesIO(data),
                },
                expected_params={
                    'Bucket': bucket,
                    'Key': key,
                }
            )

        def for_put_object_ok(
            self, bucket: str, key: str, data: bytes,
        ):
            self.add_response(
                'put_object',
                service_response={},
                expected_params={
                    'Bucket': bucket,
                    'Key': key,
                    'Body': data,
                }
            )

        def for_delete_object_ok(
            self, bucket: str, key: str,
        ):
            self.add_response(
                'delete_object',
                service_response={},
                expected_params={
                    'Bucket': bucket,
                    'Key': key,
                }
            )

        def for_get_object_error(
            self, bucket: str, key: str, error: str,
        ):
            self.add_client_error(
                'get_object',
                service_error_code=error,
                expected_params={
                    'Bucket': bucket,
                    'Key': key,
                }
            )

        def for_put_object_error(
            self, bucket: str, key: str, data: bytes, error: str,
        ):
            self.add_client_error(
                'put_object',
                service_error_code=error,
                expected_params={
                    'Bucket': bucket,
                    'Key': key,
                    'Body': data,
                }
            )

        def for_delete_object_error(
            self, bucket: str, key: str, error: str,
        ):
            self.add_client_error(
                'delete_object',
                service_error_code=error,
                expected_params={
                    'Bucket': bucket,
                    'Key': key,
                }
            )

    async with s3_client() as s3:
        # noinspection PyProtectedMember
        monkeypatch.setattr(
            s3_client,
            s3_client._create_client.__name__,
            lambda: s3._client,
        )
        yield CustomStubber(s3)
