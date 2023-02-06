async def check_fetch_for_json(dispatch_settings, expected_json):
    for expected_settings in expected_json['settings']:
        response = await dispatch_settings.get(
            '/v1/settings/fetch',
            params={
                'zone_name': expected_settings['zone_name'],
                'tariff_name': expected_settings['tariff_name'],
            },
        )
        content = await response.json()
        # Response normalization to prevent flaps
        for setting in content['settings']:
            for param in setting['parameters']:
                param['values'] = dict(sorted(param['values'].items()))

        assert response.status == 200
        assert content == {'settings': [expected_settings]}


async def test_settings_fetch_by_category(taxi_dispatch_settings_web):
    response = await taxi_dispatch_settings_web.get(
        '/v1/settings/fetch?'
        + '&'.join(('zone_name=test_zone_1', 'tariff_name=test_tariff_1')),
    )
    assert response.status == 200

    content = await response.json()

    # Response normalization to prevent flaps
    content['settings'].sort(
        key=lambda setting_obj: (
            setting_obj['zone_name'],
            setting_obj['tariff_name'],
        ),
    )
    for setting in content['settings']:
        for param in setting['parameters']:
            param['values'] = dict(sorted(param['values'].items()))

    scoring_weights = {'SCORING_WEIGHTS': {'ALPHA': 0.3, 'BETA': 1.0}}
    assert content == {
        'settings': [
            {
                'zone_name': 'test_zone_1',
                'tariff_name': 'test_tariff_1',
                'parameters': [
                    {
                        'values': dict(
                            scoring_weights,
                            QUERY_LIMIT_LIMIT=22,
                            QUERY_LIMIT_MAX_LINE_DIST=27,
                        ),
                    },
                ],
            },
        ],
    }


async def test_settings_fetch_by_category_error(taxi_dispatch_settings_web):
    response = await taxi_dispatch_settings_web.get(
        '/v1/settings/fetch?'
        + '&'.join(('zone_name=unknown_zone', 'tariff_name=test_tariff_1')),
    )
    assert response.status == 404


async def test_settings_fetch(taxi_dispatch_settings_web, load_json):
    await check_fetch_for_json(
        taxi_dispatch_settings_web, load_json('expected.json'),
    )
