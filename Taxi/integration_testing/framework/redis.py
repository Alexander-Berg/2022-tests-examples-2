import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Union

import docker.errors as docker_errors
import pytest
import redis
from redis import exceptions as redis_exceptions

from taxi.integration_testing.framework import environment, files

REDIS_HOST = 'redis.taxi.yandex'
REDIS_PORT = 6379
REDIS_SENTINEL_HOST = 'redis-sentinel.taxi.yandex'
REDIS_SENTINEL_PORT = 26379


@pytest.fixture(scope='session')
def redis_container(testenv: environment.EnvironmentManager,
                    platform: str) -> environment.TestContainer:
    with files.TarBuilder() as tar_builder:
        tar_builder.add_resource('resfs/file/taxi/integration_testing/framework/redis/fs', strip_prefix=True,
                                 mode=0o777)
        archive = tar_builder.get_bytes()

    redis_container = testenv.add_container(
        name='redis',
        image=f'registry.yandex.net/taxi/taxi-integration-{platform}-base',
        command='/taxi/run/redis.sh',
        healthcheck={
            'test': '/taxi/tools/healthcheck.sh redis-cli -h ::1',
            'timeout': '30s',
            'interval': '5s',
            'retries': '20'
        },
        environment={
            'REQUESTS_CA_BUNDLE': '/usr/local/share/ca-certificates/rootCA.crt',
            'SSL_CERT_FILE': '/usr/local/share/ca-certificates/rootCA.crt',
            'LANG': 'ru_RU.UTF-8',
            'program_name': 'taxi-redis'
        },
        archive=archive,
        ports=[REDIS_PORT],
        aliases=[
            REDIS_HOST
        ]
    )

    redis_master_ipv6 = testenv.get_ipv6(redis_container)

    with files.TarBuilder() as tar_builder:
        tar_builder.add_resource('resfs/file/taxi/integration_testing/framework/redis_sentinel/fs',
                                 strip_prefix=True,
                                 mode=0o777)
        archive = tar_builder.get_bytes()

    testenv.add_container(
        name='redis-sentinel',
        image=f'registry.yandex.net/taxi/taxi-integration-{platform}-base',
        command='/taxi/run/redis-sentinel.sh',
        healthcheck={
            'test': '/taxi/tools/healthcheck.sh redis-cli -h ::1',
            'timeout': '30s',
            'interval': '5s',
            'retries': '20'
        },
        environment={
            'REDIS_MASTER_IPV6': redis_master_ipv6,
            'REQUESTS_CA_BUNDLE': '/usr/local/share/ca-certificates/rootCA.crt',
            'SSL_CERT_FILE': '/usr/local/share/ca-certificates/rootCA.crt',
            'LANG': 'ru_RU.UTF-8',
            'program_name': 'taxi-redis-sentinel',
        },
        archive=archive,
        ports=[REDIS_SENTINEL_PORT],
        aliases=[
            REDIS_SENTINEL_HOST
        ]
    )

    return redis_container


@pytest.fixture(scope='session')
def redis_client(redis_container: environment.TestContainer) -> redis.StrictRedis:
    redis_endpoint = redis_container.get_endpoint(REDIS_PORT).split(':')
    redis_connection = redis.StrictRedis(host=redis_endpoint[0], port=int(redis_endpoint[1]))

    redis_start_timeout: timedelta = timedelta(seconds=60)
    started = datetime.now()

    while True:
        try:
            redis_connection.ping()
            break
        except redis_exceptions.ConnectionError:
            pass

        if datetime.now() > started + redis_start_timeout:
            try:
                logs = redis_container.container.logs(tail=1000)
                logging.error(logs.decode('UTF-8'))
            except docker_errors.APIError as ex:
                logging.error(
                    f'An error occurred when reading log output of '
                    f'{redis_container.container.name} service: {ex}',
                )
            raise environment.EnvironmentSetupError(
                f'{redis_container.name} did not respond during {redis_start_timeout}.')

    return redis_connection


def redis_load_binary(file_path: Union[str, os.PathLike]):
    with open(file_path, 'rb') as file_handle:
        return file_handle.read()


@pytest.fixture(scope='session')
def redis_db_surger(redis_client: redis.StrictRedis):
    timestamp = int(time.time())

    grid_desc = {
        'CellSize': 250,
        'GridId': '15450017746124931280',
        'RegionId': '15450017746124931280_%i' % timestamp,
        'Updated': timestamp,
        'TlBr': {
            'Bottom': 55.472370163516132,
            'Left': 37.135591841918192,
            'Right': 38.077641704627929,
            'Top': 56.003460457113277,
        },
    }

    redis_client.hset(
        'CPP:SURGE_FULL:GRID:DESC',
        '15450017746124931280',
        json.dumps(grid_desc),
    )

    redis_client.set(
        'CPP:SURGE_FULL:GRID:BINARY:15450017746124931280',
        redis_load_binary('tests/_data/redis/db_surger/grid.bin'),
    )

    redis_client.set(
        'CPP:SURGE_FULL:VALUES:BINARY:15450017746124931280_%i' % timestamp,
        redis_load_binary('tests/_data/redis/db_surger/cells.bin'),
    )
