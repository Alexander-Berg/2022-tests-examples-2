import datetime

import pytest

from taxi.util import dates as dates_utils

from corp_tariffs_admin.web import errors

NOW = datetime.datetime.utcnow().replace(microsecond=0)


@pytest.mark.now(NOW.isoformat())
async def test_get_list(web_app_client):
    response = await web_app_client.get('/v1/tariff-plans')

    assert response.status == 200
    assert await response.json() == {
        'items': [
            {
                'name': 'Тарифный план 1',
                'country': 'rus',
                'tariff_plan_series_id': 'tariff_plan_series_id_1',
            },
            {
                'name': 'Тарифный план 2',
                'country': 'pandora',
                'tariff_plan_series_id': 'tariff_plan_series_id_2',
            },
        ],
    }


@pytest.mark.now(NOW.isoformat())
async def test_get_list_with_country(web_app_client):
    response = await web_app_client.get(
        '/v1/tariff-plans', params={'country': 'rus'},
    )

    assert response.status == 200
    assert await response.json() == {
        'items': [
            {
                'name': 'Тарифный план 1',
                'country': 'rus',
                'tariff_plan_series_id': 'tariff_plan_series_id_1',
            },
        ],
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'series_id, tariff_plan',
    [
        (
            'tariff_plan_series_id_1',
            {
                'name': 'Тарифный план 1',
                'country': 'rus',
                'disable_fixed_price': False,
                'disable_tariff_fallback': False,
                'tariff_plan_series_id': 'tariff_plan_series_id_1',
                'default_tariff_series_id': 'moscow',
                'application_multipliers': [
                    {'application': 'callcenter', 'multiplier': 100},
                ],
                'multiplier': 1,
                'usage_count': 0,
                'in_use': False,
                'zones': [
                    {'zone': 'moscow', 'tariff_series_id': 'moscow'},
                    {'zone': 'balaha', 'tariff_series_id': 'standalone'},
                ],
            },
        ),
        (
            'tariff_plan_series_id_2',
            {
                'name': 'Тарифный план 2',
                'country': 'pandora',
                'disable_fixed_price': True,
                'disable_tariff_fallback': True,
                'tariff_plan_series_id': 'tariff_plan_series_id_2',
                'default_tariff_series_id': 'moscow',
                'multiplier': 1,
                'usage_count': 3,
                'in_use': True,
                'zones': [
                    {'zone': 'balaha', 'tariff_series_id': 'standalone'},
                ],
            },
        ),
    ],
)
async def test_get_one(web_app_client, series_id, tariff_plan):
    response = await web_app_client.get(
        f'/v1/tariff-plans/current?tariff_plan_series_id={series_id}',
    )

    assert response.status == 200
    assert await response.json() == tariff_plan


async def test_get_one_error400(web_app_client):
    series_id = 'tariff_plan_series_id_10'
    response = await web_app_client.get(
        f'/v1/tariff-plans/current?tariff_plan_series_id={series_id}',
    )

    assert response.status == 400
    assert await response.json() == dict(
        code='invalid-input',
        message=errors.TARIFF_PLAN_NOT_FOUND,
        status='error',
        details={},
    )


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'series_id, limit, offset, clients',
    [
        (
            'tariff_plan_series_id_2',
            3,
            0,
            {
                'clients': [
                    {'_id': 'client_id_1', 'name': 'Client_1'},
                    {'_id': 'client_id_2', 'name': 'Client_2'},
                    {'_id': 'client_id_3', 'name': 'Client_3'},
                ],
                'total': 3,
            },
        ),
        (
            'tariff_plan_series_id_2',
            2,
            1,
            {
                'clients': [
                    {'_id': 'client_id_2', 'name': 'Client_2'},
                    {'_id': 'client_id_3', 'name': 'Client_3'},
                ],
                'total': 3,
            },
        ),
        ('tariff_plan_series_id_2', 5, 5, {'clients': [], 'total': 3}),
        ('nonexistent_id', 1, 0, {'clients': [], 'total': 0}),
    ],
)
async def test_get_tariff_plan_clients(
        web_app_client, series_id, limit, offset, clients,
):
    response = await web_app_client.get(
        '/v1/tariff-plans/clients',
        params={
            'tariff_plan_series_id': series_id,
            'limit': limit,
            'offset': offset,
        },
    )

    assert response.status == 200
    assert await response.json() == clients


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'params, expected',
    [
        pytest.param(
            {'tariff_plan_series_id': 'tariff_plan_series_id_2'},
            'tariff_plan_clients.csv',
            id='success',
        ),
    ],
)
async def test_export_tariff_plan_clients(
        web_app_client, params, expected, load_binary,
):
    response = await web_app_client.get(
        f'/v1/tariff-plans/clients/export', params=params,
    )
    assert response.status == 200

    content = await response.content.read()
    result = content.decode('utf-8-sig').replace('\r', '')
    to_assert = load_binary(expected).decode('utf-8-sig').replace('\r\n', '')
    assert result == to_assert


@pytest.mark.now(NOW.isoformat())
async def test_delete(db, web_app_client):
    assert (
        await db.corp_tariff_plans.count(
            {'tariff_plan_series_id': 'tariff_plan_series_id_1'},
        )
        == 2
    )

    response = await web_app_client.delete(
        '/v1/tariff-plans/tariff_plan_series_id_1',
    )

    assert response.status == 200
    assert await response.json() == {}

    assert (
        await db.corp_tariff_plans.count(
            {'tariff_plan_series_id': 'tariff_plan_series_id_1'},
        )
        == 0
    )


@pytest.mark.now(NOW.isoformat())
async def test_delete_fail(db, web_app_client):
    response = await web_app_client.delete(
        '/v1/tariff-plans/tariff_plan_series_id_2',
    )

    assert response.status == 409
    assert (await response.json())['message'] == 'Tariff plan in use'


@pytest.mark.parametrize(
    ['expected_tariff_plans', 'client_id'],
    [
        pytest.param(
            [
                {
                    'tariff_plan_series_id': 'tariff_plan_series_id_1',
                    'description': 'tariff_plan_series_id_1',
                    'tags': ['fixed'],
                },
                {
                    'tariff_plan_series_id': 'tariff_plan_series_id_2',
                    'description': 'tariff_plan_series_id_1',
                    'tags': ['fixed'],
                },
            ],
            'client_id_1',
            marks=pytest.mark.config(
                CORP_AVAILABLE_TARIFF_PLANS_TO_CHOOSE={
                    'rus': [
                        {
                            'name': 'one',
                            'combination': [
                                {
                                    'tariff_plan_series_id': (
                                        'tariff_plan_series_id_1'
                                    ),
                                    'description_key': (
                                        'tariff_plan_series_id_1'
                                    ),
                                    'tags': ['fixed'],
                                },
                                {
                                    'tariff_plan_series_id': (
                                        'tariff_plan_series_id_2'
                                    ),
                                    'description_key': (
                                        'tariff_plan_series_id_1'
                                    ),
                                    'tags': ['fixed'],
                                },
                            ],
                        },
                    ],
                },
            ),
            id='client has the feature and his tp in the combination',
        ),
        pytest.param(
            [],
            'client_id_2',
            marks=pytest.mark.config(
                CORP_AVAILABLE_TARIFF_PLANS_TO_CHOOSE={
                    'rus': [
                        {
                            'name': 'one',
                            'combination': [
                                {
                                    'tariff_plan_series_id': (
                                        'tariff_plan_series_id_1'
                                    ),
                                    'description_key': (
                                        'tariff_plan_series_id_1'
                                    ),
                                    'tags': ['fixed'],
                                },
                                {
                                    'tariff_plan_series_id': (
                                        'tariff_plan_series_id_2'
                                    ),
                                    'description_key': (
                                        'tariff_plan_series_id_1'
                                    ),
                                    'tags': ['fixed'],
                                },
                            ],
                        },
                    ],
                },
            ),
            id='client has tp in the combination but not the feature',
        ),
        pytest.param(
            [],
            'client_id_1',
            marks=pytest.mark.config(
                CORP_AVAILABLE_TARIFF_PLANS_TO_CHOOSE={
                    'rus': [
                        {
                            'name': 'one',
                            'combination': [
                                {
                                    'tariff_plan_series_id': (
                                        'tariff_plan_series_id_1'
                                    ),
                                    'description_key': (
                                        'tariff_plan_series_id_1'
                                    ),
                                    'tags': ['fixed'],
                                },
                            ],
                        },
                    ],
                },
            ),
            id='client has feature but his tp not in the combination',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(CORP_TARIFF_PLAN_CHANGE_COOLDOWN=7)
@pytest.mark.translations(
    corp={'tariff_plan_series_id_1': {'ru': 'tariff_plan_series_id_1'}},
)
async def test_get_available_tariff_plans(
        db, web_app_client, expected_tariff_plans, client_id,
):
    response = await web_app_client.get(
        '/v1/tariff-plans/available', params={'client_id': client_id},
    )
    assert response.status == 200

    assert await response.json() == {
        'tariff_plans': expected_tariff_plans,
        'cooldown': 7,
        'last_changed_date': dates_utils.localize(
            NOW - datetime.timedelta(days=1),
        ).isoformat(),
    }


async def test_get_available_tariff_plans_error400(web_app_client):
    client_id = 'client_id_empty'
    response = await web_app_client.get(
        '/v1/tariff-plans/available', params={'client_id': client_id},
    )
    assert response.status == 400
    assert await response.json() == dict(
        code='invalid-input',
        message=errors.DB_CLIENT_NOT_FOUND,
        status='error',
        details={},
    )
