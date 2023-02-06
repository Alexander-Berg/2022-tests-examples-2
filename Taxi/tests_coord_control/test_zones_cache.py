# pylint: disable=import-error

import datetime

import dateutil.parser
import pytest

from geobus_tools import geobus  # noqa: F401 C5521

STRATEGY_CALCULATED_NAME = 'strategy-calculated'
CHANNEL_NAME = 'channel:yagr:signal_v2'


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
async def test_zones_cache(
        taxi_coord_control,
        redis_store,
        load_json,
        testpoint,
        mocked_time,
        experiments3,
):
    @testpoint(STRATEGY_CALCULATED_NAME)
    def strategy_calculated(data):
        return data

    @testpoint('consistent-hashing-finished')
    def consistent_hashing_finished(data):
        pass

    now = dateutil.parser.parse('2020-04-21T12:17:42+00:00')
    mocked_time.set(now)
    await taxi_coord_control.tests_control()
    await consistent_hashing_finished.wait_call()

    messages = load_json('geobus_one_driver_messages.json')
    fbs_message = geobus.serialize_signal_v2(messages, datetime.datetime.now())
    redis_store.publish(CHANNEL_NAME, fbs_message)

    assert (await strategy_calculated.wait_call())['data'][
        'performer_id'
    ] == 'dbid_uuid'

    now += datetime.timedelta(hours=0, minutes=3)
    mocked_time.set(now)
    experiments3.add_experiment(
        consumers=['coord_control/location_settings'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'initial',
                'predicate': {
                    'init': {
                        'value': 'moscow',
                        'arg_name': 'zone',
                        'arg_type': 'string',
                    },
                    'type': 'eq',
                },
                'value': {},
            },
        ],
        name='coord_control_drivers_enabling',
    )
    await taxi_coord_control.invalidate_caches()

    redis_store.publish(CHANNEL_NAME, fbs_message)
    await strategy_calculated.wait_call()
