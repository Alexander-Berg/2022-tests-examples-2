import pytest


@pytest.mark.config(
    TVM_RULES=[{'dst': 'personal', 'src': 'hiring-trigger-zend'}],
)
async def test_request(
        web_app_client,
        load_json,
        mockserver,
        patch,
        mock_infranaim_api_appdrivers,
):
    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    # pylint: disable=W0612
    async def retrieve(*args, **kwargs):
        return {
            'stat': 'stat',
            'is_loyal': 'is_loyal',
            'is_yandex_staff': 'is_yandex_staff',
            'is_taxi_staff': 'is_taxi_staff',
            'id': '00000d26b5f273e600000001',
            'phone': '+70001112233',
            'type': 'type',
            'spam_stat': 'spam_stat',
            'blocked_times': 'blocked_times',
            'personal_phone_id': '5b527dc28d804c9db5497e1ec1d13aa1',
        }

    headers = {
        'X-YaTaxi-User': 'personal_phone_id=5b527dc28d804c9db5497e1ec1d13aa1',
    }
    data = {'params': {'name': 'Jonh Doe'}}
    handler_app_drivers = mock_infranaim_api_appdrivers()
    response = await web_app_client.post(
        '/v1/data/infranaim-api/app_drivers', headers=headers, json=data,
    )
    assert response.status == 200
    assert handler_app_drivers.has_calls
