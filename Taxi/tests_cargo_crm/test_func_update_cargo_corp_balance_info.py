import pytest

from tests_cargo_crm import const

CORP_CLIENT_ID = 'corporate_client_identifier_test'
EMPLOYEE_YANDEX_UID = 'owner_yandex_uid'
BALANCE_FORM = {
    'billing_id': const.BILLING_ID,
    'person_id': const.BILLING_ID,
    'contract': const.CONTRACT,
}


@pytest.mark.parametrize(
    'cargo_corp_code, expected_code', ((200, 200), (500, 500)),
)
async def test_func_create_cargo_corp_employee(
        taxi_cargo_crm, mockserver, cargo_corp_code, expected_code,
):
    @mockserver.json_handler(
        '/cargo-corp/internal/cargo-corp/v1/client/balance/upsert',
    )
    def _handler(request):
        assert request.headers['X-B2B-Client-Id'] == CORP_CLIENT_ID
        assert request.json == BALANCE_FORM

        return mockserver.make_response(status=cargo_corp_code, json={})

    request = {
        'corp_client_id': CORP_CLIENT_ID,
        'yandex_uid': EMPLOYEE_YANDEX_UID,
        'balance_created_form': BALANCE_FORM,
    }

    response = await taxi_cargo_crm.post(
        '/functions/update-cargo-corp-balance-info', json=request,
    )
    assert response.status_code == expected_code
