import pytest

from test_hiring_partners_app import conftest


ROUTE = '/v1/users/personal-form-link'


@pytest.mark.usefixtures('mock_personal_api')
@pytest.mark.parametrize(
    'ya_cc_response, status_code',
    [([conftest.YA_CC_LINK, False], 200), ([conftest.YA_CC_LINK, True], 400)],
)
async def test_users_account_valid(
        taxi_hiring_partners_app_web, mock_ya_cc, ya_cc_response, status_code,
):
    mock_ya_cc['response'] = ya_cc_response
    headers = {'X-Yandex-Login': 'some'}
    response = await taxi_hiring_partners_app_web.get(ROUTE, headers=headers)
    assert response.status == status_code
    if status_code != 200:
        return
    body = await response.json()
    assert body['url'] == conftest.YA_CC_LINK
