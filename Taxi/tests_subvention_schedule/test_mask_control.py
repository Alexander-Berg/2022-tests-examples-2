import pytest

from tests_subvention_schedule import utils


async def mask_control_base(
        req,
        rules,
        original_db,
        expected_db,
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        mocked_time=None,
):
    bsx.reset()

    if rules:
        bsx.set_rules(load_json(rules)['rules'][0])

    if original_db:
        utils.load_db(pgsql, load_json(original_db), mocked_time)

    response = await taxi_subvention_schedule.post(
        '/internal/subvention-schedule/v1/masks/enable', json=req,
    )
    assert response.status_code == 200

    assert utils.get_schedules(pgsql) == load_json(expected_db)


@pytest.mark.now('2020-02-01T12:00:00+0300')
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
@pytest.mark.parametrize(
    'req, rules, original_db, expected_db',
    [
        (
            {
                'from': '2021-09-26T20:00:00+0000',
                'types': ['single_ride'],
                'zones': ['moscow'],
                'tariff_classes': ['eco'],
                'limit': 1,
            },
            'active_rules_before_start_rules.json',
            'simple_rule_db.json',
            'active_rules_before_start_exp_db.json',
        ),
        (
            {
                'from': '2020-02-01T00:00:00+0300',
                'types': ['single_ride'],
                'zones': ['moscow'],
                'tariff_classes': ['eco'],
                'limit': 1,
            },
            'simple_rule.json',
            'simple_rule_db.json',
            'simple_rule_db_01.json',
        ),
        (
            {
                'from': '2020-02-02T00:00:00+0300',
                'types': ['single_ride'],
                'zones': ['moscow'],
                'tariff_classes': ['eco'],
                'limit': 1,
            },
            'simple_rule.json',
            'simple_rule_db.json',
            'simple_rule_db_02.json',
        ),
        (
            {
                'from': '2020-02-03T00:00:00+0300',
                'types': ['single_ride'],
                'zones': ['moscow'],
                'tariff_classes': ['eco'],
                'limit': 1,
            },
            'simple_rule.json',
            'simple_rule_db.json',
            'simple_rule_db_03.json',
        ),
        (
            {
                'from': '2020-02-02T00:00:00+0300',
                'types': ['single_ride'],
                'zones': ['moscow'],
                'tariff_classes': ['eco'],
                'limit': 1,
            },
            'simple_rule_no_tags.json',
            'simple_rule_db.json',
            'simple_rule_db_inf.json',
        ),
        (
            {'from': '2020-02-02T00:00:00+0300', 'limit': 4},
            'simple_rule_2_zones_classes.json',
            'simple_rule_db_2_zones_classes.json',
            'simple_rule_db_expected_2_zones_classes.json',
        ),
        (
            {'from': '2020-02-02T00:00:00+0300', 'limit': 2},
            'simple_rule_2_zones_classes.json',
            'simple_rule_db_2_zones_classes.json',
            'simple_rule_db_expected_2_zones_classes_limited.json',
        ),
    ],
)
async def test_mask_enable(
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        req,
        rules,
        original_db,
        expected_db,
):
    await mask_control_base(
        req,
        rules,
        original_db,
        expected_db,
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
    )


@pytest.mark.now('2020-02-01T12:00:00+0300')
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
@pytest.mark.parametrize(
    'req, rules, original_db, expected_db',
    [
        (
            {
                'from': '2020-02-01T00:00:00+0300',
                'types': ['single_ride'],
                'zones': ['moscow'],
                'tariff_classes': ['eco'],
                'limit': 1,
            },
            'simple_rule.json',
            'simple_rule_db.json',
            'simple_rule_db_01.json',
        ),
    ],
)
async def test_mask_enable_check_rs(
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        req,
        rules,
        original_db,
        expected_db,
):
    await mask_control_base(
        req,
        rules,
        original_db,
        expected_db,
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
    )

    assert bsx.rules_select.times_called == 2
    assert bsx.rules_select.next_call()['request_data'].json == {
        'limit': 10,
        'rule_types': ['single_ride'],
        'tags_constraint': {'has_tag': True},
        'tariff_classes': ['eco'],
        'time_range': {
            'end': '2262-04-11T23:47:16.854775807+00:00',
            'start': '2020-01-31T21:00:00+00:00',
        },
        'zones': ['moscow'],
    }
    assert bsx.rules_select.next_call()['request_data'].json == {
        'cursor': '10',
        'limit': 10,
        'rule_types': ['single_ride'],
        'tags_constraint': {'has_tag': True},
        'tariff_classes': ['eco'],
        'time_range': {
            'end': '2262-04-11T23:47:16.854775807+00:00',
            'start': '2020-01-31T21:00:00+00:00',
        },
        'zones': ['moscow'],
    }


@pytest.mark.now('2020-02-04T12:00:00+0300')
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
@pytest.mark.parametrize(
    'rules, original_db, expected_db',
    [
        (
            'simple_rule_2_zones_classes.json',
            'simple_rule_db_2_zones_classes.json',
            'simple_rule_db_expected_2_zones_classes_limited.json',
        ),
    ],
)
@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': False, 'update_period': 100},
        'enable_masks_job': {'enabled': True, 'update_period': 100},
    },
    ENABLE_MASKS_SETTINGS={'limit': 2, 'enable_before_days_offset': 2},
)
async def test_mask_enable_job(
        taxi_subvention_schedule,
        pgsql,
        mocked_time,
        load_json,
        bsx,
        rules,
        original_db,
        expected_db,
):
    bsx.reset()

    if rules:
        bsx.set_rules(load_json(rules)['rules'][0])

    if original_db:
        utils.load_db(pgsql, load_json(original_db), mocked_time)

    assert (
        await taxi_subvention_schedule.post(
            '/service/cron', json={'task_name': 'enable-masks'},
        )
    ).status_code == 200

    assert utils.get_schedules(pgsql) == load_json(expected_db)
