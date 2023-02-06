import copy
import datetime

import pytest

from taxi.util import dates

from callcenter_operators import models
from callcenter_operators.storage.postgresql import db
from test_callcenter_operators import test_utils


OPERATOR = {
    'metaqueues': ['test'],
    'login': 'login',
    'uid': 'uid',
    'sub_status': 'foobar',
    'project': 'help',
}


async def _add_operator(
        operator, web_context, need_connect: bool = False,
) -> int:
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
        if need_connect:
            status = 'connected'
            metaqueues = req_op['metaqueues']
        else:
            status = 'disconnected'
            metaqueues = list()
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
                status,
                req_op.get('sub_status'),
            ),
            web_context,
            conn,
        )
    return db_operator.id


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'metaqueues': ['help'],
            'display_name': 'test',
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
)
async def test_form_state(
        taxi_callcenter_operators_web,
        mockserver,
        mock_save_status,
        pgsql,
        web_context,
):
    operator = copy.deepcopy(OPERATOR)
    await _add_operator(operator, web_context, True)
    auth_headers = test_utils.make_auth_headers(operator)
    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/form/state',
        headers=auth_headers,
        json={'project': 'help'},
    )
    assert resp.status == 200
    assert await resp.json() == {
        'info': {
            'status': 'connected',
            'sub_status': 'foobar',
            'inbound_allowed': False,
        },
        'queues_info': {'metaqueues': ['test'], 'status': 'connected'},
        'reg_info': {'reg_domain': 'yandex.ru', 'regs': ['reg1', 'reg2']},
    }

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        f' SELECT is_form_opened FROM callcenter_auth.current_info'
        f' WHERE id = 1;',
    )
    record = list(cursor.fetchone())
    assert record == [True]


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'metaqueues': ['help'],
            'display_name': 'test',
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
)
@pytest.mark.config(
    CALLCENTER_METAQUEUE_PREFIX_TO_SIP_DOMAIN={
        '__default__': 'ru',
        'by': 'by',
    },
)
async def test_form_state_too_many_reg_groups(
        taxi_callcenter_operators_web,
        mockserver,
        mock_save_status,
        pgsql,
        web_context,
        mock_callcenter_reg,
):
    @mock_callcenter_reg('/v1/reg_groups')
    async def _handle_urls(request, *args, **kwargs):
        return {
            'reg_groups': [
                {
                    'group_name': 'ru',
                    'regs': ['reg1', 'reg2'],
                    'reg_domain': 'yandex.ru',
                },
                {
                    'group_name': 'by',
                    'regs': ['reg3', 'reg4'],
                    'reg_domain': 'yandex.ru',
                },
            ],
        }

    operator = copy.deepcopy(OPERATOR)
    operator['metaqueues'].append('by_test')
    op_id = await _add_operator(operator, web_context, True)
    print(op_id)
    auth_headers = test_utils.make_auth_headers(operator)
    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/form/state',
        headers=auth_headers,
        json={'project': 'help'},
    )
    assert resp.status == 200
    assert await resp.json() == {
        'info': {
            'status': 'connected',
            'sub_status': 'foobar',
            'inbound_allowed': False,
        },
        'queues_info': {
            'metaqueues': ['test', 'by_test'],
            'status': 'connected',
        },
    }


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'metaqueues': ['help'],
            'display_name': 'test',
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
)
@pytest.mark.now('2021-03-05T12:00:00.00Z')
async def test_form_state_save_time(
        taxi_callcenter_operators_web,
        mockserver,
        mock_save_status,
        pgsql,
        web_context,
):
    operator = copy.deepcopy(OPERATOR)
    operator['now'] = dates.utc_with_tz() - datetime.timedelta(minutes=10)
    op_id = await _add_operator(operator, web_context, True)
    auth_headers = test_utils.make_auth_headers(operator)
    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/form/state',
        headers=auth_headers,
        json={'project': 'help'},
    )
    assert resp.status == 200
    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        f'SELECT last_visited_at '
        f'FROM callcenter_auth.current_info '
        f'WhERE id = {op_id}',
    )
    result = cursor.fetchone()
    assert result[0] > operator['now']
    cursor.close()


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'metaqueues': ['help'],
            'display_name': 'test',
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'test': {
            'metaqueues': ['test'],
            'display_name': 'test',
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
)
@pytest.mark.config(
    CALLCENTER_METAQUEUE_PREFIX_TO_SIP_DOMAIN={
        '__default__': 'ru',
        'by': 'by',
    },
)
async def test_form_state_alert(
        taxi_callcenter_operators_web,
        mockserver,
        mock_save_status,
        pgsql,
        web_context,
        mock_callcenter_reg,
):
    operator = copy.deepcopy(OPERATOR)
    operator['project'] = 'test'
    await _add_operator(operator, web_context, True)
    auth_headers = test_utils.make_auth_headers(operator)
    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/form/state',
        headers=auth_headers,
        json={'project': 'help'},
    )
    assert resp.status == 200
    assert await resp.json() == {
        'info': {
            'status': 'connected',
            'sub_status': 'foobar',
            'inbound_allowed': False,
        },
        'reg_info': {'reg_domain': 'yandex.ru', 'regs': ['reg1', 'reg2']},
        'queues_info': {'metaqueues': ['test'], 'status': 'connected'},
        'alert': {
            'alert_code': 'project_conflict',
            'alert_message': (
                'Ваш проект help изменился. '
                'Обратитесь к руководителю и '
                'выйдите на другую форму.'
            ),
            'extra': {'real_project': 'test'},
        },
    }


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'metaqueues': ['help'],
            'display_name': 'test',
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
)
@pytest.mark.config(
    CALLCENTER_METAQUEUE_PREFIX_TO_SIP_DOMAIN={
        '__default__': 'ru',
        'by': 'by',
    },
)
async def test_form_state_500_bad_project(
        taxi_callcenter_operators_web,
        mockserver,
        mock_save_status,
        pgsql,
        web_context,
        mock_callcenter_reg,
):
    operator = copy.deepcopy(OPERATOR)
    await _add_operator(operator, web_context, True)
    auth_headers = test_utils.make_auth_headers(operator)
    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/form/state',
        headers=auth_headers,
        json={'project': 'test'},
    )
    assert resp.status == 500
