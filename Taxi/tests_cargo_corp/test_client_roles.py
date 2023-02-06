import pytest


from tests_cargo_corp import utils


ROLE_NAME = 'horns and hooves'


def get_headers():
    return {
        'Accept-Language': 'ru',
        'X-B2B-Client-Id': utils.CORP_CLIENT_ID,
        'X-Yandex-Uid': utils.YANDEX_UID,
    }


def get_request(revision=None, permission_ids=None):
    if permission_ids is None:
        permission_ids = utils.SOME_PERMISSION_IDS

    params = {'role_name': ROLE_NAME}
    request = {'permission_ids': permission_ids}
    if revision:
        request['revision'] = revision

    return {'params': params, 'json': request}


async def test_client_role_upsert_ok(taxi_cargo_corp):
    response = await taxi_cargo_corp.put(
        '/internal/cargo-corp/v1/client/role/upsert',
        headers=get_headers(),
        **get_request(),
    )
    assert response.status_code == 200

    response_create_json = response.json()
    permissions = response_create_json['permissions']
    assert len(permissions) == 2
    utils.assert_ids_are_equal(permissions, utils.SOME_PERMISSION_IDS)

    response = await taxi_cargo_corp.put(
        '/internal/cargo-corp/v1/client/role/upsert',
        headers=get_headers(),
        **get_request(),
    )
    assert response.status_code == 200  # same request, nothing happens

    other_permission_ids = utils.SOME_PERMISSION_IDS[-1:]
    response = await taxi_cargo_corp.put(
        '/internal/cargo-corp/v1/client/role/upsert',
        headers=get_headers(),
        **get_request(permission_ids=other_permission_ids),
    )
    assert response.status_code == 409  # wrong revision, got actual role

    response = await taxi_cargo_corp.put(
        '/internal/cargo-corp/v1/client/role/upsert',
        headers=get_headers(),
        **get_request(revision=1, permission_ids=other_permission_ids),
    )
    assert response.status_code == 200  # ok edit
    response_edit_json = response.json()
    assert response_edit_json == dict(
        response_create_json,
        **{'revision': 2, 'permissions': permissions[-1:]},
    )


async def test_client_role_upsert_bad_permission(taxi_cargo_corp):
    unknown = [{'id': 'unknown'}]
    response = await taxi_cargo_corp.put(
        '/internal/cargo-corp/v1/client/role/upsert',
        headers=get_headers(),
        **get_request(permission_ids=unknown),
    )
    assert response.status_code == 409
    assert response.json()['details']['unknown_permission_ids'] == unknown


async def test_client_role_get(taxi_cargo_corp, user_has_rights, pgsql):
    role_id = utils.create_role(pgsql, role_name='role_for_get')

    response = await taxi_cargo_corp.get(
        '/internal/cargo-corp/v1/client/role/list', headers=get_headers(),
    )
    assert response.status_code == 200

    response_roles = response.json()['roles']
    assert len(response_roles) == 2
    assert set(
        (role['name'], role['is_general']) for role in response_roles
    ) == {(utils.OWNER_ROLE_TRANSLATION, True), ('role_for_get', False)}

    response = await taxi_cargo_corp.get(
        '/internal/cargo-corp/v1/client/role/list',
        params={'role_id': role_id},
        headers=get_headers(),
    )
    assert response.status_code == 200

    response_roles = response.json()['roles']
    assert len(response_roles) == 1

    response = await taxi_cargo_corp.get(
        '/internal/cargo-corp/v1/client/role/list',
        params={'role_id': 0},  # not exist
        headers=get_headers(),
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    """is_removable,
    expected_remove_code,
    expected_second_remove_code,
    expected_get_after_remove_code""",
    ((True, 200, 200, 404), (False, 409, 409, 200)),
)
async def test_client_role_remove(
        taxi_cargo_corp,
        user_has_rights,
        pgsql,
        is_removable,
        expected_remove_code,
        expected_second_remove_code,
        expected_get_after_remove_code,
):
    role_id = utils.create_role(
        pgsql, role_name='role_for_remove', is_removable=is_removable,
    )
    utils.create_employee_role(pgsql, role_id, yandex_uid=utils.YANDEX_UID)

    response = await taxi_cargo_corp.delete(
        'v1/client/role/remove',
        headers=get_headers(),
        params={'role_id': role_id},
    )
    assert response.status_code == expected_remove_code
    assert utils.get_employees_by_role(pgsql, role_id) == (
        [] if expected_remove_code == 200 else [utils.YANDEX_UID]
    )

    response = await taxi_cargo_corp.delete(
        'v1/client/role/remove',
        headers=get_headers(),
        params={'role_id': role_id},
    )
    assert response.status_code == expected_second_remove_code

    response = await taxi_cargo_corp.get(
        '/internal/cargo-corp/v1/client/role/list',
        params={'role_id': role_id},
        headers=get_headers(),
    )
    assert response.status_code == expected_get_after_remove_code


async def test_client_role_upsert_after_remove(taxi_cargo_corp, pgsql):
    role_id = utils.create_role(pgsql, role_name=ROLE_NAME, is_removable=True)

    response = await taxi_cargo_corp.delete(
        'v1/client/role/remove',
        headers=get_headers(),
        params={'role_id': role_id},
    )
    assert response.status_code == 200

    response = await taxi_cargo_corp.put(
        '/internal/cargo-corp/v1/client/role/upsert',
        headers=get_headers(),
        **get_request(),
    )
    assert response.status_code == 200


async def test_client_role_usage_ok(taxi_cargo_corp, user_has_rights, pgsql):
    role_id, _ = utils.get_role_info_by_name(pgsql, utils.OWNER_ROLE)

    response = await taxi_cargo_corp.get(
        '/internal/cargo-corp/v1/client/role/usage',
        headers=get_headers(),
        params={'role_id': role_id},
    )
    assert response.status_code == 200
    employees = response.json()['employees']
    assert len(employees) == 1
    assert employees[0]['id'] == utils.YANDEX_UID
