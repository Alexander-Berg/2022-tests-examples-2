# pylint: disable=import-error
import collections
import datetime

from heatmap_sample_storage.surge_points.fbs import SurgePointsResponse
import pytest


_NOW = datetime.datetime(2019, 3, 8, tzinfo=datetime.timezone.utc)


def parse_point(point_fb):
    point_b_adj_percentiles = []
    for j in range(point_fb.PointBAdjPercentilesLength()):
        point_b_adj_percentiles.append(point_fb.PointBAdjPercentiles(j))
    return {
        'pins': point_fb.Pins(),
        'pins_order': point_fb.PinsOrder(),
        'pins_driver': point_fb.PinsDriver(),
        'free': point_fb.Free(),
        'total': point_fb.Total(),
        'radius': point_fb.Radius(),
        'value_raw': round(point_fb.ValueRaw(), 3),
        'value_smooth': round(point_fb.ValueSmooth(), 3),
        'position': {
            'lat': point_fb.Position().Lat(),
            'lon': point_fb.Position().Lon(),
        },
        'created_ts': point_fb.CreatedTs(),
        'category': point_fb.Category().decode('utf-8'),
        'surge_value_in_tariff': point_fb.SurgeValueInTariff(),
        'ps_shift_past_raw': point_fb.PsShiftPastRaw(),
        'deviation_from_target_abs': point_fb.DeviationFromTargetAbs(),
        'point_b_adj_percentiles': point_b_adj_percentiles,
        'value_raw_graph': point_fb.ValueRawGraph(),
        'cost': point_fb.Cost(),
        'id': point_fb.Id().decode('utf-8') if point_fb.Id() else None,
    }


def parse_fb_response(response_fbs):
    parsed = (
        SurgePointsResponse.SurgePointsResponse.GetRootAsSurgePointsResponse(
            response_fbs, 0,
        )
    )
    points = []
    for i in range(parsed.PointsLength()):
        points.append(parse_point(parsed.Points(i)))
    points.sort(key=lambda val: val['category'])
    return {
        'points': points,
        'cursor': parsed.Cursor().decode('utf-8'),
        'ttl_sec': parsed.TtlSec(),
    }


# See calc_surge.json. boats are not saved due to `linear_dependency` reason
def expected_response(surge_fixed_points_from_admin):
    return {
        'cursor': 'surge_fixed_points:1552003200',
        'ttl_sec': 600,
        'points': [
            {
                'category': 'econom',
                'created_ts': 1552003200,
                'free': 12,
                'pins': 3,
                'pins_driver': 4,
                'pins_order': 5,
                'position': {'lat': 55.0, 'lon': 37.0},
                'radius': 1500,
                'total': 30,
                'value_raw': 1.2,
                'value_smooth': 0.781,
                'surge_value_in_tariff': 1.5,
                'ps_shift_past_raw': 3.33,
                'deviation_from_target_abs': 2.22,
                'point_b_adj_percentiles': [0.1, 0.2],
                'value_raw_graph': 1.1,
                'cost': 19.99,
                'id': (
                    '6010bde7eb37e20aaa602576'
                    if surge_fixed_points_from_admin
                    else None
                ),
            },
            {
                'category': 'vip',
                'created_ts': 1552003200,
                'free': 0,
                'pins': 0,
                'pins_driver': 0,
                'pins_order': 0,
                'position': {'lat': 55.0, 'lon': 37.0},
                'radius': 0,
                'total': 0,
                'value_raw': 1.17,
                'value_smooth': 0.824,
                'surge_value_in_tariff': 0.0,
                'ps_shift_past_raw': 0.0,
                'deviation_from_target_abs': 0.0,
                'point_b_adj_percentiles': [],
                'value_raw_graph': 0,
                'cost': 0,
                'id': (
                    '6010bde7eb37e20aaa602576'
                    if surge_fixed_points_from_admin
                    else None
                ),
            },
        ],
    }


def expected_surge_request(surge_fixed_points_from_admin):
    request = {
        'authorized': False,
        'classes': ['econom', 'vip'],
        'intent': 'surge_sampling',
        'point_a': [37.0, 55.0],
        'tariff_zone': 'moscow',
        'use_cache': False,
    }
    if surge_fixed_points_from_admin:
        request['geopoint_id'] = '6010bde7eb37e20aaa602576'
    return request


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    HEATMAP_SAMPLE_STORAGE_ENABLED_JOBS={'surge-sampling': True},
    SURGE_SAMPLING_CATEGORIES=['__default__', 'econom', 'vip'],
    HEATMAP_SAMPLES_TYPES=['taxi_surge'],
    SURGE_FIXED_POINTS_SAVE_RESULTS=True,
    SURGE_FIXED_POINTS_SAVE_NON_BASE_CLASSES=['vip', 'boats'],
    SURGE_SAMPLING_CREATE_PINS=True,
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'surge_fixed_points_from_admin,surge_samples_positions',
    [(False, [[37.0, 55.0]]), (True, [])],
)
async def test_surge_sampling(
        taxi_heatmap_sample_storage,
        mockserver,
        testpoint,
        load_json,
        redis_store,
        load_binary,
        taxi_config,
        surge_fixed_points_from_admin,
        surge_samples_positions,
        mocked_time,
):
    @testpoint('surge-sampling-stats')
    def surge_sampling_stats_testpoint(arg):
        pass

    @mockserver.json_handler('/surge-calculator/v1/calc-surge')
    def mock_calc_surge(request):
        return load_json('calc_surge.json')

    @mockserver.json_handler('/pin-storage/v1/create_pin')
    def mock_create_pin(request):
        return {'timestamp': _NOW.isoformat()}

    taxi_config.set_values(
        {
            'SURGE_FIXED_POINTS_FROM_ADMIN': surge_fixed_points_from_admin,
            'SURGE_SAMPLES_POSITIONS': surge_samples_positions,
        },
    )

    mocked_time.set(_NOW)
    async with taxi_heatmap_sample_storage.spawn_task(
            'distlock/surge-sampling',
    ):
        sampling_stats = await surge_sampling_stats_testpoint.wait_call()
        assert sampling_stats == {
            'arg': {
                'estimate_rps': 1,
                'points_processed': 1,
                'samples_created': 2,
                'success_rate': 1.0,
            },
        }
        surge_requests = mock_calc_surge.next_call()['request'].json
        assert surge_requests == expected_surge_request(
            surge_fixed_points_from_admin,
        )

        create_pin_request = mock_create_pin.next_call()['request'].json
        assert create_pin_request == {
            'pin': {
                'calculation_id': 'some_calculation_id',
                'classes': [
                    {
                        'calculation_meta': {
                            'counts': {
                                'free': 12,
                                'free_chain': 3,
                                'pins': 3,
                                'radius': 1500,
                                'total': 30,
                            },
                            'pins_meta': {
                                'eta_in_tariff': 0.0,
                                'pins_b': 3,
                                'pins_driver': 4,
                                'pins_order': 5,
                                'prev_pins': 2.8800000000000003,
                                'surge_in_tariff': 1.5,
                            },
                            'smooth': {
                                'point_a': {
                                    'is_default': False,
                                    'value': 0.781,
                                },
                            },
                            'ps': -4.172,
                            'reason': 'pins_free',
                        },
                        'cost': 0,
                        'name': 'econom',
                        'surge': {
                            'surcharge': {
                                'alpha': 1.0,
                                'beta': 0.0,
                                'value': 0.0,
                            },
                            'value': 1.05,
                        },
                        'value_raw': 1.2,
                    },
                    {
                        'calculation_meta': {
                            'smooth': {
                                'point_a': {
                                    'is_default': False,
                                    'value': 0.824,
                                },
                            },
                            'reason': 'rain',
                        },
                        'cost': 0,
                        'name': 'vip',
                        'surge': {
                            'surcharge': {
                                'alpha': 0.2,
                                'beta': 0.8,
                                'value': 0.0,
                            },
                            'value': 1.0,
                        },
                        'value_raw': 1.17,
                    },
                    {
                        'calculation_meta': {'reason': 'linear_dependency'},
                        'cost': 0.0,
                        'name': 'boats',
                        'surge': {'value': 2.0},
                        'value_raw': 2.0,
                    },
                ],
                'experiments': [],
                'is_fake': False,
                'is_sample': True,
                'personal_phone_id': '',
                'point_a': [37.0, 55.0],
                'zone_id': 'MSK-Yandex HQ',
                'user_id': '',
            },
        }
        assert b'surge_fixed_points:1552003200' in redis_store.keys()

    await taxi_heatmap_sample_storage.invalidate_caches()
    response = await taxi_heatmap_sample_storage.get('v1/surge_points')
    assert response.status == 200
    assert parse_fb_response(response.content) == expected_response(
        surge_fixed_points_from_admin,
    )

    # request missing cursor
    response = await taxi_heatmap_sample_storage.get(
        'v1/surge_points', params={'cursor': 'surge_fixed_points:1552003199'},
    )
    assert response.status == 200
    assert parse_fb_response(response.content) == expected_response(
        surge_fixed_points_from_admin,
    )

    # request with latest cursor
    response = await taxi_heatmap_sample_storage.get(
        'v1/surge_points', params={'cursor': 'surge_fixed_points:1552003200'},
    )
    assert response.status == 204


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    HEATMAP_SAMPLE_STORAGE_ENABLED_JOBS={'surge-sampling': True},
    SURGE_SAMPLING_CATEGORIES=['__default__', 'econom', 'vip'],
    HEATMAP_SAMPLES_TYPES=['taxi_surge'],
    SURGE_FIXED_POINTS_SAVE_RESULTS=True,
    SURGE_FIXED_POINTS_SAVE_NON_BASE_CLASSES=['vip', 'boats'],
    SURGE_SAMPLING_CREATE_PINS=True,
    SURGE_FIXED_POINTS_FROM_ADMIN=True,
    SURGE_SAMPLING_INTERVALS={
        'points': {
            'default_interval': 3,
            'tag_intervals': {'slow': 6, 'fast': 2, 'instant': 1},
        },
        'minimum_rps': 4,
    },
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_different_update_intervals(
        taxi_heatmap_sample_storage,
        mocked_time,
        testpoint,
        mockserver,
        load_json,
        admin_surger_points,
):
    @testpoint('surge-sampling-stats')
    def surge_sampling_stats_testpoint(arg):
        mocked_time.sleep(1)

    samples_count = collections.defaultdict(int)

    @mockserver.json_handler('/surge-calculator/v1/calc-surge')
    def _mock_calc_surge(request):
        samples_count[str(request.json['point_a'])] += 1
        return load_json('calc_surge.json')

    @mockserver.json_handler('/pin-storage/v1/create_pin')
    def _mock_create_pin(request):
        return {'timestamp': _NOW.isoformat()}

    points = []
    for i, tag in enumerate(['slow', 'fast', 'instant', ''], 1):
        point = dict(admin_surger_points.points[0])
        if tag:
            point['tags'] = [tag]
        point['location'] = [37 + i / 10.0, 55.0]
        point['id'] = f'almost@anything{i}'
        points.append(point)
    admin_surger_points.points = points

    mocked_time.set(_NOW)
    await taxi_heatmap_sample_storage.update_server_state()

    async with taxi_heatmap_sample_storage.spawn_task(
            'distlock/surge-sampling',
    ):
        # First sampling occurs right after spawn_task
        # Call 11 more times. Testpoint advances mocked time for one sec on
        # each call on c++ side, thus emulating 12 seconds
        for i in range(11):
            await surge_sampling_stats_testpoint.wait_call()

    # We have samples with update intervals [6, 2, 1, 3], which lead to 2 rps
    # So after 12 seconds we expect 12 / <interval> samples done
    assert samples_count == {
        '[37.1, 55.0]': 2,
        '[37.2, 55.0]': 6,
        '[37.3, 55.0]': 12,
        '[37.4, 55.0]': 4,
    }
