import pytest

from testsuite.utils import ordered_object


def _starts_at():
    return '2020-05-01T21:00:00+00:00'


def _ends_at():
    return '2020-05-30T21:00:00+00:00'


def _make_query(
        has_tag=None,
        tags=None,
        tariff_classes=None,
        zones=None,
        geoareas=None,
        has_geoarea=None,
        geoareas_constraint=None,
        starts_at=_starts_at(),
        ends_at=_ends_at(),
        branding=None,
        limit=1000,
        cursor=None,
        rule_types=None,
        drivers=None,
        schedule_ref=None,
        schedules=None,
        window=None,
        stop_tags_constraint=None,
):
    query = {
        'time_range': {'start': starts_at, 'end': ends_at},
        'limit': limit,
    }
    if tariff_classes:
        query['tariff_classes'] = tariff_classes
    if zones:
        query['zones'] = zones
    if geoareas:
        query['geoareas'] = geoareas
    if cursor:
        query['cursor'] = cursor
    if has_tag is not None or tags:
        if has_tag is not None:
            query['tags_constraint'] = {'has_tag': has_tag}
        else:
            query['tags_constraint'] = {'tags': tags}
    if has_geoarea is not None or geoareas_constraint:
        if has_geoarea is not None:
            query['geoareas_constraint'] = {'has_geoarea': has_geoarea}
        else:
            query['geoareas_constraint'] = {'geoareas': geoareas_constraint}
    if branding:
        query['branding'] = branding
    if rule_types:
        query['rule_types'] = rule_types
    if drivers is not None:
        query['drivers'] = drivers
    if schedule_ref is not None:
        query['schedule_ref'] = schedule_ref
    if schedules is not None:
        query['schedules'] = schedules
    if window is not None:
        query['window_size'] = window
    if stop_tags_constraint is not None:
        query['stop_tags_constraint'] = stop_tags_constraint
    return query


ALL_RULES = [
    '1abf062a-b607-11ea-998e-07e60204cbcf',
    '2abf062a-b607-11ea-998e-07e60204cbcf',
    '3abf062a-b607-11ea-998e-07e60204cbcf',
    '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
    'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
    '5e03538d-740b-4e0b-b5f4-1425efa59319',
]

PERSONAL_RULES = ['9b8e51df-faa7-4b65-9012-f2107061849e']


async def _check_selected_rules(taxi_billing_subventions_x, query, expected):
    response = await taxi_billing_subventions_x.post(
        '/v2/rules/by_filters', query,
    )
    assert response.status_code == 200, response.json()
    rules = [rule['id'] for rule in response.json()['rules']]
    ordered_object.assert_eq(rules, expected, '')


@pytest.mark.parametrize(
    'starts_at, ends_at, expected_rules',
    [
        (_starts_at(), _ends_at(), ALL_RULES),
        ('2020-04-01T21:00:00+00:00', '2020-05-01T20:59:00+00:00', []),
        ('2020-05-30T21:01:00+00:00', '2020-06-01T20:59:00+00:00', []),
    ],
)
async def test_v2_rules_by_filters_time_range(
        taxi_billing_subventions_x, starts_at, ends_at, expected_rules,
):
    await _check_selected_rules(
        taxi_billing_subventions_x,
        _make_query(starts_at=starts_at, ends_at=ends_at),
        expected_rules,
    )


@pytest.mark.parametrize(
    'tags, has_tag, expected_rules',
    [
        (['some_tag'], None, ['2abf062a-b607-11ea-998e-07e60204cbcf']),
        (['not_existed_tag'], None, []),
        (
            None,
            True,
            [
                '2abf062a-b607-11ea-998e-07e60204cbcf',
                '5e03538d-740b-4e0b-b5f4-1425efa59319',
            ],
        ),
        (
            None,
            False,
            [
                '1abf062a-b607-11ea-998e-07e60204cbcf',
                '3abf062a-b607-11ea-998e-07e60204cbcf',
                '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
                'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            ],
        ),
    ],
)
async def test_v2_rules_by_filters_tags(
        taxi_billing_subventions_x, tags, has_tag, expected_rules,
):
    await _check_selected_rules(
        taxi_billing_subventions_x,
        _make_query(tags=tags, has_tag=has_tag),
        expected_rules,
    )


@pytest.mark.parametrize(
    'geoareas, expected_rules',
    [
        (['not_existed_geoarea'], []),
        (
            ['butovo'],
            [
                '3abf062a-b607-11ea-998e-07e60204cbcf',
                '5e03538d-740b-4e0b-b5f4-1425efa59319',
            ],
        ),
        (['sviblovo'], ['1abf062a-b607-11ea-998e-07e60204cbcf']),
        (
            ['sviblovo', 'butovo'],
            [
                '1abf062a-b607-11ea-998e-07e60204cbcf',
                '3abf062a-b607-11ea-998e-07e60204cbcf',
                '5e03538d-740b-4e0b-b5f4-1425efa59319',
            ],
        ),
    ],
)
async def test_v2_rules_by_filters_geoareas_constraint(
        taxi_billing_subventions_x, geoareas, expected_rules,
):
    await _check_selected_rules(
        taxi_billing_subventions_x,
        _make_query(geoareas_constraint=geoareas),
        expected_rules,
    )


@pytest.mark.parametrize(
    'has_geoarea,expected_rules',
    (
        (
            False,
            [
                '2abf062a-b607-11ea-998e-07e60204cbcf',
                '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
                'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            ],
        ),
        (
            True,
            [
                '1abf062a-b607-11ea-998e-07e60204cbcf',
                '3abf062a-b607-11ea-998e-07e60204cbcf',
                '5e03538d-740b-4e0b-b5f4-1425efa59319',
            ],
        ),
    ),
)
async def test_v2_rules_by_filters_has_geoarea(
        taxi_billing_subventions_x, has_geoarea, expected_rules,
):
    await _check_selected_rules(
        taxi_billing_subventions_x,
        _make_query(has_geoarea=has_geoarea),
        expected_rules,
    )


@pytest.mark.parametrize(
    'zones, expected_rules',
    [
        (['not_existed_zone'], []),
        (['moscow', 'moscow_center'], ALL_RULES),
        (
            ['moscow'],
            [
                '1abf062a-b607-11ea-998e-07e60204cbcf',
                '2abf062a-b607-11ea-998e-07e60204cbcf',
                'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            ],
        ),
        (
            ['moscow_center'],
            [
                '3abf062a-b607-11ea-998e-07e60204cbcf',
                '5e03538d-740b-4e0b-b5f4-1425efa59319',
                '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
            ],
        ),
    ],
)
async def test_v2_rules_by_filters_zones(
        taxi_billing_subventions_x, zones, expected_rules,
):
    await _check_selected_rules(
        taxi_billing_subventions_x, _make_query(zones=zones), expected_rules,
    )


@pytest.mark.parametrize(
    'tariff_classes, expected_rules',
    [
        (['not_existed_tariff'], []),
        (
            ['econom'],
            [
                '2abf062a-b607-11ea-998e-07e60204cbcf',
                '5e03538d-740b-4e0b-b5f4-1425efa59319',
                '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
            ],
        ),
        (['econom', 'comfort', 'comfort_plus'], ALL_RULES),
        (
            ['comfort'],
            [
                '3abf062a-b607-11ea-998e-07e60204cbcf',
                'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            ],
        ),
        (['comfort_plus'], ['1abf062a-b607-11ea-998e-07e60204cbcf']),
    ],
)
async def test_v2_rules_by_filters_tariffs(
        taxi_billing_subventions_x, tariff_classes, expected_rules,
):
    await _check_selected_rules(
        taxi_billing_subventions_x,
        _make_query(tariff_classes=tariff_classes),
        expected_rules,
    )


@pytest.mark.parametrize(
    'branding, expected_rules',
    [
        (
            ['any_branding'],
            [
                '1abf062a-b607-11ea-998e-07e60204cbcf',
                '3abf062a-b607-11ea-998e-07e60204cbcf',
                '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
            ],
        ),
        (['no_full_branding'], []),
        (
            ['sticker', 'no_full_branding'],
            [
                '2abf062a-b607-11ea-998e-07e60204cbcf',
                '5e03538d-740b-4e0b-b5f4-1425efa59319',
            ],
        ),
        (
            ['sticker_and_lightbox', 'no_full_branding'],
            ['cf730f12-c02b-11ea-acc8-ab6ac87f7711'],
        ),
        (
            ['sticker_and_lightbox', 'sticker'],
            [
                '2abf062a-b607-11ea-998e-07e60204cbcf',
                '5e03538d-740b-4e0b-b5f4-1425efa59319',
                'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            ],
        ),
    ],
)
async def test_v2_rules_by_filters_branding(
        taxi_billing_subventions_x, branding, expected_rules,
):
    await _check_selected_rules(
        taxi_billing_subventions_x,
        _make_query(branding=branding),
        expected_rules,
    )


@pytest.mark.parametrize(
    'rule_types, expected_rules',
    [
        (['single_ride', 'goal'], ALL_RULES),
        (
            ['single_ride'],
            [
                '1abf062a-b607-11ea-998e-07e60204cbcf',
                '2abf062a-b607-11ea-998e-07e60204cbcf',
                '3abf062a-b607-11ea-998e-07e60204cbcf',
                '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
                'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            ],
        ),
        (['goal'], ['5e03538d-740b-4e0b-b5f4-1425efa59319']),
    ],
)
async def test_v2_rules_by_filters_rule_type(
        taxi_billing_subventions_x, rule_types, expected_rules,
):
    await _check_selected_rules(
        taxi_billing_subventions_x,
        _make_query(rule_types=rule_types),
        expected_rules,
    )


@pytest.mark.parametrize(
    'cursor, next_cursor, expected_rules',
    [
        (
            None,
            '5e03538d-740b-4e0b-b5f4-1425efa59319',
            [
                '1abf062a-b607-11ea-998e-07e60204cbcf',
                '2abf062a-b607-11ea-998e-07e60204cbcf',
                '3abf062a-b607-11ea-998e-07e60204cbcf',
                '5e03538d-740b-4e0b-b5f4-1425efa59319',
            ],
        ),
        (
            '5e03538d-740b-4e0b-b5f4-1425efa59319',
            None,
            [
                '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
                'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            ],
        ),
    ],
)
async def test_v2_rules_by_filters_cursor(
        taxi_billing_subventions_x, cursor, next_cursor, expected_rules,
):
    limit = 4
    response = await taxi_billing_subventions_x.post(
        '/v2/rules/by_filters', _make_query(cursor=cursor, limit=limit),
    )
    data = response.json()
    assert response.status_code == 200, data
    assert [r['id'] for r in data['rules']] == expected_rules
    assert data.get('next_cursor') == next_cursor


@pytest.mark.parametrize(
    'drivers, expected_rules',
    [
        (None, ALL_RULES),
        ([], []),
        (['b99ae51d-0674-458f-8c69-89fc4bfb8174'], []),
        (['2fa69ea2-8d53-4b24-ae78-a02d795f5d9d'], PERSONAL_RULES),
    ],
)
async def test_v2_rules_by_filters_drivers(
        taxi_billing_subventions_x, drivers, expected_rules,
):
    await _check_selected_rules(
        taxi_billing_subventions_x,
        _make_query(drivers=drivers),
        expected_rules,
    )


@pytest.mark.parametrize(
    'schedule_ref,drivers,expected_rules',
    (
        (None, None, ALL_RULES),
        (
            'single_ride_schedule_ref',
            None,
            [
                '2abf062a-b607-11ea-998e-07e60204cbcf',
                'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            ],
        ),
        ('goal_schedule_ref', None, ['5e03538d-740b-4e0b-b5f4-1425efa59319']),
        ('personal_goal_schedule_ref', None, []),
        (
            'personal_goal_schedule_ref',
            ['2fa69ea2-8d53-4b24-ae78-a02d795f5d9d'],
            ['9b8e51df-faa7-4b65-9012-f2107061849e'],
        ),
    ),
)
async def test_v2_rules_by_filters_schedule_ref(
        taxi_billing_subventions_x, schedule_ref, drivers, expected_rules,
):
    await _check_selected_rules(
        taxi_billing_subventions_x,
        _make_query(schedule_ref=schedule_ref, drivers=drivers),
        expected_rules,
    )


@pytest.mark.parametrize(
    'schedules,expected_rules',
    (
        (None, ALL_RULES),
        ([], []),
        (
            ['single_ride_schedule_ref', 'goal_schedule_ref'],
            [
                '2abf062a-b607-11ea-998e-07e60204cbcf',
                'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
                '5e03538d-740b-4e0b-b5f4-1425efa59319',
            ],
        ),
    ),
)
async def test_v2_rules_by_filters_schedules(
        taxi_billing_subventions_x, schedules, expected_rules,
):
    await _check_selected_rules(
        taxi_billing_subventions_x,
        _make_query(schedules=schedules),
        expected_rules,
    )


@pytest.mark.parametrize(
    'constraint, expected_rules',
    (
        (
            {'has_tag': False},
            [
                '1abf062a-b607-11ea-998e-07e60204cbcf',
                '2abf062a-b607-11ea-998e-07e60204cbcf',
                '3abf062a-b607-11ea-998e-07e60204cbcf',
                '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
                'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            ],
        ),
        ({'has_tag': True}, ['5e03538d-740b-4e0b-b5f4-1425efa59319']),
        ({'tags': ['stop_goal']}, ['5e03538d-740b-4e0b-b5f4-1425efa59319']),
        ({'tags': ['unknown_tag']}, []),
    ),
)
async def test_v2_rules_by_filters_stop_tags(
        taxi_billing_subventions_x, constraint, expected_rules,
):
    await _check_selected_rules(
        taxi_billing_subventions_x,
        _make_query(stop_tags_constraint=constraint),
        expected_rules,
    )


async def test_v2_rules_by_filters_notify_absent_zones(
        taxi_billing_subventions_x,
):
    query = _make_query(zones=None)
    async with taxi_billing_subventions_x.capture_logs() as logs:
        response = await taxi_billing_subventions_x.post(
            '/v2/rules/by_filters', query,
        )
    assert response.status == 200, response.json()
    expected = logs.select(level='INFO', text='"zones" not set in request')
    assert expected


@pytest.mark.parametrize(
    'window, expected_rules',
    [
        (None, ALL_RULES),
        (14, []),
        (7, ['5e03538d-740b-4e0b-b5f4-1425efa59319']),
    ],
)
async def test_v2_rules_by_filters_window_size(
        taxi_billing_subventions_x, window, expected_rules,
):
    await _check_selected_rules(
        taxi_billing_subventions_x, _make_query(window=window), expected_rules,
    )


@pytest.fixture(autouse=True)
def _fill_db(a_single_ride, a_goal, create_rules):
    create_rules(
        a_single_ride(
            id='2abf062a-b607-11ea-998e-07e60204cbcf',
            tag='some_tag',
            branding='sticker',
            points=60,
            schedule_ref='single_ride_schedule_ref',
        ),
        a_single_ride(
            id='cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            tariff_class='comfort',
            branding='full_branding',
            points=70,
            schedule_ref='single_ride_schedule_ref',
        ),
        a_single_ride(
            id='7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
            tariff_zone='moscow_center',
        ),
        a_single_ride(
            id='1abf062a-b607-11ea-998e-07e60204cbcf',
            tariff_class='comfort_plus',
            geoarea='sviblovo',
        ),
        a_single_ride(
            id='3abf062a-b607-11ea-998e-07e60204cbcf',
            tariff_zone='moscow_center',
            tariff_class='comfort',
            geoarea='butovo',
        ),
        a_goal(
            id='5e03538d-740b-4e0b-b5f4-1425efa59319',
            geonode='moscow_center',
            tag='tag',
            geoarea='butovo',
            branding='sticker',
            stop_tag='stop_goal',
            points=30,
            schedule_ref='goal_schedule_ref',
        ),
        a_goal(
            id='9b8e51df-faa7-4b65-9012-f2107061849e',
            geonode='moscow_center',
            tag='tag',
            geoarea='butovo',
            branding='sticker',
            points=30,
            unique_driver_id='2fa69ea2-8d53-4b24-ae78-a02d795f5d9d',
            schedule_ref='personal_goal_schedule_ref',
        ),
    )
