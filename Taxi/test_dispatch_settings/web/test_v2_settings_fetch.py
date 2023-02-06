async def test_v2_settings_fetch(taxi_dispatch_settings_web):
    response = await taxi_dispatch_settings_web.post(
        '/v2/settings/fetch',
        json={
            'categories': [
                {
                    'zone_name': '__default__',
                    'tariff_name': '__default__group1__',
                },
                {'zone_name': 'zone2', 'tariff_name': 'test_tariff_2'},
            ],
        },
    )
    assert response.status == 200
    assert await response.json() == {
        'settings': [
            {
                'parameters': [{'values': {'INTEGER_POSITIVE_FIELD': 1}}],
                'tariff_name': '__default__group1__',
                'zone_name': '__default__',
            },
            {
                'parameters': [{'values': {'NEW_INTEGER_FIELD': 4}}],
                'tariff_name': 'test_tariff_2',
                'zone_name': 'zone2',
            },
        ],
    }


async def test_v2_settings_fetch_some_non_exist(taxi_dispatch_settings_web):
    response = await taxi_dispatch_settings_web.post(
        '/v2/settings/fetch',
        json={
            'categories': [
                {
                    'zone_name': '__default__',
                    'tariff_name': '__default__group1__',
                },
                {'zone_name': 'zone2', 'tariff_name': '__default__group2__'},
            ],
        },
    )
    assert response.status == 200
    assert await response.json() == {
        'settings': [
            {
                'parameters': [{'values': {'INTEGER_POSITIVE_FIELD': 1}}],
                'tariff_name': '__default__group1__',
                'zone_name': '__default__',
            },
        ],
    }


async def test_v2_settings_fetch_empty(taxi_dispatch_settings_web):
    response = await taxi_dispatch_settings_web.post(
        '/v2/settings/fetch', json={'categories': []},
    )
    assert response.status == 200
    assert await response.json() == {'settings': []}


async def test_v2_settings_fetch_all_non_exist(taxi_dispatch_settings_web):
    response = await taxi_dispatch_settings_web.post(
        '/v2/settings/fetch',
        json={
            'categories': [
                {'zone_name': 'zone2', 'tariff_name': '__default__group2__'},
                {'zone_name': 'non_exist2', 'tariff_name': 'non_exist2'},
            ],
        },
    )
    assert response.status == 200
    assert await response.json() == {'settings': []}
