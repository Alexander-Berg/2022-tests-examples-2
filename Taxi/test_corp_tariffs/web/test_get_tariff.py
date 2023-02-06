import pytest


@pytest.mark.parametrize(
    ['params', 'expected', 'categories_file'],
    [
        pytest.param(
            {'id': '5caeed9d1bc8d21af5a07a24-multizonal-tariff_plan_1'},
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
            id='custom multizonal moscow',
        ),
        pytest.param(
            {
                'id': (
                    '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1'
                    '--callcenter'
                ),
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
            },
            'categories_ekb_callcenter.json',
            id='custom multizonal ekb with application multiplier',
        ),
        pytest.param(
            {'id': '5caeed9d1bc8d21af5a07a24-moscow-tariff_plan_2'},
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
            id='inherited moscow',
        ),
        pytest.param(
            {'id': '5caeed9d1bc8d21af5a07a24'},
            {
                'tariff': {
                    'id': '5caeed9d1bc8d21af5a07a24',
                    'home_zone': 'moscow',
                },
                'disable_paid_supply_price': False,
                'disable_fixed_price': False,
            },
            'categories_moscow_driver.json',
            id='driver_tariff moscow',
        ),
    ],
)
@pytest.mark.parametrize(
    'fallback',
    [
        pytest.param(
            'enabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_enabled.json',
                ),
            ),
        ),
        pytest.param(
            'disabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_disabled.json',
                ),
            ),
        ),
    ],
)
@pytest.mark.config(
    CORP_TARIFFS_USE_APP_MULTIPLIERS=True,
    CORP_CATEGORIES={
        '__default__': {'econom': 'name.econom', 'vip': 'name.vip'},
    },
    CORP_TARIFFS_INDIVIDUAL_TARIFFS_CACHE_SETTINGS=False,
)
async def test_tariff_current(
        web_app_client,
        cache_shield,
        db,
        individual_tariffs_mockserver,
        load_json,
        params,
        expected,
        categories_file,
        fallback,
):
    response = await web_app_client.get('/v1/tariff', params=params)
    data = await response.json()

    expected['tariff']['categories'] = load_json(categories_file)

    assert response.status == 200, data
    assert data == expected


@pytest.mark.parametrize(
    ['params', 'expected'],
    [
        pytest.param(
            {'id': '5caeed9d1bc8d21af5a07a24', 'categories': 'econom'},
            ['econom'],
            id='get_tariff filter one category',
        ),
        pytest.param(
            {'id': '5caeed9d1bc8d21af5a07a24', 'categories': 'vip,econom'},
            ['econom', 'vip'],
            id='get_tariff filter many categories',
        ),
    ],
)
@pytest.mark.parametrize(
    'fallback',
    [
        pytest.param(
            'enabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_enabled.json',
                ),
            ),
        ),
        pytest.param(
            'disabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_disabled.json',
                ),
            ),
        ),
    ],
)
@pytest.mark.config(CORP_TARIFFS_INDIVIDUAL_TARIFFS_CACHE_SETTINGS=False)
async def test_tariff_current_categories_filter(
        taxi_corp_tariffs_web,
        cache_shield,
        db,
        individual_tariffs_mockserver,
        params,
        expected,
        fallback,
):
    response = await taxi_corp_tariffs_web.get('/v1/tariff', params=params)
    data = await response.json()

    assert response.status == 200, data

    categories = [
        category['category_name'] for category in data['tariff']['categories']
    ]

    assert set(categories) == set(expected)


@pytest.mark.parametrize(
    'params, expected',
    [
        pytest.param(
            {'id': '123-456-789'},
            {
                'code': 'NOT_FOUND',
                'message': 'Not found',
                'details': {
                    'reason': (
                        'Driver tariff not found: 123; '
                        'Corp tariff not found: 456; '
                        'Corp tariff plan not found: 789'
                    ),
                },
            },
            id='compose_id(corp_tariff)',
        ),
        pytest.param(
            {'id': '123'},
            {
                'code': 'NOT_FOUND',
                'message': 'Not found',
                'details': {'reason': 'Driver tariff not found: 123'},
            },
            id='plain_id(driver_tariff)',
        ),
    ],
)
@pytest.mark.parametrize(
    'fallback',
    [
        pytest.param(
            'enabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_enabled.json',
                ),
            ),
        ),
        pytest.param(
            'disabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_disabled.json',
                ),
            ),
        ),
    ],
)
async def test_tariff_current_failed(
        web_app_client,
        cache_shield,
        db,
        individual_tariffs_mockserver,
        params,
        expected,
        fallback,
):
    response = await web_app_client.get('/v1/tariff', params=params)
    data = await response.json()

    assert response.status == 404, data
    assert data == expected
