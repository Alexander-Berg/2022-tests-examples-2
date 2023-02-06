import pytest

ROBOT_YANDEX_UID = 'robot_yandex_uid'
ROBOT_YANDEX_LOGIN = 'robot_yandex_login'
CORP_CLIENT_ID = (
    'corporate_client_identifier_test'  # use as robot_external_ref
)


@pytest.mark.parametrize(
    'cargo_robots_code, expected_code', ((200, 200), (500, 500)),
)
async def test_func_create_cargo_robot(
        taxi_cargo_crm, mockserver, cargo_robots_code, expected_code,
):
    @mockserver.json_handler('cargo-robots/v1/robot/create')
    def _handler(request):
        assert request.query['external_ref'] == CORP_CLIENT_ID
        body = None
        if cargo_robots_code == 200:
            body = {
                'external_ref': CORP_CLIENT_ID,
                'yandex_uid': ROBOT_YANDEX_UID,
                'login': ROBOT_YANDEX_LOGIN,
            }
        return mockserver.make_response(status=cargo_robots_code, json=body)

    response = await taxi_cargo_crm.post(
        '/functions/create-cargo-robot',
        json={'robot_external_ref': CORP_CLIENT_ID},
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {
            'robot_external_ref': CORP_CLIENT_ID,
            'yandex_uid': ROBOT_YANDEX_UID,
            'yandex_login': ROBOT_YANDEX_LOGIN,
        }
