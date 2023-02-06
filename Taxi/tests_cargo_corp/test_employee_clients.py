import pytest

from tests_cargo_corp import utils

LOCAL_CLIENT_ID = 'some_long_id_string_of_length_32'
LOCAL_CLIENT = {
    'id': LOCAL_CLIENT_ID,
    'name': 'test_corp_client_name',
    'is_registration_finished': False,
}
CORP_CLIENT = {
    'id': utils.CORP_CLIENT_ID,
    'name': utils.CORP_CLIENT_NAME,
    'is_registration_finished': False,
}


@pytest.mark.parametrize(
    [
        'yandex_uid',
        'expected_code',
        'expected_json',
        'x_request_mode',
        'set_additional_corp',
    ],
    (
        pytest.param(
            utils.YANDEX_UID,
            200,
            {'corp_clients': [CORP_CLIENT]},
            None,
            False,
            id='ok',
        ),
        pytest.param(
            utils.YANDEX_UID,
            200,
            {
                'corp_clients': [
                    {
                        'id': utils.CORP_CLIENT_ID,
                        'is_registration_finished': False,
                    },
                ],
            },
            'system',
            False,
            id='ok for system',
        ),
        pytest.param(
            'unknown_uid',
            404,
            {'code': 'not_found', 'message': 'Unknown corp_client'},
            None,
            False,
            id='not found',
        ),
        pytest.param(
            utils.YANDEX_UID,
            200,
            {'corp_clients': [CORP_CLIENT, LOCAL_CLIENT]},
            None,
            True,
            id='ok-multiple corp_clients',
        ),
    ),
)
async def test_employee_corp_clients(
        taxi_cargo_corp,
        user_has_rights,
        register_default_user,
        prepare_multiple_clients,
        yandex_uid,
        expected_code,
        expected_json,
        x_request_mode,
        set_additional_corp,
):
    if set_additional_corp:
        prepare_multiple_clients([LOCAL_CLIENT])

    headers = {'X-Yandex-Uid': yandex_uid}
    if x_request_mode is not None:
        headers['X-Request-Mode'] = x_request_mode

    response = await taxi_cargo_corp.post(
        '/internal/cargo-corp/v1/employee/corp-client/list', headers=headers,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert (
            sorted(
                response.json()['corp_clients'],
                key=lambda x: x.get('name', x['id']),
            )
            == expected_json['corp_clients']
        )
    else:
        assert response.json() == expected_json


@pytest.mark.parametrize(
    'role_name,expected_corp_clients',
    (
        pytest.param(
            utils.OWNER_ROLE,
            [
                {
                    'id': utils.CORP_CLIENT_ID,
                    'is_registration_finished': False,
                    'name': utils.CORP_CLIENT_NAME,
                },
            ],
            id='ok',
        ),
        pytest.param('random_role_name', [], id='wrong_role'),
    ),
)
async def test_employee_with_role_corp_clients(
        taxi_cargo_corp,
        user_has_rights,
        register_default_user,
        role_name,
        expected_corp_clients,
):
    response = await taxi_cargo_corp.post(
        '/internal/cargo-corp/v1/employee/corp-client/list',
        headers={'X-Yandex-Uid': utils.YANDEX_UID},
        params={'role_name': role_name},
    )
    assert response.status_code == 200

    assert response.json()['corp_clients'] == expected_corp_clients


@pytest.mark.parametrize(
    'corps_to_be_set, is_robot, expected_code',
    (
        pytest.param(
            [CORP_CLIENT, LOCAL_CLIENT],
            False,
            404,
            id='human employee with several corps',
        ),
        pytest.param(
            [LOCAL_CLIENT], False, 404, id='human employee with one corp',
        ),
        pytest.param(
            [CORP_CLIENT, LOCAL_CLIENT],
            True,
            404,
            id='robot employee with several corps',
        ),
        pytest.param(
            [LOCAL_CLIENT], True, 200, id='robot employee with one corp',
        ),
    ),
)
async def test_employee_corp_clients_if_robot(
        taxi_cargo_corp,
        prepare_multiple_clients,
        corps_to_be_set,
        is_robot,
        expected_code,
):
    prepare_multiple_clients(corps_to_be_set, is_robot=is_robot)

    response = await taxi_cargo_corp.post(
        '/internal/cargo-corp/v1/employee/corp-client/if-robot',
        headers={'X-Yandex-Uid': utils.YANDEX_UID},
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {'corp_client': {'id': LOCAL_CLIENT_ID}}
