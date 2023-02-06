import datetime

import pytest
import pytz

from tests_dispatch_airport import common

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'


def get_min_queued(cursor, driver_id):
    cursor.execute(
        f"""
        SELECT queued
        FROM dispatch_airport.drivers_queue
        WHERE driver_id = '{driver_id}';
    """,
    )
    return list(cursor)[0][0].astimezone(pytz.utc)


def compare_responses(
        response, etalon, with_filtered=False, with_entered=False,
):
    response_queues = response['queues']
    response_queues.sort(key=lambda queue: queue['tariff'])
    for queue in response_queues:
        for driver in queue['active_drivers']:
            assert driver.pop('queued')
        queue['active_drivers'].sort(key=lambda driver: driver['dbid_uuid'])

    is_ok = response_queues == etalon['queues']
    if with_filtered:
        response['filtered'].sort(key=lambda driver: driver['dbid_uuid'])
        is_ok &= response['filtered'] == etalon['filtered']

    if with_entered:
        response['entered'].sort(key=lambda driver: driver['dbid_uuid'])
        is_ok &= response['entered'] == etalon['entered']

    assert 'entry_limit_reached' not in response.keys()
    return is_ok


@pytest.mark.parametrize(
    'airport, response_file_name, '
    'with_filtered, with_entry_limit_reached, with_entered',
    [
        ('svo', 'response_by_moscow.json', False, False, False),
        ('unknown', 'empty_response.json', True, False, None),
        ('unknown', 'empty_response.json', False, None, False),
    ],
)
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.experiments3(
    filename='experiments3_umlaas_queue_predictions.json',
)
async def test_active_drivers_queues(
        taxi_dispatch_airport,
        load_json,
        airport,
        response_file_name,
        with_filtered,
        with_entry_limit_reached,
        with_entered,
):
    url = '/v1/active-drivers-queues'
    headers = common.DEFAULT_DISPATCH_AIRPORT_HEADER

    request_params = {'airport': airport, 'with_filtered': with_filtered}
    if with_entry_limit_reached is not None:
        request_params['with_entry_limit_reached'] = with_entry_limit_reached
    if with_entered is not None:
        request_params['with_entered'] = with_entered
    response = await taxi_dispatch_airport.get(
        url, headers=headers, params=request_params,
    )
    etalon = load_json(response_file_name)
    assert response.status_code == 200
    r_json = response.json()
    assert compare_responses(r_json, etalon, with_filtered)


@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.experiments3(
    filename='experiments3_umlaas_queue_predictions.json',
)
async def test_active_drivers_queues_added_class(
        taxi_dispatch_airport, pgsql, load_json,
):
    cursor = pgsql['dispatch_airport'].cursor()
    min_queued = get_min_queued(cursor, 'dbid_uuid9').strftime(
        format=DATETIME_FORMAT,
    )
    business_queued = (
        datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    ).strftime(format=DATETIME_FORMAT)
    cursor.execute(
        f"""
        UPDATE dispatch_airport.drivers_queue
        SET class_queued = '{{
          "econom": "{min_queued}",
          "business": "{business_queued}"
        }}'::JSONB
        WHERE driver_id = 'dbid_uuid9';
    """,
    )

    url = '/v1/active-drivers-queues'
    headers = common.DEFAULT_DISPATCH_AIRPORT_HEADER

    response = await taxi_dispatch_airport.get(
        url, headers=headers, params={'airport': 'ekb'},
    )
    assert response.status_code == 200
    r_json = response.json()

    econom_uuid9_queued = None
    business_uuid9_queued = None
    for queue in r_json['queues']:
        if queue['tariff'] == 'econom':
            for driver in queue['active_drivers']:
                if driver['dbid_uuid'] == 'dbid_uuid9':
                    econom_uuid9_queued = driver['queued']
        elif queue['tariff'] == 'business':
            for driver in queue['active_drivers']:
                if driver['dbid_uuid'] == 'dbid_uuid9':
                    business_uuid9_queued = driver['queued']
    assert econom_uuid9_queued == min_queued
    assert business_uuid9_queued == business_queued
    etalon = load_json('response_by_ekb.json')
    assert compare_responses(r_json, etalon)


@pytest.mark.parametrize('airport', ['unknown', 'svo', 'ekb'])
@pytest.mark.pgsql('dispatch_airport', files=['position_driver_events.sql'])
@pytest.mark.config(
    DISPATCH_AIRPORT_AREA_ENTRY_TRACKING={
        'ekb': {
            'maximum_number_of_entries': 2,
            'enter_accumulation_period': 5,
        },
        'svo': {
            'maximum_number_of_entries': 2,
            'enter_accumulation_period': 5,
        },
    },
)
@pytest.mark.now('2020-04-20T10:05:00+0000')
async def test_entry_limit_reached_drivers(
        taxi_dispatch_airport, load_json, airport,
):
    url = '/v1/active-drivers-queues'
    headers = common.DEFAULT_DISPATCH_AIRPORT_HEADER

    response = await taxi_dispatch_airport.get(
        url,
        headers=headers,
        params={'airport': airport, 'with_entry_limit_reached': True},
    )
    assert response.status_code == 200

    response = response.json()
    response['entry_limit_reached'].sort(
        key=lambda driver: driver['dbid_uuid'],
    )
    etalon = load_json('entry_limit_reached_response.json')[airport]
    assert response['entry_limit_reached'] == etalon


@pytest.mark.pgsql('dispatch_airport', files=['entered_drivers_queue.sql'])
@pytest.mark.now('2020-04-20T10:05:00+0000')
async def test_entered(taxi_dispatch_airport, load_json):
    url = '/v1/active-drivers-queues'
    headers = common.DEFAULT_DISPATCH_AIRPORT_HEADER

    response = await taxi_dispatch_airport.get(
        url, headers=headers, params={'airport': 'ekb', 'with_entered': True},
    )
    etalon = load_json('response_with_entered.json')
    assert response.status_code == 200
    r_json = response.json()
    assert compare_responses(r_json, etalon, False, True)
