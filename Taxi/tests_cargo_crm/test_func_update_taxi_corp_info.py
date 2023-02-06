import pytest

CORP_CLIENT_ID = 'some_long_id_string_of_length_32'
YANDEX_UID = '1120000000187371'
COMPANY_INFO = {
    'name': 'test_company_name_edited',
    'country': 'Russia',
    'city': 'Moscow',
    'email': '',
    'website': 'service.ru',
}
COMPANY_INFO_PD = {'email_pd_id': 'test_id'}


@pytest.mark.parametrize(
    ('corp_clients_response_code', 'corp_clients_response_json'),
    (
        pytest.param(200, {}, id='ok'),
        pytest.param(
            400,
            {
                'code': '400',
                'message': 'Changing client\'s country is forbidden',
            },
            id='bad-400',
        ),
        pytest.param(
            403, {'code': '403', 'message': 'Forbidden'}, id='bad-403',
        ),
        pytest.param(
            404, {'code': '404', 'message': 'Client not found'}, id='bad-404',
        ),
        pytest.param(
            406,
            {
                'code': '406',
                'message': 'Duplicate yandex_uid for yandex_login',
            },
            id='bad-406',
        ),
    ),
)
async def test_update_taxi_corp(
        taxi_cargo_crm,
        personal_ctx,
        personal_handler_bulk_retrieve,
        mockserver,
        corp_clients_response_code,
        corp_clients_response_json,
):
    @mockserver.json_handler('/corp-clients-uservices/v1/clients')
    def _handler(request):
        assert request.query['client_id'] == CORP_CLIENT_ID
        assert request.headers['X-Yandex-UID'] == YANDEX_UID
        assert 'country' not in request.json
        for param in ('name', 'city'):
            assert request.json[param] == COMPANY_INFO[param]
        assert request.json['email'] == 'test@service.ru'
        return mockserver.make_response(
            status=corp_clients_response_code, json=corp_clients_response_json,
        )

    personal_ctx.set_emails([{'id': 'test_id', 'value': 'test@service.ru'}])

    response = await taxi_cargo_crm.post(
        '/functions/update-taxi-corp-info',
        json={
            'corp_client_id': CORP_CLIENT_ID,
            'yandex_uid': YANDEX_UID,
            'company_info_form': COMPANY_INFO,
            'company_info_pd_form': COMPANY_INFO_PD,
        },
    )
    expected_code = 200 if corp_clients_response_code == 200 else 500
    assert response.status_code == expected_code
