import pytest

INF = float('+inf')


ROLE_MAP = {
    'role1': {
        '_id': 'role1',
        'name': 'Продавцы',
        'is_cabinet_only': False,
        'counters': {'users': 0},
        'limit': 5000,
        'classes': ['econom'],
        'deletable': True,
        'putable': True,
        'no_specific_limit': False,
        'period': 'month',
        'orders': {'no_specific_limit': True},
        'restrictions': [],
        'geo_restrictions': [],
    },
    'role7': {
        '_id': 'role7',
        'counters': {'users': 0},
        'is_cabinet_only': False,
        'name': 'no_specific_limit',
        'classes': ['econom'],
        'deletable': True,
        'putable': True,
        'no_specific_limit': True,
        'period': 'month',
        'orders': {'no_specific_limit': True},
        'restrictions': [],
        'geo_restrictions': [],
    },
    'role8': {
        '_id': 'role8',
        'counters': {'users': 0},
        'name': 'country_categories',
        'classes': ['econom'],
        'is_cabinet_only': True,
        'deletable': False,
        'putable': False,
        'no_specific_limit': True,
        'period': 'day',
        'orders': {'limit': 1000, 'no_specific_limit': False},
        'restrictions': [],
        'geo_restrictions': [
            {'source': 'geo_id_1', 'destination': 'geo_id_2'},
        ],
    },
}


@pytest.mark.parametrize(
    ['role_id', 'expected_result'],
    [
        ('role1', ROLE_MAP['role1']),
        ('role7', ROLE_MAP['role7']),
        ('role8', ROLE_MAP['role8']),
    ],
)
@pytest.mark.config(
    CORP_CATEGORIES={'__default__': {'econom': 'country_econom'}},
)
async def test_single_get(web_app_client, role_id, expected_result):
    response = await web_app_client.get(
        '/v1/roles', params={'role_id': role_id},
    )
    response_json = await response.json()

    assert response.status == 200, 'Response is %s' % response_json
    assert response_json == expected_result


@pytest.mark.parametrize(['role_id', 'response_code'], [('role404', 404)])
async def test_single_get_fail(web_app_client, role_id, response_code):
    response = await web_app_client.get(
        '/v1/roles', params={'role_id': role_id},
    )

    assert response.status == response_code
    response_data = await response.json()
    assert response_data == {
        'code': 'NOT_FOUND',
        'message': 'Not found',
        'reason': 'Role role404 not found',
    }
