import pytest

from tests_grocery_dispatch import constants as const


def setup_gdepots(mockserver, zones):
    @mockserver.json_handler('/grocery-depots/internal/v1/depots/v1/zones')
    def _handle_zones(_request):
        return zones


DEFAULT_ZONES = {
    'zones': [
        {
            'depot_id': 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010011',
            'effective_from': '2019-12-01T01:01:01+00:00',
            'geozone': {
                'coordinates': [
                    [
                        [
                            {
                                'lat': 55.720862999999999,
                                'lon': 37.190533000000001,
                            },
                            {
                                'lat': 55.734552853773316,
                                'lon': 37.190533000000001,
                            },
                            {
                                'lat': 55.73770593659091,
                                'lon': 37.74182090759277,
                            },
                            {
                                'lat': 55.70701735403676,
                                'lon': 37.94008283615112,
                            },
                            {
                                'lat': 55.720862999999999,
                                'lon': 37.190533000000001,
                            },
                        ],
                    ],
                ],
                'type': 'MultiPolygon',
            },
            'timetable': [
                {
                    'day_type': 'Everyday',
                    'working_hours': {
                        'from': {'hour': 8, 'minute': 0},
                        'to': {'hour': 19, 'minute': 0},
                    },
                },
            ],
            'zone_id': '09e28de3a73645a5aee40773cbb0f84d000200010001',
            'zone_status': 'active',
            'zone_type': 'pedestrian',
        },
    ],
}


@pytest.mark.now('2020-02-02T19:14:00+00:00')
async def test_14_mins_since_closing(
        experiments3, stq_runner, grocery_dispatch_pg, mockserver,
):
    experiments3.add_config(
        name='grocery_dispatch_watchdog',
        consumers=['grocery_dispatch/dispatch_watchdog'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={'interval': 60, 'is_enabled': True},
    )

    exp3_recorder = experiments3.record_match_tries(
        'grocery_dispatch_watchdog',
    )

    setup_gdepots(mockserver, DEFAULT_ZONES)

    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=const.DISPATCH_TYPE,
    )

    await stq_runner.grocery_dispatch_watchdog.call(
        task_id='dummy_task', kwargs={'dispatch_id': dispatch.dispatch_id},
    )

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    assert match_tries[0].kwargs['time_since_closing'] == 14


@pytest.mark.now('2020-02-02T18:14:00+00:00')
async def test_depot_is_avalible(
        experiments3, stq_runner, grocery_dispatch_pg, mockserver,
):
    experiments3.add_config(
        name='grocery_dispatch_watchdog',
        consumers=['grocery_dispatch/dispatch_watchdog'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={'interval': 60, 'is_enabled': True},
    )

    exp3_recorder = experiments3.record_match_tries(
        'grocery_dispatch_watchdog',
    )

    setup_gdepots(mockserver, DEFAULT_ZONES)

    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=const.DISPATCH_TYPE,
    )

    await stq_runner.grocery_dispatch_watchdog.call(
        task_id='dummy_task', kwargs={'dispatch_id': dispatch.dispatch_id},
    )

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    assert 'time_since_closing' not in match_tries[0].kwargs
