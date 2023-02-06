# pylint: disable=import-error
import datetime

import pytest

from geobus_tools import geobus  # noqa: F401 C5521


QUEUE_KEY = 'location_settings:queue'
PERFORMER_INFO_KEY = 'location_settings:performer_info:{}'.format
STRATEGY_CALCULATED_NAME = 'strategy-calculated'
CONSISTENT_HASHING_NAME = 'consistent-hashing-finished'
FIND_NEAREST_ZONE_NAME = 'find-nearest-zone'
GET_TRANSPORT_TYPE_NAME = 'get-transport-type'
PERFORMERS_TO_CALCULATE_NAME = 'performers-to-calculate'
PERFORMER_FROM_PUBSUB_NAME = 'performer-from-pubsub-received'
CHANNEL_NAME = 'channel:yagr:signal_v2'
TRANSPORT_TYPES = {
    'dbid_uuid': 'pedestrian',
    'dbid_uuid_1': 'car',
    'dbid_uuid_2': 'car',
}


def _has_response(redis_store, performer_id):
    return redis_store.hexists(PERFORMER_INFO_KEY(performer_id), 'response')


def _is_correct_transport_type(tested_value):
    assert tested_value
    driver_id = tested_value['driver_id']
    transport_type = tested_value['transport_type']
    assert TRANSPORT_TYPES[driver_id] == transport_type


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
async def test_strategy_calculator(
        taxi_coord_control, redis_store, load_json, testpoint,
):
    @testpoint(FIND_NEAREST_ZONE_NAME)
    def get_zone(data):
        return data

    @testpoint(GET_TRANSPORT_TYPE_NAME)
    def get_transport_type(data):
        return data

    @testpoint(STRATEGY_CALCULATED_NAME)
    def strategy_calculated(data):
        return data

    @testpoint(CONSISTENT_HASHING_NAME)
    def consistent_hashing_finished(data):
        pass

    @testpoint(PERFORMER_FROM_PUBSUB_NAME)
    def performer_from_pubsub_received(data):
        return data

    messages = load_json('geobus_messages.json')
    driver_id = messages[0]['driver_id']
    dbid, uuid = driver_id.split('_')

    # fill taximeter_version and agent info
    response = await taxi_coord_control.get(
        'location_settings',
        params={
            'driver_profile_id': uuid,
            'park_db_id': dbid,
            'taximeter_agent_info': 'Taximeter-BETA 9.33 (1234)',
        },
        headers={'location_settings_etag': 'etag'},
    )
    await consistent_hashing_finished.wait_call()

    assert response.status_code == 404
    assert response.json()['message'] == 'no_performer'

    fbs_message = geobus.serialize_signal_v2(messages, datetime.datetime.now())
    # publish to coord-control input channel
    redis_store.publish(CHANNEL_NAME, fbs_message)

    transport_type = (await get_transport_type.wait_call())['data']
    _is_correct_transport_type(transport_type)

    performer_id = (await strategy_calculated.wait_call())['data'][
        'performer_id'
    ]
    assert performer_id == driver_id
    await performer_from_pubsub_received.wait_call()

    response = await taxi_coord_control.get(
        'location_settings',
        params={
            'driver_profile_id': uuid,
            'park_db_id': dbid,
            'taximeter_agent_info': 'Taximeter-BETA 9.33 (1234)',
        },
        headers={'location_settings_etag': 'etag'},
    )

    zone_name = (await get_zone.wait_call())['data']
    assert zone_name == 'moscow'
    assert response.status_code == 404
    assert response.json()['message'] == 'saved_metainfo'

    response = await taxi_coord_control.get(
        'location_settings',
        params={
            'driver_profile_id': uuid,
            'park_db_id': dbid,
            'taximeter_agent_info': 'Taximeter-BETA 9.33 (1234)',
        },
        headers={'location_settings_etag': 'etag'},
    )

    assert response.status_code == 200
    assert response.json()


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
async def test_strategy_calculator_filter_old_points(
        taxi_coord_control, redis_store, load_json, testpoint,
):
    @testpoint(PERFORMERS_TO_CALCULATE_NAME)
    def performers_to_calculate(data):
        return data

    await taxi_coord_control.enable_testpoints()
    messages = load_json('geobus_messages.json')

    fbs_message = geobus.serialize_signal_v2(messages, datetime.datetime.now())
    redis_store.publish(CHANNEL_NAME, fbs_message)

    assert (await performers_to_calculate.wait_call())['data']

    redis_store.publish(CHANNEL_NAME, fbs_message)

    assert not (await performers_to_calculate.wait_call())['data']
