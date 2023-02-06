import pytest

import tests_dispatch_airport.utils as utils


def check_stq_call(kwargs, etalon):
    assert kwargs['trigger_name'] == etalon['trigger_name']
    if 'unique_driver_id' in kwargs or 'unique_driver_id' in etalon:
        assert kwargs['unique_driver_id'] == etalon['unique_driver_id']


def check_stq_calls(stq, etalons):
    for _ in range(stq.contractor_statistics_view_trigger_update.times_called):
        call = stq.contractor_statistics_view_trigger_update.next_call()
        check_stq_call(call['kwargs'], etalons[call['id']])


# dbid0_uuid0: aero_parking_finished_order:
#     input_order_id + empty busy && tag = newbie_aero_parking4
#     already have one sent notification
# dbid1_uuid1: aero_parking_finished_order:
#     input_order_id + busy different order_id && tag = newbie_aero_parking
#     already have tree sent notifications
# dbid2_uuid2: aero_no_parking_finished_order:
#     input_order_id + empty busy && tag = newbie_aero_no_parking
# dbid3_uuid3: aero_no_parking_finidhed_order:
#     input_order_id + busy dufferent order_id && tag = newbie_aero_no_parking
# dbid4_uuid4: aero_parking_entered_free:
#     empty input_order_id + state = entered && tag = newbie_aero_parking
# dbid5_uuid5: aero_no_parking_entered_free:
#     empty input_order_id + state = entered && tag = newbie_aero_no_parking
# dbid6_uuid6: aero_parking_queued:
#     state = queued && tag = newbie_aero_parking
# dbid7_uuid7: aero_no_parking_queued:
#     state = queued && tag = newbie_aero_no_parking
@pytest.mark.parametrize('enabled', [True, False])
@pytest.mark.pgsql('dispatch_airport', files=['drivers_success_send.sql'])
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid0', 'newbie_aero_parking'),
        ('dbid_uuid', 'dbid1_uuid1', 'newbie_aero_parking'),
        ('dbid_uuid', 'dbid2_uuid2', 'newbie_aero_no_parking'),
        ('dbid_uuid', 'dbid3_uuid3', 'newbie_aero_no_parking'),
        ('dbid_uuid', 'dbid4_uuid4', 'newbie_aero_parking'),
        ('dbid_uuid', 'dbid5_uuid5', 'newbie_aero_no_parking'),
        ('dbid_uuid', 'dbid6_uuid6', 'newbie_aero_parking'),
        ('dbid_uuid', 'dbid7_uuid7', 'newbie_aero_no_parking'),
        ('dbid_uuid', 'dbid7_uuid7', 'newbie_aero_parking'),
    ],
    topic_relations=[
        ('airport_queue', 'newbie_aero_parking'),
        ('airport_queue', 'newbie_aero_no_parking'),
    ],
)
@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid1_uuid1',
            'order_id': '444444',
            'taxi_status': 3,
            'final_destination': {'lat': 1.0, 'lon': 1.0},
        },
        {
            'driver_id': 'dbid3_uuid3',
            'order_id': '555555',
            'taxi_status': 3,
            'final_destination': {'lat': 1.0, 'lon': 1.0},
        },
    ],
)
async def test_successful_stq_send(
        taxi_dispatch_airport,
        mockserver,
        stq,
        load_json,
        pgsql,
        taxi_config,
        enabled,
):
    @mockserver.json_handler('/tags/v2/upload')
    def _tags(_):
        return {}

    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_CONTRACTOR_STATISTICS_VIEW_'
            'TRIGGER_UPDATE_SETTINGS': {
                'enabled': enabled,
                'airports_with_parking': ['svo'],
                'airports_without_parking': ['ekb'],
            },
        },
    )

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-svo')

    if enabled:
        etalons = load_json('etalons_success_send.json')
        utils.check_drivers_queue(pgsql['dispatch_airport'], etalons)

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-svo')

    if enabled:
        etalons = load_json('etalons_repeat_send.json')
        utils.check_drivers_queue(pgsql['dispatch_airport'], etalons)

    assert stq.contractor_statistics_view_trigger_update.times_called == (
        8 if enabled else 0
    )

    stq_etalons = load_json('etalons_success_stq.json')
    check_stq_calls(stq, stq_etalons)


# dbid0_uuid0:
#     has input_order_id, but has busy with same order_id
# dbid1_uuid1:
#     has already sent notification
# dbid2_uuid2:
#     has wrong tag
# dbid3_uuid3:
#     has no unique_driver_id
# dbid4_uuid4:
#     airport does not set in config
@pytest.mark.config(
    DISPATCH_AIRPORT_CONTRACTOR_STATISTICS_VIEW_TRIGGER_UPDATE_SETTINGS={
        'enabled': True,
        'airports_with_parking': ['svo'],
        'airports_without_parking': [],
    },
)
@pytest.mark.pgsql('dispatch_airport', files=['drivers_failed_send.sql'])
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid_uuid0', 'newbie_aero_parking'),
        ('dbid_uuid', 'dbid_uuid1', 'newbie_aero_parking'),
        ('dbid_uuid', 'dbid_uuid2', 'some_tag'),
        ('dbid_uuid', 'dbid_uuid3', 'newbie_aero_parking'),
        ('dbid_uuid', 'dbid_uuid4', 'newbie_aero_parking'),
    ],
    topic_relations=[
        ('airport_queue', 'newbie_aero_parking'),
        ('airport_queue', 'some_tag'),
    ],
)
@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid0_uuid0',
            'order_id': '000000',
            'taxi_status': 3,
            'final_destination': {'lat': 1.0, 'lon': 1.0},
        },
    ],
)
async def test_failed_stq_send(
        taxi_dispatch_airport, mockserver, stq, load_json, pgsql,
):
    @mockserver.json_handler('/tags/v2/upload')
    def _tags(_):
        return {}

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-svo')

    etalons = load_json('etalons_failed_send.json')
    utils.check_drivers_queue(pgsql['dispatch_airport'], etalons)

    assert stq.contractor_statistics_view_trigger_update.times_called == 0
