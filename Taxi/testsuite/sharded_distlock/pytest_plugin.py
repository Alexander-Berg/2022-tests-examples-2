import typing

import pytest

from taxi_testsuite.plugins import config
from tests_plugins import userver_client
from testsuite.plugins import testpoint as testpoint_plugin

from . import solomon_labels


class ShardedDistLockError(Exception):
    def __init__(self, text: str):
        super(ShardedDistLockError, self).__init__(
            f'{text}. '
            + 'see: https://wiki.yandex-team.ru/'
            + 'users/sazikov-a/sharded-distlock/',
        )


class ShardedDistLockTask:
    def __init__(
            self,
            service: userver_client.Client,
            configs: config.TaxiConfig,
            tp: testpoint_plugin.TestpointFixture,
            name: str,
    ):
        self._service = service
        self._taxi_config = configs
        self._task_name = name
        self._testpoint = tp
        self._task_shards: typing.Set[str] = set()

        self._enabled = True
        self._settings: typing.Dict = {'__default__': {}}

    async def add_shard(
            self, shard: str, settings: typing.Optional[typing.Dict] = None,
    ) -> None:
        await self.add_shards({shard}, {shard: settings} if settings else None)

    async def add_shards(
            self,
            shards: typing.Set[str],
            settings: typing.Optional[typing.Dict[str, typing.Dict]] = None,
    ) -> None:
        for shard in shards:
            if shard in self._task_shards:
                raise ShardedDistLockError(f'shard {shard} already exists')

        self._task_shards |= shards
        self._settings.update(settings or {})

        await self._update_settings()

    def get_shards(self) -> typing.Set[str]:
        return self._task_shards

    async def remove_shard(self, shard: str) -> None:
        await self.remove_shards({shard})

    async def remove_shards(self, shards: typing.Set[str]) -> None:
        self._task_shards -= shards

        await self._update_settings()

    async def update_shard(self, shard: str, settings: typing.Dict) -> None:
        if shard not in self._task_shards:
            raise ShardedDistLockError(f'shard {shard} is not exist')

        self._settings[shard] = settings

        await self._update_settings()

    async def _update_settings(self) -> None:
        self._taxi_config.set_values(
            {
                'SHARDED_DISTLOCK_SETTINGS': {
                    self._task_name: {
                        'enabled': self._enabled,
                        'shards': list(self._task_shards),
                        'settings': self._settings,
                    },
                },
            },
        )
        await self._service.invalidate_caches(
            cache_names=['dynamic-config-client-updater'],
        )
        await self._service.run_task(f'{self._task_name}-watchdog')

    async def enable_task(self) -> None:
        self._enabled = True
        await self._update_settings()

    async def disable_task(self) -> None:
        self._enabled = False
        await self._update_settings()

    async def run_shard(self, shard: str) -> None:
        @self._testpoint(f'{self._task_name}-{shard}::result')
        def result_testpoint(request):
            return request

        try:
            await self._service.run_task(f'{self._task_name}-{shard}')
            args = await result_testpoint.wait_call()
            return args['request']
        except userver_client.TestsuiteTaskNotFound:
            raise ShardedDistLockError(f'shard {shard} is not exist')


@pytest.fixture(name='sharded_distlock_task')
async def _sharded_distlock_task(taxi_config, testpoint):
    def _wrapper(service_fixture: userver_client.Client, name: str):
        return ShardedDistLockTask(
            service_fixture, taxi_config, testpoint, name,
        )

    return _wrapper


@pytest.fixture(name='get_metric_labels')
async def _get_metric_labels():
    def wrapper(metrics_json):
        return solomon_labels.SolomonMetrics(metrics_json)

    return wrapper
