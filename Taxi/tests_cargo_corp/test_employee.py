# pylint: disable=too-many-lines
# TODO: split into multiple files

import copy
import datetime
from typing import Optional

import pytest

from testsuite.utils import matching

from tests_cargo_corp import utils


EMPLOYEE_UID = 'employee_y_uid'
PHONES = [{'number': '0987654321'}, {'number': '12345678910'}]
PHONES_PD_ID = ['0987654321_id', '12345678910_id']
EMPLOYEE_LOGIN_PD_ID = 'Chumaboy_id'
EMPLOYEE_EMAIL_PD_ID = 'one@employee.ru_id'
EMPLOYEE = {
    'name': 'Чумабой',
    'phones': PHONES[1:],
    'email': 'one@employee.ru',
    'yandex_login': 'Chumaboy',
}
EMPLOYEE_RESPONSE = dict(**EMPLOYEE, is_removable=True)
EMPLOYEE_WITH_FEW_PHONES = {
    'name': 'Чумабой',
    'phones': PHONES,
    'email': 'several@employee.ru',
    'yandex_login': 'Chumaboy',
}
EMPLOYEE_WITH_FEW_PHONES_RESPONSE = dict(
    **EMPLOYEE_WITH_FEW_PHONES, is_removable=True,
)
EMPLOYEE_WITH_LOGIN_PD_ID = {
    'name': 'Чумабой',
    'phones': PHONES[1:],
    'email': 'one@employee.ru',
    'yandex_login_pd_id': EMPLOYEE_LOGIN_PD_ID,
}
EMPLOYEE_WITH_LOGIN_PD_ID_RESPONSE = {
    'name': 'Чумабой',
    'phones': PHONES[1:],
    'email': 'one@employee.ru',
    'is_removable': True,
}
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
EMPLOYEE_ROLES = [[ROLES[0]], [ROLES[1]], [ROLES[0], ROLES[2]], [ROLES[3]]]
EMPLOYEE_UIDS = [
    'employee_y_uid_1',
    'employee_y_uid_2',
    'employee_y_uid_3',
    'employee_y_uid_4',
]
EMPLOYEES_PHONES = [
    {'number': '0987654321'},
    {'number': '15'},
    {'number': '12345'},
    {'number': '54321'},
    {'number': '543210'},
]
EMPLOYEES_EMAILS = [
    'first@employee.ru',
    'second@employee.ru',
    'third@employee.ru',
    'fourth@employee.ru',
    'fifth@employee.ru',
]

EMPLOYEES = [
    {
        'name': 'Чумабой',
        'phones': [EMPLOYEES_PHONES[0]],
        'email': EMPLOYEES_EMAILS[0],
        'yandex_login': 'Chumaboy',
    },
    {
        'name': 'Чумабой_2',
        'phones': [EMPLOYEES_PHONES[1]],
        'yandex_login': 'Chumaboy_2',
    },
    {
        'name': 'Чумабой_3',
        'phones': [EMPLOYEES_PHONES[2], EMPLOYEES_PHONES[3]],
        'email': EMPLOYEES_EMAILS[3],
        'yandex_login': 'Chumaboy_3',
    },
    {
        'name': 'Чумабой_4',
        'phones': [EMPLOYEES_PHONES[1], EMPLOYEES_PHONES[4]],
        'yandex_login': 'Chumaboy_4',
    },
]

EMPLOYEES_RESPONSE = []
for item in EMPLOYEES:
    EMPLOYEES_RESPONSE.append(dict(**item, is_removable=True))


@pytest.fixture(name='make_client_employee_edit_request')
def _make_client_employee_edit_request(taxi_cargo_corp):
    async def wrapper(is_internal=True, json=None):
        client_employee_edit_url = '/v1/client/employee/edit'
        if is_internal:
            client_employee_edit_url = (
                utils.INTERNAL_PREFIX + client_employee_edit_url
            )
        response = await taxi_cargo_corp.post(
            client_employee_edit_url,
            headers={
                'X-B2B-Client-Id': utils.CORP_CLIENT_ID,
                'X-Yandex-Uid': utils.YANDEX_UID,
            },
            json=json or {},
        )
        return response

    return wrapper


@pytest.fixture(name='populate_roles')
def _populate_roles(insert_role):
    def wrapper(corp_client_id: Optional[str] = None):
        for role_arr in EMPLOYEE_ROLES:
            for role in role_arr:
                insert_role(
                    corp_client_id=corp_client_id,
                    role_id=role['id'],
                    role_name=role['name'],
                    permissions=[p['id'] for p in utils.ALL_PERMISSION_IDS],
                )

    return wrapper


def _build_pg_employee_row(revision=1):
    row = {
        'corp_client_id': utils.CORP_CLIENT_ID,
        'created_ts': matching.IsInstance(datetime.datetime),
        'email_pd_id': EMPLOYEE_EMAIL_PD_ID,
        'is_disabled': False,
        'is_removed': False,
        'name': EMPLOYEE['name'],
        'phone_pd_ids': PHONES_PD_ID[1:],
        'revision': revision,
        'robot_external_ref': None,
        'uid_revision': 0,
        'updated_ts': matching.IsInstance(datetime.datetime),
        'yandex_login_pd_id': EMPLOYEE_LOGIN_PD_ID,
        'yandex_uid': EMPLOYEE_UID,
    }

    return row


async def test_internal_employee_upsert_ok(
        call_internal_employee_upsert, select_employee,
):
    """
    Tests /internal/cargo-corp/v1/client/employee/upsert handler
    with OK response
    """
    request = {'id': EMPLOYEE_UID, 'info': EMPLOYEE}
    expected_ok_json = {
        'id': EMPLOYEE_UID,
        'info': EMPLOYEE_RESPONSE,
        'is_disabled': False,
        'revision': 1,
    }

    response_json = await call_internal_employee_upsert(request=request)
    assert response_json == expected_ok_json

    employee = select_employee(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=EMPLOYEE_UID,
    )

    assert employee == _build_pg_employee_row()


async def test_internal_employee_upsert_twice_same(
        call_internal_employee_upsert, select_employee,
):
    """
    Tests /internal/cargo-corp/v1/client/employee/upsert handler
    using two calls with the same data
    """
    request = {'id': EMPLOYEE_UID, 'info': EMPLOYEE}

    expected_ok_json = {
        'id': EMPLOYEE_UID,
        'info': EMPLOYEE_RESPONSE,
        'is_disabled': False,
        'revision': 1,
    }

    response_json = await call_internal_employee_upsert(request=request)
    assert response_json == expected_ok_json

    response_json = await call_internal_employee_upsert(request=request)
    assert response_json == expected_ok_json

    employee = select_employee(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=EMPLOYEE_UID,
    )

    assert employee == _build_pg_employee_row(revision=1)


async def test_internal_employee_upsert_updated(
        call_internal_employee_upsert, select_employee,
):
    """
    Tests /internal/cargo-corp/v1/client/employee/upsert handler
    using two calls with different data, but right revision
    """
    request = {'id': EMPLOYEE_UID, 'info': EMPLOYEE_WITH_FEW_PHONES}
    expected_ok_json = {
        'id': EMPLOYEE_UID,
        'info': EMPLOYEE_WITH_FEW_PHONES_RESPONSE,
        'is_disabled': False,
        'revision': 1,
    }

    response_json = await call_internal_employee_upsert(request=request)
    assert response_json == expected_ok_json

    request = {'id': EMPLOYEE_UID, 'info': EMPLOYEE, 'revision': 1}
    expected_ok_json = {
        'id': EMPLOYEE_UID,
        'info': EMPLOYEE_RESPONSE,
        'is_disabled': False,
        'revision': 2,
    }

    response_json = await call_internal_employee_upsert(request=request)
    assert response_json == expected_ok_json

    employee = select_employee(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=EMPLOYEE_UID,
    )

    assert employee == _build_pg_employee_row(revision=2)


async def test_internal_employee_upsert_twice_conflict(
        call_internal_employee_upsert, select_employee,
):
    """
    Tests /internal/cargo-corp/v1/client/employee/upsert handler
    using two calls with different data, but wrong revision.
    Expects conflict error.
    """
    request = {'id': EMPLOYEE_UID, 'info': EMPLOYEE}
    expected_ok_json = {
        'id': EMPLOYEE_UID,
        'info': EMPLOYEE_RESPONSE,
        'is_disabled': False,
        'revision': 1,
    }

    response_json = await call_internal_employee_upsert(request=request)
    assert response_json == expected_ok_json

    request = {'id': EMPLOYEE_UID, 'info': EMPLOYEE_WITH_FEW_PHONES}

    response_json = await call_internal_employee_upsert(
        request=request, expected_code=409,
    )
    assert response_json['code'] == 'not_actual_revision'

    employee = select_employee(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=EMPLOYEE_UID,
    )

    assert employee == _build_pg_employee_row(revision=1)


async def test_internal_employee_upsert_login_pd_id(
        call_internal_employee_upsert, select_employee,
):
    """
    Tests /internal/cargo-corp/v1/client/employee/upsert handler
    with passed yandex_login_pd_id instead of yandex_login
    """
    request = {'id': EMPLOYEE_UID, 'info': EMPLOYEE_WITH_LOGIN_PD_ID}
    expected_ok_json = {
        'id': EMPLOYEE_UID,
        'info': EMPLOYEE_WITH_LOGIN_PD_ID_RESPONSE,
        'is_disabled': False,
        'revision': 1,
    }

    response_json = await call_internal_employee_upsert(request=request)
    assert response_json == expected_ok_json

    employee = select_employee(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=EMPLOYEE_UID,
    )

    assert employee == _build_pg_employee_row()


@pytest.mark.parametrize(
    'data_type, expected_code',
    [
        ('phones', 'invalid_phone'),
        ('emails', 'invalid_email'),
        ('yandex_logins', 'invalid_yandex_login'),
    ],
)
async def test_internal_employee_upsert_invalid_data(
        call_internal_employee_upsert,
        select_employee,
        mockserver,
        data_type,
        expected_code,
):
    @mockserver.json_handler(f'/personal/v1/{data_type}/store')
    def _store(request):
        response = {'code': '400', 'message': 'invalid data'}
        return mockserver.make_response(status=400, json=response)

    @mockserver.json_handler(f'/personal/v1/{data_type}/bulk_store')
    def _bulk_store(request):
        response = {'code': '400', 'message': 'invalid data'}
        return mockserver.make_response(status=400, json=response)

    request = {'id': EMPLOYEE_UID, 'info': EMPLOYEE}

    response_json = await call_internal_employee_upsert(
        request=request, expected_code=400,
    )
    assert response_json['code'] == expected_code

    employee = select_employee(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=EMPLOYEE_UID,
    )

    assert employee is None


async def test_internal_employee_upsert_bad_request(
        call_internal_employee_upsert, select_employee,
):
    info = copy.deepcopy(EMPLOYEE)
    info['yandex_login_pd_id'] = 'pd_id'

    request = {'id': EMPLOYEE_UID, 'info': info}

    response_json = await call_internal_employee_upsert(
        request=request, expected_code=400,
    )
    assert response_json['code'] == 'bad_request'

    employee = select_employee(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=EMPLOYEE_UID,
    )

    assert employee is None


async def test_employee_create_and_modify(
        pgsql,
        taxi_cargo_corp,
        user_has_rights,
        mockserver,
        blackbox,
        call_internal_employee_list_request,
        make_client_employee_edit_request,
):
    candidate = EMPLOYEE_CANDIDATE
    candidate['role_id'] = ROLES[0]['id']
    candidate['role_name'] = ROLES[0]['name']

    @mockserver.json_handler('/cargo-corp/v1/client/employee-candidate/info')
    def _candidate_info(request):
        return {
            'confirmation_code': request.query['confirmation_code'],
            'revision': 1,
            'info': candidate,
            'corp_client_name': utils.CORP_CLIENT_NAME,
        }

    utils.create_role(
        pgsql, role_id=ROLES[0]['id'], role_name=ROLES[0]['name'],
    )
    response = await taxi_cargo_corp.put(
        '/internal/cargo-corp/v1/client/employee-candidate/upsert',
        headers={'X-B2B-Client-Id': utils.CORP_CLIENT_ID},
        json=candidate,
    )
    assert response.status_code == 200

    confirmation_code = response.json()['confirmation_code']
    corp_client_id = (
        utils.CORP_CLIENT_ID
    )  # FIXME (dipterix): add url/corp_client_id to response?

    response = await taxi_cargo_corp.post(
        'v1/client/employee-candidate/confirm',
        headers={
            'X-Yandex-Uid': 'yandex_uid2',
            'X-Yandex-Login': 'yandex_login2',
            'X-Ya-User-Ticket': 'test_ya_ticket',
        },
        params={
            'confirmation_code': confirmation_code,
            'corp_client_id': corp_client_id,
        },
    )
    assert response.status_code == 200

    request = response.json()
    del request['info']['is_removable']
    for key in ['name']:
        request['info'][key] += '_edited'
    request['is_disabled'] = True

    for _ in range(2):
        response = await make_client_employee_edit_request(json=request)
        assert response.status_code == 200

    request['is_disabled'] = False
    response = await make_client_employee_edit_request(json=request)
    assert response.status_code == 409

    response_json = await call_internal_employee_list_request()

    expected_role = {'id': utils.ROLE_ID, 'name': utils.OWNER_ROLE_TRANSLATION}

    assert response_json == {
        'employees': [
            {
                'id': utils.YANDEX_UID,
                'is_disabled': False,
                'info': {
                    'name': utils.EMPLOYEE_NAME,
                    'is_removable': False,
                    'phones': [{'number': utils.PHONE}],
                    'yandex_login': utils.YANDEX_LOGIN,
                    'email': utils.YANDEX_EMAIL,
                },
                'roles': [expected_role],
                'revision': 1,
                'created_ts': matching.datetime_string,
                'updated_ts': matching.datetime_string,
            },
            {
                'id': 'yandex_uid2',
                'info': {
                    'name': 'Чумабой_edited',
                    'email': 'candidate@client.ru',
                    'yandex_login': 'yandex_login2',
                    'phones': PHONES[:1],
                    'is_removable': True,
                },
                'roles': [ROLES[0]],
                'is_disabled': True,
                'revision': 2,
                'created_ts': matching.datetime_string,
                'updated_ts': matching.datetime_string,
            },
        ],
    }


async def test_employee_edit(
        pgsql,
        taxi_cargo_corp,
        user_has_rights,
        make_client_employee_edit_request,
):
    expected_response = {
        'id': utils.YANDEX_UID,
        'is_disabled': False,
        'info': {'name': '', 'is_removable': True},
        'revision': 1,
    }

    # should not be disabled cuz system::owner role
    request1 = copy.deepcopy(expected_response)
    del request1['info']['is_removable']
    request1['is_disabled'] = True
    response = await make_client_employee_edit_request(json=request1)
    assert response.status_code == 409

    # but it still can be edited
    request2 = copy.deepcopy(expected_response)
    del request2['info']['is_removable']
    request2['is_disabled'] = False
    request2['info']['name'] = 'new_name'
    expected_response['info']['name'] = 'new_name'
    expected_response['revision'] = 2
    response = await make_client_employee_edit_request(json=request2)
    assert response.status_code == 200
    assert response.json() == expected_response


async def test_internal_employee_list_show_robots(
        taxi_cargo_corp,
        user_has_rights,
        call_internal_employee_list_request,
        call_internal_employee_upsert,
):
    """
    Tests /internal/cargo-corp/v1/client/employee/list handler
    for the return list of robots in admin mode
    """

    request = {
        'id': EMPLOYEE_UID,
        'info': EMPLOYEE,
        'robot_external_ref': 'test_robot_external_ref',
    }

    await call_internal_employee_upsert(request=request)

    # employee/list in admin mode
    response_json = await call_internal_employee_list_request(
        request_mode='admin',
    )

    expected = [
        {
            'id': utils.YANDEX_UID,
            'is_disabled': False,
            'info': {
                'name': utils.EMPLOYEE_NAME,
                'is_removable': False,
                'phones': [{'number': utils.PHONE}],
                'email': utils.YANDEX_EMAIL,
                'yandex_login': utils.YANDEX_LOGIN,
                'phone_pd_ids': [utils.PHONE_PD_ID],
                'email_pd_id': utils.YANDEX_EMAIL_PD_ID,
                'yandex_login_pd_id': utils.YANDEX_LOGIN_PD_ID,
            },
            'roles': [
                {'id': utils.ROLE_ID, 'name': utils.OWNER_ROLE_TRANSLATION},
            ],
            'revision': 1,
            'created_ts': matching.datetime_string,
            'updated_ts': matching.datetime_string,
        },
        {
            'id': EMPLOYEE_UID,
            'robot_external_ref': 'test_robot_external_ref',
            'info': {
                **EMPLOYEE_RESPONSE,
                'phone_pd_ids': [PHONES[1]['number'] + '_id'],
                'email_pd_id': EMPLOYEE_RESPONSE['email'] + '_id',
                'yandex_login_pd_id': (
                    EMPLOYEE_RESPONSE['yandex_login'] + '_id'
                ),
            },
            'is_disabled': False,
            'revision': 1,
            'created_ts': matching.datetime_string,
            'updated_ts': matching.datetime_string,
        },
    ]

    assert list(response_json.keys()) == ['employees']
    utils.assert_items_equal(response_json['employees'], expected)


@pytest.mark.parametrize(
    'request_mode, hide_robots',
    [
        ('b2b', True),
        ('b2b', False),
        ('admin', True),
        ('system', True),
        ('system', False),
    ],
)
async def test_internal_employee_list_hide_robots(
        request_mode,
        hide_robots,
        taxi_cargo_corp,
        user_has_rights,
        call_internal_employee_list_request,
        call_internal_employee_upsert,
):
    """
    Tests /internal/cargo-corp/v1/client/employee/list handler
    for the return list without robots
    """

    request = {
        'id': EMPLOYEE_UID,
        'info': EMPLOYEE,
        'robot_external_ref': 'test_robot_external_ref',
    }

    await call_internal_employee_upsert(request=request)

    response_json = await call_internal_employee_list_request(
        request_mode=request_mode, params={'hide_robots': hide_robots},
    )

    expected = {
        'id': utils.YANDEX_UID,
        'is_disabled': False,
        'info': {
            'name': utils.EMPLOYEE_NAME,
            'is_removable': False,
            'phones': [{'number': utils.PHONE}],
            'email': utils.YANDEX_EMAIL,
            'yandex_login': utils.YANDEX_LOGIN,
        },
        'roles': [{'id': utils.ROLE_ID, 'name': utils.OWNER_ROLE_TRANSLATION}],
        'revision': 1,
        'created_ts': matching.datetime_string,
        'updated_ts': matching.datetime_string,
    }

    if request_mode == 'admin':
        expected['info']['phone_pd_ids'] = [utils.PHONE_PD_ID]
        expected['info']['email_pd_id'] = utils.YANDEX_EMAIL_PD_ID
        expected['info']['yandex_login_pd_id'] = utils.YANDEX_LOGIN_PD_ID

    assert list(response_json.keys()) == ['employees']
    assert response_json['employees'] == [expected]


@pytest.mark.parametrize('request_mode', ['b2b', 'admin', 'system'])
@pytest.mark.config(
    CARGO_CORP_ROLL_OUT_OPTIONS_ENABLED={
        'should_hide_personal_data_admin_employee_list': True,
    },
)
async def test_internal_employee_list_hide_personal_admin(
        request_mode,
        taxi_cargo_corp,
        user_has_rights,
        call_internal_employee_list_request,
):
    """
    Tests /internal/cargo-corp/v1/client/employee/list handler
    that personal data not returned
    """

    response_json = await call_internal_employee_list_request(
        request_mode=request_mode,
    )

    expected = {
        'id': utils.YANDEX_UID,
        'is_disabled': False,
        'info': {
            'name': utils.EMPLOYEE_NAME,
            'is_removable': False,
            'phones': [{'number': utils.PHONE}],
            'email': utils.YANDEX_EMAIL,
            'yandex_login': utils.YANDEX_LOGIN,
        },
        'roles': [{'id': utils.ROLE_ID, 'name': utils.OWNER_ROLE_TRANSLATION}],
        'revision': 1,
        'created_ts': matching.datetime_string,
        'updated_ts': matching.datetime_string,
    }

    if request_mode == 'admin':
        expected['info'].pop('phones')
        expected['info'].pop('email')
        expected['info'].pop('yandex_login')
        expected['info']['phone_pd_ids'] = [utils.PHONE_PD_ID]
        expected['info']['email_pd_id'] = utils.YANDEX_EMAIL_PD_ID
        expected['info']['yandex_login_pd_id'] = utils.YANDEX_LOGIN_PD_ID

    assert list(response_json.keys()) == ['employees']
    assert response_json['employees'] == [expected]


@pytest.mark.parametrize(
    ('phone', 'role_id', 'email', 'name', 'expected_json'),
    (
        pytest.param(
            None,
            None,
            None,
            None,
            {
                'employees': [
                    {
                        'id': EMPLOYEE_UIDS[i],
                        'info': info,
                        'is_disabled': False,
                        'revision': 1,
                        'roles': EMPLOYEE_ROLES[i],
                        'created_ts': matching.datetime_string,
                        'updated_ts': matching.datetime_string,
                    }
                    for i, info in enumerate(EMPLOYEES_RESPONSE)
                ],
            },
            id='ok-no filters-1',
        ),
        pytest.param(
            EMPLOYEES_PHONES[0]['number'],
            None,
            EMPLOYEES_EMAILS[0],
            None,
            {
                'employees': [
                    {
                        'id': EMPLOYEE_UIDS[0],
                        'info': EMPLOYEES_RESPONSE[0],
                        'is_disabled': False,
                        'revision': 1,
                        'roles': EMPLOYEE_ROLES[0],
                        'created_ts': matching.datetime_string,
                        'updated_ts': matching.datetime_string,
                    },
                ],
            },
            id='ok-phone filters-1',
        ),
        pytest.param(
            EMPLOYEES_PHONES[1]['number'],
            None,
            None,
            None,
            {
                'employees': [
                    {
                        'id': EMPLOYEE_UIDS[i],
                        'info': EMPLOYEES_RESPONSE[i],
                        'is_disabled': False,
                        'revision': 1,
                        'roles': EMPLOYEE_ROLES[i],
                        'created_ts': matching.datetime_string,
                        'updated_ts': matching.datetime_string,
                    }
                    for i in [1, 3]
                ],
            },
            id='ok-phone_and_email filters-1',
        ),
        pytest.param(
            None,
            ROLES[0]['id'],
            None,
            None,
            {
                'employees': [
                    {
                        'id': EMPLOYEE_UIDS[i],
                        'info': EMPLOYEES_RESPONSE[i],
                        'is_disabled': False,
                        'revision': 1,
                        'roles': EMPLOYEE_ROLES[i],
                        'created_ts': matching.datetime_string,
                        'updated_ts': matching.datetime_string,
                    }
                    for i in [0, 2]
                ],
            },
            id='ok-role filters-1',
        ),
        pytest.param(
            None,
            ROLES[2]['id'],
            None,
            None,
            {
                'employees': [
                    {
                        'id': EMPLOYEE_UIDS[2],
                        'info': EMPLOYEES_RESPONSE[2],
                        'is_disabled': False,
                        'revision': 1,
                        'roles': EMPLOYEE_ROLES[2],
                        'created_ts': matching.datetime_string,
                        'updated_ts': matching.datetime_string,
                    },
                ],
            },
            id='ok-role filters-2',
        ),
        pytest.param(
            None,
            None,
            None,
            EMPLOYEES[0]['name'],
            {
                'employees': [
                    {
                        'id': EMPLOYEE_UIDS[i],
                        'info': info,
                        'is_disabled': False,
                        'revision': 1,
                        'roles': EMPLOYEE_ROLES[i],
                        'created_ts': matching.datetime_string,
                        'updated_ts': matching.datetime_string,
                    }
                    for i, info in enumerate(EMPLOYEES_RESPONSE)
                ],
            },
            id='ok-name filters-1',
        ),
        pytest.param(
            None,
            None,
            None,
            EMPLOYEES[3]['name'],
            {
                'employees': [
                    {
                        'id': EMPLOYEE_UIDS[3],
                        'info': EMPLOYEES_RESPONSE[3],
                        'is_disabled': False,
                        'revision': 1,
                        'roles': EMPLOYEE_ROLES[3],
                        'created_ts': matching.datetime_string,
                        'updated_ts': matching.datetime_string,
                    },
                ],
            },
            id='ok-name filters-2',
        ),
        pytest.param(
            EMPLOYEES_PHONES[1]['number'],
            'unknown_role_id',
            None,
            EMPLOYEES[0]['name'],
            {'employees': []},
            id='ok-empty_role_id filters-1',
        ),
        pytest.param(
            EMPLOYEES_PHONES[1]['number'],
            None,
            'unknown@employee.ru',
            EMPLOYEES[1]['name'],
            {'employees': []},
            id='ok-empty_email filters-1',
        ),
        pytest.param(
            '8902835394',
            None,
            None,
            EMPLOYEES[2]['name'],
            {'employees': []},
            id='ok-empty_number filters-1',
        ),
    ),
)
async def test_employee_list_filters(
        pgsql,
        taxi_cargo_corp,
        mockserver,
        phone,
        role_id,
        email,
        name,
        expected_json,
        call_internal_employee_list_request,
        call_internal_employee_upsert,
):
    @mockserver.json_handler('/personal/v1/phones/find')
    def _phones_find(request):
        assert request.json.keys() == {'value', 'primary_replica'}
        phone = request.json['value']
        if phone in [p['number'] for p in EMPLOYEES_PHONES]:
            return {'id': phone + '_id', 'value': phone}
        return mockserver.make_response(
            status=404,
            json={'code': '404', 'message': 'Doc not found in mongo'},
        )

    @mockserver.json_handler('/personal/v1/emails/find')
    def _emails_find(request):
        assert request.json.keys() == {'value', 'primary_replica'}
        email = request.json['value']
        if email in EMPLOYEES_EMAILS:
            return {'id': email + '_id', 'value': email}
        return mockserver.make_response(
            status=404,
            json={'code': '404', 'message': 'Doc not found in mongo'},
        )

    for i, info in enumerate(EMPLOYEES):
        request = {'id': EMPLOYEE_UIDS[i], 'info': info}
        await call_internal_employee_upsert(request=request)

    for i, role_arr in enumerate(EMPLOYEE_ROLES):
        for role in role_arr:
            utils.create_role(
                pgsql, role_id=role['id'], role_name=role['name'],
            )
            utils.create_employee_role(
                pgsql, role_id=role['id'], yandex_uid=EMPLOYEE_UIDS[i],
            )
    # end of prepare

    query = {}
    if phone:
        query['phone'] = phone
    if role_id:
        query['role_id'] = role_id
    if email:
        query['email'] = email
    if name:
        query['name'] = name

    response_json = await call_internal_employee_list_request(params=query)
    for employee in response_json['employees']:
        employee['info']['phones'].sort(key=lambda x: x['number'])

    assert response_json == expected_json


async def test_employee_list_with_few_phones(
        taxi_cargo_corp,
        call_internal_employee_upsert,
        call_internal_employee_list_request,
):
    request = {'id': EMPLOYEE_UID, 'info': EMPLOYEE_WITH_FEW_PHONES}
    await call_internal_employee_upsert(request=request)

    response_json = await call_internal_employee_list_request()

    expected_employee_info = {
        'id': EMPLOYEE_UID,
        'info': EMPLOYEE_WITH_FEW_PHONES_RESPONSE,
        'is_disabled': False,
        'revision': 1,
        'created_ts': matching.datetime_string,
        'updated_ts': matching.datetime_string,
    }
    # order of phones is not guarantied
    for employee in response_json['employees']:
        if 'phones' not in employee['info']:
            continue
        employee['info']['phones'].sort(key=lambda x: x['number'])
    assert expected_employee_info in response_json['employees']


@pytest.mark.parametrize(
    'corp_client_id, yandex_uid, expected_code, expected_json',
    [
        (
            utils.CORP_CLIENT_ID,
            utils.YANDEX_UID,
            200,
            {'is_disabled': False, 'is_employee': True},
        ),
        (
            'bad' + utils.CORP_CLIENT_ID[3:],
            utils.YANDEX_UID,
            200,
            {'is_disabled': True, 'is_employee': False},
        ),
        (
            utils.CORP_CLIENT_ID,
            'bad' + utils.YANDEX_UID[3:],
            200,
            {'is_disabled': True, 'is_employee': False},
        ),
    ],
)
async def test_employee_traits(
        taxi_cargo_corp,
        user_has_rights,
        corp_client_id,
        yandex_uid,
        expected_code,
        expected_json,
):

    response = await taxi_cargo_corp.post(
        '/internal/cargo-corp/v1/client/employee/traits',
        headers={
            'X-B2B-Client-Id': corp_client_id,
            'X-Yandex-Uid': yandex_uid,
        },
    )
    assert response.status_code == expected_code

    result = response.json()
    assert result == expected_json


@pytest.mark.parametrize(
    'url',
    [
        'v1/client/employee/remove',
        '/internal/cargo-corp/v1/client/employee/remove',
    ],
)
async def test_employees_remove_illegal_role(
        url,
        pgsql,
        taxi_cargo_corp,
        user_has_rights,
        select_employee,
        insert_card,
        select_cards,
        select_employee_roles,
        populate_roles,
        insert_employee_role,
        call_internal_employee_upsert,
):
    """
    Test v1/client/employee/remove handler with illegal role
    """

    populate_roles(corp_client_id=utils.CORP_CLIENT_ID)

    # owner
    owner_employee = select_employee(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=utils.YANDEX_UID,
    )
    owner_roles = select_employee_roles(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=utils.YANDEX_UID,
    )
    owner_card = insert_card(
        corp_client_id=utils.CORP_CLIENT_ID,
        yandex_uid=utils.YANDEX_UID,
        card_id=utils.CARD_ID,
    )

    # unchanged employee
    request = {
        'id': EMPLOYEE_UIDS[0],
        'info': EMPLOYEE,
        'roles': EMPLOYEE_ROLES[0],
    }
    await call_internal_employee_upsert(request=request)
    unchanged_employee = select_employee(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=EMPLOYEE_UIDS[0],
    )
    unchanged_role = insert_employee_role(
        corp_client_id=utils.CORP_CLIENT_ID,
        yandex_uid=EMPLOYEE_UIDS[0],
        role_id=ROLES[0]['id'],
    )
    unchanged_card = insert_card(
        corp_client_id=utils.CORP_CLIENT_ID,
        yandex_uid=EMPLOYEE_UIDS[0],
        card_id=utils.CARD_ID + '_2',
    )

    response = await taxi_cargo_corp.post(
        url,
        headers={'X-B2B-Client-Id': utils.CORP_CLIENT_ID},
        json={
            'employees': [{'id': utils.YANDEX_UID}, {'id': EMPLOYEE_UIDS[0]}],
        },
    )
    # utils.YANDEX_UID is owner and can't be removed
    assert response.status_code == 409
    assert response.json()['code'] == 'not_deletable_employee'

    employees = [
        select_employee(
            corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=utils.YANDEX_UID,
        ),
        select_employee(
            corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=EMPLOYEE_UIDS[0],
        ),
    ]

    assert employees == [owner_employee, unchanged_employee]

    roles = [
        select_employee_roles(
            corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=utils.YANDEX_UID,
        ),
        select_employee_roles(
            corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=EMPLOYEE_UIDS[0],
        ),
    ]
    assert roles == [owner_roles, [unchanged_role]]

    cards = select_cards(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=utils.YANDEX_UID,
    )
    assert cards == [owner_card]

    cards = select_cards(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=EMPLOYEE_UIDS[0],
    )
    assert cards == [unchanged_card]


@pytest.mark.parametrize(
    'url',
    [
        'v1/client/employee/remove',
        '/internal/cargo-corp/v1/client/employee/remove',
    ],
)
async def test_employees_remove(
        url,
        pgsql,
        taxi_cargo_corp,
        user_has_rights,
        call_internal_employee_upsert,
        select_employee,
        insert_card,
        select_cards,
        select_employee_roles,
        populate_roles,
        insert_employee_role,
):
    """
    Test v1/client/employee/remove handler with successful removal
    """

    populate_roles(corp_client_id=utils.CORP_CLIENT_ID)

    # owner
    owner_employee = select_employee(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=utils.YANDEX_UID,
    )
    owner_roles = select_employee_roles(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=utils.YANDEX_UID,
    )
    owner_card = insert_card(
        corp_client_id=utils.CORP_CLIENT_ID,
        yandex_uid=utils.YANDEX_UID,
        card_id=utils.CARD_ID,
    )

    # unchanged employee
    request = {
        'id': EMPLOYEE_UIDS[0],
        'info': EMPLOYEE,
        'roles': EMPLOYEE_ROLES[0],
    }
    await call_internal_employee_upsert(request=request)
    unchanged_employee = select_employee(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=EMPLOYEE_UIDS[0],
    )
    unchanged_role = insert_employee_role(
        corp_client_id=utils.CORP_CLIENT_ID,
        yandex_uid=EMPLOYEE_UIDS[0],
        role_id=ROLES[0]['id'],
    )

    # employee to remove
    request = {
        'id': EMPLOYEE_UIDS[1],
        'info': EMPLOYEE_WITH_FEW_PHONES,
        'roles': EMPLOYEE_ROLES[1],
    }
    await call_internal_employee_upsert(request=request)
    employee_to_remove = select_employee(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=EMPLOYEE_UIDS[1],
    )
    card_to_remove = insert_card(
        corp_client_id=utils.CORP_CLIENT_ID,
        yandex_uid=EMPLOYEE_UIDS[1],
        card_id=utils.CARD_ID + '_2',
    )
    role_to_remove = insert_employee_role(
        corp_client_id=utils.CORP_CLIENT_ID,
        yandex_uid=EMPLOYEE_UIDS[1],
        role_id=ROLES[1]['id'],
    )

    response = await taxi_cargo_corp.post(
        url,
        headers={'X-B2B-Client-Id': utils.CORP_CLIENT_ID},
        json={'employees': [{'id': EMPLOYEE_UIDS[1]}]},
    )

    assert response.status_code == 200
    assert response.json() == {}

    employees = [
        select_employee(
            corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=utils.YANDEX_UID,
        ),
        select_employee(
            corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=EMPLOYEE_UIDS[0],
        ),
    ]

    assert employees == [owner_employee, unchanged_employee]

    employee = select_employee(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=EMPLOYEE_UIDS[1],
    )
    employee_to_remove['is_removed'] = True
    employee_to_remove['revision'] += 1
    utils.assert_increased_updated_ts(employee, employee_to_remove)

    roles = [
        select_employee_roles(
            corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=utils.YANDEX_UID,
        ),
        select_employee_roles(
            corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=EMPLOYEE_UIDS[0],
        ),
    ]
    assert roles == [owner_roles, [unchanged_role]]

    roles = select_employee_roles(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=EMPLOYEE_UIDS[1],
    )
    assert len(roles) == 1

    role_to_remove['is_removed'] = True
    utils.assert_increased_updated_ts(roles[0], role_to_remove)

    cards = select_cards(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=utils.YANDEX_UID,
    )
    assert cards == [owner_card]

    cards = select_cards(
        corp_client_id=utils.CORP_CLIENT_ID, yandex_uid=EMPLOYEE_UIDS[1],
    )
    assert len(cards) == 1
    card_to_remove['is_removed'] = True
    utils.assert_increased_updated_ts(cards[0], card_to_remove)
