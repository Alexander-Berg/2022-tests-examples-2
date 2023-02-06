import json

import pytest
import redis as redisdb

from taxi_tests.environment.services import redis


@pytest.fixture(scope='session')
def redis_service(
        request, ensure_service_started, _redis_masters, redis_sentinels,
        _redis_slaves):
    if (not request.config.getoption('--no-redis') and
            not request.config.getoption('--redis-host')):
        ensure_service_started(
            'redis',
            masters_ports=[port for _, port in _redis_masters],
            slaves_ports=[port for _, port in _redis_slaves],
            sentinel_port=redis_sentinels[0]['port'],
        )


@pytest.fixture
def redis_store(request, load_json, redis_service, _redis_masters):
    if request.config.getoption('--no-redis'):
        yield
        return

    redis_commands = []

    marker = request.node.get_marker('redis_store')
    if marker:
        store_file = marker.kwargs.get('file')
        if store_file is not None:
            redis_commands_from_file = load_json(
                '%s.json' % store_file, object_hook=_json_object_hook,
            )
            redis_commands.extend(redis_commands_from_file)

        if marker.args:
            redis_commands.extend(marker.args)

    redis_db = redisdb.StrictRedis(*_redis_masters[0])

    for redis_command in redis_commands:
        func = getattr(redis_db, redis_command[0])
        func(*redis_command[1:])
    try:
        yield redis_db
    finally:
        redis_db.flushall()


@pytest.fixture(scope='session')
def _redis_masters(request, worker_id, get_free_port):
    redis_host = request.config.getoption('--redis-host') or redis.DEFAULT_HOST
    redis_port = request.config.getoption('--redis-master-port')
    if worker_id == 'master':
        return [
            (redis_host, redis_port or redis.MASTER_DEFAULT_PORT),
        ]
    ports = [get_free_port() for _ in range(redis.MASTERS_NUMBER)]
    if redis_port:
        ports.pop()
        ports.append((redis_host, redis_port))
    return [
        (redis_host, port) for port in reversed(ports)
    ]


@pytest.fixture(scope='session')
def _redis_slaves(request, worker_id, get_free_port):
    redis_host = request.config.getoption('--redis-host') or redis.DEFAULT_HOST
    if worker_id == 'master':
        return [
            (redis_host, redis.SLAVE_DEFAULT_PORT),
        ]
    ports = [get_free_port() for _ in range(redis.SLAVES_NUMBER)]
    return [
        (redis_host, port) for port in ports
    ]


@pytest.fixture(scope='session')
def redis_sentinels(request, worker_id, _redis_masters, get_free_port):
    redis_host = request.config.getoption('--redis-host') or redis.DEFAULT_HOST
    redis_port = request.config.getoption('--redis-sentinel-port')
    if worker_id == 'master':
        return [
            {
                'host': redis_host,
                'port': redis_port or redis.SENTINEL_DEFAULT_PORT,
            },
        ]
    return [
        {
            'host': redis_host,
            'port': redis_port or get_free_port(),
        },
    ]


def pytest_addoption(parser):
    group = parser.getgroup('redis')
    group.addoption('--redis-host', help='Redis host')
    group.addoption('--redis-master-port', type=int, help='Redis master port')
    group.addoption(
        '--redis-sentinel-port', type=int, help='Redis sentinel port',
    )
    group.addoption(
        '--no-redis', help='Do not fill redis storage', action='store_true',
    )


def _json_object_hook(dct):
    if '$json' in dct:
        return json.dumps(dct['$json'])
    return dct
