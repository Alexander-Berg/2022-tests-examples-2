import pytest

import tests_dispatch_airport.utils as utils


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('driver_is_on_other_parking', [False, True])
async def test_external_activations_filter(
        taxi_dispatch_airport,
        taxi_config,
        testpoint,
        redis_store,
        mockserver,
        now,
        pgsql,
        driver_is_on_other_parking,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint('set-external-activation-time-filter-finished')
    def filter_finished(data):
        return data

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    @mockserver.json_handler(
        '/dispatch-airport-partner-protocol/service/v2/parked_drivers',
    )
    def _dapp_parked_drivers(request):
        assert 'parking_id' in request.json
        if request.json['parking_id'] == 'ekb_parking':
            return {
                'drivers': [
                    {
                        'driver_id': 'dbid_uuid1',
                        'arrived_at': '2020-10-02T10:36:36+0000',
                    },
                ],
            }

        if request.json['parking_id'] == 'svo_parking':
            return {
                'drivers': [
                    {
                        'driver_id': 'dbid_uuid1',
                        'arrived_at': (
                            '2021-10-02T10:36:36+0000'
                            if driver_is_on_other_parking
                            else '2019-10-02T10:36:36+0000'
                        ),
                    },
                ],
            }
        assert False
        return {}

    zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    zones_config['ekb']['partner_parking_id'] = 'ekb_parking'
    zones_config['ekb']['use_external_activation_time'] = True
    zones_config['svo']['partner_parking_id'] = 'svo_parking'
    zones_config['svo']['use_external_activation_time'] = True

    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': zones_config})

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    positions = {
        'dbid_uuid1': {'position': utils.WAITING_POSITION, 'timestamp': now},
        'dbid_uuid2': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': now,
        },
    }

    utils.publish_positions(redis_store, positions, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    response = (await filter_finished.wait_call())['data']
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': [],
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
        },
    }
    if driver_is_on_other_parking:
        updated_etalons.pop('dbid_uuid1')
    assert len(response) == len(updated_etalons)
    for driver in response:
        etalon = updated_etalons[driver['driver_id']]
        utils.check_drivers(driver, etalon)
        if driver['driver_id'] == 'dbid_uuid1':
            assert driver['queued'] == '2020-10-02T10:36:36+00:00'

    assert not utils.get_driver_events(pgsql['dispatch_airport'])
