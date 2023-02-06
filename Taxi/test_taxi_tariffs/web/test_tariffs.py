# pylint: disable=unused-wildcard-import
# pylint: disable=import-only-modules
# pylint: disable=redefined-outer-name
# flake8: noqa: F401
# flake8: noqa: F811

import copy
import http

import pytest

MOSCOW_TARIFF_ID = '5caeed9d1bc8d21af5a07a24'


@pytest.mark.parametrize(
    ['tariff_id', 'expected_status', 'expected_file'],
    [(MOSCOW_TARIFF_ID, 200, 'moscow.json')],
)
@pytest.mark.parametrize(
    'exp_name',
    [
        pytest.param(
            'fallback_enabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_enabled.json',
                )
            ),
        ),
        pytest.param(
            'fallback_disabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_disabled.json',
                )
            ),
        ),
    ],
)
async def test_get_tariff(
        web_app_client,
        cache_shield,
        tariffs_context,
        mock_individual_tariffs,
        tariff_id,
        expected_status,
        expected_file,
        load_json,
        exp_name,
):
    tariffs_context.set_tariffs_list_response(
        load_json('tariff_by_zones_response.json'),
    )
    response = await web_app_client.get('/v1/tariff', params={'id': tariff_id})
    data = await response.json()
    assert response.status == expected_status, data
    assert data == load_json(expected_file)


@pytest.mark.parametrize(
    ['tariff_id', 'expected_status', 'expected_data'],
    [
        (
            'not_found_id',
            404,
            {
                'code': 'not_found',
                'message': 'can not find tariff: not_found_id',
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'exp_name',
    [
        pytest.param(
            'fallback_enabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_enabled.json',
                )
            ),
        ),
        pytest.param(
            'fallback_disabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_disabled.json',
                )
            ),
        ),
    ],
)
async def test_get_tariff_failed(
        web_app_client,
        cache_shield,
        tariffs_context,
        mock_individual_tariffs,
        tariff_id,
        expected_status,
        expected_data,
        exp_name,
):
    tariffs_context.set_error(404, expected_data)
    response = await web_app_client.get('/v1/tariff', params={'id': tariff_id})
    data = await response.json()
    assert response.status == expected_status, data
    assert data == expected_data


@pytest.mark.parametrize(
    ['category_id', 'expected_status', 'expected_file'],
    [
        ('05156a5d865a429a960ddb4dde20e735', 200, 'moscow.json'),
        ('59d3027127a542989074e7cdfe6122a5', 200, 'moscow.json'),
    ],
)
@pytest.mark.parametrize(
    'exp_name',
    [
        pytest.param(
            'fallback_enabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_enabled.json',
                ),
            ),
        ),
        pytest.param(
            'fallback_disabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_disabled.json',
                ),
            ),
        ),
    ],
)
async def test_get_tariff_by_category(
        web_app_client,
        cache_shield,
        tariffs_context,
        individual_tariffs_mockserver,
        category_id,
        expected_status,
        expected_file,
        exp_name,
        load_json,
):
    expected_data = load_json(expected_file)

    tariffs_context.set_tariffs(load_json('individual_tariffs.json'))

    response = await web_app_client.get(
        '/v1/tariff/by_category', params={'category_id': category_id},
    )
    data = await response.json()
    assert response.status == expected_status, data
    assert data == expected_data


@pytest.mark.parametrize(
    ['category_id', 'expected_status', 'expected_data'],
    [
        (
            'not_found_id',
            404,
            {
                'code': 'not_found',
                'message': 'can not find tariff with category: not_found_id',
            },
        ),
        (
            MOSCOW_TARIFF_ID,
            404,
            {
                'code': 'not_found',
                'message': (
                    f'can not find tariff with category: {MOSCOW_TARIFF_ID}'
                ),
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'exp_name',
    [
        pytest.param(
            'fallback_enabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_enabled.json',
                )
            ),
        ),
        pytest.param(
            'fallback_disabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_disabled.json',
                )
            ),
        ),
    ],
)
async def test_get_tariff_by_category_failed(
        web_app_client,
        cache_shield,
        tariffs_context,
        individual_tariffs_mockserver,
        category_id,
        exp_name,
        expected_status,
        expected_data,
):
    tariffs_context.set_error(expected_status, expected_data)
    response = await web_app_client.get(
        '/v1/tariff/by_category', params={'category_id': category_id},
    )
    data = await response.json()
    assert response.status == expected_status, data
    assert data == expected_data


TARIFFS = {
    'tariffs': [
        {
            'id': MOSCOW_TARIFF_ID,
            'home_zone': 'moscow',
            'activation_zone': 'moscow_activation',
            'related_zones': ['moscow', 'moscow_activation', 'foo'],
            'categories_names': ['econom', 'mkk', 'vip'],
        },
        {
            'id': '5caeed9d1bc8d21af5a07a25',
            'home_zone': 'spb',
            'activation_zone': 'spb_activation',
            'related_zones': ['spb', 'spb_activation', 'bar'],
            'categories_names': [],
        },
    ],
}

INDIVIDUAL_TARIFFS_RESPONSE = [
    {
        'id': MOSCOW_TARIFF_ID,
        'home_zone': 'moscow',
        'activation_zone': 'moscow_activation',
        'related_zones': ['moscow', 'moscow_activation', 'foo'],
        'categories_names': ['econom', 'mkk', 'vip'],
        'city_id': 'city_id',
        'country': 'country',
        'timezone': 'timezone',
    },
    {
        'id': '5caeed9d1bc8d21af5a07a25',
        'home_zone': 'spb',
        'activation_zone': 'spb_activation',
        'related_zones': ['spb', 'spb_activation', 'bar'],
        'categories_names': [],
        'city_id': 'city_id',
        'country': 'country',
        'timezone': 'timezone',
    },
]


@pytest.mark.parametrize('extended_with_price', (False, True, None))
@pytest.mark.parametrize(
    'exp_name',
    [
        pytest.param(
            'fallback_enabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_enabled.json',
                )
            ),
        ),
        pytest.param(
            'fallback_disabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_disabled.json',
                )
            ),
        ),
    ],
)
async def test_get_tariffs(
        web_app_client,
        cache_shield,
        tariffs_context,
        mock_individual_tariffs,
        extended_with_price,
        exp_name,
        load_json,
):
    expected_minimal_prices = load_json('extended_with_price.json')

    tariffs = copy.deepcopy(INDIVIDUAL_TARIFFS_RESPONSE)
    if extended_with_price:
        tariffs[0]['minimal_prices'] = expected_minimal_prices
    tariffs_context.set_tariffs(tariffs)

    params = None
    if extended_with_price is not None:
        params = {'extended_with_price': str(extended_with_price)}
    response = await web_app_client.get('/v1/tariffs', params=params)
    data = await response.json()
    assert response.status == 200
    minimal_prices = list()
    for tariff in data['tariffs']:
        tariff['categories_names'].sort()
        if tariff.get('minimal_prices') is not None:
            minimal_prices.extend(tariff.pop('minimal_prices'))
    assert data == TARIFFS
    if extended_with_price:
        assert minimal_prices == expected_minimal_prices
    else:
        assert not minimal_prices


@pytest.mark.parametrize(
    'zone, expected_status, expected_data',
    (
        ('moscow', http.HTTPStatus.OK, 'moscow.json'),
        (
            'invalid',
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'not_found',
                'message': 'can not find tariff with zone=invalid',
            },
        ),
    ),
)
@pytest.mark.parametrize(
    'exp_name',
    [
        pytest.param(
            'fallback_enabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_enabled.json',
                )
            ),
        ),
        pytest.param(
            'fallback_disabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_disabled.json',
                )
            ),
        ),
    ],
)
async def test_get_current_tariff(
        web_app_client,
        tariffs_context,
        mock_individual_tariffs,
        zone,
        expected_status,
        expected_data,
        cache_shield,
        load_json,
        exp_name,
):
    if isinstance(expected_data, str):
        expected_data = load_json(expected_data)
        tariffs_context.set_tariffs_list_response(
            load_json('tariff_by_zones_response.json'),
        )
    else:
        tariffs_context.set_error(expected_status, expected_data)

    response = await web_app_client.get(
        '/v1/tariff/current', params={'zone': zone},
    )
    assert response.status == expected_status
    assert await response.json() == expected_data
