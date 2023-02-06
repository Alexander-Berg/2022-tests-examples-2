from typing import Dict

import pytest

from testsuite.utils import ordered_object


def _default_time_range():
    return {
        'start': '2020-01-01T19:00:00+03:00',
        'end': '2020-12-01T22:00:00+03:00',
    }


def _zone(name, count, rule_type='single_ride'):
    return _zone_multiple(name, {rule_type: count})


def _zone_multiple(name: str, types: Dict) -> Dict:
    return {
        'zone': name,
        'rules_count_by_type': [
            {'count': count, 'rule_type': rule_type}
            for (rule_type, count) in types.items()
        ],
    }


@pytest.mark.parametrize(
    'time_range,expected',
    (
        (
            _default_time_range(),
            [_zone('moscow_center', 1), _zone('moscow', 2)],
        ),
        (
            {
                'start': '2020-05-01T21:00:00+00:00',
                'end': '2020-05-12T21:00:00+00:00',
            },
            [_zone('moscow', 2)],
        ),
        (
            {
                'start': '2020-05-12T21:00:00+00:00',
                'end': '2020-05-15T21:00:00+00:00',
            },
            [],
        ),
        (
            {
                'start': '2020-05-02T21:00:00+00:00',
                'end': '2020-05-04T21:00:00+00:00',
            },
            [_zone('moscow', 1)],
        ),
    ),
)
async def test_count_filtered_by_time_range(
        taxi_billing_subventions_x, time_range, expected,
):
    query = _make_query(time_range=time_range)
    response = await taxi_billing_subventions_x.post('/v2/rules/count/', query)
    _assert_expected(response, expected)


@pytest.mark.parametrize(
    'zones,expected',
    (
        (None, [_zone('moscow_center', 1), _zone('moscow', 2)]),
        ([], []),
        (['moscow'], [_zone('moscow', 2)]),
        (['moscow_center'], [_zone('moscow_center', 1)]),
    ),
)
async def test_count_filtered_by_tariff_zones(
        taxi_billing_subventions_x, zones, expected,
):
    query = _make_query(zones=zones)
    response = await taxi_billing_subventions_x.post('/v2/rules/count/', query)
    _assert_expected(response, expected)


@pytest.mark.parametrize(
    'tariff_classes,expected',
    (
        (None, [_zone('moscow_center', 1), _zone('moscow', 2)]),
        ([], []),
        (['comfort'], []),
        (['econom'], [_zone('moscow_center', 1), _zone('moscow', 2)]),
    ),
)
async def test_count_filtered_by_tariff_classes(
        taxi_billing_subventions_x, tariff_classes, expected,
):
    query = _make_query(tariff_classes=tariff_classes)
    response = await taxi_billing_subventions_x.post('/v2/rules/count/', query)
    _assert_expected(response, expected)


@pytest.mark.parametrize(
    'brandings,expected',
    (
        (None, [_zone('moscow_center', 1), _zone('moscow', 2)]),
        (['any_branding'], [_zone('moscow_center', 1)]),
        (['sticker'], [_zone('moscow', 1)]),
        (['sticker', 'no_full_branding'], [_zone('moscow', 2)]),
        (['sticker_and_lightbox'], []),
    ),
)
async def test_count_filtered_by_brandings(
        taxi_billing_subventions_x, brandings, expected,
):
    query = _make_query(brandings=brandings)
    response = await taxi_billing_subventions_x.post('/v2/rules/count/', query)
    _assert_expected(response, expected)


@pytest.mark.parametrize(
    'geoareas,expected',
    ((['butovo'], [_zone('moscow', 2)]), (['sviblovo'], [])),
)
async def test_count_filtered_by_geoareas_constraint(
        taxi_billing_subventions_x, geoareas, expected,
):
    query = _make_query(geoareas_constraint=geoareas)
    response = await taxi_billing_subventions_x.post('/v2/rules/count/', query)
    _assert_expected(response, expected)


@pytest.mark.parametrize(
    'has_geoarea,expected',
    ((True, [_zone('moscow', 2)]), (False, [_zone('moscow_center', 1)])),
)
async def test_count_filtered_by_has_geoarea(
        taxi_billing_subventions_x, has_geoarea, expected,
):
    query = _make_query(has_geoarea=has_geoarea)
    response = await taxi_billing_subventions_x.post('/v2/rules/count/', query)
    _assert_expected(response, expected)


@pytest.mark.parametrize(
    'has_tag,expected',
    (
        (None, [_zone('moscow_center', 1), _zone('moscow', 2)]),
        (False, [_zone('moscow', 1)]),
        (True, [_zone('moscow_center', 1), _zone('moscow', 1)]),
    ),
)
async def test_count_filtered_by_has_tag(
        taxi_billing_subventions_x, has_tag, expected,
):
    query = _make_query(has_tag=has_tag)
    response = await taxi_billing_subventions_x.post('/v2/rules/count/', query)
    _assert_expected(response, expected)


@pytest.mark.parametrize(
    'tags,expected',
    (
        (None, [_zone('moscow_center', 1), _zone('moscow', 2)]),
        (['tag'], [_zone('moscow', 1)]),
        (['another'], [_zone('moscow_center', 1)]),
    ),
)
async def test_count_filtered_by_tags(
        taxi_billing_subventions_x, tags, expected,
):
    query = _make_query(tags=tags)
    response = await taxi_billing_subventions_x.post('/v2/rules/count/', query)
    _assert_expected(response, expected)


@pytest.mark.parametrize(
    'rule_types,expected',
    (
        (['single_ride'], [_zone('moscow_center', 1), _zone('moscow', 2)]),
        (['goal'], [_zone('br_moscow', 1, 'goal')]),
        (
            ['single_ride', 'goal'],
            [
                _zone('moscow_center', 1),
                _zone('br_moscow', 1, 'goal'),
                _zone('moscow', 2),
            ],
        ),
        (
            ['single_ride', 'goal', 'single_ontop'],
            [
                _zone_multiple(
                    'moscow_center', {'single_ontop': 1, 'single_ride': 1},
                ),
                _zone('br_moscow', 1, 'goal'),
                _zone('moscow', 2),
            ],
        ),
    ),
)
async def test_count_filtered_by_rule_types(
        taxi_billing_subventions_x, rule_types, expected,
):
    query = _make_query(rule_types=rule_types)
    response = await taxi_billing_subventions_x.post('/v2/rules/count/', query)
    _assert_expected(response, expected)


@pytest.mark.parametrize(
    'drivers,expected',
    (
        (
            None,
            [
                _zone('moscow_center', 1),
                _zone('br_moscow', 1, 'goal'),
                _zone('moscow', 2),
            ],
        ),
        ([], []),
        (
            ['2fa69ea2-8d53-4b24-ae78-a02d795f5d9d'],
            [_zone('br_moscow', 1, 'goal')],
        ),
        (['544105d6-eeb2-4e15-afa1-5f795bafbfbf'], []),
    ),
)
async def test_count_filtered_by_drivers(
        taxi_billing_subventions_x, drivers, expected,
):
    query = _make_query(rule_types=['single_ride', 'goal'], drivers=drivers)
    response = await taxi_billing_subventions_x.post('/v2/rules/count/', query)
    _assert_expected(response, expected)


@pytest.mark.parametrize(
    'schedules,expected',
    (
        (
            None,
            [
                _zone_multiple(
                    'moscow_center', {'single_ontop': 1, 'single_ride': 1},
                ),
                _zone('br_moscow', 1, 'goal'),
                _zone('moscow', 2),
            ],
        ),
        ([], []),
        (
            ['schedule_ref_single_ride'],
            [
                _zone('moscow_center', 1, 'single_ride'),
                _zone('moscow', 1, 'single_ride'),
            ],
        ),
        (
            ['schedule_ref_goal', 'schedule_ref_single_ontop'],
            [
                _zone('br_moscow', 1, 'goal'),
                _zone('moscow_center', 1, 'single_ontop'),
            ],
        ),
    ),
)
async def test_count_filtered_by_schedules(
        taxi_billing_subventions_x, schedules, expected,
):
    query = _make_query(
        rule_types=['single_ride', 'goal', 'single_ontop'],
        schedules=schedules,
    )
    response = await taxi_billing_subventions_x.post('/v2/rules/count', query)
    _assert_expected(response, expected)


def _assert_expected(response, expected):
    assert response.status_code == 200
    response_json = response.json()
    ordered_object.assert_eq(
        response_json['rules_count'], expected, ['', 'zone'],
    )


def _make_query(
        brandings=None,
        geoareas=None,
        geoareas_constraint=None,
        rule_types=None,
        tariff_classes=None,
        time_range=None,
        zones=None,
        tags=None,
        has_tag=None,
        has_geoarea=None,
        drivers=None,
        schedules=None,
):
    query = {
        'branding': brandings,
        'rule_types': rule_types or ['single_ride'],
        'time_range': time_range or _default_time_range(),
        'tariff_classes': tariff_classes,
        'zones': zones,
        'geoareas': geoareas,
        'tags_constraint': None,
        'geoareas_constraint': None,
        'drivers': drivers,
        'schedules': schedules,
    }
    if has_tag is not None:
        query['tags_constraint'] = {'has_tag': has_tag}
    elif tags is not None:
        query['tags_constraint'] = {'tags': tags}
    if has_geoarea is not None:
        query['geoareas_constraint'] = {'has_geoarea': has_geoarea}
    elif geoareas_constraint:
        query['geoareas_constraint'] = {'geoareas': geoareas_constraint}
    return {key: value for key, value in query.items() if value is not None}


@pytest.fixture(autouse=True)
def _fill_db(a_single_ride, a_goal, a_single_ontop, create_rules):
    create_rules(
        a_single_ride(
            start='2020-05-01T21:00:00+00:00',
            end='2020-05-02T21:00:00+00:00',
            branding='sticker',
            geoarea='butovo',
            tag='tag',
            schedule_ref='schedule_ref_single_ride',
        ),
        a_single_ride(
            start='2020-05-03T21:00:00+00:00',
            end='2020-05-12T21:00:00+00:00',
            branding='no_full_branding',
            geoarea='butovo',
        ),
        a_single_ride(
            tariff_zone='moscow_center',
            start='2020-05-15T21:00:00+00:00',
            end='2020-05-18T21:00:00+00:00',
            tag='another',
            schedule_ref='schedule_ref_single_ride',
        ),
        a_goal(
            geonode='br_moscow',
            start='2020-04-30T21:00:00+00:00',
            end='2020-05-31T21:00:00+00:00',
            schedule_ref='schedule_ref_goal',
        ),
        a_goal(
            geonode='br_moscow',
            start='2020-04-30T21:00:00+00:00',
            end='2020-05-31T21:00:00+00:00',
            unique_driver_id='2fa69ea2-8d53-4b24-ae78-a02d795f5d9d',
            schedule_ref='schedule_ref_goal',
        ),
        a_single_ontop(
            tariff_zone='moscow_center',
            start='2020-06-15T21:00:00+00:00',
            end='2020-06-18T21:00:00+00:00',
            tag='another',
            schedule_ref='schedule_ref_single_ontop',
        ),
    )
