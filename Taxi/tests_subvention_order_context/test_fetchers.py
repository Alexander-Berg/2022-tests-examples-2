import copy
import datetime

import pytest

from . import test_common


@test_common.fetcher_test('activity_points')
async def test_activity_points_fetcher(mongodb, stq_runner):
    await stq_runner.subventions_driving_v2.call(
        task_id='task_id', kwargs=test_common.DEFAULT_KWARGS,
    )
    stored = mongodb.subvention_order_context.find_one()
    assert stored['value']['activity_points'] == 91


@pytest.mark.config(SUBVENTION_ORDER_CONTEXT_FORCED_ACTIVITY_FETCHER=True)
@test_common.fetcher_test('activity_points')
async def test_activity_points_forced_fetcher(mockserver, mongodb, stq_runner):
    @mockserver.json_handler('/driver-metrics-storage/v2/activity_values/list')
    def _mock_v2_activity_values_list(request):
        return {'items': [{'unique_driver_id': 'udid', 'value': 33}]}

    await stq_runner.subventions_driving_v2.call(
        task_id='task_id', kwargs=test_common.DEFAULT_KWARGS,
    )

    stored = mongodb.subvention_order_context.find_one()
    assert stored['value']['activity_points'] == 33


@test_common.fetcher_test('ref_time')
async def test_ref_time_fetcher(mongodb, stq_runner):
    await stq_runner.subventions_driving_v2.call(
        task_id='task_id', kwargs=test_common.DEFAULT_KWARGS,
    )
    stored = mongodb.subvention_order_context.find_one()
    assert stored['value']['ref_time'] == datetime.datetime(2020, 1, 1, 11, 59)


@test_common.fetcher_test('tariff_class')
async def test_tariff_class_fetcher(mongodb, stq_runner):
    await stq_runner.subventions_driving_v2.call(
        task_id='task_id', kwargs=test_common.DEFAULT_KWARGS,
    )
    stored = mongodb.subvention_order_context.find_one()
    assert stored['value']['tariff_class'] == 'econom'


@test_common.fetcher_test('unique_driver_id')
async def test_unique_driver_id_fetcher(mongodb, stq_runner, unique_drivers):
    await stq_runner.subventions_driving_v2.call(
        task_id='task_id', kwargs=test_common.DEFAULT_KWARGS,
    )
    stored = mongodb.subvention_order_context.find_one()
    assert stored['value']['unique_driver_id'] == 'unique_driver_id'


@test_common.fetcher_test('branding')
async def test_branding_fetcher(mongodb, stq_runner):
    kwargs = copy.deepcopy(test_common.DEFAULT_KWARGS)
    kwargs['branding'] = {'has_lightbox': True, 'has_sticker': False}

    await stq_runner.subventions_driving_v2.call(
        task_id='task_id', kwargs=kwargs,
    )
    stored = mongodb.subvention_order_context.find_one()

    assert stored['value']['branding'] == {
        'has_lightbox': True,
        'has_sticker': False,
    }


@pytest.mark.parametrize(
    'branding_value, expected',
    [
        (['lightbox', 'sticker'], {'has_lightbox': True, 'has_sticker': True}),
        (['lightbox'], {'has_lightbox': True, 'has_sticker': False}),
        ([], {'has_lightbox': False, 'has_sticker': False}),
        (None, {'has_lightbox': False, 'has_sticker': False}),
    ],
)
@pytest.mark.config(SUBVENTION_ORDER_CONTEXT_FORCED_BRANDING_FETCHER=True)
@test_common.fetcher_test('branding')
async def test_branding_fetcher_forced(
        mongodb, stq_runner, vehicles, branding_value, expected,
):
    kwargs = copy.deepcopy(test_common.DEFAULT_KWARGS)

    if branding_value is not None:
        vehicles.set_branding('dbid_uuid', branding_value)

    await stq_runner.subventions_driving_v2.call(
        task_id='task_id', kwargs=kwargs,
    )
    stored = mongodb.subvention_order_context.find_one()

    assert stored['value']['branding'] == expected


@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_moscow_adm',
            'name_en': 'Moscow (adm)',
            'name_ru': 'Москва (адм)',
            'node_type': 'node',
            'parent_name': 'br_root',
            'tariff_zones': ['boryasvo', 'moscow', 'vko'],
            'region_id': '213',
        },
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
    ],
)
@test_common.fetcher_test('geonodes')
async def test_geonodes_fetcher(mongodb, stq_runner):
    kwargs = copy.deepcopy(test_common.DEFAULT_KWARGS)
    kwargs['nz'] = 'dont_use_this_zone'

    await stq_runner.subventions_driving_v2.call(
        task_id='task_id', kwargs=kwargs,
    )
    stored = mongodb.subvention_order_context.find_one()

    assert stored['value']['geonodes'] == 'br_root/br_moscow_adm/moscow'


@test_common.fetcher_test('time_zone')
async def test_time_zone_fetcher(mongodb, tariff_settings, stq_runner):
    await stq_runner.subventions_driving_v2.call(
        task_id='task_id', kwargs=test_common.DEFAULT_KWARGS,
    )
    stored = mongodb.subvention_order_context.find_one()

    assert stored['value']['time_zone'] == 'Europe/Moscow'


@pytest.mark.parametrize(
    'kwargs_driver_point, order_core_reponse, expected',
    [
        ([99.9, 11.1], None, [99.9, 11.1]),
        (None, 'order_proc_ok.json', [37.609576, 55.746054]),
        (None, 'order_proc_only_seen_point.json', [22.222222, 11.111111]),
        (None, 'order_proc_only_candidate_point.json', [55.555555, 44.444444]),
    ],
)
@pytest.mark.config(SUBVENTION_ORDER_CONTEXT_ENABLE_DRIVER_POINT_FALLBACK=True)
@test_common.fetcher_test('driver_point')
async def test_driver_point_fetcher(
        mongodb,
        stq_runner,
        load_json,
        mock_order_core,
        kwargs_driver_point,
        order_core_reponse,
        expected,
):
    kwargs = copy.deepcopy(test_common.DEFAULT_KWARGS)
    if kwargs_driver_point:
        kwargs['driver_point'] = kwargs_driver_point
    else:
        del kwargs['driver_point']

    if order_core_reponse:
        mock_order_core.set_response(load_json(order_core_reponse))

    await stq_runner.subventions_driving_v2.call(
        task_id='task_id', kwargs=kwargs,
    )
    stored = mongodb.subvention_order_context.find_one()
    assert stored['value']['driver_point'] == expected


@pytest.mark.parametrize(
    'enable_since, should_be_enabled',
    [
        pytest.param(
            test_common.DEFAULT_KWARGS['driving_at'], True, id='enabled',
        ),
        pytest.param('2030-01-01T00:00:00+0000', False, id='disabled'),
    ],
)
@test_common.fetcher_test('virtual_tags')
async def test_virtual_tags_fetcher(
        mockserver,
        mongodb,
        taxi_config,
        stq_runner,
        enable_since,
        should_be_enabled,
):
    kwargs = copy.deepcopy(test_common.DEFAULT_KWARGS)

    taxi_config.set_values(
        {
            'SUBVENTION_ORDER_CONTEXT_FETCH_VIRTUAL_TAGS': {
                'enable_since': enable_since,
            },
        },
    )

    @mockserver.json_handler('/driver-mode-index/v1/driver/virtual_tags')
    def _mock_v1_driver_virtual_tags(request):
        assert request.json['driver_info']['park_id'] == 'dbid'
        assert request.json['driver_info']['driver_profile_id'] == 'uuid'
        return {'virtual_tags': ['vtag']}

    await stq_runner.subventions_driving_v2.call(
        task_id='task_id', kwargs=kwargs,
    )

    stored = mongodb.subvention_order_context.find_one()

    if should_be_enabled:
        assert stored['value']['virtual_tags'] == ['vtag']
    else:
        assert stored['value']['virtual_tags'] == []
        assert _mock_v1_driver_virtual_tags.times_called == 0


@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
@pytest.mark.parametrize(
    'driver_point, expected_subvention_areas',
    [
        (
            [1.5, 1.5],
            [
                'another_center_name',
                'big_center_name',
                'another_lower_right_name',
                'lower_right_name',
            ],
        ),
        (
            [0.5, 0.5],
            ['another_center_name', 'big_center_name', 'lower_left_name'],
        ),
        ([4, 4], ['upper_right_name']),
        ([10, 10], []),
    ],
)
@pytest.mark.config(ENABLE_GEOAREAS_SUBVENTIONS_SORT_BY_AREA_ASCENDING=True)
async def test_fetcher_subvention_geoareas(
        mongodb, stq_runner, driver_point, expected_subvention_areas,
):
    context_data = copy.deepcopy(test_common.DEFAULT_CONTEXT_DATA)
    del context_data['value']['subvention_geoareas']
    context_data['value']['driver_point'] = driver_point
    mongodb.subvention_order_context.insert_one(context_data)

    kwargs = copy.deepcopy(test_common.DEFAULT_KWARGS)

    await stq_runner.subventions_driving_v2.call(
        task_id='task_id', kwargs=kwargs,
    )

    stored = mongodb.subvention_order_context.find_one()

    if driver_point is None:
        assert 'subvention_geoareas' not in stored['value']
    else:
        subvention_geoareas = stored['value']['subvention_geoareas']
        assert subvention_geoareas == expected_subvention_areas


@pytest.mark.config(ADD_GEO_EXP_TAG_IN_ORDER_COMPLETED_EVENT=True)
@pytest.mark.experiments3(filename='geo_experiments_two_oks.json')
@pytest.mark.parametrize(
    'driver_tags', [pytest.param(['driver_tag']), pytest.param(None)],
)
@test_common.fetcher_test('tags')
async def test_fetcher_tags(
        mockserver, mongodb, stq_runner, driver_tags, unique_drivers,
):
    kwargs = copy.deepcopy(test_common.DEFAULT_KWARGS)
    del kwargs['tags']

    if driver_tags:
        kwargs['tags'] = driver_tags

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _mock_v1_drivers_match_profile(request):
        return {'tags': ['driver_tag']}

    await stq_runner.subventions_driving_v2.call(
        task_id='task_id', kwargs=kwargs,
    )

    stored = mongodb.subvention_order_context.find_one()

    assert set(stored['value']['tags']) == set(
        ['driver_tag', 'geo_exp_tag_2', 'geo_exp_tag_1'],
    )


@pytest.mark.config(
    ADD_GEO_EXP_TAG_IN_ORDER_COMPLETED_EVENT=True,
    SUBVENTION_ORDER_CONTEXT_FORCED_TAG_FETCHER=True,
)
@pytest.mark.experiments3(filename='geo_experiments_two_oks.json')
@pytest.mark.parametrize(
    'driver_tags', [pytest.param(['driver_tag']), pytest.param(None)],
)
@test_common.fetcher_test('tags')
async def test_tag_fetcher_forced(
        mockserver, mongodb, stq_runner, driver_tags, unique_drivers,
):
    kwargs = copy.deepcopy(test_common.DEFAULT_KWARGS)
    del kwargs['tags']

    if driver_tags:
        kwargs['tags'] = driver_tags

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _mock_v1_drivers_match_profile(request):
        return {'tags': ['service_driver_tag']}

    await stq_runner.subventions_driving_v2.call(
        task_id='task_id', kwargs=kwargs,
    )

    stored = mongodb.subvention_order_context.find_one()

    assert set(stored['value']['tags']) == set(
        ['service_driver_tag', 'geo_exp_tag_2', 'geo_exp_tag_1'],
    )


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'driver_point, nearest_zone, expected_tariff_zone',
    [
        ([37.5444031, 55.7054503], 'moscow1', 'moscow'),  # inside polygon
        ([38.1074524, 55.6713893], 'moscow1', 'moscow1'),  # outside polygon
        (
            [36.90840238790664, 55.347194847462745],
            'moscow1',
            'moscow1',
        ),  # polygon edge point
        ([0.01, 0.01], 'moscow1', 'moscow1'),
    ],
)
async def test_fetcher_tariff_zone(
        mongodb, stq_runner, driver_point, nearest_zone, expected_tariff_zone,
):
    context_data = copy.deepcopy(test_common.DEFAULT_CONTEXT_DATA)
    del context_data['value']['tariff_zone']
    context_data['value']['driver_point'] = driver_point
    mongodb.subvention_order_context.insert_one(context_data)

    kwargs = copy.deepcopy(test_common.DEFAULT_KWARGS)
    kwargs['nz'] = nearest_zone

    await stq_runner.subventions_driving_v2.call(
        task_id='task_id', kwargs=kwargs,
    )

    stored = mongodb.subvention_order_context.find_one()

    assert stored['value']['tariff_zone'] == expected_tariff_zone
