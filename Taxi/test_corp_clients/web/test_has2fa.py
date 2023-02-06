# pylint: disable=redefined-outer-name
import pytest


@pytest.fixture
def get_info_by_uid_mock(patch, load_json):
    @patch('taxi.clients.passport.PassportClient.get_info_by_uid')
    async def _get_info_by_uid(*args, **kwargs):
        return {'login': 'company_login', 'attributes': {'200': '1'}}


async def test_has2fa(web_app_client, load_json, get_info_by_uid_mock):
    response = await web_app_client.get(
        '/v1/has_2fa', params={'client_id': 'client_id_1'},
    )

    assert response.status == 200
    response_json = await response.json()

    assert response_json['has_2fa']
