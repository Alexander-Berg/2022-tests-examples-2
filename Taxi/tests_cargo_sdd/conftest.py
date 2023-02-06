# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from cargo_sdd_plugins import *  # noqa: F403 F401


@pytest.fixture(name='run_task_once')
def _run_task_once(taxi_cargo_sdd, testpoint):
    async def _wrapper(task_name):
        @testpoint('%s::result' % task_name)
        def task_result(result):
            pass

        await taxi_cargo_sdd.run_task(task_name)
        args = await task_result.wait_call()
        assert not task_result.has_calls

        return args['result']

    return _wrapper


@pytest.fixture(name='sdd_exp_config')
def _moscow_sdd_exp_config(experiments3):
    async def _wrapper(config: dict):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_sdd_delivery_settings_for_clients',
            consumers=['cargo-sdd/stq-check-routing'],
            clauses=[
                {
                    'title': 'clause',
                    'alias': 'alias',
                    'predicate': {'init': {}, 'type': 'true'},
                    'value': config,
                },
            ],
            default_value={
                'settings': {
                    'delivery_guarantees': [],
                    'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                    'taxi_classes': [],
                    'fake_depot': {'lon': 0, 'lat': 0},
                },
            },
        )

    return _wrapper
