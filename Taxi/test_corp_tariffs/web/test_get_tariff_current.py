# pylint: disable=redefined-outer-name
import pytest


@pytest.mark.parametrize(
    ['params', 'expected', 'categories_file', 'zones'],
    [
        pytest.param(
            {
                'tariff_plan_series_id': 'tariff_plan_series_id_1',
                'zone_name': 'moscow',
            },
            {
                'tariff': {
                    'id': '5caeed9d1bc8d21af5a07a24-multizonal-tariff_plan_1',
                    'home_zone': 'moscow',
                },
                'disable_paid_supply_price': False,
                'disable_fixed_price': True,
                'name': 'Многозонный',
            },
            'categories_moscow_multizonal.json',
            [],
            id='custom multizonal moscow',
        ),
        pytest.param(
            {
                'tariff_plan_series_id': 'tariff_plan_series_id_2',
                'zone_name': 'moscow',
            },
            {
                'tariff': {
                    'id': '5caeed9d1bc8d21af5a07a24-moscow-tariff_plan_2',
                    'home_zone': 'moscow',
                },
                'disable_paid_supply_price': True,
                'disable_fixed_price': False,
                'name': 'Москва',
            },
            'categories_moscow.json',
            [],
            id='inherited moscow',
        ),
        pytest.param(
            {
                'tariff_plan_series_id': 'tariff_plan_series_id_4',
                'zone_name': 'samara',
            },
            {
                'tariff': {
                    'id': '5caeed9d1bc8d21af5a07a20',
                    'home_zone': 'samara',
                },
                'disable_paid_supply_price': False,
                'disable_fixed_price': False,
            },
            'categories_samara.json',
            [
                {
                    'name': 'samara',
                    'time_zone': 'Europe/Samara',
                    'country': 'rus',
                    'translation': 'Самара',
                    'currency': 'RUB',
                },
            ],
            id='fallback to default tp (category_type=call_center)',
        ),
        pytest.param(
            {
                'tariff_plan_series_id': 'tariff_plan_series_id_3',
                'zone_name': 'ekb',
            },
            {
                'tariff': {
                    'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_3',
                    'home_zone': 'ekb',
                },
                'disable_paid_supply_price': False,
                'disable_fixed_price': True,
                'name': 'Многозонный',
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
                'tariff_plan_series_id': 'tariff_plan_series_id_2',
                'zone_name': 'ekb',
            },
            {
                'tariff': {
                    'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_4',
                    'home_zone': 'ekb',
                },
                'disable_paid_supply_price': False,
                'name': 'Многозонный',
                'disable_fixed_price': False,
            },
            'categories_ekb.json',
            [],
            marks=pytest.mark.config(
                CORP_DEFAULT_TARIFF_PLANS={
                    'rus': {
                        'tariff_plan_series_id': 'tariff_plan_series_id_4',
                    },
                },
            ),
            id='fallback to default tariff failed.'
            ' tariff_zones cache returned {}. Fallback to default tp',
        ),
        pytest.param(
            {
                'tariff_plan_series_id': 'tariff_plan_series_id_1',
                'zone_name': 'spb',
            },
            {
                'tariff': {
                    'id': '5caeed9d1bc8d21af5a07a25',
                    'home_zone': 'spb',
                },
                'disable_paid_supply_price': False,
                'disable_fixed_price': False,
            },
            'categories_spb.json',
            [],
            marks=pytest.mark.config(
                CORP_DEFAULT_TARIFF_PLANS={
                    'rus': {
                        'tariff_plan_series_id': 'tariff_plan_series_id_3',
                    },
                },
            ),
            id='fallback to driver tariff from default tariff plan',
        ),
    ],
)
@pytest.mark.config(
    CORP_CATEGORIES={
        '__default__': {'econom': 'name.econom', 'vip': 'name.vip'},
    },
)
async def test_tariff_current(
        mock_tariff_zones,
        taxi_corp_tariffs_web,
        cache_shield,
        load_json,
        params,
        expected,
        categories_file,
        zones,
):
    mock_tariff_zones.data.zones = {'zones': zones}
    response = await taxi_corp_tariffs_web.get(
        '/v1/tariff/current', params=params,
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
                'tariff_plan_series_id': 'tariff_plan_series_id_2',
                'zone_name': 'moscow',
                'categories': 'vip',
            },
            ['vip'],
            id='get_tariff_current filter one category',
        ),
        pytest.param(
            {
                'tariff_plan_series_id': 'tariff_plan_series_id_2',
                'zone_name': 'moscow',
                'categories': 'vip,econom',
            },
            ['vip', 'econom'],
            id='get_tariff_current filter many categories',
        ),
    ],
)
async def test_tariff_current_categories_filter(
        taxi_corp_tariffs_web, cache_shield, params, expected,
):
    response = await taxi_corp_tariffs_web.get(
        '/v1/tariff/current', params=params,
    )
    data = await response.json()

    categories = [
        category['category_name'] for category in data['tariff']['categories']
    ]

    assert response.status == 200, data
    assert set(categories) == set(expected)


@pytest.mark.parametrize(
    'params, expected',
    [
        (
            {'tariff_plan_series_id': '12345', 'zone_name': 'moscow'},
            {
                'code': 'NOT_FOUND',
                'message': 'Not found',
                'details': {'reason': 'Tariff plan 12345 not found'},
            },
        ),
        (
            {
                'tariff_plan_series_id': 'tariff_plan_series_id_1',
                'zone_name': 'unkn',
            },
            {
                'code': 'NOT_FOUND',
                'message': 'Not found',
                'details': {'reason': 'Driver tariff for zone unkn not found'},
            },
        ),
    ],
)
async def test_tariff_current_failed(
        web_app_client, cache_shield, params, expected,
):
    response = await web_app_client.get('/v1/tariff/current', params=params)
    data = await response.json()

    assert response.status == 404, data
    assert data == expected
