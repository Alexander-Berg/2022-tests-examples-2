import pytest

KNOWN_ID_1 = 'f6e811b3-3062-493b-ad73-8ca554a613bf'
KNOWN_ID_2 = '92ad3bcf-13c9-47f8-b85f-fbf4c99d29de'
KNOWN_ID_3 = 'b51cb0fd-85ee-4a08-8abc-3a130317d447'
UNKNOWN_ID_1 = '1c7d1363-b8f3-4ce0-919c-3a9d8cb14405'
NEW_ID_1 = 'f0840a89-2509-4c3c-86f3-9f66872fde6d'

CURSOR_LIMIT_2_EMPTY = 'eyJvZmZzZXQiOjAsImxpbWl0IjoyfQ'
CURSOR_LIMIT_2_EMPTY_PAGE_2 = 'eyJvZmZzZXQiOjIsImxpbWl0IjoyfQ'


def _get_organization(organization_id, pgsql):
    cursor = pgsql['edc-app-organizations'].cursor()
    cursor.execute(
        'SELECT id, name, city_id, address '
        'from edc_app_organizations.organizations '
        f'WHERE id=\'{organization_id}\'',
    )
    row = cursor.fetchone()
    if row:
        return {
            'id': row[0],
            'name': row[1],
            'city_id': row[2],
            'address': row[3],
        }
    return {}


@pytest.mark.pgsql(
    'edc-app-organizations', files=['pg_edc_app_organizations.sql'],
)
@pytest.mark.parametrize(
    'params',
    [
        # known id
        (
            {
                'headers': {},
                'query': {'id': KNOWN_ID_1},
                'response_code': 200,
                'response_body': {
                    'id': KNOWN_ID_1,
                    'name': 'Organization 1 LLC',
                    'city_id': '4522a7d9-6fa4-43e7-9a6e-ddeeefe1f455',
                    'address': 'Lenina str, 1',
                },
            }
        ),
        # unknown id
        (
            {
                'headers': {'X-Driver-Session': 'session_000'},
                'query': {'id': UNKNOWN_ID_1},
                'response_code': 404,
                'response_body': {
                    'code': 'organization_not_found',
                    'message': 'Organization not found',
                },
            }
        ),
    ],
)
async def test_organizations_item_get(taxi_edc_app_organizations, params):
    response = await taxi_edc_app_organizations.get(
        '/v1/organizations/item',
        headers=params['headers'],
        params=params['query'],
    )

    assert response.status_code == params['response_code']
    if response:
        actual_response_body = response.json()
        assert actual_response_body == params['response_body']


@pytest.mark.pgsql(
    'edc-app-organizations', files=['pg_edc_app_organizations.sql'],
)
@pytest.mark.parametrize(
    'params',
    [
        (
            {
                'headers': {},
                'id': KNOWN_ID_1,
                'response_code': 200,
                'response_body': {},
                'data': {
                    'address': 'Mira str, 1',
                    'city_id': '4522a7d9-6fa4-43e7-9a6e-ddeeefe1f455',
                    'name': 'Organization 1 LLC NEW',
                },
            }
        ),
    ],
)
async def test_organizations_item_put(
        taxi_edc_app_organizations, params, pgsql,
):
    response = await taxi_edc_app_organizations.put(
        '/v1/organizations/item',
        headers=params['headers'],
        params={'id': params['id']},
        json=params['data'],
    )

    assert response.status_code == params['response_code']
    if response:
        actual_response_body = response.json()
        assert actual_response_body == params['response_body']

    org = _get_organization(params['id'], pgsql)
    assert org['address'] == params['data']['address']
    assert org['city_id'] == params['data']['city_id']
    assert org['name'] == params['data']['name']


@pytest.mark.pgsql(
    'edc-app-organizations', files=['pg_edc_app_organizations.sql'],
)
@pytest.mark.parametrize(
    'params',
    [
        (
            {
                'headers': {},
                'id': NEW_ID_1,
                'response_code': 200,
                'response_body': {},
                'data': {
                    'id': NEW_ID_1,
                    'address': 'Mira str, 1',
                    'city_id': '4522a7d9-6fa4-43e7-9a6e-ddeeefe1f455',
                    'name': 'Organization 1 LLC NEW',
                },
            }
        ),
    ],
)
async def test_organizations_item_post(
        taxi_edc_app_organizations, params, pgsql,
):
    response = await taxi_edc_app_organizations.post(
        '/v1/organizations', headers=params['headers'], json=params['data'],
    )

    assert response.status_code == params['response_code']
    if response:
        actual_response_body = response.json()
        assert actual_response_body == params['response_body']

    org = _get_organization(params['id'], pgsql)
    assert org == params['data']


@pytest.mark.pgsql(
    'edc-app-organizations', files=['pg_edc_app_organizations.sql'],
)
@pytest.mark.parametrize(
    'params',
    [
        (
            {
                'headers': {},
                'json': {'limit': 2},
                'response_code': 200,
                'response_body': {'cursor': CURSOR_LIMIT_2_EMPTY},
            }
        ),
    ],
)
async def test_organizations_search_post(taxi_edc_app_organizations, params):
    response = await taxi_edc_app_organizations.post(
        '/v1/organizations/search',
        headers=params['headers'],
        json=params['json'],
    )

    assert response.status_code == params['response_code']
    if response:
        actual_response_body = response.json()
        assert actual_response_body == params['response_body']


@pytest.mark.pgsql(
    'edc-app-organizations', files=['pg_edc_app_organizations.sql'],
)
@pytest.mark.parametrize(
    'params',
    [
        (
            {
                'headers': {},
                'query': {'cursor': CURSOR_LIMIT_2_EMPTY},
                'response_code': 200,
                'response_body': {
                    'cursor': CURSOR_LIMIT_2_EMPTY,
                    'cursor_next': CURSOR_LIMIT_2_EMPTY_PAGE_2,
                    'items': [
                        {
                            'address': 'Lenina str, 1',
                            'city_id': '4522a7d9-6fa4-43e7-9a6e-ddeeefe1f455',
                            'id': KNOWN_ID_1,
                            'name': 'Organization 1 LLC',
                        },
                        {
                            'address': 'Lenina str, 2',
                            'city_id': '4522a7d9-6fa4-43e7-9a6e-ddeeefe1f455',
                            'id': KNOWN_ID_2,
                            'name': 'Organization 2 Ltd',
                        },
                    ],
                },
            }
        ),
        (
            {
                'headers': {},
                'query': {'cursor': CURSOR_LIMIT_2_EMPTY_PAGE_2},
                'response_code': 200,
                'response_body': {
                    'cursor': CURSOR_LIMIT_2_EMPTY_PAGE_2,
                    'cursor_prev': CURSOR_LIMIT_2_EMPTY,
                    'items': [
                        {
                            'address': 'Lenina str, 3',
                            'city_id': '4522a7d9-6fa4-43e7-9a6e-ddeeefe1f455',
                            'id': KNOWN_ID_3,
                            'name': 'Organization 3 Ltd',
                        },
                    ],
                },
            }
        ),
    ],
)
async def test_organizations_search_get(taxi_edc_app_organizations, params):
    response = await taxi_edc_app_organizations.get(
        '/v1/organizations/search',
        headers=params['headers'],
        params=params['query'],
    )

    assert response.status_code == params['response_code']
    if response:
        actual_response_body = response.json()
        assert actual_response_body == params['response_body']
