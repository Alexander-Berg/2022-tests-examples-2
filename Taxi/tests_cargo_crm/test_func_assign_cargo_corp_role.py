import pytest

CORP_CLIENT_ID = 'corporate_client_identifier_test'
EMPLOYEE_YANDEX_UID = 'owner_yandex_uid'
ROLE_ID = '10242048'


@pytest.mark.parametrize(
    'cargo_corp_code, expected_code', ((200, 200), (500, 500)),
)
async def test_func_create_cargo_corp_employee(
        taxi_cargo_crm, mockserver, cargo_corp_code, expected_code,
):
    @mockserver.json_handler(
        '/cargo-corp/internal/cargo-corp/v1/client/role/bulk-assign',
    )
    def _handler(request):
        expected_json = {
            'employees': [{'id': EMPLOYEE_YANDEX_UID, 'revision': 1}],
        }
        assert request.headers['X-B2B-Client-Id'] == CORP_CLIENT_ID
        assert request.query['role_id'] == str(ROLE_ID)
        assert request.json == expected_json

        return mockserver.make_response(status=cargo_corp_code, json={})

    request = {
        'corp_client_id': CORP_CLIENT_ID,
        'yandex_uid': EMPLOYEE_YANDEX_UID,
        'role_id': ROLE_ID,
        'revision': 1,
    }

    response = await taxi_cargo_crm.post(
        '/functions/assign-cargo-corp-role', json=request,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {}
