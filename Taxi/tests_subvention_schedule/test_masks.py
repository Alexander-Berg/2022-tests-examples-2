# pylint: disable=C0302
import pandas as pd
import pytest

from tests_subvention_schedule import utils


# pylint: disable=W0102
async def common_test(
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        classes,
        zones,
        activity,
        has_lightbox,
        has_sticker,
        rules,
        expected_db,
        expected,
        ignored_restrictions,
        start='2021-02-01T12:00:00+0300',
        end='2021-02-06T12:00:00+0300',
        check_bsx_calls_count=True,
        tags=['t1', 't2'],
        expected_code=200,
):
    expected_bsx_calls = 2 * len(classes) * len(zones)

    bsx.reset()

    request = {
        'types': ['single_ride'],
        'ignored_restrictions': ignored_restrictions,
        'time_range': {'from': start, 'to': end},
        'activity_points': activity,
        'branding': {'has_lightbox': has_lightbox, 'has_sticker': has_sticker},
        'tags': tags,
        'tariff_classes': classes,
        'zones': zones,
    }

    if rules:
        bsx_rules = load_json(rules)['rules']
        bsx.set_rules(bsx_rules)

        data = pd.DataFrame(bsx_rules)
        expected_bsx_calls = expected_bsx_calls + len(data.groupby('zone')) * 2

    response = await taxi_subvention_schedule.post(
        '/internal/subvention-schedule/v1/schedule', json=request,
    )

    assert response.status_code == expected_code

    if isinstance(expected_db, str):
        expected_db = load_json(expected_db)

    assert utils.get_schedules(pgsql) == expected_db

    if check_bsx_calls_count:
        assert bsx.rules_select.times_called == expected_bsx_calls
    last_bsx_call_count = bsx.rules_select.times_called

    if expected_code == 200 and expected:
        assert utils.sort_response(response.json()) == utils.sort_response(
            load_json(expected),
        )

    response = await taxi_subvention_schedule.post(
        '/internal/subvention-schedule/v1/schedule', json=request,
    )

    assert response.status_code == expected_code

    assert utils.get_schedules(pgsql) == expected_db

    assert bsx.rules_select.times_called == last_bsx_call_count

    if expected_code == 200 and expected:
        assert utils.sort_response(response.json()) == utils.sort_response(
            load_json(expected),
        )

    assert utils.check_update_time_valid(pgsql)


@pytest.mark.now('2021-02-01T12:00:00+0300')
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {
            'name': 'br_russia',
            'name_en': 'Russia',
            'name_ru': 'Россия',
            'node_type': 'root',
            'parent_name': 'br_root',
            'region_id': '225',
        },
        {
            'name': 'br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'root',
            'parent_name': 'br_russia',
            'tariff_zones': ['moscow'],
        },
        {
            'name': 'br_spb',
            'name_en': 'St. Petersburg',
            'name_ru': 'Cанкт-Петербург',
            'node_type': 'root',
            'parent_name': 'br_russia',
            'tariff_zones': ['spb'],
            'region_id': '2',
        },
        {
            'name': 'br_almaty',
            'name_en': 'Almaty',
            'name_ru': 'Алматы',
            'node_type': 'root',
            'parent_name': 'br_russia',
            'tariff_zones': ['almaty'],
            'region_id': '162',
        },
    ],
)
@pytest.mark.experiments3(filename='experiment_use_masks.json')
@pytest.mark.config(
    SUBVENTION_SCHEDULE_RPS_LIMITER_SETTINGS_V2=utils.RPS_LIMITER_CONFIG,
    CLAMP_ITEMS_TO_DESCRIPTOR_BEGIN=True,
)
@pytest.mark.parametrize(
    'classes, zones, tags, init_db, expected, start, end',
    [
        (
            ['eco'],
            ['moscow'],
            ['t1'],
            'simple_mask_db.json',
            'expected_simple_mask_100.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
        ),
        (
            ['eco'],
            ['moscow'],
            [],
            'simple_mask_db.json',
            'expected_simple_mask_200.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
        ),
        (
            ['eco'],
            ['moscow'],
            ['t2'],
            'simple_mask_db.json',
            'expected_simple_mask_200.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
        ),
        (
            ['eco'],
            ['moscow'],
            [],
            'empty_mask_db.json',
            'expected_simple_mask_200.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
        ),
        (
            ['eco'],
            ['moscow'],
            ['t1'],
            'empty_mask_db.json',
            'expected_simple_mask_200.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
        ),
        (
            ['eco'],
            ['moscow'],
            ['t2'],
            'empty_mask_db.json',
            'expected_simple_mask_200.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
        ),
        (
            ['eco'],
            ['moscow'],
            ['t2', 't3'],
            'two_tags_mask_db.json',
            'expected_simple_mask_300.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
        ),
        (
            ['eco'],
            ['moscow'],
            ['t1', 't3'],
            'two_tags_mask_db.json',
            'expected_simple_mask_100.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
        ),
        (
            ['eco'],
            ['moscow'],
            ['t1', 't2', 't3'],
            'two_tags_mask_db.json',
            'expected_simple_mask_400.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
        ),
        (
            ['eco', 'uber'],
            ['moscow'],
            ['t1', 't2', 't3'],
            'two_classes_one_mask_db.json',
            'expected_two_classes_mask.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
        ),
        (
            ['eco', 'uber'],
            ['moscow'],
            ['t1', 't2', 't3'],
            'two_classes_two_masks_db.json',
            'expected_two_classes_mask.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
        ),
        (
            ['eco'],
            ['moscow'],
            ['t1'],
            'two_mask_db.json',
            'two_mask_expected.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
        ),
        (
            ['eco'],
            ['moscow'],
            ['t1'],
            'two_mask_exact_db.json',
            'two_mask_expected.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
        ),
        (
            ['eco'],
            ['moscow'],
            ['t1'],
            'active_db_inf_with_items.json',
            'expected_active_inf.json',
            '2020-02-01T12:00:00+0300',
            '2020-02-06T12:00:00+0300',
        ),
    ],
)
async def test_fetch(
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        classes,
        zones,
        tags,
        init_db,
        expected,
        start,
        end,
):
    utils.load_db(pgsql, load_json(init_db))

    await common_test(
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        classes,
        zones,
        activity=50,
        has_lightbox=True,
        has_sticker=True,
        rules=None,
        expected_db=init_db,
        expected=expected,
        ignored_restrictions=['activity'],
        start=start,
        end=end,
        check_bsx_calls_count=False,
        tags=tags,
    )


@pytest.mark.now('2021-02-01T12:00:00+0300')
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {
            'name': 'br_russia',
            'name_en': 'Russia',
            'name_ru': 'Россия',
            'node_type': 'root',
            'parent_name': 'br_root',
            'region_id': '225',
        },
        {
            'name': 'br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'root',
            'parent_name': 'br_russia',
            'tariff_zones': ['moscow'],
        },
        {
            'name': 'br_spb',
            'name_en': 'St. Petersburg',
            'name_ru': 'Cанкт-Петербург',
            'node_type': 'root',
            'parent_name': 'br_russia',
            'tariff_zones': ['spb'],
            'region_id': '2',
        },
        {
            'name': 'br_almaty',
            'name_en': 'Almaty',
            'name_ru': 'Алматы',
            'node_type': 'root',
            'parent_name': 'br_russia',
            'tariff_zones': ['almaty'],
            'region_id': '162',
        },
    ],
)
@pytest.mark.experiments3(filename='experiment_use_masks.json')
@pytest.mark.config(
    SUBVENTION_SCHEDULE_RPS_LIMITER_SETTINGS_V2=utils.RPS_LIMITER_CONFIG,
    CLAMP_ITEMS_TO_DESCRIPTOR_BEGIN=True,
)
@pytest.mark.parametrize(
    'classes, zones, tags, init_db, expected_db, start, end',
    [
        pytest.param(
            ['eco'],
            ['moscow'],
            ['t1'],
            'mask_clamp_db_no_cross.json',
            'mask_clamp_db_no_cross_expected.json',
            '2020-02-01T16:00:00+0300',
            '2020-02-06T12:00:00+0300',
            marks=[
                pytest.mark.config(ROUND_TIME_RANGE_TO_DAYS_IN_HANDLE=True),
            ],
        ),
        pytest.param(
            ['eco'],
            ['moscow'],
            ['t1'],
            'mask_clamp_db.json',
            'mask_clamp_db_expected.json',
            '2020-02-02T16:00:00+0300',
            '2020-02-06T12:00:00+0300',
            marks=[
                pytest.mark.config(ROUND_TIME_RANGE_TO_DAYS_IN_HANDLE=True),
            ],
        ),
        pytest.param(
            ['eco'],
            ['moscow'],
            ['t1'],
            'simple_mask_db_no_data.json',
            'simple_mask_db_no_data_t1.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
            marks=[
                pytest.mark.config(ROUND_TIME_RANGE_TO_DAYS_IN_HANDLE=False),
            ],
        ),
        pytest.param(
            ['eco'],
            ['moscow'],
            ['t1'],
            'active_db_inf_after_update.json',
            'expected_active_db_inf_after_update.json',
            '2020-02-01T12:00:00+0300',
            '2020-02-06T12:00:00+0300',
            marks=[
                pytest.mark.config(ROUND_TIME_RANGE_TO_DAYS_IN_HANDLE=True),
            ],
        ),
    ],
)
async def test_get(
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        classes,
        zones,
        tags,
        init_db,
        expected_db,
        start,
        end,
):
    utils.load_db(pgsql, load_json(init_db))

    await common_test(
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        classes,
        zones,
        50,
        True,
        True,
        None,
        expected_db,
        None,
        ['activity'],
        start,
        end,
        False,
        tags=tags,
    )
