import datetime
import math

import pytest
import pytz

from . import utils

UPDATE_INTERVAL = 60


def sync_places_info_config(**kwargs):
    return dict(
        {
            'period_seconds': 60,
            'places_batch_size': 100,
            'working_intervals_limit': 7,
        },
        **kwargs,
    )


@utils.periodic_dispatcher_config3()
async def test_sync_places_info_no_places(
        taxi_eats_picker_dispatch, places_environment,
):
    await taxi_eats_picker_dispatch.run_distlock_task(
        'eats-picker-dispatch-sync-places-info',
    )
    assert places_environment.mock_places_updates.times_called == 1
    assert places_environment.mock_retrieve_delivery_zones.times_called == 0


@utils.periodic_dispatcher_config3()
@pytest.mark.now
@pytest.mark.parametrize('business', ['restaurant', 'shop'])
@pytest.mark.parametrize(
    'places_batch_size, working_intervals_limit', [[2, 7], [7, 2]],
)
async def test_sync_places_info_different_limits(
        taxi_eats_picker_dispatch,
        taxi_config,
        now,
        business,
        places_batch_size,
        working_intervals_limit,
        places_environment,
        get_places,
):
    places_count = 10
    taxi_config.set_values(
        {
            'EATS_PICKER_DISPATCH_SYNC_PLACES_INFO_PARAMS': (
                sync_places_info_config(
                    places_batch_size=places_batch_size,
                    working_intervals_limit=working_intervals_limit,
                )
            ),
        },
    )
    place_ids = places_environment.create_places(
        places_count,
        dict(
            updated_at=now - datetime.timedelta(seconds=10), business=business,
        ),
    )
    delivery_zones = {}
    places = []
    for place_id in place_ids:
        (delivery_zones[place_id],) = places_environment.create_delivery_zones(
            place_id,
            1,
            working_intervals=[
                {
                    'from': now + datetime.timedelta(days=i),
                    'to': now + datetime.timedelta(days=i + 1),
                }
                for i in range(10)
            ],
        )
        places.append(places_environment.catalog_places[place_id])
    expected_data = utils.make_expected_data(
        places, delivery_zones, working_intervals_limit,
    )
    await taxi_eats_picker_dispatch.run_distlock_task(
        'eats-picker-dispatch-sync-places-info',
    )
    batches = math.ceil(places_count / places_batch_size)
    assert (
        places_environment.mock_places_updates.times_called
        == batches + int(places_count % places_batch_size == 0)
    )
    assert places_environment.mock_retrieve_delivery_zones.times_called == (
        batches if business == 'shop' else 0
    )
    utils.compare_db_with_expected_data(get_places(), expected_data)


@utils.periodic_dispatcher_config3()
@pytest.mark.now
async def test_sync_places_info_multiple_zones(
        taxi_eats_picker_dispatch, now, places_environment, get_places,
):
    place_id = places_environment.create_places(
        1, dict(updated_at=now - datetime.timedelta(seconds=10)),
    )[0]
    places_environment.create_delivery_zones(place_id, 1, enabled=False)
    places_environment.create_delivery_zones(place_id, 1)
    # будут использованы интервалы этой зоны, т. к. это первая зона с
    # enabled=True и непустым списком working_intervals
    (delivery_zone,) = places_environment.create_delivery_zones(
        place_id,
        1,
        working_intervals=[
            {'from': now, 'to': now + datetime.timedelta(days=1)},
        ],
    )
    places_environment.create_delivery_zones(
        place_id,
        1,
        working_intervals=[
            {
                'from': now + datetime.timedelta(days=1),
                'to': now + datetime.timedelta(days=2),
            },
        ],
    )
    expected_data = utils.make_expected_data(
        [places_environment.catalog_places[place_id]],
        {place_id: delivery_zone},
    )
    await taxi_eats_picker_dispatch.run_distlock_task(
        'eats-picker-dispatch-sync-places-info',
    )
    assert places_environment.mock_places_updates.times_called == 1
    assert places_environment.mock_retrieve_delivery_zones.times_called == 1
    utils.compare_db_with_expected_data(get_places(), expected_data)


@utils.periodic_dispatcher_config3()
async def test_sync_places_info_places_updates_error(
        taxi_eats_picker_dispatch, mockserver, places_environment, get_places,
):
    places_environment.create_places(1)

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/updates',
    )
    def _mock_places_updates(request):
        return mockserver.make_response(status=500)

    await taxi_eats_picker_dispatch.run_distlock_task(
        'eats-picker-dispatch-sync-places-info',
    )
    assert _mock_places_updates.times_called == 1
    assert places_environment.mock_retrieve_delivery_zones.times_called == 0
    assert not get_places()


@utils.periodic_dispatcher_config3()
async def test_sync_places_info_zones_error(
        taxi_eats_picker_dispatch, mockserver, places_environment, get_places,
):
    places_environment.create_places(1)

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/delivery_zones/retrieve-by-place-ids',
    )
    def _mock_zones(request):
        return mockserver.make_response(status=500)

    await taxi_eats_picker_dispatch.run_distlock_task(
        'eats-picker-dispatch-sync-places-info',
    )
    assert places_environment.mock_places_updates.times_called == 1
    assert _mock_zones.times_called == 1
    assert not get_places()


@utils.periodic_dispatcher_config3()
@pytest.mark.now
async def test_sync_places_info_auto_disabled(
        taxi_eats_picker_dispatch,
        now,
        places_environment,
        create_place,
        get_places,
):
    place_id = places_environment.create_places(1, dict(enabled=False))[0]

    auto_disabled_at = now - datetime.timedelta(seconds=1800)
    auto_disabled_at = auto_disabled_at.replace(tzinfo=pytz.UTC)
    create_place(place_id, enabled=False, auto_disabled_at=auto_disabled_at)

    await taxi_eats_picker_dispatch.run_distlock_task(
        'eats-picker-dispatch-sync-places-info',
    )

    (place,) = get_places([place_id])
    assert not place['enabled']
    assert place['auto_disabled_at'] == auto_disabled_at


@utils.periodic_dispatcher_config3()
@pytest.mark.parametrize(
    'enabled_in_catalog, enabled_in_core, is_manually_disabled',
    [
        (False, False, True),
        (False, True, False),
        (True, False, True),
        (True, True, False),
        (False, None, True),
        (True, None, False),
    ],
)
async def test_sync_places_info_manually_disabled(
        taxi_eats_picker_dispatch,
        places_environment,
        create_place,
        get_places,
        now_utc,
        enabled_in_catalog,
        enabled_in_core,
        is_manually_disabled,
):
    place_id = places_environment.create_places(
        1,
        dict(enabled=enabled_in_catalog),
        dict(available=enabled_in_core, disabled_details={'reason': 99}),
    )[0]

    create_place(
        place_id,
        enabled=True,
        updated_at=now_utc() - datetime.timedelta(microseconds=1),
    )

    await taxi_eats_picker_dispatch.run_distlock_task(
        'eats-picker-dispatch-sync-places-info',
    )

    (place,) = get_places([place_id])
    if is_manually_disabled:
        assert not place['enabled']
    else:
        assert place['enabled']
    assert place['auto_disabled_at'] is None


@utils.periodic_dispatcher_config3()
@pytest.mark.now
async def test_sync_places_info_manually_enabled(
        taxi_eats_picker_dispatch,
        now_utc,
        places_environment,
        create_place,
        get_places,
):
    place_id = places_environment.create_places(1, dict(enabled=True))[0]

    auto_disabled_at = now_utc() - datetime.timedelta(seconds=1800)
    create_place(
        place_id,
        enabled=False,
        auto_disabled_at=auto_disabled_at,
        updated_at=auto_disabled_at,
    )

    await taxi_eats_picker_dispatch.run_distlock_task(
        'eats-picker-dispatch-sync-places-info',
    )

    (place,) = get_places([place_id])
    assert place['enabled']
    assert place['auto_disabled_at'] is None


@utils.periodic_dispatcher_config3()
async def test_sync_places_info_shop_picking_type(
        taxi_eats_picker_dispatch, places_environment, now, pgsql,
):
    features = {
        'ignore_surge': False,
        'supports_preordering': False,
        'fast_food': False,
        'shop_picking_type': 'shop_picking',
    }
    places_environment.create_places(1, dict(features=features))
    places_environment.create_places(1)

    await taxi_eats_picker_dispatch.run_distlock_task(
        'eats-picker-dispatch-sync-places-info',
    )

    assert places_environment.mock_places_updates.times_called == 1

    cursor = pgsql['eats_picker_dispatch'].cursor()
    cursor.execute(
        """SELECT id, shop_picking_type
        from eats_picker_dispatch.places""",
    )
    data = list(cursor)
    assert sorted(data) == [(100000, 'shop_picking'), (100001, 'our_picking')]


@utils.periodic_dispatcher_config3()
@pytest.mark.now
async def test_sync_places_info_save_only_new(
        taxi_eats_picker_dispatch,
        now,
        places_environment,
        create_place,
        get_places,
):
    now = now.replace(tzinfo=pytz.UTC)
    auto_disabled_at = now - datetime.timedelta(seconds=1800)
    place_ids = places_environment.create_places(
        3, dict(enabled=True, updated_at=now - datetime.timedelta(seconds=1)),
    )

    for i in range(3):
        create_place(
            place_ids[i],
            enabled=False,
            auto_disabled_at=auto_disabled_at,
            updated_at=now - datetime.timedelta(seconds=i),
        )

    await taxi_eats_picker_dispatch.run_distlock_task(
        'eats-picker-dispatch-sync-places-info',
    )

    db_places = get_places(place_ids)
    assert not db_places[0]['enabled']
    assert not db_places[1]['enabled']
    assert db_places[2]['enabled']
    assert db_places[0]['auto_disabled_at'] == auto_disabled_at
    assert db_places[1]['auto_disabled_at'] == auto_disabled_at
    assert db_places[2]['auto_disabled_at'] is None


@pytest.mark.now
@utils.periodic_dispatcher_config3()
@pytest.mark.parametrize(
    'n_total_places,n_places_with_intervals,delivery_zones_times_called',
    [
        [2, 2, 0],  # get all working intervals from places handle
        [2, 1, 1],  # get 1st interval from places, 2nd from zones
        [2, 0, 1],  # try places then fallback to delivery zones
    ],
)
async def test_sync_places_info_get_working_intervals_from_places(
        n_total_places,
        n_places_with_intervals,
        delivery_zones_times_called,
        taxi_eats_picker_dispatch,
        places_environment,
        now,
        get_places,
):
    assert n_places_with_intervals <= n_total_places

    places_with_intervals_ids = places_environment.create_places(
        n_places_with_intervals,
        dict(
            working_intervals=[
                {'from': now, 'to': now + datetime.timedelta(hours=10)},
            ],
        ),
    )
    places_without_intervals_ids = places_environment.create_places(
        n_total_places - n_places_with_intervals,
    )
    for place_without_intervals_id in places_without_intervals_ids:
        places_environment.create_delivery_zones(
            place_without_intervals_id,
            1,
            working_intervals=[
                {'from': now, 'to': now + datetime.timedelta(hours=10)},
            ],
        )

    await taxi_eats_picker_dispatch.run_distlock_task(
        'eats-picker-dispatch-sync-places-info',
    )
    assert places_environment.mock_places_updates.times_called == 1
    assert (
        places_environment.mock_retrieve_delivery_zones.times_called
        == delivery_zones_times_called
    )

    place_ids = places_without_intervals_ids + places_with_intervals_ids
    db_places = get_places(place_ids)
    assert len(db_places[0]['working_intervals']) == 1
    assert len(db_places[1]['working_intervals']) == 1


# @utils.periodic_dispatcher_config3()
@utils.merge_working_intervals_exp3()
@pytest.mark.parametrize(
    'place_intervals,zone_intervals,expected_intervals',
    [
        pytest.param(
            [],
            [
                {
                    'from': '2022-03-17T12:00:00+00:00',
                    'to': '2022-03-17T13:00:00+00:00',
                },
            ],
            [],
            id='empty_place_intervals',
        ),
        pytest.param(
            [
                {
                    'from': '2022-03-17T12:00:00+00:00',
                    'to': '2022-03-17T13:00:00+00:00',
                },
            ],
            [],
            [['2022-03-17T12:00:00+00:00', '2022-03-17T13:00:00+00:00']],
            id='empty_zone_intervals',
        ),
        pytest.param(
            [
                {
                    'from': '2022-03-17T12:00:00+00:00',
                    'to': '2022-03-17T13:00:00+00:00',
                },
                {
                    'from': '2022-03-17T13:00:00+00:00',
                    'to': '2022-03-17T14:00:00+00:00',
                },
                {
                    'from': '2022-03-17T14:00:01+00:00',
                    'to': '2022-03-17T15:00:00+00:00',
                },
            ],
            [],
            [
                ['2022-03-17T12:00:00+00:00', '2022-03-17T14:00:00+00:00'],
                ['2022-03-17T14:00:01+00:00', '2022-03-17T15:00:00+00:00'],
            ],
            id='join_place_intervals',
        ),
        pytest.param(
            None,
            [
                {
                    'from': '2022-03-17T12:00:00+00:00',
                    'to': '2022-03-17T13:00:00+00:00',
                },
                {
                    'from': '2022-03-17T13:00:00+00:00',
                    'to': '2022-03-17T14:00:00+00:00',
                },
                {
                    'from': '2022-03-17T14:00:01+00:00',
                    'to': '2022-03-17T15:00:00+00:00',
                },
            ],
            [
                ['2022-03-17T12:00:00+00:00', '2022-03-17T14:00:00+00:00'],
                ['2022-03-17T14:00:01+00:00', '2022-03-17T15:00:00+00:00'],
            ],
            id='join_zone_intervals',
        ),
        pytest.param(
            [
                {
                    'from': '2022-03-17T12:00:00+00:00',
                    'to': '2022-03-17T13:00:00+00:00',
                },
                {
                    'from': '2022-03-17T15:00:00+00:00',
                    'to': '2022-03-17T16:00:00+00:00',
                },
                {
                    'from': '2022-03-17T17:00:00+00:00',
                    'to': '2022-03-17T18:00:00+00:00',
                },
            ],
            [
                {
                    'from': '2022-03-17T13:00:00+00:00',
                    'to': '2022-03-17T14:00:00+00:00',
                },
                {
                    'from': '2022-03-17T15:45:00+00:00',
                    'to': '2022-03-17T16:30:00+00:00',
                },
                {
                    'from': '2022-03-17T16:45:00+00:00',
                    'to': '2022-03-17T17:30:00+00:00',
                },
            ],
            [
                ['2022-03-17T15:45:00+00:00', '2022-03-17T16:00:00+00:00'],
                ['2022-03-17T17:00:00+00:00', '2022-03-17T17:30:00+00:00'],
            ],
            id='merge_intervals',
        ),
    ],
)
async def test_sync_places_info_merge_working_intervals(
        place_intervals,
        zone_intervals,
        expected_intervals,
        taxi_eats_picker_dispatch,
        get_places,
        places_environment,
):
    if place_intervals:
        place_intervals = [
            {k: utils.parse_datetime(v) for k, v in interval.items()}
            for interval in place_intervals
        ]
    if zone_intervals:
        zone_intervals = [
            {k: utils.parse_datetime(v) for k, v in interval.items()}
            for interval in zone_intervals
        ]
    expected_intervals = [
        list(map(utils.parse_datetime, interval))
        for interval in expected_intervals
    ]

    place_id = places_environment.create_places(
        1, dict(working_intervals=place_intervals),
    )[0]
    places_environment.create_delivery_zones(
        place_id, 1, working_intervals=zone_intervals,
    )

    await taxi_eats_picker_dispatch.run_distlock_task(
        'eats-picker-dispatch-sync-places-info',
    )

    db_place = get_places([place_id])[0]
    assert db_place['working_intervals'] == expected_intervals
