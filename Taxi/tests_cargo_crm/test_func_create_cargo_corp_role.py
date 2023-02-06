import pytest

CORP_CLIENT_ID = 'corporate_client_identifier_test'
BASIC_ROLE = 'owner'
ROLE_ID = '102402048'
PERM_IDS = 'corp_client', 'claims'
PERMS = [{'id': perm, 'name': perm} for perm in PERM_IDS]


@pytest.mark.parametrize(
    'cargo_corp_code, expected_code', ((200, 200), (500, 500)),
)
async def test_func_create_cargo_corp_employee(
        taxi_cargo_crm, mockserver, cargo_corp_code, expected_code,
):
    @mockserver.json_handler('cargo-corp/v1/permission/list')
    def _perm_list_handler(request):
        assert request.headers['X-B2B-Client-Id'] == CORP_CLIENT_ID
        assert request.headers['Accept-Language'] == 'ru'

        body = {'permissions': PERMS}
        return mockserver.make_response(status=200, json=body)

    @mockserver.json_handler(
        'cargo-corp/internal/cargo-corp/v1/client/role/upsert',
    )
    def _role_upsert_handler(request):
        expected_json = {
            'permission_ids': [{'id': perm} for perm in PERM_IDS],
            'is_removable': False,
        }
        assert request.headers['X-B2B-Client-Id'] == CORP_CLIENT_ID
        assert request.headers['Accept-Language'] == 'ru'
        assert request.query['role_name'] == BASIC_ROLE
        assert request.json == expected_json

        body = None
        if cargo_corp_code == 200:
            body = {
                'id': ROLE_ID,
                'name': BASIC_ROLE,
                'permissions': PERMS,
                'is_removable': False,
                'is_general': False,
            }
        return mockserver.make_response(status=cargo_corp_code, json=body)

    request = {'corp_client_id': CORP_CLIENT_ID, 'basic_role': BASIC_ROLE}

    response = await taxi_cargo_crm.post(
        '/functions/create-cargo-corp-role', json=request,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {'role_id': ROLE_ID}
