import datetime

import psycopg2
import pytest


@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'tariffs.sql', 'rules.sql'],
)
async def test_classification_rule_update(taxi_classifier, pgsql):
    response = await taxi_classifier.put(
        '/v1/classifiers/tariffs/classification-rules',
        params={'rule_id': '1'},
        json={
            'is_allowing': True,
            'price_from': 2000,
            'price_to': 3000,
            'year_from': 1995,
            'year_to': 1997,
            'vehicle_before': '2019-06-12T00:00:00+00:00',
            'started_at': '2010-06-12T00:00:00+00:00',
        },
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'is_allowing': True,
        'price_from': 2000,
        'price_to': 3000,
        'rule_id': '1',
        'started_at': '2010-06-12T00:00:00+00:00',
        'vehicle_before': '2019-06-12T00:00:00+00:00',
        'year_from': 1995,
        'year_to': 1997,
    }

    cursor = pgsql['classifier'].cursor()
    cursor.execute(
        (
            f'SELECT classifier_id, tariff_id, is_allowing, '
            f'brand, model, price_from, price_to, year_from, year_to, '
            f'vehicle_before, started_at, ended_at '
            f'FROM classifier.rules '
            f'WHERE id = 1;'
        ),
    )

    assert cursor.fetchall() == [
        (
            'classifier_id_1',
            'tariff_id_1',
            True,
            None,
            None,
            2000,
            3000,
            1995,
            1997,
            datetime.datetime(
                2019,
                6,
                12,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            datetime.datetime(
                2010,
                6,
                12,
                4,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=240, name=None),
            ),
            None,
        ),
    ]


@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'tariffs.sql', 'rules.sql'],
)
async def test_classification_rule_not_found(taxi_classifier, pgsql):
    response = await taxi_classifier.put(
        '/v1/classifiers/tariffs/classification-rules',
        params={'rule_id': '228'},
        json={
            'is_allowing': True,
            'price_from': 2000,
            'price_to': 3000,
            'year_from': 1995,
            'year_to': 1997,
            'vehicle_before': '2019-06-12T00:00:00+00:00',
            'started_at': '2010-06-12T00:00:00+00:00',
        },
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'rule_not_found',
        'message': 'Rule with id 228 was not found',
    }

    cursor = pgsql['classifier'].cursor()
    cursor.execute(
        (
            f'SELECT classifier_id, tariff_id, is_allowing, '
            f'brand, model, price_from, price_to, year_from, year_to, '
            f'vehicle_before, started_at, ended_at '
            f'FROM classifier.rules '
            f'WHERE id = 228;'
        ),
    )

    assert cursor.fetchall() == []


@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'tariffs.sql', 'rules.sql'],
)
@pytest.mark.parametrize(
    ['request_rule', 'expected_response'],
    [
        (
            {'is_allowing': True, 'model': 'A6'},
            {
                'code': 'incomplete_brand_model',
                'message': (
                    'Both brand and model must be set if one of them is setted'
                ),
            },
        ),
        (
            {'is_allowing': True, 'price_from': 5000, 'price_to': 1000},
            {
                'code': 'invalid_price_range',
                'message': 'price_from must be less or equal than price_to',
            },
        ),
        (
            {'is_allowing': True, 'year_from': 2020, 'year_to': 1990},
            {
                'code': 'invalid_year_range',
                'message': 'year_from must be less or equal than year_to',
            },
        ),
        (
            {'is_allowing': True, 'started_at': '2020-05-19T01:00:00+00:00'},
            {
                'code': 'empty_limiting_fields',
                'message': 'At least one limiting field must be present',
            },
        ),
        (
            {
                'is_allowing': True,
                'price_from': 1000,
                'started_at': '2020-05-19T01:00:00+00:00',
            },
            {
                'code': 'invalid_date_format',
                'message': 'Timestamps must be in date format',
            },
        ),
        (
            {'is_allowing': True, 'brand': 'Audi*', 'model': 'A8'},
            {
                'code': 'invalid_brand',
                'message': 'Brand must not contain `*`, got: Audi*',
            },
        ),
        (
            {'is_allowing': True, 'brand': 'Audi', 'model': 'A*8'},
            {
                'code': 'invalid_stared_model',
                'message': (
                    'Model can contain `*` only in the last position'
                    ', got: A*8'
                ),
            },
        ),
        (
            {
                'is_allowing': True,
                'brand': 'Audi',
                'model': 'A8',
                'started_at': '2020-05-19T00:00:00+00:00',
                'ended_at': '2019-05-19T00:00:00+00:00',
            },
            {
                'code': 'invalid_validity_range',
                'message': 'started_at date must be less than ended_at date',
            },
        ),
    ],
)
async def test_bad_request(taxi_classifier, request_rule, expected_response):
    response = await taxi_classifier.put(
        '/v1/classifiers/tariffs/classification-rules',
        params={'rule_id': '1'},
        json=request_rule,
    )

    assert response.status_code == 400, response.text
    assert response.json() == expected_response
