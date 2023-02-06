# pylint:disable=redefined-outer-name

import collections
import datetime
from unittest import mock

import pytest

NOW = datetime.datetime.utcnow().replace(microsecond=0)

TARIFFS = [
    {
        'home_zone': 'moscow',
        'country': 'rus',
        'name': 'Однозонный Москва 30%',
        'tariff_series_id': 'moscow',
    },
    {
        'home_zone': 'balaha',
        'country': 'paradise',
        'name': 'Однозонный Балаха 30%',
        'tariff_series_id': 'balaha',
    },
    {
        'home_zone': None,
        'country': 'rus',
        'name': 'Многозонный 30%',
        'tariff_series_id': 'standalone30',
    },
    {
        'home_zone': None,
        'country': 'kaz',
        'name': 'Многозонный 40%',
        'tariff_series_id': 'standalone40',
    },
    {
        'home_zone': None,
        'country': 'rus',
        'name': 'Многозонный кастомный',
        'tariff_series_id': 'multizone_custom',
    },
]

TARIFF_MOSCOW = {
    'country': 'rus',
    'classes': [
        {
            'name': 'econom',
            'disable_surge': True,
            'inherited': True,
            'policy': {
                'multiplier': 1.3,
                'category': {
                    'minimal': {'method': 'multiply', 'value': 1.1},
                    'waiting_price': {'method': 'multiply', 'value': 1.2},
                    'distance_price': {'method': 'add', 'value': 3},
                    'time_price': {'method': 'specific', 'value': 10},
                },
                'transfer': {
                    'minimal': {'method': 'multiply', 'value': 1.3},
                    'waiting_price': {'method': 'multiply', 'value': 1.4},
                    'distance_price': {'method': 'add', 'value': 4},
                    'time_price': {'method': 'specific', 'value': 11},
                },
            },
        },
    ],
    'disable_paid_supply_price': True,
    'home_zone': 'moscow',
    'name': 'Однозонный Москва 30%',
    'tariff_series_id': 'moscow',
    'usage_count': 2,
    'in_use': True,
}

TARIFF_MULTIZONE_CUSTOM = {
    'country': 'rus',
    'classes': [
        {
            'name': 'econom',
            'disable_surge': False,
            'inherited': False,
            'intervals': [
                {
                    'id': 'example_id',
                    'add_minimal_to_paid_cancel': True,
                    'category_type': 'application',
                    'currency': 'RUB',
                    'day_type': 2,
                    'included_one_of': [],
                    'meters': [],
                    'minimal': 50,
                    'minimal_price': 100,
                    'name_key': 'interval.day',
                    'paid_cancel_fix': 1,
                    'special_taximeters': [],
                    'summable_requirements': [],
                    'time_from': '00:00',
                    'time_to': '23:59',
                    'zonal_prices': [],
                },
            ],
        },
    ],
    'disable_paid_supply_price': False,
    'home_zone': None,
    'name': 'Многозонный кастомный',
    'tariff_series_id': 'multizone_custom',
    'usage_count': 1,
    'in_use': True,
}


@pytest.fixture
def request_mock(db, taxi_corp_admin_app, taxi_corp_admin_client):
    return mock.MagicMock(db=db, app=taxi_corp_admin_app)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize('country', [None, 'rus', 'kaz', 'paradise'])
async def test_get_list(taxi_corp_admin_client, country):
    params = {}
    if country:
        params['country'] = country
    response = await taxi_corp_admin_client.get('/v1/tariffs', params=params)

    multizonal_tariffs = []
    zonal_tariffs = collections.defaultdict(list)
    for tariff in TARIFFS:
        if country is None or country == tariff['country']:
            if tariff['home_zone'] is None:
                multizonal_tariffs.append(tariff)
            else:
                zonal_tariffs[tariff['home_zone']].append(tariff)

    expected = {
        'multizonal_tariffs': multizonal_tariffs,
        'zonal_tariffs': [
            {'home_zone': home_zone, 'tariffs': tariffs}
            for home_zone, tariffs in zonal_tariffs.items()
        ],
    }

    data = await response.json()

    assert response.status == 200, data
    assert data == expected


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'url, expected_status, expected_response',
    [
        ('/v1/tariffs/current?tariff_series_id=moscow', 200, TARIFF_MOSCOW),
        (
            '/v1/tariffs/current?tariff_series_id=multizone_custom',
            200,
            TARIFF_MULTIZONE_CUSTOM,
        ),
        (
            '/v1/tariffs/current?tariff_series_id=404',
            400,
            {
                'code': 'invalid-input',
                'details': {},
                'message': 'tariff \'404\' not found',
                'status': 'error',
            },
        ),
        (
            '/v1/tariffs/current?tariff_series_id=',
            400,
            {
                'code': 'invalid-input',
                'details': {},
                'message': 'tariff \'\' not found',
                'status': 'error',
            },
        ),
        (
            '/v1/tariffs/current',
            400,
            {
                'code': 'invalid-input',
                'details': {
                    '': ['\'tariff_series_id\' is a required property'],
                },
                'message': 'Invalid input',
                'status': 'error',
            },
        ),
    ],
)
async def test_get_one(
        taxi_corp_admin_client, url, expected_status, expected_response,
):
    response = await taxi_corp_admin_client.get(url)
    response_json = await response.json()
    assert response.status == expected_status, response_json
    assert response_json == expected_response


@pytest.mark.now(NOW.isoformat())
async def test_delete(db, taxi_corp_admin_client):
    assert (
        await db.corp_tariffs.count({'tariff_series_id': 'standalone30'}) == 2
    )

    response = await taxi_corp_admin_client.delete('/v1/tariffs/standalone30')
    assert response.status == 200
    assert await response.json() == {}

    assert (
        await db.corp_tariffs.count({'tariff_series_id': 'standalone30'}) == 0
    )


@pytest.mark.now(NOW.isoformat())
async def test_delete_fail(db, taxi_corp_admin_client):
    response = await taxi_corp_admin_client.delete('/v1/tariffs/balaha')

    assert response.status == 409
    assert (await response.json())['message'] == 'Tariff in use'


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'params, expected',
    [
        pytest.param(
            {'tariff_series_id': 'moscow'},
            {
                'tariff_plans': [
                    {
                        'name': 'Тарифный план 1',
                        'tariff_plan_series_id': 'tariff_plan_series_id_1',
                    },
                    {
                        'name': 'Тарифный план 2',
                        'tariff_plan_series_id': 'tariff_plan_series_id_2',
                    },
                ],
                'total': 2,
            },
            id='without paging',
        ),
        pytest.param(
            {'tariff_series_id': 'moscow', 'limit': 1, 'offset': 1},
            {
                'tariff_plans': [
                    {
                        'name': 'Тарифный план 2',
                        'tariff_plan_series_id': 'tariff_plan_series_id_2',
                    },
                ],
                'total': 2,
            },
            id='with paging',
        ),
        pytest.param(
            {'tariff_series_id': 'nonexistent_id'},
            {'tariff_plans': [], 'total': 0},
            id='not exists',
        ),
    ],
)
async def test_get_tariff_plans_in_use(
        taxi_corp_admin_client, params, expected,
):
    response = await taxi_corp_admin_client.get(
        f'/v1/tariffs/tariff-plans-in-use', params=params,
    )

    response_json = await response.json()

    assert response.status == 200, response_json
    assert await response.json() == expected


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'params, expected',
    [
        pytest.param(
            {'tariff_series_id': 'moscow'},
            'tariff_plans_in_use_export.csv',
            id='success',
        ),
    ],
)
async def test_export_tariff_plans_in_use(
        taxi_corp_admin_client, params, expected, load_binary,
):
    response = await taxi_corp_admin_client.get(
        f'/v1/tariffs/tariff-plans-in-use/export', params=params,
    )
    assert response.status == 200

    content = await response.content.read()
    result = content.decode('utf-8-sig').replace('\r', '')

    to_assert = load_binary(expected).decode('utf-8-sig').replace('\r\n', '')
    assert result == to_assert
