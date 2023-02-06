import pytest


async def test_v2_admin_fetch_negative(taxi_dispatch_settings_web):
    response = await taxi_dispatch_settings_web.get(
        '/v2/admin/fetch',
        params={
            'zone_name': 'nonexisting_test_zone_1',
            'tariff_name': 'test_tariff_1',
        },
    )
    assert response.status == 404
    content = await response.json()
    assert content['code'] == 'no_such_zone'

    response = await taxi_dispatch_settings_web.get(
        '/v2/admin/fetch',
        params={
            'zone_name': 'test_zone_1',
            'tariff_name': 'nonexisting_test_tariff_1',
        },
    )
    assert response.status == 404
    content = await response.json()
    assert content['code'] == 'no_such_tariff'

    response = await taxi_dispatch_settings_web.get(
        '/v2/admin/fetch',
        params={
            'zone_name': 'test_zone_1',
            'tariff_name': 'nonexisting_test_tariff_1',
        },
    )
    assert response.status == 404
    content = await response.json()
    assert content['code'] == 'no_such_tariff'

    await taxi_dispatch_settings_web.invalidate_caches()
    response = await taxi_dispatch_settings_web.get(
        '/v2/admin/fetch',
        params={'zone_name': 'test_zone_1', 'tariff_name': 'test_tariff_4'},
    )
    assert response.status == 404
    content = await response.json()
    assert content['code'] == 'no_such_settings'


@pytest.mark.parametrize(
    'zone,tariff,fetch_policy,expected_response',
    [
        # check zone + tariff
        (
            'test_zone_1',
            'test_tariff_1',
            'matched_or_nearest_default',
            {
                'are_default_settings': False,
                'settings': [
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 3, 'version': 3},
                ],
            },
        ),
        # check zone + tariff + nearest_default
        (
            'test_zone_1',
            'test_tariff_1',
            'nearest_default',
            {
                'are_default_settings': True,
                'settings': [
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 2, 'version': 2},
                ],
            },
        ),
        # check nearest_default for zone + __default__base__
        (
            'test_zone_1',
            '__default__base__',
            'nearest_default',
            {
                'are_default_settings': True,
                'settings': [
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 6, 'version': 6},
                ],
            },
        ),
        # check nearest_default for __default__ + __default__base__
        ('__default__', '__default__base__', 'nearest_default', 404),
        # check fallback with resetted settings: zone + __default__base__
        (
            'test_zone_1',
            'test_tariff_2',
            'matched_or_nearest_default',
            {
                'are_default_settings': True,
                'settings': [
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 2, 'version': 2},
                ],
            },
        ),
        # check fallback with resetted settings: zone + __default__base__
        # + nearest_default
        (
            'test_zone_1',
            'test_tariff_2',
            'nearest_default',
            {
                'are_default_settings': True,
                'settings': [
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 2, 'version': 2},
                ],
            },
        ),
        # check fallback: zone + __default__base__
        (
            'test_zone_1',
            'test_tariff_3',
            'matched_or_nearest_default',
            {
                'are_default_settings': True,
                'settings': [
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 2, 'version': 2},
                ],
            },
        ),
        # check fallback: zone + __default__base__ + nearest_default
        (
            'test_zone_1',
            'test_tariff_3',
            'nearest_default',
            {
                'are_default_settings': True,
                'settings': [
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 2, 'version': 2},
                ],
            },
        ),
        # check fallback: __default__ zone + tariff
        (
            'test_zone_2',
            'test_tariff_1',
            'matched_or_nearest_default',
            {
                'are_default_settings': True,
                'settings': [
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 5, 'version': 5},
                ],
            },
        ),
        # check fallback: __default__ zone + tariff + nearest_default
        (
            'test_zone_2',
            'test_tariff_1',
            'nearest_default',
            {
                'are_default_settings': True,
                'settings': [
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 5, 'version': 5},
                ],
            },
        ),
        # check fallback: __default__ zone + __default__base__
        (
            'test_zone_2',
            'test_tariff_2',
            'matched_or_nearest_default',
            {
                'are_default_settings': True,
                'settings': [
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 6, 'version': 6},
                ],
            },
        ),
        # check fallback: __default__ zone + __default__base__
        # + nearest_default
        (
            'test_zone_2',
            'test_tariff_2',
            'nearest_default',
            {
                'are_default_settings': True,
                'settings': [
                    {'name': 'QUERY_LIMIT_LIMIT', 'value': 6, 'version': 6},
                ],
            },
        ),
    ],
)
async def test_v2_admin_fetch_positive(
        taxi_dispatch_settings_web,
        zone,
        tariff,
        fetch_policy,
        expected_response,
):

    response = await taxi_dispatch_settings_web.get(
        '/v2/admin/fetch',
        params={
            'zone_name': zone,
            'tariff_name': tariff,
            'fetch_policy': fetch_policy,
        },
    )
    if isinstance(expected_response, dict):
        assert response.status == 200
        content = await response.json()
        content['settings'].sort(key=lambda x: x['name'])
        assert content == expected_response
    else:
        assert response.status == expected_response
