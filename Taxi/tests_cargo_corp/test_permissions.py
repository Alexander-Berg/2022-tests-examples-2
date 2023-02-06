from tests_cargo_corp import utils


def get_headers():
    return {
        'Accept-Language': 'ru',
        'X-B2B-Client-Id': utils.CORP_CLIENT_ID,
        'X-Yandex-Uid': 'yandex_uid1',
    }


async def test_permission_list(taxi_cargo_corp):
    response = await taxi_cargo_corp.get(
        'v1/permission/list', headers=get_headers(),
    )
    assert response.status_code == 200

    permissions = response.json()['permissions']
    utils.assert_ids_are_equal(permissions, utils.ALL_PERMISSION_IDS)
