# pylint: disable=redefined-outer-name
import datetime

import pytest

from taxi.util import dates as dates_utils

NOW = datetime.datetime.utcnow().replace(microsecond=0)


def timedelta_dec(**kwargs):
    return dates_utils.localize(NOW - datetime.timedelta(**kwargs)).isoformat()


def timedelta_inc(**kwargs):
    return dates_utils.localize(NOW + datetime.timedelta(**kwargs)).isoformat()


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ['params', 'expected', 'categories_file', 'zones'],
    [
        pytest.param(
            {
                'client_id': 'client_id_1',
                'zone_name': 'moscow',
                'application': 'taxi',
            },
            {
                'tariff': {
                    'id': '5caeed9d1bc8d21af5a07a24-moscow-tariff_plan_2',
                    'home_zone': 'moscow',
                },
                'disable_paid_supply_price': True,
                'disable_fixed_price': False,
                'name': 'Москва',
                'client_tariff_plan': {
                    'tariff_plan_series_id': 'tariff_plan_series_id_2',
                    'date_from': timedelta_dec(hours=12),
                    'date_to': timedelta_inc(hours=12),
                },
            },
            'categories_moscow.json',
            [],
            id='tariff in client plan',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'zone_name': 'ekb',
                'application': 'taxi',
            },
            {
                'tariff': {
                    'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1',
                    'home_zone': 'ekb',
                },
                'disable_paid_supply_price': False,
                'disable_fixed_price': True,
                'name': 'Многозонный',
                'client_tariff_plan': {
                    'tariff_plan_series_id': 'tariff_plan_series_id_2',
                    'date_from': timedelta_dec(hours=12),
                    'date_to': timedelta_inc(hours=12),
                },
            },
            'categories_ekb.json',
            [],
            id='fallback to default tariff plan',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'zone_name': 'ekb',
                'application': 'callcenter',
            },
            {
                'tariff': {
                    'id': (
                        '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1'
                        '--callcenter'
                    ),
                    'home_zone': 'ekb',
                },
                'disable_paid_supply_price': False,
                'disable_fixed_price': True,
                'name': 'Многозонный',
                'client_tariff_plan': {
                    'tariff_plan_series_id': 'tariff_plan_series_id_2',
                    'date_from': timedelta_dec(hours=12),
                    'date_to': timedelta_inc(hours=12),
                },
            },
            'categories_ekb_callcenter.json',
            [],
            id='fallback to default tariff plan and application multiplier',
        ),
        pytest.param(
            {
                'client_id': 'client_id_3',
                'zone_name': 'ekb',
                'application': 'taxi',
            },
            {
                'tariff': {
                    'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_3',
                    'home_zone': 'ekb',
                },
                'disable_paid_supply_price': False,
                'disable_fixed_price': True,
                'name': 'Многозонный',
                'client_tariff_plan': {
                    'tariff_plan_series_id': 'tariff_plan_series_id_3',
                    'date_from': timedelta_dec(hours=12),
                    'date_to': timedelta_inc(hours=12),
                },
            },
            'categories_ekb.json',
            [
                {
                    'name': 'ekb',
                    'time_zone': 'Asia/Yekaterinburg',
                    'country': 'rus',
                    'translation': 'Екатеринбург',
                    'currency': 'RUB',
                },
            ],
            id='fallback to default tariff',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'zone_name': 'spb',
                'application': 'taxi',
            },
            {
                'tariff': {
                    'id': '5caeed9d1bc8d21af5a07a25',
                    'home_zone': 'spb',
                },
                'disable_paid_supply_price': False,
                'disable_fixed_price': False,
                'client_tariff_plan': {
                    'tariff_plan_series_id': 'tariff_plan_series_id_2',
                    'date_from': timedelta_dec(hours=12),
                    'date_to': timedelta_inc(hours=12),
                },
            },
            'categories_spb.json',
            [],
            id='fallback to driver tariff',
        ),
        pytest.param(
            {
                'client_id': 'client_id_4',
                'zone_name': 'samara',
                'application': 'taxi',
            },
            {
                'tariff': {
                    'id': '5caeed9d1bc8d21af5a07a20',
                    'home_zone': 'samara',
                },
                'disable_paid_supply_price': False,
                'disable_fixed_price': False,
                'client_tariff_plan': {
                    'tariff_plan_series_id': 'tariff_plan_series_id_4',
                    'date_from': timedelta_dec(hours=12),
                    'date_to': timedelta_inc(hours=12),
                },
            },
            'categories_samara.json',
            [],
            id='fallback to driver tariff (category_type=call_center)',
        ),
        pytest.param(
            {
                'client_id': 'client_id_4',
                'zone_name': 'moscow',
                'application': 'taxi',
                'tariff_plan_series_id': 'tariff_plan_series_id_2',
            },
            {
                'tariff': {
                    'id': '5caeed9d1bc8d21af5a07a24-moscow-tariff_plan_2',
                    'home_zone': 'moscow',
                },
                'disable_paid_supply_price': True,
                'disable_fixed_price': False,
                'name': 'Москва',
                'client_tariff_plan': {
                    'tariff_plan_series_id': 'tariff_plan_series_id_4',
                    'date_from': timedelta_dec(hours=12),
                    'date_to': timedelta_inc(hours=12),
                },
            },
            'categories_moscow.json',
            [],
            id='tariff_plan_series_id is provided manually',
        ),
    ],
)
@pytest.mark.config(
    APPLICATION_MAP_PLATFORM={'callcenter': 'callcenter'},
    CORP_TARIFFS_USE_APP_MULTIPLIERS=True,
    CORP_CATEGORIES={
        '__default__': {'econom': 'name.econom', 'vip': 'name.vip'},
    },
    CORP_DEFAULT_TARIFF_PLANS={
        'rus': {'tariff_plan_series_id': 'tariff_plan_series_id_1'},
    },
)
async def test_client_tariff_current(
        taxi_corp_tariffs_web,
        cache_shield,
        load_json,
        params,
        expected,
        categories_file,
        mock_tariff_zones,
        zones,
):
    mock_tariff_zones.data.zones = {'zones': zones}
    response = await taxi_corp_tariffs_web.get(
        '/v1/client_tariff/current', params=params,
    )
    data = await response.json()

    expected['tariff']['categories'] = load_json(categories_file)

    assert response.status == 200, data
    assert data == expected


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ['params', 'expected', 'categories_file'],
    [
        pytest.param(
            {
                'client_id': 'client_id_1',
                'zone_name': 'ekb',
                'application': 'cargo',
            },
            {
                'tariff': {
                    'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1',
                    'home_zone': 'ekb',
                },
                'disable_paid_supply_price': False,
                'disable_fixed_price': True,
                'name': 'Многозонный',
                'client_tariff_plan': {
                    'tariff_plan_series_id': 'tariff_plan_series_id_2',
                    'date_from': timedelta_dec(hours=12),
                    'date_to': timedelta_inc(hours=12),
                },
            },
            'categories_ekb.json',
            id='fallback to default cargo tariff plan',
        ),
    ],
)
@pytest.mark.config(
    CORP_CATEGORIES={
        '__default__': {'econom': 'name.econom', 'vip': 'name.vip'},
    },
    CORP_CARGO_DEFAULT_TARIFF_PLANS={
        'rus': {'tariff_plan_series_id': 'tariff_plan_series_id_1'},
    },
)
async def test_client_cargo_tariff_current(
        web_app_client,
        cache_shield,
        load_json,
        params,
        expected,
        categories_file,
):
    response = await web_app_client.get(
        '/v1/client_tariff/current', params=params,
    )
    data = await response.json()

    expected['tariff']['categories'] = load_json(categories_file)

    assert response.status == 200, data
    assert data == expected


@pytest.mark.parametrize(
    ['params', 'expected'],
    [
        pytest.param(
            {
                'client_id': 'client_id_1',
                'zone_name': 'moscow',
                'application': 'taxi',
                'categories': 'econom',
            },
            ['econom'],
            id='get_client_tariff_current filter one category',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'zone_name': 'moscow',
                'application': 'taxi',
                'categories': 'econom,vip',
            },
            ['econom', 'vip'],
            id='get_client_tariff_current filter many categories',
        ),
    ],
)
async def test_client_tariff_current_categories_filter(
        web_app_client, cache_shield, params, expected,
):
    response = await web_app_client.get(
        '/v1/client_tariff/current', params=params,
    )
    data = await response.json()

    assert response.status == 200, data
    categories = [
        category['category_name'] for category in data['tariff']['categories']
    ]

    assert set(categories) == set(expected)


@pytest.mark.parametrize(
    ['params', 'expected_tariff_id'],
    [
        pytest.param(
            {
                'client_id': 'client_id_2',
                'zone_name': 'moscow',
                'application': 'taxi',
            },
            '5caeed9d1bc8d21af5a07a24-moscow-tariff_plan_2',
            id='home zone ride',
        ),
        pytest.param(
            {
                'client_id': 'client_id_2',
                'zone_name': 'ekb',
                'application': 'taxi',
            },
            '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_roaming',
            id='roaming ride',
        ),
        pytest.param(
            {
                'client_id': 'client_id_2',
                'zone_name': 'ekb',
                'application': 'cargo',
            },
            '5caeed9d1bc8d21af5a07a26',
            id='cargo',
        ),
    ],
)
@pytest.mark.config(
    CORP_DEFAULT_TARIFF_PLANS={
        'rus': {'tariff_plan_series_id': 'tariff_plan_series_id_2'},
    },
    CORP_ROAMING_TARIFF_PLANS_MAP={
        'rus': [
            {
                'tariff_plan_series_id': 'tariff_plan_series_id_2',
                'roaming_tariff_plan_series_id': (
                    'tariff_plan_series_id_roaming'
                ),
                'description': 'test',
            },
        ],
    },
)
async def test_client_tariff_current_roaming(
        web_app_client, cache_shield, params, expected_tariff_id,
):
    response = await web_app_client.get(
        '/v1/client_tariff/current', params=params,
    )
    data = await response.json()

    assert response.status == 200, data
    assert data['tariff']['id'] == expected_tariff_id


@pytest.mark.parametrize(
    'params, expected',
    [
        (
            {'client_id': 'unknown', 'zone_name': 'moscow'},
            {
                'code': 'NOT_FOUND',
                'message': 'Not found',
                'details': {
                    'reason': 'Client unknown does not have tariff plan',
                },
            },
        ),
        (
            {
                'client_id': 'client_id_1',
                'zone_name': 'moscow',
                'tariff_plan_series_id': 'nonexistent',
            },
            {
                'code': 'NOT_FOUND',
                'message': 'Not found',
                'details': {'reason': 'Tariff plan nonexistent not found'},
            },
        ),
    ],
)
async def test_client_tariff_current_failed(
        web_app_client, cache_shield, params, expected,
):
    response = await web_app_client.get(
        '/v1/client_tariff/current', params=params,
    )
    data = await response.json()

    assert response.status == 404, data
    assert data == expected
