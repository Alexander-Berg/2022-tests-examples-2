import pytest


ROUTE = '/v1/subscriptions/suggests'


@pytest.mark.usefixtures('sub_suggests_fill')
@pytest.mark.parametrize('name', ['status', 'not_status'])
async def test_statuses(pgsql, make_tariffs_request, name):
    params = {'name': name}
    response = await make_tariffs_request(ROUTE, method='get', params=params)
    if name == 'status':
        assert response['suggests']
    else:
        assert not response['suggests']
