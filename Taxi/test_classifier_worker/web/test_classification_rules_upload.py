import datetime

import aiohttp
import psycopg2
import pytest

FILENAME = 'rules.csv'


@pytest.mark.pgsql('classifier', files=['rules.sql'])
@pytest.mark.now('2019-12-27T23:37:00+0000')
async def test_upload_rules_with_delete(web_app_client, pgsql):

    file_content = (
        b'classifier_id;tariff_id;started_at;ended_at;'
        b'is_allowing;brand;model;price_from;price_to;year_from;'
        b'year_to;vehicle_before\n'
        b'classifier_id_1;econom;None;None;1;'
        b'Ford;Focus;1000;3000;1920;1955;None;\n'
        b'classifier_id_2;econom_2;2020-02-21;2030-12-27;0;'
        b'Cadillac;Escalade;888;999;1990;2020;2025-02-21;\n'
    )

    form = aiohttp.FormData()
    form.add_field(name='file', value=file_content, filename=FILENAME)

    response = await web_app_client.post(
        '/v1/classifiers/tariffs/rules/upload',
        params={
            'duplicate_to_uber': 'false',
            'dry_run': 'false',
            'delete_current_rules': 'true',
        },
        data=form,
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {'rules_log': {'added': 2, 'deleted': 3}}

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
            FROM classifier.rules;
        """,
    )

    assert cursor.fetchall() == [
        (
            'classifier_id_1',
            'econom',
            None,
            None,
            True,
            'Ford',
            'Focus',
            1000,
            3000,
            1920,
            1955,
            None,
        ),
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
            'Cadillac',
            'Escalade',
            888,
            999,
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
    ]


@pytest.mark.now('2019-12-27T23:37:00+0000')
async def test_dry_run(web_app_client, pgsql):

    file_content = (
        b'classifier_id;tariff_id;started_at;ended_at;'
        b'is_allowing;brand;model;price_from;price_to;year_from;'
        b'year_to;vehicle_before\n'
        b'classifier_id_1;econom;None;None;1;'
        b'Ford;Focus;1000;3000;1920;1955;None;\n'
        b'classifier_id_2;econom_2;2020-02-21;2030-12-27;0;'
        b'Cadillac;Escalade;888;999;1990;2020;None;\n'
    )
    form = aiohttp.FormData()
    form.add_field(name='file', value=file_content, filename=FILENAME)

    response = await web_app_client.post(
        '/v1/classifiers/tariffs/rules/upload',
        params={
            'duplicate_to_uber': 'false',
            'dry_run': 'true',
            'delete_current_rules': 'true',
        },
        data=form,
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {'rules_log': {'added': 0, 'deleted': 0}}

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
            FROM classifier.rules;
        """,
    )

    assert cursor.fetchall() == []


@pytest.mark.pgsql('classifier', files=['rules.sql'])
@pytest.mark.now('2019-12-27T23:37:00+0000')
async def test_upload_without_delete(web_app_client, pgsql):

    file_content = (
        b'classifier_id;tariff_id;started_at;ended_at;'
        b'is_allowing;brand;model;price_from;price_to;year_from;'
        b'year_to;vehicle_before\n'
        b'classifier_id_1;econom;None;None;1;'
        b'Ford;Focus;1000;3000;1920;1955;None;\n'
        b'classifier_id_2;econom_2;2020-02-21;2030-12-27;0;'
        b'Cadillac;Escalade;888;999;1990;2020;None;\n'
    )
    form = aiohttp.FormData()
    form.add_field(name='file', value=file_content, filename=FILENAME)

    response = await web_app_client.post(
        '/v1/classifiers/tariffs/rules/upload',
        params={
            'duplicate_to_uber': 'false',
            'dry_run': 'false',
            'delete_current_rules': 'false',
        },
        data=form,
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {'rules_log': {'added': 2, 'deleted': 0}}

    cursor = pgsql['classifier'].cursor()
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
            FROM classifier.rules;
        """,
    )

    assert cursor.fetchall() == [
        (
            'classifier_id_1',
            'tariff_id_1',
            True,
            'Pagani',
            'Zonda',
            3000000,
            6000000,
            0,
            3,
        ),
        (
            'classifier_id_2',
            'tariff_id_2',
            True,
            None,
            None,
            None,
            None,
            None,
            None,
        ),
        (
            'classifier_id_2',
            'tariff_id_2_1',
            True,
            'Audi',
            None,
            None,
            None,
            None,
            None,
        ),
        (
            'classifier_id_1',
            'econom',
            True,
            'Ford',
            'Focus',
            1000,
            3000,
            1920,
            1955,
        ),
        (
            'classifier_id_2',
            'econom_2',
            False,
            'Cadillac',
            'Escalade',
            888,
            999,
            1990,
            2020,
        ),
    ]


@pytest.mark.now('2019-12-27T23:37:00+0000')
@pytest.mark.config(
    TARIFF_CLASSES_MAPPING={
        'uber_econom': {'classes': 'econom'},
        'uber_vip': {'classes': 'vip'},
    },
)
async def test_uber_tariffs(web_app_client, pgsql):

    file_content = (
        b'classifier_id;tariff_id;started_at;ended_at;'
        b'is_allowing;brand;model;price_from;price_to;year_from;'
        b'year_to;vehicle_before\n'
        b'classifier_id_1;econom;None;None;1;'
        b'Ford;Focus;1000;3000;1920;1955;None;\n'
        b'classifier_id_2;vip;2020-02-21;2030-12-27;0;'
        b'Cadillac;Escalade;888;999;1990;2020;None;\n'
    )
    form = aiohttp.FormData()
    form.add_field(name='file', value=file_content, filename=FILENAME)

    response = await web_app_client.post(
        '/v1/classifiers/tariffs/rules/upload',
        params={
            'duplicate_to_uber': 'true',
            'dry_run': 'false',
            'delete_current_rules': 'true',
        },
        data=form,
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {'rules_log': {'added': 4, 'deleted': 0}}

    cursor = pgsql['classifier'].cursor()
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
            FROM classifier.rules;
        """,
    )

    assert cursor.fetchall() == [
        (
            'classifier_id_1',
            'econom',
            True,
            'Ford',
            'Focus',
            1000,
            3000,
            1920,
            1955,
        ),
        (
            'classifier_id_1',
            'uber_econom',
            True,
            'Ford',
            'Focus',
            1000,
            3000,
            1920,
            1955,
        ),
        (
            'classifier_id_2',
            'vip',
            False,
            'Cadillac',
            'Escalade',
            888,
            999,
            1990,
            2020,
        ),
        (
            'classifier_id_2',
            'uber_vip',
            False,
            'Cadillac',
            'Escalade',
            888,
            999,
            1990,
            2020,
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
            b'Ford;None;1000;3000;1920;1955;None;\n',
            {
                'code': 'incorrect_rule',
                'message': (
                    'Incorrect rule: Both brand and model '
                    'must be specified if one of them was'
                ),
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_1;econom;None;None;1;'
            b'Ford;Focus;5000;3000;1920;1955;None;\n',
            {
                'code': 'incorrect_rule',
                'message': (
                    'Incorrect rule: Lower price border must '
                    'be less or equal than top price border'
                ),
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'classifier_id_1;econom;None;None;1;'
            b'Ford;Focus;1000;3000;2010;1955;None;\n',
            {
                'code': 'incorrect_rule',
                'message': (
                    'Incorrect rule: Lower manufacture year '
                    'border must be less or equal than top '
                    'manufacture year border'
                ),
            },
        ),
        (
            b'classifier_id;tariff_id;started_at;ended_at;'
            b'is_allowing;brand;model;price_from;price_to;year_from;'
            b'year_to;vehicle_before\n'
            b'None;econom;None;None;1;'
            b'Ford;Focus;1000;3000;1920;1955;None;\n',
            {
                'code': 'incorrect_rule',
                'message': (
                    'Incorrect rule: Every rule must '
                    'contain classifier and tariff names'
                ),
            },
        ),
    ],
)
async def test_bad_rules(
        web_app_client, rules_file_content, extected_bad_response,
):

    form = aiohttp.FormData()
    form.add_field(name='file', value=rules_file_content, filename=FILENAME)

    response = await web_app_client.post(
        '/v1/classifiers/tariffs/rules/upload',
        params={
            'duplicate_to_uber': 'true',
            'dry_run': 'false',
            'delete_current_rules': 'true',
        },
        data=form,
    )
    assert response.status == 400, await response.text()
    assert await response.json() == extected_bad_response
