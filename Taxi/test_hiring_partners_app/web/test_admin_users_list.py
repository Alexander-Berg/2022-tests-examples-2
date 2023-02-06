import pytest

ROUTE = '/admin/v1/users/list'
REQUESTS_FILE = 'requests.json'


@pytest.mark.usefixtures('mock_personal_api')
@pytest.mark.parametrize(
    'request_name',
    ['default', 'filtered', 'yandex_login', 'phone', 'meta_role', 'status'],
)
async def test_users_list(
        taxi_hiring_partners_app_web, load_json, request_name,
):
    async def make_request(data=None, status=200):
        _response = await taxi_hiring_partners_app_web.post(ROUTE, json=data)
        assert _response.status == status
        return _response

    test_setting = load_json(REQUESTS_FILE)[request_name]
    request = test_setting['REQUEST']
    response_body = test_setting.get('RESPONSE')
    response = await make_request(**request)
    body = await response.json()
    assert body
    if response_body is not None:
        assert body == response_body
