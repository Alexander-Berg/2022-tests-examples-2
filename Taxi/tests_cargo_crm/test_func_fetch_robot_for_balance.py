import pytest

from tests_cargo_crm import const

EMPLOYEE_INFO = {'name': 'Robot for Yandex Balance'}


@pytest.mark.parametrize(
    (
        'employee_list_code',
        'employee_list_json',
        'expected_code',
        'expected_json',
    ),
    [
        pytest.param(
            200,
            {'employees': [{'id': const.UID, 'info': EMPLOYEE_INFO.copy()}]},
            200,
            {'yandex_uid': const.UID},
            id='OK',
        ),
        pytest.param(200, {'employees': []}, 500, {}, id='empty_eployees'),
        pytest.param(
            404,
            {},
            404,
            {
                'code': 'not_found',
                'message': 'Unknown corp client.',
                'details': {},
            },
            id='unknown_cci',
        ),
    ],
)
async def test_func_balance_robot(
        taxi_cargo_crm,
        get_employee_list,
        employee_list_code,
        employee_list_json,
        expected_code,
        expected_json,
):
    get_employee_list.set_response(employee_list_code, employee_list_json)

    request = {'corp_client_id': const.CORP_CLIENT_ID}
    response = await taxi_cargo_crm.post(
        '/functions/fetch-robot-for-balance', json=request,
    )
    assert response.status == expected_code
    assert response.json() == expected_json
