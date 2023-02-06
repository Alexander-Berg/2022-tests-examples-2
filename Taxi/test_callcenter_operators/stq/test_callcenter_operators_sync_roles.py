import json

from aiohttp import web
import pytest

from test_callcenter_operators import params


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_test_sync_op_roles.sql'],
)
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES_FOR_STQ_TASK,  # noqa: E501
)
@pytest.mark.parametrize(
    [
        'uid',
        'expected_ac_db',
        'expected_cc_reg_add_times_called',
        'expected_cc_reg_del_times_called',
    ],
    (
        pytest.param(
            'uid2',
            {
                'uid1': {
                    'operators',
                    'account_managers',
                    'support_operators',
                    'group_that_not_in_cc',
                },
                'uid2': {'operators', 'g1', 'g2', 'g3'},
                'uid6': {'group_to_delete'},
                'uid_to_delete': {},
            },
            1,
            0,
            id='add',
        ),
        pytest.param(
            'uid6',
            {
                'uid1': {
                    'operators',
                    'account_managers',
                    'support_operators',
                    'group_that_not_in_cc',
                },
                'uid2': {'g1', 'g2', 'g3'},
                'uid6': set(),
                'uid_to_delete': {},
            },
            0,
            1,
            id='delete',
        ),
        pytest.param(
            'uid1',
            {
                'uid1': {
                    'operators',
                    'call_center_heads',
                    'team_leaders',
                    'group_that_not_in_cc',
                },
                'uid2': {'g1', 'g2', 'g3'},
                'uid6': {'group_to_delete'},
                'uid_to_delete': {},
            },
            1,
            0,
            id='add + delete',
        ),
        pytest.param(
            'not_uid',
            {
                'uid1': {
                    'operators',
                    'account_managers',
                    'support_operators',
                    'group_that_not_in_cc',
                },
                'uid2': {'g1', 'g2', 'g3'},
                'uid6': {'group_to_delete'},
                'uid_to_delete': {},
            },
            0,
            1,
            id='bad uid',
        ),
        pytest.param(
            'uid_to_delete',
            {
                'uid1': {
                    'operators',
                    'account_managers',
                    'support_operators',
                    'group_that_not_in_cc',
                },
                'uid2': {'g1', 'g2', 'g3'},
                'uid6': {'group_to_delete'},
            },
            0,
            1,
            id='deleting operator',
        ),
        pytest.param(
            'uid7',
            {
                'uid1': {
                    'operators',
                    'account_managers',
                    'support_operators',
                    'group_that_not_in_cc',
                },
                'uid2': {'g1', 'g2', 'g3'},
                'uid6': {'group_to_delete'},
                'uid_to_delete': {},
                'uid7': {'operators'},
            },
            0,
            0,
            id='add operator without agent_id',
        ),
    ),
)
async def test_sync_op_roles(
        mock_access_control_users,
        stq_runner,
        uid,
        expected_ac_db,
        expected_cc_reg_add_times_called,
        expected_cc_reg_del_times_called,
        mockserver,
):
    @mockserver.json_handler('/callcenter-reg/v1/agent/add_bulk')
    async def handle_add_bulk(request, *args, **kwargs):
        print('cc-reg agents:', request.json['agents'])
        body = {'results': []}
        for agent in request.json['agents']:
            body['results'].append(
                {
                    'yandex_uid': agent['yandex_uid'],
                    'sip_username': agent['sip_username'],
                    'code': (
                        'ok'
                        if agent['yandex_uid'] != 'uid1'
                        else 'already_added'
                    ),
                },
            )
        return web.Response(status=200, body=json.dumps(body))

    @mockserver.json_handler('/callcenter-reg/v1/agent/delete_bulk')
    async def handle_delete_bulk(request, *args, **kwargs):
        print('cc-reg yandex_uids:', request.json['yandex_uids'])
        body = {'results': []}
        for yandex_uid in request.json['yandex_uids']:
            body['results'].append(
                {
                    'yandex_uid': yandex_uid,
                    'code': (
                        'ok' if yandex_uid != 'uid1' else 'already_deleted'
                    ),
                },
            )
        return web.Response(status=200, body=json.dumps(body))

    mock_access_control_users.reset_user_groups()
    await stq_runner.callcenter_operators_sync_roles.call(
        task_id=uid, args=[], kwargs={'uid': uid}, exec_tries=1,
    )
    assert mock_access_control_users.user_groups == expected_ac_db
    assert handle_add_bulk.times_called == expected_cc_reg_add_times_called
    assert handle_delete_bulk.times_called == expected_cc_reg_del_times_called
