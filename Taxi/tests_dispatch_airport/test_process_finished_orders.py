import pytest

import tests_dispatch_airport.utils as utils


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.config(
    DISPATCH_AIRPORT_ML_SETTINGS={},
    DISPATCH_AIRPORT_AVAILABLE_PARKINGS_CACHE_SETTINGS={'enabled': True},
    DISPATCH_AIRPORT_DEMAND_CALCULATION_SETTINGS={
        '__default__': {
            'account_entered_on_action_without_reposition': False,
            'account_entered_with_sintegro_repo': True,
            'account_relocation_to_parking_offer': True,
        },
    },
)
@pytest.mark.parametrize(
    'parking_available, stq_call_enabled',
    [(True, True), (True, False), (False, True)],
)
@pytest.mark.experiments3(
    filename='experiments3_dispatch_airport_relocation_to_parkings.json',
)
async def test_send_relocation_offers(
        taxi_dispatch_airport,
        taxi_config,
        mockserver,
        testpoint,
        stq,
        parking_available,
        stq_call_enabled,
):
    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @testpoint('relocate driver with finished order')
    def relocate_driver(data):
        assert data in ('dbid_uuid1', 'dbid_uuid5')

    @testpoint('expected_to_be_queued_with_relocation_offer')
    def expected_to_be_queued(_):
        pass

    @mockserver.json_handler(
        '/dispatch-airport-partner-protocol/internal/v1/available_parkings',
    )
    def _available_parkings(_):
        if parking_available:
            return {'polygon_id': ['ekb_parking', 'svo_parking']}
        return {'polygon_id': []}

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(_):
        return {}

    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_RELOCATION_TO_PARKINGS_SETTINGS': {
                'ekb': {
                    'partner_parking_id': 'ekb_parking',
                    'relocation_airport_id': 'svo',
                    'relocation_limits_by_class': {
                        'econom': {'car_count_limit': 10},
                        'vip': {'car_count_limit': 0},
                    },
                    'stq_call_enabled': stq_call_enabled,
                },
            },
        },
    )

    # dbid_uuid1: relocation should be sent if parkings is available
    # dbid_uuid2: car limit reached
    # dbid_uuid3: no demand
    # dbid_uuid4: same as dbid_uuid1, but disabled by experiment
    # dbid_uuid5: same as dbid_uuid1, but without order

    await taxi_dispatch_airport.enable_testpoints()
    await taxi_dispatch_airport.invalidate_caches()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    # no drivers we expected to be queued
    assert expected_to_be_queued.times_called == 0

    stq_queue = stq.dispatch_airport_partner_protocol_relocate_driver

    expected_relocations_count = 2

    if not parking_available:
        assert relocate_driver.times_called == 0
    else:
        assert relocate_driver.times_called == expected_relocations_count
        if stq_call_enabled:
            assert stq_queue.times_called == expected_relocations_count

            for _ in range(expected_relocations_count):
                call = stq_queue.next_call()
                assert call['kwargs']['app_locale'] == 'ru'
                assert call['kwargs']['car_id'] in ('car_id1', 'car_id5')
                assert call['kwargs']['dbid'] == 'dbid'
                assert call['kwargs']['target_class'] == 'econom'
                assert call['kwargs']['target_polygon_id'] == 'ekb_parking'
                assert call['kwargs']['udid'] in ('udid1', 'udid5')
                assert call['kwargs']['uuid'] in ('uuid1', 'uuid5')
        else:
            assert stq_queue.times_called == 0

        for _ in range(expected_relocations_count):
            relocate_driver.next_call()

        # Check that there is no new calls after next iteration
        await taxi_dispatch_airport.invalidate_caches()
        await taxi_dispatch_airport.run_task(
            'distlock/queue-update-scheduler-ekb',
        )
        await utils.wait_certain_testpoint('ekb', queue_update_finished)

        # dbid_uuid1 and dbid_uuid5 expected to be queued for three classes
        assert expected_to_be_queued.times_called == 6

        assert relocate_driver.times_called == 0
        assert stq_queue.times_called == 0
