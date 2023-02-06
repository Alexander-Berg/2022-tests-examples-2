import datetime

import aiohttp
import psycopg2
import pytest


def make_extra(file_content):
    if not isinstance(file_content, bytes):
        file_content = str(file_content).encode('utf-8')
    with aiohttp.MultipartWriter('form-data') as data:
        payload = aiohttp.payload.BytesPayload(
            file_content, headers={'Content-Type': 'text/csv'},
        )
        payload.set_content_disposition('form-data', name='file')
        data.append_payload(payload)
    return {
        'data': data,
        'headers': {
            'Content-Type': 'multipart/form-data; boundary=' + data.boundary,
        },
    }


@pytest.mark.pgsql('classifier', files=['rules.sql'])
@pytest.mark.now('2019-12-27T23:37:00+0000')
async def test_upload_rules_with_delete(taxi_classifier, pgsql):

    file_content = (
        b'classifier_id;tariff_id;started_at;ended_at;'
        b'is_allowing;brand;model;price_from;price_to;year_from;'
        b'year_to;vehicle_before'
        b'is_new_tariff_allowing;is_new_classifier_allowing\n'
        b'classifier_id_1;econom;;None;1;'
        b';;1000;3000;1920;1955;;1;1\n'
        b'classifier_id_2;econom_2;2020-02-21;2030-12-27;0;'
        b'BmW;X6*;;;1990;2020;2025-02-21;0;0\r\n'
    )

    response = await taxi_classifier.post(
        '/v1/classifiers/tariffs/rules/upload',
        params={
            'duplicate_to_uber': 'false',
            'dry_run': 'false',
            'delete_current_rules': 'true',
        },
        **make_extra(file_content),
    )
    assert response.status == 200, response.text
    assert response.json() == {
        'rules_log': {
            'updated_classifier_ids': ['classifier_id_2', 'classifier_id_1'],
            'added': 2,
            'deleted': 3,
        },
    }

    cursor = pgsql['classifier'].cursor()

    # check classifiers
    cursor.execute(
        """
            SELECT
                classifier_id,
                is_allowing
            FROM classifier.classifiers
            WHERE is_deleted = FALSE
        """,
    )

    assert cursor.fetchall() == [
        ('classifier_id_2', False),
        ('classifier_id_1', True),
    ]

    # check tariffs
    cursor.execute(
        """
            SELECT
                classifier_id,
                tariff_id,
                is_allowing
            FROM classifier.tariffs
            WHERE is_deleted = FALSE
        """,
    )
    assert cursor.fetchall() == [
        ('classifier_id_2', 'econom_2', False),
        ('classifier_id_1', 'econom', True),
    ]

    # check rules
    cursor.execute(
        """
            SELECT
                classifier_id,
                tariff_id,
                started_at,
                ended_at,
                is_allowing,
                brand,
                model,
                price_from,
                price_to,
                year_from,
                year_to,
                vehicle_before
            FROM classifier.rules
            WHERE is_deleted = FALSE;
        """,
    )

    assert cursor.fetchall() == [
        # old rule
        (
            'classifier_id_1',
            'vip',
            datetime.datetime(
                2019,
                12,
                27,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            datetime.datetime(
                2020,
                12,
                27,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            True,
            'Pagani',
            'Zonda',
            3000000,
            6000000,
            0,
            3,
            datetime.datetime(
                2018,
                1,
                1,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
        ),
        # new rules
        (
            'classifier_id_2',
            'econom_2',
            datetime.datetime(
                2020,
                2,
                21,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            datetime.datetime(
                2030,
                12,
                27,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            False,
            'BMW',
            'X6*',
            None,
            None,
            1990,
            2020,
            datetime.datetime(
                2025,
                2,
                21,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
        ),
        (
            'classifier_id_1',
            'econom',
            None,
            None,
            True,
            None,
            None,
            1000,
            3000,
            1920,
            1955,
            None,
        ),
    ]


@pytest.mark.pgsql('classifier', files=['rules.sql'])
@pytest.mark.now('2019-12-27T23:37:00+0000')
async def test_dry_run(taxi_classifier, pgsql):

    file_content = (
        b'classifier_id;tariff_id;started_at;ended_at;'
        b'is_allowing;brand;model;price_from;price_to;year_from;'
        b'year_to;vehicle_before'
        b'is_new_tariff_allowing;is_new_classifier_allowing\n'
        b'classifier_id_1;econom;;None;1;'
        b'Audi;TT;None;None;1920;1955;;1;1\n'
        b'classifier_id_2;econom_2;2020-02-21;2030-12-27;0;'
        b';;888;999;1990;2020;2025-02-21;0;0\n'
        b'classifier_id_2;econom_2;;;0;'
        b'BMW;X3;;;1990;2020;;;\n'
    )

    response = await taxi_classifier.post(
        '/v1/classifiers/tariffs/rules/upload',
        params={
            'duplicate_to_uber': 'false',
            'dry_run': 'true',
            'delete_current_rules': 'true',
        },
        **make_extra(file_content),
    )
    assert response.status == 200, response.text
    assert response.json() == {
        'rules_log': {
            'added': 3,
            'deleted': 3,
            'updated_classifier_ids': ['classifier_id_2', 'classifier_id_1'],
        },
    }

    cursor = pgsql['classifier'].cursor()
    # check classifiers
    cursor.execute(
        """
            SELECT
                classifier_id,
                is_allowing
            FROM classifier.classifiers
            WHERE is_deleted = FALSE
        """,
    )

    assert cursor.fetchall() == []

    # check tariffs
    cursor.execute(
        """
            SELECT
                classifier_id,
                tariff_id,
                is_allowing
            FROM classifier.tariffs
            WHERE is_deleted = FALSE
        """,
    )
    assert cursor.fetchall() == []

    cursor = pgsql['classifier'].cursor()
    cursor.execute(
        """
            SELECT
                classifier_id,
                tariff_id,
                started_at,
                ended_at,
                is_allowing,
                brand,
                model,
                price_from,
                price_to,
                year_from,
                year_to,
                vehicle_before
            FROM classifier.rules
            WHERE is_deleted = FALSE;
        """,
    )

    assert cursor.fetchall() == [
        # Rules were not changed
        (
            'classifier_id_1',
            'econom',
            None,
            None,
            False,
            'BMW',
            'X1',
            None,
            None,
            None,
            None,
            None,
        ),
        (
            'classifier_id_1',
            'econom',
            None,
            None,
            True,
            'Pagani',
            'Huayra',
            None,
            None,
            None,
            None,
            None,
        ),
        (
            'classifier_id_2',
            'econom_2',
            None,
            None,
            True,
            'Pagani',
            'Zonda',
            None,
            None,
            None,
            None,
            None,
        ),
        (
            'classifier_id_1',
            'vip',
            datetime.datetime(
                2019,
                12,
                27,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            datetime.datetime(
                2020,
                12,
                27,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            True,
            'Pagani',
            'Zonda',
            3000000,
            6000000,
            0,
            3,
            datetime.datetime(
                2018,
                1,
                1,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
        ),
    ]


@pytest.mark.now('2019-12-27T23:37:00+0000')
@pytest.mark.config(
    TARIFF_CLASSES_MAPPING={
        'unknown_vip': {'classes': ['vip']},
        'uber_vip': {'classes': ['vip', 'business']},
        'uber_econom': {'classes': ['econom']},
    },
)
async def test_duplicate_uber_tariffs(taxi_classifier, pgsql):

    file_content = (
        b'classifier_id;tariff_id;started_at;ended_at;'
        b'is_allowing;brand;model;price_from;price_to;year_from;'
        b'year_to;vehicle_before;is_new_classifier_allowing;'
        b'is_new_tariff_allowing\n'
        b'classifier_id_1;econom;None;None;1;'
        b'BMW;X3;;;1920;1955;None;;\n'
        b'classifier_id_2;vip;2020-02-21;2030-12-27;0;'
        b';;888;999;1990;2020;None;;\n'
    )

    response = await taxi_classifier.post(
        '/v1/classifiers/tariffs/rules/upload',
        params={
            'duplicate_to_uber': 'true',
            'dry_run': 'false',
            'delete_current_rules': 'true',
        },
        **make_extra(file_content),
    )
    assert response.status == 200, response.text
    assert response.json() == {
        'rules_log': {
            'added': 4,
            'deleted': 0,
            'updated_classifier_ids': ['classifier_id_2', 'classifier_id_1'],
        },
    }

    cursor = pgsql['classifier'].cursor()

    # check classifiers
    cursor.execute(
        """
            SELECT
                classifier_id,
                is_allowing
            FROM classifier.classifiers
            WHERE is_deleted = FALSE
        """,
    )

    assert cursor.fetchall() == [
        ('classifier_id_2', True),
        ('classifier_id_1', True),
    ]

    # check tariffs
    cursor.execute(
        """
            SELECT
                classifier_id,
                tariff_id,
                is_allowing
            FROM classifier.tariffs
            WHERE is_deleted = FALSE
        """,
    )
    assert cursor.fetchall() == [
        ('classifier_id_2', 'uber_vip', True),
        ('classifier_id_2', 'vip', True),
        ('classifier_id_1', 'uber_econom', True),
        ('classifier_id_1', 'econom', True),
    ]

    # check rules
    cursor.execute(
        """
            SELECT
                classifier_id,
                tariff_id,
                is_allowing,
                brand,
                model,
                price_from,
                price_to,
                year_from,
                year_to
            FROM classifier.rules
            WHERE is_deleted = FALSE;
        """,
    )

    assert cursor.fetchall() == [
        (
            'classifier_id_2',
            'uber_vip',
            False,
            None,
            None,
            888,
            999,
            1990,
            2020,
        ),
        ('classifier_id_2', 'vip', False, None, None, 888, 999, 1990, 2020),
        (
            'classifier_id_1',
            'uber_econom',
            True,
            'BMW',
            'X3',
            None,
            None,
            1920,
            1955,
        ),
        (
            'classifier_id_1',
            'econom',
            True,
            'BMW',
            'X3',
            None,
            None,
            1920,
            1955,
        ),
    ]


@pytest.mark.parametrize(
    ['rules_file_content', 'extected_bad_response'],
    [
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_1;econom;None;None;1;'
            b'Audi;None;;;1920;1955;None;1;1\n',
            {
                'code': 'incomplete_brand_model',
                'message': (
                    'Both brand and model must be set if one of them is '
                    'setted, line: 1'
                ),
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_1;econom;None;None;1;'
            b'UnknownBrand;Focus;;;1920;1955;None;1;1\n',
            {
                'code': 'invalid_brand',
                'message': (
                    'Can\'t find brand UnknownBrand in '
                    'auto_dictionary, line: 1'
                ),
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_1;econom;None;None;1;'
            b';;5000;3000;1920;1955;None;1;1\n',
            {
                'code': 'invalid_price_range',
                'message': (
                    'price_from must be less or equal than price_to, line: 1'
                ),
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_1;econom;None;None;1;'
            b';;1000;3000;2010;1955;None;1;1\n',
            {
                'code': 'invalid_year_range',
                'message': (
                    'year_from must be less or equal than year_to, line: 1'
                ),
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'None;econom;None;None;1;'
            b'Audi;A8;;;1920;1955;None;1;1\n',
            {
                'code': 'empty_classifier_id',
                'message': 'Classifier name must not be empty, line: 1',
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'None;econom;None;None;1;'
            b'Audi;A8;;;1920;1955;None;\n',
            {
                'code': 'invalid_csv_size',
                'message': (
                    'CSV columns number mismatch: expected 14, got 13, line: 1'
                ),
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_1;;None;None;1;'
            b'Audi;A8;;;1920;1955;None;1;1\n',
            {
                'code': 'empty_tariff_id',
                'message': 'Tariff name must not be empty, line: 1',
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_1;econom;2020-10-12T00:00:00;None;1;'
            b'Audi;A8;;;1920;1955;None;1;1\n',
            {
                'code': 'invalid_date_format',
                'message': (
                    'Failed to parse date: '
                    '2020-10-12T00:00:00 ; use %Y-%m-%d format, line: 1'
                ),
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_1;econom;None;None;true;'
            b';;1000;3000;1920;1955;None;1;1\n',
            {
                'code': 'invalid_is_allowing_value',
                'message': (
                    'is_allowing must be equal either 1 or 0, got: true,'
                    ' line: 1'
                ),
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_1;econom;None;None;1;'
            b';;eeee;3000;1920;1955;None;1;1\n',
            {
                'code': 'invalid_price_from_value',
                'message': (
                    'price_from must be unsigned integer, got: eeee, line: 1'
                ),
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_1;econom;None;None;1;'
            b';;1000;3000;tttt;1955;None;1;1\n',
            {
                'code': 'invalid_year_from_value',
                'message': (
                    'year_from must be unsigned integer, got: tttt, line: 1'
                ),
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_1;econom;None;None;1;'
            b';;1000;3000;1920;1955;2020-10-;1;1\n',
            {
                'code': 'invalid_date_format',
                'message': (
                    'Failed to parse date: 2020-10- ; use %Y-%m-%d format'
                    ', line: 1'
                ),
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_1;econom;None;None;1;'
            b';;1000;3000;1920;1955;None;true;1\n',
            {
                'code': 'invalid_is_new_tariff_allowing_allowing_value',
                'message': (
                    'is_new_tariff_allowing must '
                    'be equal either 1 or 0, got: true, line: 1'
                ),
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_1;econom;None;None;1;'
            b';;1000;3000;1920;1955;None;1;false\n',
            {
                'code': 'invalid_is_new_classifier_allowing_value',
                'message': (
                    'is_new_classifier_allowing must '
                    'be equal either 1 or 0, got: false, line: 1'
                ),
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_1;econom;None;None;1;'
            b';;;2600000000;1920;1955;None;1;1\n',
            {
                'code': 'invalid_price_to',
                'message': (
                    'price_to value overflow, got: -1694967296, line: 1'
                ),
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_1;econom;None;None;1;'
            b';;1000;3000;1;100000000;None;1;1\n',
            {
                'code': 'invalid_year_to',
                'message': 'year_to value overflow, got: 100000000, line: 1',
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_1;econom;None;None;1;'
            b'Audi;TT;1000;3000;1;100000000;None;1;1\n',
            {
                'code': 'invalid_rule_structure',
                'message': (
                    'Rule can\'t contain both brand-model and price, line: 1'
                ),
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_1;econom;None;None;1;'
            b'Audi;TT;1000;3000;1;100000000;None;1;1\n'
            b'classifier_id_1;econom;None;None;1;'
            b';;1000;3000;1;100000000;None;1;1\n'
            b'classifier_id_1;econom;None;None;1;'
            b';;1000;3000;1920;1955;None;1;1\n'
            b'classifier_id_1;econom;None;None;1;'
            b';;1000;3000;1920;1955;None;1;false\n',
            {
                'code': 'multiple_errors',
                'message': (
                    'Rule can\'t contain both brand-model and price, '
                    'line: 1  ||  '
                    'year_to value overflow, got: 100000000, line: 2  ||  '
                    'is_new_classifier_allowing must be equal either 1 or 0,'
                    ' got: false, line: 4'
                ),
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_2;econom_2;2020-02-21;2030-12-27;0;'
            b'BmW;QWE*;;;1990;2020;2025-02-21;0;0\r\n',
            {
                'code': 'invalid_model',
                'message': (
                    'Can\'t find model `QWE*` in auto_dictionary, line: 1'
                ),
            },
        ),
    ],
)
async def test_bad_rules(
        taxi_classifier, rules_file_content, extected_bad_response,
):
    response = await taxi_classifier.post(
        '/v1/classifiers/tariffs/rules/upload',
        params={
            'duplicate_to_uber': 'true',
            'dry_run': 'false',
            'delete_current_rules': 'true',
        },
        **make_extra(rules_file_content),
    )
    assert response.status == 400, response.text
    assert response.json() == extected_bad_response


@pytest.mark.pgsql('classifier', files=['rules.sql'])
@pytest.mark.now('2019-12-27T23:37:00+0000')
async def test_upload_rules_with_unavailable_tariffs(taxi_classifier, pgsql):

    file_content = (
        b'classifier_id;tariff_id;started_at;ended_at;'
        b'is_allowing;brand;model;price_from;price_to;year_from;'
        b'year_to;vehicle_before'
        b'is_new_tariff_allowing;is_new_classifier_allowing\n'
        b'classifier_id_1;bad_1;;None;1;'
        b';;1000;3000;1920;1955;;1;1\n'
        b'classifier_id_2;bad_2;2020-02-21;2030-12-27;0;'
        b'BMW;X6;;;1990;2020;2025-02-21;0;0\r\n'
    )

    response = await taxi_classifier.post(
        '/v1/classifiers/tariffs/rules/upload',
        params={
            'duplicate_to_uber': 'false',
            'dry_run': 'false',
            'delete_current_rules': 'false',
        },
        **make_extra(file_content),
    )
    assert response.status == 400, response.text
    assert response.json() == {
        'code': 'multiple_errors',
        'message': (
            'Tariff bad_1 doesn\'t exist, line: 1  '
            '||  Tariff bad_2 doesn\'t exist, line: 2'
        ),
    }
