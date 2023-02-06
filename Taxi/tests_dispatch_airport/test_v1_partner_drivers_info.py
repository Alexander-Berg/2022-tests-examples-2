import pytest

from tests_dispatch_airport import common


@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
async def test_v1_partner_drivers_info(
        taxi_dispatch_airport, taxi_config, load_json,
):
    zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    zones_config['ekb'].update(
        {
            'partner_parking_id': 'ekb_p4',
            'partner_parking_check_enabled': False,
        },
    )
    zones_config['svo'].update(
        {
            'partner_parking_id': 'svo_p3',
            'partner_parking_check_enabled': False,
        },
    )
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': zones_config})

    url = '/v1/partner_drivers_info'
    headers = common.DEFAULT_DISPATCH_AIRPORT_HEADER

    request_ids = [
        'dbid_uuid1',
        'dbid_uuid2',
        'dbid_uuid3',
        'dbid_uuid4',
        'dbid_uuid5',
        'dbid_uuid6',
        'dbid_uuid7',
        'dbid_uuid8',
    ]
    request_drivers_ids = [
        {'dbid_uuid': dbid_uuid} for dbid_uuid in request_ids
    ] + [{'dbid_uuid': 'non_existing_uuid'}]

    response = await taxi_dispatch_airport.post(
        url, {'driver_ids': request_drivers_ids}, headers=headers,
    )

    filtered_drivers = response.json()['filtered_drivers']
    filtered_drivers.sort(key=lambda x: x['dbid_uuid'])
    assert filtered_drivers == load_json('filtered_etalons.json')

    queued_drivers = response.json()['queued_drivers']
    queued_drivers.sort(key=lambda x: x['dbid_uuid'])
    for queued_driver in queued_drivers:
        queued_driver['times_queued'].sort(key=lambda x: x['class'])
    assert queued_drivers == load_json('queued_etalons.json')
