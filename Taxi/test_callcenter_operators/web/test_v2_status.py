import copy

import pytest

from taxi.util import dates

from callcenter_operators import models
from callcenter_operators.storage.postgresql import db
from test_callcenter_operators import test_utils


OPERATOR = {
    'metaqueues': ['test'],
    'login': 'login',
    'uid': 'uid',
    'project': 'help',
}


async def _add_operator(operator, web_context) -> int:
    req_op = copy.deepcopy(operator)
    req_op['yandex_login'] = req_op['login']
    req_op['yandex_uid'] = req_op['uid']
    req_op['callcenter_id'] = 'cc_1'
    req_op['first_name'] = 'first'
    req_op['last_name'] = 'last'
    req_op['password'] = 'password1111'
    req_op['now'] = req_op.get('now') or dates.utc_with_tz()
    req_op['working_domain'] = 'test.com'
    req_op['roles_to_add'] = list()
    pool = db.OperatorsRepo.get_pool(web_context)
    async with pool.acquire() as conn, conn.transaction():
        await db.OperatorsRepo.grant_access(web_context, conn, **req_op)
        db_record = await db.OperatorsRepo.get_operator(
            web_context, conn, uid=req_op['yandex_uid'], with_not_ready=True,
        )
        db_operator = models.Operator.from_db(db_record)
        op_id = int(db_operator.id)
        agent_id = str(db_operator.agent_id)
        name_in_tel = str(db_operator.name_in_telephony)
        await db.OperatorsRepo.set_operator_as_ready(
            op_id, req_op['now'], web_context, conn,
        )
        metaqueues = req_op['metaqueues']
        await db.OperatorsRepo.set_operator_control_model(
            models.OperatorControlModel(
                op_id,
                agent_id,
                req_op['uid'],
                req_op['login'],
                req_op['working_domain'],
                req_op.get('now') or dates.utc_with_tz(),
                name_in_tel,
                metaqueues,
                req_op['project'],
                req_op.get('status'),
                req_op.get('sub_status'),
            ),
            web_context,
            conn,
        )
    return db_operator.id


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'display_name': 'Дисп',
            'metaqueues': ['disp'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
)
@pytest.mark.parametrize(
    ('status', 'sub_status', 'expected_status', 'expected_sub_status'),
    (
        ('disconnected', None, 'connected', None),
        ('disconnected', None, 'paused', None),
        ('connected', None, 'disconnected', None),
        ('connected', None, 'paused', None),
        ('paused', None, 'connected', None),
        ('paused', None, 'disconnected', None),
        ('connected', None, 'connected', 'foobar'),
        ('connected', 'foobar', 'connected', None),
    ),
)
async def test_v2_status(
        taxi_callcenter_operators_web,
        mockserver,
        mock_save_status,
        pgsql,
        web_context,
        mock_set_status_cc_queues,
        status,
        sub_status,
        expected_status,
        expected_sub_status,
):
    operator = copy.deepcopy(OPERATOR)
    operator['status'] = status
    operator['sub_status'] = sub_status
    op_id = await _add_operator(operator, web_context)
    auth_headers = test_utils.make_auth_headers(operator)
    if expected_sub_status is not None:
        request = {
            'new_status': {
                'status': expected_status,
                'sub_status': expected_sub_status,
            },
        }
    else:
        request = {'new_status': {'status': expected_status}}
    request['project'] = 'help'
    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v2/status',
        headers=auth_headers,
        json=request,
    )
    assert resp.status == 200
    assert mock_save_status.handle_urls.times_called == 1
    assert mock_set_status_cc_queues.handle_urls.times_called == 1
    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        f' SELECT status, sub_status'
        f' FROM callcenter_auth.current_info'
        f' WHERE id = {op_id};',
    )
    record = cursor.fetchone()
    assert record[0] == expected_status
    assert record[1] == expected_sub_status


@pytest.mark.config(
    CALLCENTER_STATS_USE_NEW_DATA=True,
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'display_name': 'Дисп',
            'metaqueues': ['disp'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
)
@pytest.mark.parametrize(
    ('status', 'sub_status', 'expected_status', 'expected_sub_status'),
    (('connected', 'foobar', 'connected', None),),
)
async def test_status_change_new(
        taxi_callcenter_operators_web,
        mockserver,
        mock_save_status,
        pgsql,
        web_context,
        mock_set_status_cc_queues,
        status,
        sub_status,
        expected_status,
        expected_sub_status,
):
    operator = copy.deepcopy(OPERATOR)
    operator['status'] = status
    operator['sub_status'] = sub_status
    op_id = await _add_operator(operator, web_context)
    auth_headers = test_utils.make_auth_headers(operator)
    if expected_sub_status is not None:
        request = {
            'new_status': {
                'status': expected_status,
                'sub_status': expected_sub_status,
            },
        }
    else:
        request = {'new_status': {'status': expected_status}}
    request['project'] = 'help'
    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v2/status',
        headers=auth_headers,
        json=request,
    )
    assert resp.status == 200
    # check save history in cc-stats
    assert mock_save_status.handle_urls.times_called == 1
    # check no request in cc-queues
    assert not mock_set_status_cc_queues.handle_urls.times_called
    # check save status in cc-reg
    assert mock_save_status.save_status_cc_reg.times_called == 1
    # check save status locally
    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        f' SELECT status, sub_status'
        f' FROM callcenter_auth.current_info'
        f' WHERE id = {op_id};',
    )
    record = cursor.fetchone()
    assert record[0] == expected_status
    assert record[1] == expected_sub_status


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'disp': {
            'display_name': 'Дисп',
            'metaqueues': ['disp'],
            'should_use_internal_queue_service': False,
            'reg_groups': ['ru'],
        },
    },
)
@pytest.mark.parametrize(
    ('status', 'sub_status', 'expected_status', 'expected_sub_status'),
    (
        ('disconnected', None, 'connected', None),
        ('disconnected', None, 'paused', None),
        ('connected', None, 'disconnected', None),
        ('connected', None, 'paused', None),
        ('paused', None, 'connected', None),
        ('paused', None, 'disconnected', None),
        ('connected', None, 'connected', 'foobar'),
        ('connected', 'foobar', 'connected', None),
    ),
)
async def test_v2_status_no_queues_service(
        taxi_callcenter_operators_web,
        mockserver,
        mock_save_status,
        pgsql,
        web_context,
        mock_set_status_cc_queues,
        status,
        sub_status,
        expected_status,
        expected_sub_status,
):
    operator = copy.deepcopy(OPERATOR)
    operator['status'] = status
    operator['sub_status'] = sub_status
    operator['project'] = 'disp'
    op_id = await _add_operator(operator, web_context)
    auth_headers = test_utils.make_auth_headers(operator)
    if expected_sub_status is not None:
        request = {
            'new_status': {
                'status': expected_status,
                'sub_status': expected_sub_status,
            },
        }
    else:
        request = {'new_status': {'status': expected_status}}
    request['project'] = 'disp'
    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v2/status',
        headers=auth_headers,
        json=request,
    )
    assert resp.status == 200
    assert mock_save_status.handle_urls.times_called  # always
    assert not mock_set_status_cc_queues.handle_urls.times_called
    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        f' SELECT status, sub_status'
        f' FROM callcenter_auth.current_info'
        f' WHERE id = {op_id};',
    )
    record = cursor.fetchone()
    assert record[0] == expected_status
    assert record[1] == expected_sub_status


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'disp': {
            'display_name': 'Дисп',
            'metaqueues': ['disp'],
            'should_use_internal_queue_service': False,
            'reg_groups': ['ru'],
        },
    },
)
@pytest.mark.config(CALLCENTER_OPERATORS_ERROR_ON_PROJECT_MISMATCH=True)
async def test_project_mismatch(
        taxi_callcenter_operators_web, mockserver, pgsql, web_context,
):
    operator = copy.deepcopy(OPERATOR)
    operator['status'] = 'disconnected'
    operator['project'] = 'help'
    await _add_operator(operator, web_context)
    auth_headers = test_utils.make_auth_headers(operator)
    request = {'new_status': {'status': 'connected'}, 'project': 'disp'}
    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v2/status',
        headers=auth_headers,
        json=request,
    )
    assert resp.status == 400  # project mismatch
