import uuid

import pytest

from tests_cargo_corp import utils


NEW_EMPLOYEE = 'user1'
OLD_TIMESTAMP = '2021-10-08T10:04:55+00:00'
NEW_TIMESTAMP = '2022-01-08T10:04:55+00:00'

PERMISSIONS_CARD = ['corp_client', 'claims_view', 'claims_edit']
PERMISSIONS_OFFER = ['corp_client', 'claims_view']
PERMISSIONS_CUSTOM = ['corp_client', 'claims_edit']

BILLING_ID = 'billing_id'


def get_permission_ids(permissions):
    return [{'id': perm} for perm in permissions]


CARGO_CORP_COUNTRY_SPECIFICS = {
    'rus': {
        'permits': {
            'allowed_permissions': {
                'card': PERMISSIONS_CARD,
                'offer': PERMISSIONS_OFFER,
            },
        },
    },
}

CARGO_CORP_CUSTOM_PERMISSIONS_DEFAULT = {}

CARGO_CORP_CUSTOM_PERMISSIONS_ALL = {utils.CORP_CLIENT_ID: {'alias': 'magnit'}}

CARGO_CORP_CUSTOM_PERMISSIONS_PARTLY = {
    utils.CORP_CLIENT_ID: {
        'alias': 'magnit',
        'allowed_permissions': PERMISSIONS_CUSTOM,
    },
}


def get_unique_name():
    return str(uuid.uuid4())


def get_headers(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=utils.YANDEX_UID,
):
    return {'X-B2B-Client-Id': corp_client_id, 'X-Yandex-Uid': yandex_uid}


def prepare_db(
        pgsql,
        employee_exists,
        role_exists=None,
        relation_exists=True,
        permission_ids=utils.SOME_PERMISSION_IDS,
):
    role_id = 'role_id'
    if role_exists is not None:
        role_id = utils.create_role(
            pgsql,
            role_name=get_unique_name(),
            permission_ids=permission_ids,
            is_removed=(not role_exists),
        )

    if employee_exists is not None:
        utils.create_employee(
            pgsql, yandex_uid=NEW_EMPLOYEE, is_removed=(not employee_exists),
        )

    if (
            employee_exists is not None
            and role_exists is not None
            and relation_exists
    ):
        utils.create_employee_role(pgsql, role_id, yandex_uid=NEW_EMPLOYEE)

    return role_id


@pytest.mark.parametrize(
    'employee_exists,role_exists,expected_code',
    (
        pytest.param(True, True, 200, id='ok'),
        pytest.param(True, False, 409, id='role was removed'),
        pytest.param(True, None, 409, id='role not in db'),
        pytest.param(False, True, 409, id='employee was removed'),
        pytest.param(None, True, 409, id='employee not in db'),
    ),
)
async def test_assign_role(
        taxi_cargo_corp, pgsql, employee_exists, role_exists, expected_code,
):
    role_id = prepare_db(
        pgsql, employee_exists, role_exists, relation_exists=False,
    )

    response = await taxi_cargo_corp.post(
        '/internal/cargo-corp/v1/client/role/bulk-assign',
        headers=get_headers(),
        params={'role_id': role_id},
        json={'employees': [{'id': NEW_EMPLOYEE}]},
    )
    assert response.status_code == expected_code

    # retry
    response = await taxi_cargo_corp.post(
        '/internal/cargo-corp/v1/client/role/bulk-assign',
        headers=get_headers(),
        params={'role_id': role_id},
        json={'employees': [{'id': NEW_EMPLOYEE}]},
    )
    assert response.status_code == expected_code


async def prepare_billing_client(
        make_client_balance_upsert_request, billing_id, corp_client_id,
):
    request = {'billing_id': billing_id, 'contract': utils.PHOENIX_CONTRACT}
    response = await make_client_balance_upsert_request(
        corp_client_id, request,
    )
    assert response.status_code == 200


# TODO (dipterix): split tests
@pytest.mark.parametrize(
    (
        'client_type',
        'registered_ts',
        'expected_permissions',
        'cargo_corp_country_specifics',
        'cargo_corp_custom_permissions',
    ),
    (
        pytest.param(
            'card',
            None,
            utils.ALL_PERMISSION_IDS,
            {},
            CARGO_CORP_CUSTOM_PERMISSIONS_DEFAULT,
            id='unregistered',
        ),
        pytest.param(
            'card',
            OLD_TIMESTAMP,
            utils.ALL_PERMISSION_IDS,
            {},
            CARGO_CORP_CUSTOM_PERMISSIONS_DEFAULT,
            id='registered',
        ),
        pytest.param(
            'card',
            NEW_TIMESTAMP,
            get_permission_ids(PERMISSIONS_CARD),
            CARGO_CORP_COUNTRY_SPECIFICS,
            CARGO_CORP_CUSTOM_PERMISSIONS_DEFAULT,
            id='card client',
        ),
        pytest.param(
            'offer',
            NEW_TIMESTAMP,
            get_permission_ids(PERMISSIONS_OFFER),
            CARGO_CORP_COUNTRY_SPECIFICS,
            CARGO_CORP_CUSTOM_PERMISSIONS_DEFAULT,
            id='offer client',
        ),
        pytest.param(
            'card',
            NEW_TIMESTAMP,
            utils.ALL_PERMISSION_IDS,
            CARGO_CORP_COUNTRY_SPECIFICS,
            CARGO_CORP_CUSTOM_PERMISSIONS_ALL,
            id='personal permissions - all',
        ),
        pytest.param(
            'card',
            NEW_TIMESTAMP,
            get_permission_ids(PERMISSIONS_CUSTOM),
            CARGO_CORP_COUNTRY_SPECIFICS,
            CARGO_CORP_CUSTOM_PERMISSIONS_PARTLY,
            id='personal permissions - partly',
        ),
    ),
)
async def test_assign_general_role(
        taxi_cargo_corp,
        taxi_config,
        user_has_rights,
        pgsql,
        make_client_balance_upsert_request,
        client_type,
        registered_ts,
        expected_permissions,
        cargo_corp_country_specifics,
        cargo_corp_custom_permissions,
):
    taxi_config.set_values(
        {'CARGO_CORP_COUNTRY_SPECIFICS': cargo_corp_country_specifics},
    )
    taxi_config.set_values(
        {'CARGO_CORP_CUSTOM_PERMISSIONS': cargo_corp_custom_permissions},
    )
    await taxi_cargo_corp.invalidate_caches()

    if registered_ts:
        await taxi_cargo_corp.post(
            '/internal/cargo-corp/v1/client/update-registered',
            json={'registered_ts': registered_ts},
            headers=get_headers(),
        )

    prepare_db(pgsql, employee_exists=True)
    general_role_id, _ = utils.get_role_info_by_name(pgsql, utils.OWNER_ROLE)

    response = await taxi_cargo_corp.post(
        '/internal/cargo-corp/v1/client/role/bulk-assign',
        headers=get_headers(),
        params={'role_id': general_role_id},
        json={'employees': [{'id': NEW_EMPLOYEE}]},
    )
    assert response.status_code == 200

    if client_type == 'offer':
        await prepare_billing_client(
            make_client_balance_upsert_request,
            BILLING_ID,
            utils.CORP_CLIENT_ID,
        )

    response = await taxi_cargo_corp.post(
        '/internal/cargo-corp/v1/client/employee/permission/list',
        headers=get_headers(yandex_uid=NEW_EMPLOYEE),
    )
    assert response.status_code == 200

    permission_ids = response.json()['permission_ids']
    assert len(permission_ids) == len(expected_permissions)
    utils.assert_ids_are_equal(permission_ids, expected_permissions)


@pytest.mark.parametrize(
    'employee_exists,role_exists,expected_code',
    (
        pytest.param(True, True, 200, id='ok'),
        pytest.param(True, False, 409, id='role was removed'),
        pytest.param(True, None, 409, id='role not in db'),
        pytest.param(False, True, 409, id='employee was removed'),
        pytest.param(None, True, 409, id='employee not in db'),
    ),
)
async def test_employee_roles_update(
        taxi_cargo_corp,
        user_has_rights,
        pgsql,
        employee_exists,
        role_exists,
        expected_code,
):
    role_id = prepare_db(
        pgsql, employee_exists, role_exists, relation_exists=False,
    )
    role_name_2 = 'name_2'
    utils.create_role(pgsql, role_id='role_id_2', role_name=role_name_2)
    role_id_2, _ = utils.get_role_info_by_name(
        pgsql, role_name_2, utils.CORP_CLIENT_ID,
    )

    request = {
        'employee': {'id': NEW_EMPLOYEE, 'revision': 1},
        'role_ids': [{'id': role_id_2}, {'id': role_id}],
    }

    response = await taxi_cargo_corp.put(
        'v1/client/employee/roles/update', headers=get_headers(), json=request,
    )

    assert response.status_code == expected_code

    employees_with_role = utils.get_employees_by_role(pgsql, role_id)
    employees_with_role_2 = utils.get_employees_by_role(pgsql, role_id_2)

    if expected_code == 200:
        assert employees_with_role == [NEW_EMPLOYEE]
        assert NEW_EMPLOYEE in employees_with_role_2
    else:
        assert employees_with_role == []
        assert NEW_EMPLOYEE not in employees_with_role_2

    # retry
    response = await taxi_cargo_corp.put(
        'v1/client/employee/roles/update', headers=get_headers(), json=request,
    )
    assert response.status_code == expected_code, 'retry'


async def test_employee_remove_owner_role(
        pgsql, taxi_cargo_corp, user_has_rights,
):
    request = {
        'employee': {'id': utils.YANDEX_UID, 'revision': 1},
        'role_ids': [],
    }

    response = await taxi_cargo_corp.put(
        'v1/client/employee/roles/update', headers=get_headers(), json=request,
    )
    assert response.status_code == 409

    employees_with_role = utils.get_employees_by_role(pgsql, utils.ROLE_ID)
    # cuz system::owner should not be removable
    assert utils.YANDEX_UID in employees_with_role


# TODO (dipterix): add tests with losing 'paydata_edit' perm, and check cards
async def test_employee_roles_update_process(taxi_cargo_corp, pgsql):
    role_id = prepare_db(pgsql, employee_exists=True, role_exists=True)
    other_role_id = utils.create_role(pgsql, role_name='other_role')

    request = {
        'employee': {'id': NEW_EMPLOYEE, 'revision': 1},
        'role_ids': [{'id': other_role_id}],
    }

    response = await taxi_cargo_corp.put(
        'v1/client/employee/roles/update', headers=get_headers(), json=request,
    )
    assert response.status_code == 200
    assert utils.get_employees_by_role(pgsql, role_id) == []
    assert utils.get_employees_by_role(pgsql, other_role_id) == [NEW_EMPLOYEE]

    request['role_ids'] = [{'id': role_id}]
    response = await taxi_cargo_corp.put(
        'v1/client/employee/roles/update', headers=get_headers(), json=request,
    )
    assert response.status_code == 409
    assert utils.get_employees_by_role(pgsql, role_id) == []
    assert utils.get_employees_by_role(pgsql, other_role_id) == [NEW_EMPLOYEE]

    request['employee']['revision'] = 2
    response = await taxi_cargo_corp.put(
        'v1/client/employee/roles/update', headers=get_headers(), json=request,
    )
    assert response.status_code == 200
    assert utils.get_employees_by_role(pgsql, role_id) == [NEW_EMPLOYEE]
    assert utils.get_employees_by_role(pgsql, other_role_id) == []


@pytest.mark.parametrize(
    'corp_client_id,employee_exists,role_exists,expected_code',
    (
        pytest.param(utils.CORP_CLIENT_ID, True, True, 200, id='ok'),
        pytest.param(
            utils.CORP_CLIENT_ID, True, False, 200, id='ok-role was removed',
        ),
        pytest.param(
            utils.CORP_CLIENT_ID,
            False,
            True,
            404,
            id='bad-employee was removed',
        ),
        pytest.param(
            utils.CORP_CLIENT_ID[::-1],
            True,
            True,
            404,
            id='bad-corp client does not exist',
        ),
    ),
)
async def test_employee_permissions(
        taxi_cargo_corp,
        pgsql,
        corp_client_id,
        employee_exists,
        role_exists,
        expected_code,
):
    some_permission_ids = utils.SOME_PERMISSION_IDS
    other_permission_ids = utils.ALL_PERMISSION_IDS[:2]

    prepare_db(
        pgsql,
        employee_exists,
        role_exists,
        permission_ids=some_permission_ids,
    )
    prepare_db(
        pgsql,
        employee_exists,
        role_exists,
        permission_ids=other_permission_ids,
    )

    response = await taxi_cargo_corp.post(
        '/internal/cargo-corp/v1/client/employee/permission/list',
        headers=get_headers(
            corp_client_id=corp_client_id, yandex_uid=NEW_EMPLOYEE,
        ),
    )
    assert response.status_code == expected_code

    if expected_code == 200:
        permission_ids = response.json()['permission_ids']
        assert len(permission_ids) == (4 if role_exists else 0)
        if role_exists:
            utils.assert_ids_are_equal(
                permission_ids, some_permission_ids + other_permission_ids,
            )
        return

    if not employee_exists:
        assert response.json() == {
            'code': 'not_found',
            'message': 'Unknown employee',
        }
    else:
        assert response.json() == {
            'code': 'not_found',
            'message': 'Unknown corp_client',
        }


@pytest.mark.config(CARGO_CORP_AVAILABLE_ROLE_IDS={'enabled': True, 'b2b': []})
async def test_employee_unavailable_role_update(
        taxi_cargo_corp, user_has_rights,
):
    request = {
        'employee': {'id': utils.YANDEX_UID, 'revision': 1},
        'role_ids': [{'id': 'unavailable_role_id'}],
    }

    response = await taxi_cargo_corp.put(
        'v1/client/employee/roles/update', headers=get_headers(), json=request,
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'wrong_role_id'
