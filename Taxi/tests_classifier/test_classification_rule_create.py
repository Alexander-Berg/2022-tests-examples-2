import datetime

import psycopg2
import pytest


@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'tariffs.sql', 'rules.sql'],
)
async def test_classification_rule_create(taxi_classifier, pgsql):
    response = await taxi_classifier.post(
        '/v1/classifiers/tariffs/classification-rules',
        params={'classifier_id': 'classifier_id_1', 'tariff_id': 'econom'},
        headers={'X-Idempotency-Token': '123abcdiuianidnsaindsiadn'},
        json={
            'is_allowing': True,
            'brand': 'Audi',
            'model': 'A6',
            'year_from': 1995,
            'year_to': 1997,
            'vehicle_before': '2019-06-12T00:00:00+00:00',
            'started_at': '2010-06-12T00:00:00+00:00',
            'ended_at': '2015-01-01T00:00:00+00:00',
        },
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'brand': 'Audi',
        'ended_at': '2015-01-01T00:00:00+00:00',
        'is_allowing': True,
        'model': 'A6',
        'rule_id': '8',
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
            f'WHERE classifier_id = \'classifier_id_1\' '
            f'AND tariff_id = \'econom\''
        ),
    )

    assert cursor.fetchall() == [
        (
            'classifier_id_1',
            'econom',
            True,
            'Audi',
            'A6',
            None,
            None,
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
            datetime.datetime(
                2015,
                1,
                1,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
        ),
    ]


@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'tariffs.sql', 'rules.sql'],
)
async def test_idempotency_token_exists(taxi_classifier, pgsql):
    cursor = pgsql['classifier'].cursor()
    cursor.execute(
        """
            INSERT INTO classifier.rules (
                classifier_id,
                tariff_id,
                is_allowing,
                brand,
                model,
                idempotency_token
            )
            VALUES (
                'classifier_id_1',
                'econom',
                FALSE,
                'Audi',
                'A6',
                '123abcdiuianidnsaindsiadn'
            )
            """,
    )

    response = await taxi_classifier.post(
        '/v1/classifiers/tariffs/classification-rules',
        params={'classifier_id': 'classifier_id_1', 'tariff_id': 'econom'},
        headers={'X-Idempotency-Token': '123abcdiuianidnsaindsiadn'},
        json={
            'is_allowing': True,
            'brand': 'Audi',
            'model': 'A6',
            'year_from': 1995,
            'year_to': 1997,
            'vehicle_before': '2019-06-12T00:00:00+00:00',
            'started_at': '2010-06-12T00:00:00+00:00',
            'ended_at': '2015-01-01T00:00:00+00:00',
        },
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'brand': 'Audi',
        'ended_at': '2015-01-01T00:00:00+00:00',
        'is_allowing': True,
        'model': 'A6',
        'rule_id': '8',
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
            f'WHERE classifier_id = \'classifier_id_1\' '
            f'AND tariff_id = \'econom\''
        ),
    )

    assert cursor.fetchall() == [
        (
            'classifier_id_1',
            'econom',
            False,
            'Audi',
            'A6',
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ),
    ]


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
            {'is_allowing': True, 'brand': 'Audi', 'model': 'InvalidModel'},
            {
                'code': 'invalid_model',
                'message': (
                    'Can\'t find model `InvalidModel` in auto_dictionary'
                ),
            },
        ),
        (
            {'is_allowing': True, 'brand': 'Audi', 'model': 'A*8'},
            {
                'code': 'invalid_stared_model',
                'message': (
                    'Model can contain `*` only in the last position, got: A*8'
                ),
            },
        ),
    ],
)
async def test_bad_request(taxi_classifier, request_rule, expected_response):
    response = await taxi_classifier.post(
        '/v1/classifiers/tariffs/classification-rules',
        params={'classifier_id': 'classifier_id_1', 'tariff_id': 'econom'},
        headers={'X-Idempotency-Token': '11231njadskjdnsakjd'},
        json=request_rule,
    )

    assert response.status_code == 400, response.text
    assert response.json() == expected_response
