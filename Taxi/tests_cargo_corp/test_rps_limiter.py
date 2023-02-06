import pytest

from tests_cargo_corp import utils

PHONES = [{'number': '0987654321'}, {'number': '12345678910'}]
EMPLOYEE_CANDIDATE = {
    'name': 'Чумабой',
    'email': 'candidate@client.ru',
    'phone': PHONES[0],
    'role_id': utils.ROLE_ID,
}
ROLES = [
    {'id': 'role_id_1', 'name': 'role_name_1'},
    {'id': 'role_id_2', 'name': 'role_name_2'},
    {'id': 'role_id_3', 'name': 'role_name_3'},
    {'id': 'role_id_4', 'name': 'role_name_4'},
]


async def employee_candidate_upsert(taxi_cargo_corp, corp_client_id):
    candidate = EMPLOYEE_CANDIDATE
    candidate['role_id'] = ROLES[0]['id']
    candidate['role_name'] = ROLES[0]['name']

    return await taxi_cargo_corp.put(
        '/internal/cargo-corp/v1/client/employee-candidate/upsert',
        headers={'X-B2B-Client-Id': corp_client_id},
        json=candidate,
    )


@pytest.mark.config(
    CARGO_CORP_RPS_LIMITER_GROUP_AMOUNT=2,
    CARGO_CORP_RPS_LIMITER_MAPPING={
        '__default__': 'default',
        'group_0': 'group_0',
        'group_1': 'group_1',
    },
    CARGO_CORP_RPS_LIMITER_QUOTAS={
        '/internal/cargo-corp/v1/client/employee-candidate/upsert/put': {
            '__default__': {'limit': 1, 'interval': 60},
            'group_0': {'limit': 6, 'interval': 60},
            'group_1': {'limit': 6, 'interval': 60},
        },
    },
)
async def test_rps_limiter(pgsql, taxi_cargo_corp, rps_limiter):
    utils.create_role(
        pgsql, role_id=ROLES[0]['id'], role_name=ROLES[0]['name'],
    )

    rps_limiter.set_budget(
        '/internal/cargo-corp/v1/client/employee-candidate/upsert/put:default',
        1,
    )
    rps_limiter.set_budget(
        '/internal/cargo-corp/v1/client/employee-candidate/upsert/put:group_0',
        6,
    )
    rps_limiter.set_budget(
        '/internal/cargo-corp/v1/client/employee-candidate/upsert/put:group_1',
        6,
    )

    for expected_code in [200] * 6 + [429] * 2:
        response = await employee_candidate_upsert(
            taxi_cargo_corp, utils.CORP_CLIENT_ID,
        )
        assert response.status_code == expected_code


async def test_rps_limiter_no_quotas(pgsql, taxi_cargo_corp):
    utils.create_role(
        pgsql, role_id=ROLES[0]['id'], role_name=ROLES[0]['name'],
    )

    for expected_code in [200] * 10:
        response = await employee_candidate_upsert(
            taxi_cargo_corp, utils.CORP_CLIENT_ID,
        )
        assert response.status_code == expected_code


@pytest.mark.config(
    CARGO_CORP_RPS_LIMITER_GROUP_AMOUNT=2,
    CARGO_CORP_RPS_LIMITER_MAPPING={
        '__default__': 'default',
        'group_0': 'group_0',
        'group_1': 'group_1',
        utils.CORP_CLIENT_ID: 'x5',
    },
    CARGO_CORP_RPS_LIMITER_QUOTAS={
        '/internal/cargo-corp/v1/client/employee-candidate/upsert/put': {
            '__default__': {'limit': 1, 'interval': 60},
            'group_0': {'limit': 6, 'interval': 60},
            'group_1': {'limit': 6, 'interval': 60},
            'x5': {'limit': 9, 'interval': 60},
        },
    },
)
async def test_rps_limiter_personal_quota(pgsql, taxi_cargo_corp, rps_limiter):
    utils.create_role(
        pgsql, role_id=ROLES[0]['id'], role_name=ROLES[0]['name'],
    )

    rps_limiter.set_budget(
        '/internal/cargo-corp/v1/client/employee-candidate/upsert/put:default',
        1,
    )
    rps_limiter.set_budget(
        '/internal/cargo-corp/v1/client/employee-candidate/upsert/put:group_0',
        6,
    )
    rps_limiter.set_budget(
        '/internal/cargo-corp/v1/client/employee-candidate/upsert/put:group_1',
        6,
    )
    rps_limiter.set_budget(
        '/internal/cargo-corp/v1/client/employee-candidate/upsert/put:x5', 9,
    )

    for expected_code in [404] * 6 + [429] * 2:
        response = await employee_candidate_upsert(
            taxi_cargo_corp, utils.CORP_CLIENT_ID_1,
        )
        assert response.status_code == expected_code

    for expected_code in [200] * 9 + [429] * 2:
        response = await employee_candidate_upsert(
            taxi_cargo_corp, utils.CORP_CLIENT_ID,
        )
        assert response.status_code == expected_code
