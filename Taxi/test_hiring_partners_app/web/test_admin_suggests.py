import pytest

ROUTE_PERMISSIONS = '/admin/v1/suggests/permissions-groups'
ROUTE_ACCOUNT_PARK_IDS = '/admin/v1/suggests/account-park-ids'


@pytest.mark.parametrize(
    'route',
    (
        '/admin/v1/suggests/juridical-status/organizations',
        '/admin/v1/suggests/juridical-status/users',
        '/admin/v1/suggests/meta-roles',
        '/admin/v1/suggests/organizations',
        '/admin/v1/suggests/roles',
        '/admin/v1/suggests/user-statuses',
    ),
)
async def test_simple_suggests(taxi_hiring_partners_app_web, route):
    response = await taxi_hiring_partners_app_web.get(route)
    assert response.status == 200
    body = await response.json()
    assert body
    assert body['values']


@pytest.mark.parametrize(
    'organization_id, is_body_empty',
    [('0001', False), (None, False), ('NO_HIRE', True)],
)
@pytest.mark.parametrize(
    'route',
    ('/admin/v1/suggests/permissions-groups', '/admin/v1/suggests/user-ids'),
)
async def test_suggests_permissions_groups(
        taxi_hiring_partners_app_web, organization_id, is_body_empty, route,
):

    params = {'organization_id': organization_id} if organization_id else None
    response = await taxi_hiring_partners_app_web.get(
        ROUTE_PERMISSIONS, params=params,
    )
    assert response.status == 200
    body = await response.json()
    assert body
    assert bool(body['values']) is not is_body_empty


async def test_account_park_ids(taxi_hiring_partners_app_web):
    response = await taxi_hiring_partners_app_web.get(ROUTE_ACCOUNT_PARK_IDS)
    assert response.status == 200
    body = await response.json()
    assert body
    assert body == {'values': [{'value': 'Value', 'title': 'Title'}]}
