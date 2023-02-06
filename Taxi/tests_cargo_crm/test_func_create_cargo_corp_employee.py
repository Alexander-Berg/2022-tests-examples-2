import pytest

from tests_cargo_crm import const


CORP_CLIENT_ID = 'corporate_client_identifier_test'
EMPLOYEE_YANDEX_UID = 'owner_yandex_uid'
EMPLOYEE_YANDEX_LOGIN = 'mylogin'
EMPLOYEE_YANDEX_LOGIN_PD_ID = 'mylogin_pd_id'
EMPLOYEE_NAME = 'corporate_client_employee'


@pytest.mark.parametrize('robot_kind', ('api', None))
@pytest.mark.parametrize(
    'cargo_corp_code, expected_code', ((200, 200), (500, 500)),
)
async def test_func_create_cargo_corp_employee(
        taxi_cargo_crm,
        mockserver,
        robot_kind,
        cargo_corp_code,
        expected_code,
        personal_ctx,
        personal_handler_bulk_retrieve,
):
    @mockserver.json_handler(
        'cargo-corp/internal/cargo-corp/v1/client/employee/upsert',
    )
    def _handler(request):
        expected_json = {
            'id': EMPLOYEE_YANDEX_UID,
            'info': {
                'name': EMPLOYEE_NAME,
                'phones': [{'number': const.PHONE}],
                'yandex_login': EMPLOYEE_YANDEX_LOGIN,
            },
            'is_disabled': False,
            'revision': 0,
        }
        if robot_kind:
            expected_json[
                'robot_external_ref'
            ] = f'corp:{CORP_CLIENT_ID}:{robot_kind}'

        assert request.headers['X-B2B-Client-Id'] == CORP_CLIENT_ID
        assert request.json == expected_json

        body = None
        if cargo_corp_code == 200:
            body = dict(expected_json, **{'revision': 1})
        return mockserver.make_response(status=cargo_corp_code, json=body)

    personal_ctx.set_phones([{'id': const.PHONE_PD_ID, 'value': const.PHONE}])

    request = {
        'corp_client_id': CORP_CLIENT_ID,
        'yandex_uid': EMPLOYEE_YANDEX_UID,
        'yandex_login': EMPLOYEE_YANDEX_LOGIN,
        'employee_name': EMPLOYEE_NAME,
        'employee_phone_pd_id': const.PHONE_PD_ID,
        'robot_kind': robot_kind,
    }

    response = await taxi_cargo_crm.post(
        '/functions/create-cargo-corp-employee', json=request,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {'revision': 1}


async def test_func_create_cargo_corp_employee_login_pd_id(
        taxi_cargo_crm,
        mockserver,
        personal_ctx,
        personal_handler_bulk_retrieve,
):
    @mockserver.json_handler(
        'cargo-corp/internal/cargo-corp/v1/client/employee/upsert',
    )
    def _handler(request):
        expected_json = {
            'id': EMPLOYEE_YANDEX_UID,
            'info': {
                'name': EMPLOYEE_NAME,
                'phones': [{'number': const.PHONE}],
                'yandex_login_pd_id': EMPLOYEE_YANDEX_LOGIN_PD_ID,
            },
            'is_disabled': False,
            'revision': 0,
        }

        assert request.headers['X-B2B-Client-Id'] == CORP_CLIENT_ID
        assert request.json == expected_json

        body = None
        body = dict(expected_json, **{'revision': 1})
        return mockserver.make_response(status=200, json=body)

    personal_ctx.set_phones([{'id': const.PHONE_PD_ID, 'value': const.PHONE}])

    request = {
        'corp_client_id': CORP_CLIENT_ID,
        'yandex_uid': EMPLOYEE_YANDEX_UID,
        'yandex_login_pd_id': EMPLOYEE_YANDEX_LOGIN_PD_ID,
        'employee_name': EMPLOYEE_NAME,
        'employee_phone_pd_id': const.PHONE_PD_ID,
    }

    response = await taxi_cargo_crm.post(
        '/functions/create-cargo-corp-employee', json=request,
    )
    assert response.status_code == 200
    assert response.json() == {'revision': 1}
