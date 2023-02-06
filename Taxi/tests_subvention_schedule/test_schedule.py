# pylint: disable=C0302
import pandas as pd
import pytest

from tests_subvention_schedule import utils

# pylint: disable=W0102
async def common_test(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
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
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='subvention_schedule_use_bulk_rules_match',
        consumers=['subvention-schedule/v1/schedule'],
        clauses=[],
        default_value={'mode': use_bulk_match},
    )

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

    if expected_code == 200:
        assert utils.sort_response(response.json()) == utils.sort_response(
            load_json(expected),
        )

    response = await taxi_subvention_schedule.post(
        '/internal/subvention-schedule/v1/schedule', json=request,
    )

    assert response.status_code == expected_code

    assert utils.get_schedules(pgsql) == expected_db

    assert bsx.rules_select.times_called == last_bsx_call_count

    if expected_code == 200:
        assert utils.sort_response(response.json()) == utils.sort_response(
            load_json(expected),
        )

    assert utils.check_update_time_valid(pgsql)


@pytest.mark.parametrize('use_bulk_match', ['disabled', 'enabled'])
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
        {
            'name': 'br_israel',
            'name_en': 'Israel',
            'name_ru': 'Израиль',
            'node_type': 'root',
            'parent_name': 'br_root',
            'region_id': '181',
        },
        {
            'name': 'br_tel_aviv',
            'name_en': 'Tel\'Aviv',
            'name_ru': 'Тельавив',
            'node_type': 'root',
            'parent_name': 'br_israel',
            'tariff_zones': ['tel_aviv'],
            'region_id': '131',
        },
    ],
)
@pytest.mark.config(
    SUBVENTION_SCHEDULE_RPS_LIMITER_SETTINGS_V2=utils.RPS_LIMITER_CONFIG,
    PG_READ_MASTER_STRATEGY={'__default__': 'allowed'},
)
@pytest.mark.parametrize(
    'classes, zones, rules, expected_db, expected, start, end, check_calls',
    [
        (
            ['eco'],
            ['tel_aviv'],
            'tel_aviv_every_day_rule.json',
            'tel_aviv_every_day_rule_expected_db.json',
            'tel_aviv_every_day_rule_expected.json',
            '2021-10-30T12:00:00+0300',
            '2021-11-02T12:00:00+0200',
            True,
        ),
        (
            ['eco'],
            ['tel_aviv'],
            'tel_aviv_every_day_rule_noon.json',
            'tel_aviv_every_day_rule_noon_expected_db.json',
            'tel_aviv_every_day_rule_noon_expected.json',
            '2021-10-30T11:00:00+0300',
            '2021-11-02T11:00:00+0200',
            True,
        ),
        (
            ['eco'],
            ['moscow'],
            None,
            'expected_empty_db.json',
            'expected_empty.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
            True,
        ),
        (
            ['eco'],
            ['moscow'],
            'simple_rule.json',
            'expected_simple_rule_db.json',
            'expected_simple_rule.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
            True,
        ),
        (
            ['eco'],
            ['almaty'],
            'simple_rule_almaty.json',
            'expected_simple_rule_db_almaty.json',
            'expected_simple_rule_almaty.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
            True,
        ),
        (
            ['eco', 'comf'],
            ['moscow', 'spb'],
            None,
            'expected_empty_db_2_zones.json',
            'expected_empty.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
            True,
        ),
        (
            ['eco', 'comf'],
            ['moscow', 'spb'],
            'simple_rule.json',
            'expected_db_2_zones.json',
            'expected_simple_rule.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
            True,
        ),
        (
            ['eco'],
            ['moscow'],
            'simple_rule_with_geoarea.json',
            'expected_simple_rule_geoarea_db.json',
            'expected_simple_rule_geoarea.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
            True,
        ),
        (
            ['eco'],
            ['moscow'],
            'simple_rule_2.json',
            'expected_simple_rule_2_db.json',
            'expected_simple_rule_2.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
            True,
        ),
        (
            ['eco'],
            ['moscow'],
            'simple_rule_4.json',
            'expected_simple_rule_4_db.json',
            'expected_simple_rule_4.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-06T12:00:00+0300',
            True,
        ),
        (
            ['eco'],
            ['moscow'],
            'simple_rule.json',
            'expected_simple_rule_db.json',
            'expected_simple_rule_2_weeks.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-08T12:00:00+0300',
            True,
        ),
        (
            ['eco'],
            ['moscow'],
            'every_day_rule.json',
            'expected_every_day_rule_db.json',
            'expected_every_day_rule_1_16.json',
            '2021-02-01T12:00:00+0300',
            '2021-02-16T12:00:00+0300',
            True,
        ),
        (
            ['eco'],
            ['moscow'],
            'every_day_rule.json',
            'expected_every_day_rule_out_of_range_db.json',
            'expected_every_day_rule_out_of_range.json',
            '2021-02-01T12:00:00+0300',
            '2021-03-11T12:00:00+0300',
            False,
        ),
        (
            ['eco'],
            ['moscow'],
            'every_day_rule.json',
            'expected_every_day_rule_7_db.json',
            'expected_every_day_rule_8_9_month.json',
            '2021-02-08T12:00:00+0300',
            '2021-03-07T12:00:00+0300',
            True,
        ),
        (
            ['eco'],
            ['moscow'],
            'every_day_rule.json',
            'expected_every_day_rule_7_db.json',
            'expected_every_day_rule_8_9.json',
            '2021-02-08T12:00:00+0300',
            '2021-02-09T12:00:00+0300',
            True,
        ),
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(marks=[pytest.mark.config(USE_TAGS_FOR_UPDATE=True)]),
        pytest.param(marks=[pytest.mark.config(USE_TAGS_FOR_UPDATE=False)]),
    ],
)
async def test_schedule(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        classes,
        zones,
        rules,
        expected_db,
        expected,
        start,
        end,
        check_calls,
):
    await common_test(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        classes,
        zones,
        50,
        True,
        True,
        rules,
        expected_db,
        expected,
        ['activity'],
        start,
        end,
        check_calls,
    )


@pytest.mark.parametrize('use_bulk_match', ['disabled', 'enabled'])
@pytest.mark.now('2021-02-01T12:00:00+0300')
@pytest.mark.parametrize(
    'activity, rules, restrictions, expected_db, expected',
    [
        (
            50,
            'simple_rule_with_activity.json',
            [],
            'expected_simple_rule_activity_db.json',
            'expected_simple_rule_activity.json',
        ),
        (
            50,
            'simple_rule_with_activity.json',
            ['activity'],
            'expected_simple_rule_activity_db.json',
            'expected_simple_rule_activity.json',
        ),
        (
            30,
            'simple_rule_with_activity.json',
            ['activity'],
            'expected_simple_rule_db_low_acti.json',
            'expected_simple_rule_low_acti.json',
        ),
        (
            30,
            'simple_rule_with_activity.json',
            [],
            'expected_simple_rule_activity_no_match_db.json',
            'expected_empty.json',
        ),
    ],
)
async def test_activity_clamp(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        activity,
        rules,
        expected_db,
        expected,
        restrictions,
):
    db = load_json(expected_db)

    for i in range(0, len(db['descriptors'])):
        db['descriptors'][i][5] = '{{{0}}}'.format(','.join(restrictions))

    await common_test(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        ['eco'],
        ['moscow'],
        activity,
        True,
        True,
        rules,
        db,
        expected,
        restrictions,
    )


@pytest.mark.parametrize('use_bulk_match', ['disabled', 'enabled'])
@pytest.mark.now('2021-02-01T12:00:00+0300')
@pytest.mark.parametrize(
    'has_lightbox, has_sticker, rules, expected_db, expected',
    [
        (
            False,
            False,
            'simple_rule_with_branding.json',
            'expected_simple_rule_branding_db_none.json',
            'expected_simple_rule_branding_false.json',
        ),
        (
            False,
            True,
            'simple_rule_with_branding.json',
            'expected_simple_rule_branding_db_sticker.json',
            'expected_simple_rule_branding.json',
        ),
        (
            True,
            False,
            'simple_rule_with_branding.json',
            'expected_simple_rule_branding_db_lightbox.json',
            'expected_simple_rule_branding_false.json',
        ),
        (
            True,
            True,
            'simple_rule_with_branding.json',
            'expected_simple_rule_branding_db_full.json',
            'expected_simple_rule_branding.json',
        ),
    ],
)
async def test_branding(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        has_lightbox,
        has_sticker,
        rules,
        expected_db,
        expected,
):
    await common_test(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        ['eco'],
        ['moscow'],
        50,
        has_lightbox,
        has_sticker,
        rules,
        expected_db,
        expected,
        ['branding'],
    )


@pytest.mark.parametrize('use_bulk_match', ['disabled', 'enabled'])
@pytest.mark.now('2021-02-01T12:00:00+0300')
async def test_schedule_item_boundaries(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
):
    await common_test(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        ['eco'],
        ['moscow'],
        50,
        True,
        True,
        'every_day_rule.json',
        'expected_every_day_rule_db.json',
        'expected_every_day_rule_3_6.json',
        ['activity'],
        '2021-02-03T12:00:00+0300',
        '2021-02-06T12:00:00+0300',
    )

    await common_test(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        ['eco'],
        ['moscow'],
        50,
        True,
        True,
        'every_day_rule.json',
        'expected_every_day_rule_db.json',
        'expected_every_day_rule_5_8.json',
        ['activity'],
        '2021-02-05T12:00:00+0300',
        '2021-02-08T12:00:00+0300',
    )

    await common_test(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        ['eco'],
        ['moscow'],
        50,
        True,
        True,
        'every_day_rule.json',
        'expected_every_day_rule_db.json',
        'expected_every_day_rule_month.json',
        ['activity'],
        '2021-02-02T12:00:00+0300',
        '2021-03-07T12:00:00+0300',
    )


@pytest.mark.parametrize('use_bulk_match', ['disabled', 'enabled'])
async def test_tags(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
):
    await common_test(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        ['eco'],
        ['moscow'],
        50,
        True,
        True,
        'simple_rule.json',
        'expected_simple_rule_db_tags.json',
        'expected_simple_rule.json',
        [],
        start='2021-02-01T12:00:00+0300',
        end='2021-02-06T12:00:00+0300',
        check_bsx_calls_count=False,
        tags=[],
    )

    assert bsx.rules_select.times_called == 2

    await common_test(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        ['eco'],
        ['moscow'],
        50,
        True,
        True,
        'simple_rule_3.json',
        'expected_simple_rule_db_tags_2.json',
        'expected_simple_rule_3.json',
        [],
        start='2021-02-01T12:00:00+0300',
        end='2021-02-06T12:00:00+0300',
        check_bsx_calls_count=False,
        tags=['t1'],
    )

    assert bsx.rules_select.times_called == 6


@pytest.mark.parametrize('use_bulk_match', ['disabled', 'enabled'])
@pytest.mark.now('2021-02-01T12:00:00+0300')
async def test_schedule_read_past(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
):
    await common_test(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        ['eco'],
        ['moscow'],
        50,
        True,
        True,
        'every_day_rule.json',
        'expected_every_day_rule_7_db.json',
        'expected_every_day_rule_8_9.json',
        ['activity'],
        '2021-02-08T12:00:00+0300',
        '2021-02-09T12:00:00+0300',
    )

    await common_test(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        ['eco'],
        ['moscow'],
        50,
        True,
        True,
        'simple_rule.json',
        'expected_every_day_rule_8_9_updated_db.json',
        'expected_simple_rule.json',
        ['activity'],
        '2021-02-03T12:00:00+0300',
        '2021-02-06T12:00:00+0300',
        False,
    )

    await common_test(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        ['eco'],
        ['moscow'],
        50,
        True,
        True,
        'simple_rule.json',
        'expected_every_day_rule_8_9_updated_db.json',
        'expected_every_day_rule_8_9.json',
        ['activity'],
        '2021-02-08T12:00:00+0300',
        '2021-02-09T12:00:00+0300',
        False,
    )


@pytest.mark.parametrize('use_bulk_match', ['disabled', 'enabled'])
@pytest.mark.now('2021-02-01T12:00:00+0300')
async def test_schedule_boundaries(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
):
    await common_test(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        ['eco'],
        ['moscow'],
        50,
        True,
        True,
        'simple_rule_2.json',
        'expected_simple_rule_2_offseted_db.json',
        'expected_simple_rule_2_offseted.json',
        ['activity'],
        '2021-02-03T12:00:00+0300',
        '2021-02-06T12:00:00+0300',
    )

    await common_test(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        ['eco'],
        ['moscow'],
        50,
        True,
        True,
        'simple_rule_2.json',
        'expected_simple_rule_2_offseted_db.json',
        'expected_simple_rule_2_offseted.json',
        ['activity'],
        '2021-02-01T12:00:00+0300',
        '2021-02-06T12:00:00+0300',
    )

    await common_test(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        ['eco'],
        ['moscow'],
        50,
        True,
        True,
        'simple_rule_2.json',
        'expected_simple_rule_2_offseted_snd_db.json',
        'expected_simple_rule_2_offseted_snd.json',
        ['activity'],
        '2021-02-02T12:00:00+0300',
        '2021-03-09T12:00:00+0300',
        False,
    )


@pytest.mark.parametrize('use_bulk_match', ['disabled', 'enabled'])
@pytest.mark.now('2021-02-01T12:00:00+0300')
@pytest.mark.parametrize(
    'expected_request',
    [
        {
            'activity_points': 0,
            'geoareas': [],
            'has_lightbox': True,
            'has_sticker': True,
            'reference_time': '2021-01-31T21:00:00+00:00',
            'tags': ['t1', 't2'],
            'tariff_class': 'eco',
            'zone': 'moscow',
            'geonode': (
                'br_root/br_russia/br_tsentralnyj_fo/'
                'br_moskovskaja_obl/br_moscow/br_moscow_adm'
            ),
            'timezone': 'Europe/Moscow',
            'rule_types': ['single_ride'],
        },
    ],
)
@pytest.mark.config(SCHEDULE_MATCHER_SETTINGS={'rules_select_limit': 99})
async def test_check_bsx_calls(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        expected_request,
):
    await common_test(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        ['eco'],
        ['moscow'],
        50,
        True,
        True,
        'simple_rule.json',
        'expected_simple_rule_db.json',
        'expected_simple_rule.json',
        ['activity'],
        '2021-02-01T12:00:00+0300',
        '2021-02-06T12:00:00+0300',
        True,
    )

    if use_bulk_match == 'disabled':
        assert bsx.match.times_called == 1
        for _ in range(0, bsx.match.times_called):
            assert (
                bsx.match.next_call()['request_data'].json == expected_request
            )
    elif use_bulk_match == 'enabled':
        expected_request['reference_times'] = [
            expected_request['reference_time'],
        ]
        expected_request.pop('reference_time')
        expected_request.pop('rule_types')
        expected_request.pop('geonode')
        assert bsx.bulk_match.times_called == 1
        for _ in range(0, bsx.bulk_match.times_called):
            assert (
                bsx.bulk_match.next_call()['request_data'].json
                == expected_request
            )

    expected_rules_select = [
        {
            'limit': 99,
            'rule_types': ['single_ride'],
            'tags_constraint': {'tags': ['t1', 't2']},
            'tariff_classes': ['eco'],
            'time_range': {
                'end': '2021-02-07T21:00:00+00:00',
                'start': '2021-01-31T21:00:00+00:00',
            },
            'zones': ['moscow'],
        },
        {
            'cursor': '99',
            'limit': 99,
            'rule_types': ['single_ride'],
            'tags_constraint': {'tags': ['t1', 't2']},
            'tariff_classes': ['eco'],
            'time_range': {
                'end': '2021-02-07T21:00:00+00:00',
                'start': '2021-01-31T21:00:00+00:00',
            },
            'zones': ['moscow'],
        },
        {
            'limit': 99,
            'rule_types': ['single_ride'],
            'tags_constraint': {'has_tag': False},
            'tariff_classes': ['eco'],
            'time_range': {
                'end': '2021-02-07T21:00:00+00:00',
                'start': '2021-01-31T21:00:00+00:00',
            },
            'zones': ['moscow'],
        },
        {
            'cursor': '99',
            'limit': 99,
            'rule_types': ['single_ride'],
            'tags_constraint': {'has_tag': False},
            'tariff_classes': ['eco'],
            'time_range': {
                'end': '2021-02-07T21:00:00+00:00',
                'start': '2021-01-31T21:00:00+00:00',
            },
            'zones': ['moscow'],
        },
    ]

    assert bsx.rules_select.times_called == len(expected_rules_select)
    select_calls = [
        bsx.rules_select.next_call()['request_data'].json
        for _ in range(0, bsx.rules_select.times_called)
    ]

    def _sort_lambda(x):
        return (1 if 'cursor' in x else 0) + (
            4 if 'has_tag' in x['tags_constraint'] else 2
        )

    select_calls.sort(key=_sort_lambda)
    expected_rules_select.sort(key=_sort_lambda)
    assert select_calls == expected_rules_select


@pytest.mark.parametrize('use_bulk_match', ['disabled', 'enabled'])
@pytest.mark.now('2021-02-01T12:00:00+0300')
async def test_check_match_errors(
        taxi_subvention_schedule, use_bulk_match, load_json, bsx,
):
    request = {
        'types': ['single_ride'],
        'ignored_restrictions': [],
        'time_range': {
            'from': '2021-02-01T12:00:00+0300',
            'to': '2021-02-06T12:00:00+0300',
        },
        'activity_points': 43,
        'branding': {'has_lightbox': True, 'has_sticker': True},
        'tags': [],
        'tariff_classes': ['eco'],
        'zones': ['msc'],
    }

    bsx.set_rules(load_json('simple_rule.json')['rules'])
    if use_bulk_match == 'disabled':
        bsx.set_match_throws(True)
    elif use_bulk_match == 'enabled':
        bsx.set_bulk_match_throws(True)

    response = await taxi_subvention_schedule.post(
        '/internal/subvention-schedule/v1/schedule', json=request,
    )

    assert response.status_code == 500


@pytest.mark.parametrize('use_bulk_match', ['disabled', 'enabled'])
@pytest.mark.now('2021-02-01T12:00:00+0300')
@pytest.mark.parametrize(
    'classes, zones, original_db, expected, start, end',
    [
        (
            ['eco'],
            ['moscow'],
            'expected_simple_rule_db_closed_rule.json',
            'expected_simple_rule_closed.json',
            '2021-02-03T12:00:00+0300',
            '2021-02-07T12:00:00+0300',
        ),
        (
            ['eco'],
            ['moscow'],
            'expected_simple_rule_db_multiple_batches.json',
            'expected_multiple_batches.json',
            '2021-07-14T18:47:07+0000',
            '2021-07-18T21:00:00+0000',
        ),
        (
            ['eco'],
            ['moscow'],
            'mid_week_update_db.json',
            'expected_empty.json',
            '2021-07-20T18:47:07+0000',
            '2021-07-25T21:00:00+0000',
        ),
    ],
)
async def test_predefined_schedule(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        classes,
        zones,
        original_db,
        expected,
        start,
        end,
):
    utils.load_db(pgsql, load_json(original_db))
    await common_test(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        classes,
        zones,
        50,
        True,
        True,
        None,
        original_db,
        expected,
        ['activity'],
        start,
        end,
        False,
    )


@pytest.mark.parametrize('use_bulk_match', ['disabled', 'enabled'])
@pytest.mark.now('2021-02-01T12:00:00+0300')
@pytest.mark.parametrize(
    'classes, zones, original_db,expected_db, expected, start, end',
    [
        (
            ['eco'],
            ['moscow'],
            'partial_schedule_db.json',
            'partial_schedule_db_expected.json',
            'partial_schedule_expected.json',
            '2021-07-19T18:47:07+0000',
            '2021-07-25T21:00:00+0000',
        ),
    ],
)
@pytest.mark.config(ROUND_TIME_RANGE_TO_DAYS_IN_HANDLE=True)
async def test_partial_week_schedule(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
        pgsql,
        load_json,
        bsx,
        classes,
        zones,
        original_db,
        expected_db,
        expected,
        start,
        end,
):
    utils.load_db(pgsql, load_json(original_db))
    await common_test(
        taxi_subvention_schedule,
        experiments3,
        use_bulk_match,
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
        expected,
        ['activity'],
        start,
        end,
        False,
    )


@pytest.mark.now('2021-02-01T12:00:00+0300')
@pytest.mark.parametrize('do_preload', [True, False])
@pytest.mark.parametrize('do_throw', [True, False])
@pytest.mark.parametrize(
    'classes, zones, preload_db, expected, start, end',
    [
        (
            ['eco'],
            ['moscow'],
            'expected_simple_rule_2_db.json',
            'expected_simple_rule_2_two_weeks.json',
            '2021-02-03T12:00:00+0300',
            '2021-02-09T12:00:00+0300',
        ),
    ],
)
async def test_override_fallback(
        taxi_subvention_schedule,
        testpoint,
        pgsql,
        load_json,
        taxi_config,
        bsx,
        do_preload,
        do_throw,
        classes,
        zones,
        preload_db,
        expected,
        start,
        end,
):
    taxi_config.set(REQUIRE_DESCRIPTORS_SAVE_IN_HANDLE=do_throw)

    @testpoint('testpoint::handle::pre_save')
    def pre_save_point(data):
        if not hasattr(pre_save_point, 'already_preloaded'):
            pre_save_point.already_preloaded = 0

        if do_preload and not pre_save_point.already_preloaded:
            pre_save_point.already_preloaded = True
            utils.load_db(pgsql, load_json(preload_db))

    expected_code = 200
    if do_preload and do_throw:
        expected_code = 500

    bsx.reset()
    request = {
        'types': ['single_ride'],
        'ignored_restrictions': ['activity'],
        'time_range': {'from': start, 'to': end},
        'activity_points': 50,
        'branding': {'has_lightbox': True, 'has_sticker': True},
        'tags': ['t1', 't2'],
        'tariff_classes': classes,
        'zones': zones,
    }

    bsx_rules = load_json('simple_rule_2.json')['rules']
    bsx.set_rules(bsx_rules)

    response = await taxi_subvention_schedule.post(
        '/internal/subvention-schedule/v1/schedule', json=request,
    )

    assert response.status_code == expected_code

    if expected_code == 200:
        assert utils.sort_response(response.json()) == utils.sort_response(
            load_json(expected),
        )

    assert pre_save_point.times_called > 0
