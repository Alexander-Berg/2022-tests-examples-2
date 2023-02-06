import pytest

CORP_CLIENT_ID = 'corporate_client_identifier_test'
CORP_CLIENT_ID_1 = 'corporate_client_identifier_test_1'
EMPLOYEE_YANDEX_UID = 'owner_yandex_uid'


@pytest.mark.parametrize(
    'num_of_clients, expected_times_called, is_somebody_else',
    ((0, 1, False), (1, 1, False), (1, 0, True), (2, 0, True)),
)
async def test_func_disable_2fa_light(
        taxi_cargo_crm,
        mockserver,
        num_of_clients,
        expected_times_called,
        is_somebody_else,
):
    @mockserver.json_handler(
        '/cargo-corp/internal/cargo-corp/v1/employee/corp-client/list',
    )
    def _handler_cargo_corp(request):
        corp_clients = []
        if num_of_clients == 2:
            corp_clients = [
                {'id': CORP_CLIENT_ID, 'is_registration_finished': True},
                {'id': CORP_CLIENT_ID_1, 'is_registration_finished': True},
            ]
        if num_of_clients == 1 and is_somebody_else:
            corp_clients = [
                {'id': CORP_CLIENT_ID_1, 'is_registration_finished': True},
            ]
        if num_of_clients == 1 and not is_somebody_else:
            corp_clients = [
                {'id': CORP_CLIENT_ID, 'is_registration_finished': True},
            ]
        return {'corp_clients': corp_clients}

    @mockserver.json_handler('/passport-card-verification/delete_list')
    def _handler_delete_list(request):
        assert request.json['items'] == [EMPLOYEE_YANDEX_UID]
        return mockserver.make_response(status=200, json={})

    request = {
        'corp_client_id': CORP_CLIENT_ID,
        'yandex_uid': EMPLOYEE_YANDEX_UID,
    }

    response = await taxi_cargo_crm.post(
        '/functions/disable-2fa-light', json=request,
    )

    assert _handler_delete_list.times_called == expected_times_called

    assert response.status_code == 200
    assert response.json() == {}
