import pytest

from tests_cargo_corp import utils


@pytest.mark.parametrize(
    'is_robot_active, cargo_robots_code, expected_code',
    ((True, 200, 200), (True, 404, 404), (False, 200, 404)),
)
async def test_robot_token_info(
        pgsql,
        taxi_cargo_corp,
        mockserver,
        is_robot_active,
        cargo_robots_code,
        expected_code,
):
    external_ref = utils.EXTERNAL_REF_FMT.format(utils.CORP_CLIENT_ID)

    @mockserver.json_handler('cargo-robots/v1/robot/token')
    def _handler(request):
        assert request.query['external_ref'] == external_ref
        if cargo_robots_code == 200:
            return {'token': utils.ROBOT_TOKEN}
        return mockserver.make_response(
            status=cargo_robots_code, json=utils.BAD_RESPONSE,
        )

    if is_robot_active:
        utils.create_employee(
            pgsql, corp_client_id=utils.CORP_CLIENT_ID, is_robot=True,
        )
    response = await taxi_cargo_corp.post(
        'v1/client/robot/token/info',
        headers={
            'X-B2B-Client-Id': utils.CORP_CLIENT_ID,
            'X-Yandex-Uid': utils.YANDEX_UID,
        },
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {
            'token': utils.ROBOT_TOKEN,
            'revision': 1,
            'is_enabled': is_robot_active,
        }


@pytest.mark.parametrize(
    'is_robot_exist, is_robot_enabled, expected_code',
    ((True, True, 200), (True, False, 200), (False, False, 404)),
)
async def test_robot_token_edit(
        pgsql,
        taxi_cargo_corp,
        is_robot_exist,
        is_robot_enabled,
        expected_code,
):
    if is_robot_exist:
        utils.create_employee(
            pgsql,
            corp_client_id=utils.CORP_CLIENT_ID,
            is_disabled=is_robot_enabled,
            is_robot=True,
        )

    for _ in range(2):
        body = {'revision': 1, 'is_enabled': is_robot_enabled}
        response = await taxi_cargo_corp.post(
            'v1/client/robot/token/edit',
            headers={
                'X-B2B-Client-Id': utils.CORP_CLIENT_ID,
                'X-Yandex-Uid': utils.YANDEX_UID,
            },
            json=body,
        )
        assert response.status_code == expected_code
        if expected_code == 200:
            assert response.json() == {
                'revision': 2,
                'is_enabled': is_robot_enabled,
            }
