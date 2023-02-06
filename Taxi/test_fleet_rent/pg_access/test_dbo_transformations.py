import datetime as dt

import pytest

from fleet_rent.pg_access import dbo_transformations


@pytest.mark.parametrize(
    'type_,jsonb',
    [
        ('car', {'car_id': 'sci', 'car_copy_id': 'scci'}),
        ('car', {'car_id': 'sci'}),
        ('other', {'subtype': 'other_subtype', 'description': 'hello'}),
        ('other', {'subtype': 'other_subtype'}),
    ],
)
def test_asset(type_, jsonb):
    parsed = dbo_transformations.deserialize_asset(type_, jsonb)
    rev_t, rev_json = dbo_transformations.serialize_asset(parsed)
    assert rev_t == type_
    assert rev_json == jsonb


@pytest.mark.parametrize(
    'type_,jsonb',
    [
        ('free', None),
        (
            'daily',
            {
                'daily_price': '50.01',
                'total_withhold_limit': '100.02',
                'periodicity': {'type': 'constant', 'params': {}},
                'time': '03:00:00',
            },
        ),
        (
            'daily',
            {
                'daily_price': '50.01',
                'total_withhold_limit': '100.02',
                'periodicity': {
                    'type': 'fraction',
                    'params': {'numerator': 5, 'denominator': 7},
                },
                'time': '03:00:00',
            },
        ),
        (
            'daily',
            {
                'daily_price': '50.01',
                'periodicity': {
                    'type': 'isoweekdays',
                    'params': {'isoweekdays': [1, 5, 7]},
                },
                'time': '03:00:00',
            },
        ),
        (
            'daily',
            {
                'daily_price': '50.01',
                'periodicity': {
                    'type': 'monthdays',
                    'params': {'monthdays': [1, 5, 7, 24]},
                },
                'time': '03:00:00',
            },
        ),
        (
            'daily',
            {
                'daily_price': '50.01',
                'periodicity': {'type': 'constant', 'params': {}},
                'time': '03:00:00',
            },
        ),
        (
            'daily',
            {
                'daily_price': '50.01',
                'time': '16:27:03.123456',
                'periodicity': {'type': 'constant', 'params': {}},
            },
        ),
        (
            'active_days',
            {'daily_price': '50.01', 'total_withhold_limit': '100.02'},
        ),
        ('active_days', {'daily_price': '50.01'}),
    ],
)
def test_charging(type_, jsonb):
    starts_at = dt.datetime(2020, 10, 15, 23, 11, 3, 0, tzinfo=dt.timezone.utc)
    charging = dbo_transformations.deserialize_charging(
        type_, jsonb, starts_at, None,
    )
    rev_t, rev_json = dbo_transformations.serialize_charging(charging)
    assert rev_t == type_
    assert rev_json == jsonb
