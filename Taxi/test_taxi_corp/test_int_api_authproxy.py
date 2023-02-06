import typing

import pytest

from taxi_corp.util import hdrs
from test_taxi_corp import load_util

DEPARTMENT_MANAGER_PERMISSIONS = [
    # this better be in sync with from access_data_permissions_by_role.json
    'taxi',
    'taxi_department_create',
    'taxi_department_part',
    'taxi_department_full',
    'taxi_other',
]


def authproxy_headers(
        client_id: str, department_id: typing.Optional[str] = None,
) -> typing.Dict[str, str]:
    headers = {
        hdrs.X_YANDEX_UID: f'{client_id}_uid',
        hdrs.X_YANDEX_LOGIN: f'{client_id}_login',
    }
    if department_id is not None:
        headers.update(
            {
                hdrs.X_YATAXI_CORP_ACL_CLIENT_ID: client_id,
                hdrs.X_YATAXI_CORP_ACL_DEPARTMENT_ID: department_id,
                hdrs.X_YATAXI_CORP_ACL_PERMISSIONS: ','.join(
                    DEPARTMENT_MANAGER_PERMISSIONS,
                ),
                hdrs.X_YATAXI_CORP_ACL_ROLE: 'department_manager',
            },
        )
    return headers


def load_access_data(load_json, yandex_uid):
    data = load_util.load_access_data(load_json, yandex_uid)
    if data is None:
        return {}
    permissions = data['permissions']
    if data['role'] == 'client':
        # mimicking acl.filter_permissions
        permissions = [
            perm
            for perm in data['permissions']
            if perm != 'taxi_department_create'
        ]
    return dict(
        yandex_uid=yandex_uid,
        client_id=data['client_id'],
        role=data['role'],
        department_id=data['department_id'],
        permissions=permissions,
    )


@pytest.mark.parametrize(
    [
        'client',
        'passport_mock_with_call_checks',
        'request_uid',
        'request_headers',
        'passport_called_times',
        'corp_managers_called_times',
    ],
    [
        pytest.param(
            'taxi_corp_real_auth_client',
            'client1',  # passport_mock
            'client1_uid',
            {},  # request_headers
            1,  # passport_called_times
            1,  # corp_managers_called_times
            id='no-authproxy-client1',
        ),
        pytest.param(
            'taxi_corp_real_auth_client',
            'client3',  # passport_mock
            'client3_uid',
            {},  # request_headers
            1,  # passport_called_times
            1,  # corp_managers_called_times
            id='no-authproxy-client3',
        ),
        pytest.param(
            'taxi_corp_authproxy_client',
            'client1',  # passport_mock
            'client1_uid',
            authproxy_headers('client1'),
            0,  # passport_called_times (got headers with UID and login)
            1,  # corp_managers_called_times
            id='authproxy-passport-headers-only',
        ),
        pytest.param(
            'taxi_corp_authproxy_client',
            'client3',  # passport_mock
            'client3_uid',
            authproxy_headers('client3', department_id='dep1'),
            0,  # passport_called_times
            0,  # corp_managers_called_times
            id='authproxy-all-headers',
        ),
    ],
    indirect=['client', 'passport_mock_with_call_checks'],
)
async def test_authproxy(
        load_json,
        client,
        passport_mock_with_call_checks,
        request_uid,
        request_headers,
        passport_called_times,
        corp_managers_called_times,
):
    """This is to test @corp_web.from_authproxy decorator"""

    response = await client.get('/test/access_data', headers=request_headers)
    assert response.status == 200

    # check calls to passport
    passport_handler = passport_mock_with_call_checks.get_passport_info
    assert len(passport_handler.calls) == passport_called_times

    # check calls to corp-managers
    access_data_mock = client.server.app.access_data_mock
    access_data_handler = access_data_mock.corp_managers_access_data
    assert access_data_handler.times_called == corp_managers_called_times

    # check access data from handle
    response_data = await response.json()
    expected_response = load_access_data(load_json, request_uid)
    assert response_data == expected_response
