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
            'metaqueues': ['test'],
            'display_name': 'test',
            'should_use_internal_queue_service': False,
            'reg_groups': ['ru'],
        },
    },
)
@pytest.mark.parametrize(
    ('connected', 'expected'),
    (
        (
            True,
            {
                'sip_username': '1000000000',
                'flow_info': [],
                'reg_info': {
                    'reg_domain': 'yandex.ru',
                    'regs': ['reg1', 'reg2'],
                },
                'config_info': {
                    'CALLCENTER_SIP_OPTIONS': {
                        'answerTimer': 1000,
                        'chainIdHeader': 'X-TC-GUID',
                        'domainToSip': {
                            'by': ['reg3', 'reg4'],
                            'ru': ['reg1', 'reg2'],
                        },
                        'originalDNHeader': 'X-CC-OriginalDN',
                        'port': 7443,
                        'stunServers': ['stun:141.8.146.81:3478'],
                        'urls': {'by': 'yandex.ru', 'ru': 'yandex.ru'},
                        'volume': 0.7,
                        'websocketConnectionTimeout': 4000,
                    },
                    'CALLCENTER_OPERATOR_LOGINS_TO_SIP_MAP': {},
                },
            },
        ),
        (
            False,
            {
                'sip_username': '1000000000',
                'reg_info': {
                    'reg_domain': 'yandex.ru',
                    'regs': ['reg1', 'reg2'],
                },
                'flow_info': [],
                'config_info': {
                    'CALLCENTER_SIP_OPTIONS': {
                        'answerTimer': 1000,
                        'chainIdHeader': 'X-TC-GUID',
                        'domainToSip': {
                            'by': ['reg3', 'reg4'],
                            'ru': ['reg1', 'reg2'],
                        },
                        'originalDNHeader': 'X-CC-OriginalDN',
                        'port': 7443,
                        'stunServers': ['stun:141.8.146.81:3478'],
                        'urls': {'by': 'yandex.ru', 'ru': 'yandex.ru'},
                        'volume': 0.7,
                        'websocketConnectionTimeout': 4000,
                    },
                    'CALLCENTER_OPERATOR_LOGINS_TO_SIP_MAP': {},
                },
            },
        ),
    ),
)
async def test_form_launch(
        taxi_callcenter_operators_web,
        mockserver,
        mock_save_status,
        pgsql,
        web_context,
        connected,
        expected,
):
    operator = copy.deepcopy(OPERATOR)
    await _add_operator(operator, web_context, connected)
    auth_headers = test_utils.make_auth_headers(operator)
    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/form/launch',
        headers=auth_headers,
        json={'project': 'help'},
    )
    assert resp.status == 200
    assert await resp.json() == expected

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
            'metaqueues': ['test'],
            'display_name': 'test',
            'should_use_internal_queue_service': False,
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
async def test_form_launch_too_many_reg_groups(
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
        '/cc/v1/callcenter-operators/v1/form/launch',
        headers=auth_headers,
        json={'project': 'help'},
    )
    assert resp.status == 200
    assert await resp.json() == {
        'sip_username': '1000000000',
        'flow_info': [],
        'config_info': {
            'CALLCENTER_SIP_OPTIONS': {
                'answerTimer': 1000,
                'chainIdHeader': 'X-TC-GUID',
                'domainToSip': {
                    'by': ['reg3', 'reg4'],
                    'ru': ['reg1', 'reg2'],
                },
                'originalDNHeader': 'X-CC-OriginalDN',
                'port': 7443,
                'stunServers': ['stun:141.8.146.81:3478'],
                'urls': {'by': 'yandex.ru', 'ru': 'yandex.ru'},
                'volume': 0.7,
                'websocketConnectionTimeout': 4000,
            },
            'CALLCENTER_OPERATOR_LOGINS_TO_SIP_MAP': {},
        },
    }


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'metaqueues': ['test'],
            'display_name': 'test',
            'should_use_internal_queue_service': False,
            'reg_groups': ['ru'],
        },
    },
)
async def test_form_launch_no_queue_service_one_project_reg(
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
            ],
        }

    operator = copy.deepcopy(OPERATOR)
    await _add_operator(operator, web_context, True)
    auth_headers = test_utils.make_auth_headers(operator)
    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/form/launch',
        headers=auth_headers,
        json={'project': 'help'},
    )
    assert resp.status == 200
    assert await resp.json() == {
        'sip_username': '1000000000',
        'reg_info': {'reg_domain': 'yandex.ru', 'regs': ['reg1', 'reg2']},
        'flow_info': [],
        'config_info': {
            'CALLCENTER_SIP_OPTIONS': {
                'answerTimer': 1000,
                'chainIdHeader': 'X-TC-GUID',
                'domainToSip': {
                    'by': ['reg3', 'reg4'],
                    'ru': ['reg1', 'reg2'],
                },
                'originalDNHeader': 'X-CC-OriginalDN',
                'port': 7443,
                'stunServers': ['stun:141.8.146.81:3478'],
                'urls': {'by': 'yandex.ru', 'ru': 'yandex.ru'},
                'volume': 0.7,
                'websocketConnectionTimeout': 4000,
            },
            'CALLCENTER_OPERATOR_LOGINS_TO_SIP_MAP': {},
        },
    }


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'metaqueues': ['test'],
            'display_name': 'test',
            'should_use_internal_queue_service': False,
            'reg_groups': ['ru', 'by'],
        },
    },
)
async def test_form_launch_no_queue_service_two_project_reg(
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
    await _add_operator(operator, web_context, True)
    auth_headers = test_utils.make_auth_headers(operator)
    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/form/launch',
        headers=auth_headers,
        json={'project': 'help'},
    )
    assert resp.status == 200
    assert await resp.json() == {
        'sip_username': '1000000000',
        'flow_info': [],
        'config_info': {
            'CALLCENTER_SIP_OPTIONS': {
                'answerTimer': 1000,
                'chainIdHeader': 'X-TC-GUID',
                'domainToSip': {
                    'by': ['reg3', 'reg4'],
                    'ru': ['reg1', 'reg2'],
                },
                'originalDNHeader': 'X-CC-OriginalDN',
                'port': 7443,
                'stunServers': ['stun:141.8.146.81:3478'],
                'urls': {'by': 'yandex.ru', 'ru': 'yandex.ru'},
                'volume': 0.7,
                'websocketConnectionTimeout': 4000,
            },
            'CALLCENTER_OPERATOR_LOGINS_TO_SIP_MAP': {},
        },
    }


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'metaqueues': ['test'],
            'display_name': 'test',
            'should_use_internal_queue_service': False,
            'reg_groups': ['ru', 'by'],
        },
    },
)
async def test_form_launch_500_from_reg(
        taxi_callcenter_operators_web,
        mockserver,
        mock_save_status,
        pgsql,
        web_context,
        mock_callcenter_reg,
):
    @mock_callcenter_reg('/v1/reg_groups')
    async def _handle_urls(request, *args, **kwargs):
        return mockserver.make_response(status=500)

    operator = copy.deepcopy(OPERATOR)
    await _add_operator(operator, web_context, True)
    auth_headers = test_utils.make_auth_headers(operator)
    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/form/launch',
        headers=auth_headers,
        json={'project': 'help'},
    )
    assert resp.status == 500


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'metaqueues': ['test'],
            'display_name': 'test',
            'should_use_internal_queue_service': False,
            'reg_groups': ['ru', 'by'],
        },
    },
)
async def test_form_launch_404(
        taxi_callcenter_operators_web,
        mockserver,
        mock_save_status,
        pgsql,
        web_context,
):
    operator = copy.deepcopy(OPERATOR)
    auth_headers = test_utils.make_auth_headers(operator)
    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/form/launch',
        headers=auth_headers,
        json={'project': 'help'},
    )
    assert resp.status == 404


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
async def test_form_launch_403(
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
        '/cc/v1/callcenter-operators/v1/form/launch',
        headers=auth_headers,
        json={'project': 'help'},
    )
    assert resp.status == 403
    # project and metaqueues project doesn't match


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'test': {
            'metaqueues': ['test'],
            'display_name': 'test',
            'should_use_internal_queue_service': False,
            'reg_groups': ['ru', 'by'],
        },
    },
)
async def test_form_launch_bad_project(
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
        '/cc/v1/callcenter-operators/v1/form/launch',
        headers=auth_headers,
        json={'project': 'help'},
    )
    assert resp.status == 500


LOCAL_VAD_CONFIG = {
    'speech_complete_timeout_ms': 1000,
    'speech_timeout_ms': 10000,
    'vad_silence_ms': 20,
    'vad_threshold': 40,
    'vad_voice_ms': 20,
}
PRJ_CONFIG = {
    'metaqueues': ['test'],
    'display_name': 'test',
    'should_use_internal_queue_service': False,
    'reg_groups': ['ru'],
}


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'prj1': PRJ_CONFIG,
        'prj2': PRJ_CONFIG,
        'prj3': PRJ_CONFIG,
        'bad_project': PRJ_CONFIG,
    },
    IVR_FRAMEWORK_FLOW_CONFIG={
        'flow1': {
            'base_url': 'mock_url',
            'tvm_name': 'ivr-dispatcher',
            'asr_config': {'language_code': 'ru-ru', 'model': 'general'},
            'local_vad_config': LOCAL_VAD_CONFIG,
            'outbound_number': '+74992296688',
            'outbound_routes': {
                '__default__': 'taxi_external',
                'to_operator': 'taxi_phonecall',
            },
            'record_call': True,
            'tts_config': {'language': 'ru-RU', 'speed': 1, 'voice': 'alena'},
            'use_tanya_backend': True,
            'is_form_flow': True,
            'project': 'prj1',
        },
        'flow2': {
            'asr_config': {'language_code': 'ru-ru', 'model': 'general'},
            'local_vad_config': LOCAL_VAD_CONFIG,
            'outbound_number': '+74992296688',
            'outbound_routes': {
                '__default__': 'taxi_external',
                'to_operator': 'taxi_phonecall',
            },
            'record_call': True,
            'tts_config': {'language': 'ru-RU', 'speed': 1, 'voice': 'alena'},
            'use_tanya_backend': True,
            'is_form_flow': True,
            'project': 'prj1',
        },
        'flow3': {
            'asr_config': {'language_code': 'ru-ru', 'model': 'general'},
            'local_vad_config': LOCAL_VAD_CONFIG,
            'outbound_number': '+74992296688',
            'outbound_routes': {
                '__default__': 'taxi_external',
                'to_operator': 'taxi_phonecall',
            },
            'record_call': True,
            'tts_config': {'language': 'ru-RU', 'speed': 1, 'voice': 'alena'},
            'use_tanya_backend': True,
            'is_form_flow': True,
            'project': 'prj2',
        },
        'flow4': {
            'asr_config': {'language_code': 'ru-ru', 'model': 'general'},
            'local_vad_config': LOCAL_VAD_CONFIG,
            'outbound_number': '+74992296688',
            'outbound_routes': {
                '__default__': 'taxi_external',
                'to_operator': 'taxi_phonecall',
            },
            'record_call': True,
            'tts_config': {'language': 'ru-RU', 'speed': 1, 'voice': 'alena'},
            'use_tanya_backend': True,
            'project': 'prj3',
        },
    },
)
@pytest.mark.parametrize(
    'project_name, expected_flows',
    [
        ('prj1', ['flow1', 'flow2']),
        ('prj2', ['flow3']),
        ('bad_project', []),
        ('prj3', []),
    ],
    ids=('my_forms', 'another_forms', 'bad: no_forms', 'empty: no_forms'),
)
async def test_form_launch_flow_config(
        taxi_callcenter_operators_web,
        mockserver,
        mock_save_status,
        pgsql,
        web_context,
        mock_callcenter_reg,
        project_name,
        expected_flows,
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
            ],
        }

    operator = copy.deepcopy(OPERATOR)
    await _add_operator(operator, web_context, True)
    auth_headers = test_utils.make_auth_headers(operator)
    request = dict()
    if project_name:
        request['project'] = project_name
    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/form/launch',
        headers=auth_headers,
        json=request,
    )
    assert resp.status == 200
    body = await resp.json()
    flow_info = body.get('flow_info')
    assert flow_info == expected_flows
