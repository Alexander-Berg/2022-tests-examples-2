import json

import pytest


@pytest.fixture
def update_client_id_mock(request, patch):
    @patch('taxi.clients.admin.AdminApiClient.get_park')
    async def _get_park(*args, **kwargs):
        return {
            'common_fields': {
                'billing_client_id': {
                    'start_date': '2020-07-17T12:59:55.000000+0300',
                    'client_id': '123',
                },
            },
        }

    @patch('taxi.clients.admin.AdminApiClient.put_common_fields')
    async def _put_common_fields(*args, **kwargs):
        return 'ok'


@pytest.fixture
async def mock_secdist(simple_secdist):
    simple_secdist['settings_override'][
        'PARTNER_CONTRACTS_ADMIN_TOKEN'
    ] = 'abc'
    return simple_secdist


@pytest.mark.servicetest
@pytest.mark.usefixtures('update_client_id_mock')
async def test_update_client_id(
        web_app_client, mock_secdist,  # pylint: disable=redefined-outer-name
):
    data = {'client_id': '321', 'clid': '111', 'start_dt': '123'}
    response = await web_app_client.post(
        '/v1/admin/park/client_id/update', data=json.dumps(data),
    )

    assert response.status == 200
    content = await response.text()
    assert content == ''
