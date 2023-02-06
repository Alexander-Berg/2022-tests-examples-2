import json

import pytest

from tests_ivr_dispatcher import fwt_utils as utils


@pytest.fixture(name='mock_personal_store')
def _personal_store(mockserver):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_store(request, *args, **kwargs):
        p_id = request.json['id']
        return mockserver.make_response(
            json={'id': p_id, 'value': p_id.replace('_id', '')}, status=200,
        )

    @mockserver.json_handler('/personal/v1/phones/store')
    def _get_phone_id(request, *args, **kwargs):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'cc-authproxy', 'dst': 'ivr-dispatcher'}],
    TVM_SERVICES=utils.MOCK_TVM_SERVICES,
    IVR_FRAMEWORK_FLOW_CONFIG=utils.LOCAL_FLOW_CONFIG,
)
@pytest.mark.parametrize(
    'flow_id, status',
    [('mock_flow', 403), (utils.FLOW_ID, 200), (utils.NO_FLOW_ID, 404)],
    ids=(
        'no_form ivr_flow_id',
        'correct ivr_flow_id',
        'nonexistent ivr_flow_id',
    ),
)
async def test_request_parameters(
        flow_id,
        status,
        mockserver,
        mock_personal_store,
        mock_tanya,
        taxi_ivr_dispatcher,
        mongodb,
        tvm2_client,
        load,
):
    tvm2_client.set_ticket(json.dumps({'30': {'ticket': 'some_ticket'}}))

    data = {
        'project': utils.PROJECT_ID,
        'call_external_id': utils.EXT_CALL_ID,
        'ivr_flow_id': flow_id,
        'flow_args': {'phone_number': '+79991234567', 'deflect_to_ext': True},
    }
    my_headers = {
        utils.TICKET_HEADER: utils.read_tvm_ticket(
            'proxy_to_disp_ticket.txt', load,
        ),
        utils.USER_UID_HEADER: utils.OPERATOR_UID,
        utils.USER_LOGIN_HEADER: utils.OPERATOR_LOGIN,
    }

    response = await taxi_ivr_dispatcher.post(
        '/cc/v1/ivr-dispatcher/v1/ivr-framework/form-create-call',
        json=data,
        headers=my_headers,
    )

    assert response.status == status
    if status != 200:
        return

    body = response.json()
    assert 'call_external_id' in body
    assert body['call_external_id'] == utils.EXT_CALL_ID

    db_session_doc = mongodb.ivr_disp_sessions.find_one(
        {'context.call_id': {'$eq': utils.EXT_CALL_ID}},
    )

    assert 'created' in db_session_doc
    assert db_session_doc['worker_id'] == utils.WORKER_ID
    assert 'context' in db_session_doc
    assert mock_tanya.tanya.times_called == 1
    worker_context = db_session_doc['context']
    assert (
        worker_context['actions'][0]['originate']['yandex_uid']
        == utils.OPERATOR_UID
    )


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'cc-authproxy', 'dst': 'ivr-dispatcher'}],
    TVM_SERVICES=utils.MOCK_TVM_SERVICES,
    IVR_FRAMEWORK_FLOW_CONFIG=utils.LOCAL_FLOW_CONFIG,
)
async def test_dial_flow_ok(
        mockserver,
        mock_personal_store,
        mock_tanya,
        taxi_ivr_dispatcher,
        mongodb,
        tvm2_client,
        load,
):
    tvm2_client.set_ticket(json.dumps({'30': {'ticket': 'some_ticket'}}))

    data = {
        'project': utils.PROJECT_ID,
        'call_external_id': utils.EXT_CALL_ID,
        'ivr_flow_id': utils.FLOW_ID,
        'flow_args': {'phone_number': '+79991234567', 'deflect_to_ext': True},
    }
    my_headers = {
        utils.TICKET_HEADER: utils.read_tvm_ticket(
            'proxy_to_disp_ticket.txt', load,
        ),
    }

    my_headers[utils.USER_UID_HEADER] = utils.OPERATOR_UID
    my_headers[utils.USER_LOGIN_HEADER] = utils.OPERATOR_LOGIN

    response = await taxi_ivr_dispatcher.post(
        '/cc/v1/ivr-dispatcher/v1/ivr-framework/form-create-call',
        json=data,
        headers=my_headers,
    )

    body = response.json()
    assert 'call_external_id' in body
    assert body['call_external_id'] == utils.EXT_CALL_ID

    db_session_doc = mongodb.ivr_disp_sessions.find_one(
        {'context.call_id': {'$eq': utils.EXT_CALL_ID}},
    )

    assert 'created' in db_session_doc
    assert db_session_doc['worker_id'] == utils.WORKER_ID
    assert 'context' in db_session_doc
    assert mock_tanya.tanya.times_called == 1
    worker_context = db_session_doc['context']
    assert (
        worker_context['actions'][0]['originate']['yandex_uid']
        == utils.OPERATOR_UID
    )
    session_id = db_session_doc['_id']
    request = {
        'session_id': session_id,
        'action_result': {
            'type': 'initial',
            'base_url': utils.TANYA_BASE_URL,
            'direction': 'outbound',
        },
    }

    response = await taxi_ivr_dispatcher.post(
        '/external/v1/action', json=request,
    )
    assert response.status == 200, response.text
    response = response.json()
    assert (
        response['action']['params']['call_external_id'] == utils.EXT_CALL_ID
    )
    assert response['action']['params']['call_to'] == '1000000111'
    request = {
        'session_id': session_id,
        'action_result': {'status': 'OK', 'type': 'originate'},
    }

    response = await taxi_ivr_dispatcher.post(
        '/external/v1/action', json=request,
    )
    assert response.status == 200, response.text
    response = response.json()
    assert (
        response['action']['params']['call_external_id'] == utils.EXT_CALL_ID
    )
    assert response['action']['params']['call_to'] == '+79991234567'
    assert response['action']['params']['enable_provision']


HANGUP_ACTION = {
    'action': {'params': {'cause': 'NORMAL_CALL_CLEARING'}, 'type': 'hangup'},
}


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'cc-authproxy', 'dst': 'ivr-dispatcher'}],
    TVM_SERVICES=utils.MOCK_TVM_SERVICES,
    IVR_FRAMEWORK_FLOW_CONFIG=utils.LOCAL_FLOW_CONFIG,
)
async def test_dial_flow_bad_operator(
        mockserver,
        mock_personal_store,
        mock_tanya,
        taxi_ivr_dispatcher,
        mongodb,
        tvm2_client,
        load,
):
    tvm2_client.set_ticket(json.dumps({'30': {'ticket': 'some_ticket'}}))

    data = {
        'project': utils.PROJECT_ID,
        'call_external_id': utils.EXT_CALL_ID,
        'ivr_flow_id': utils.FLOW_ID,
        'flow_args': {'phone_number': '+79991234567', 'deflect_to_ext': True},
    }
    my_headers = {
        utils.TICKET_HEADER: utils.read_tvm_ticket(
            'proxy_to_disp_ticket.txt', load,
        ),
    }

    my_headers[utils.USER_UID_HEADER] = 'BAD_OPERATOR'
    my_headers[utils.USER_LOGIN_HEADER] = utils.OPERATOR_LOGIN

    response = await taxi_ivr_dispatcher.post(
        '/cc/v1/ivr-dispatcher/v1/ivr-framework/form-create-call',
        json=data,
        headers=my_headers,
    )

    body = response.json()
    assert 'call_external_id' in body
    assert body['call_external_id'] == utils.EXT_CALL_ID

    db_session_doc = mongodb.ivr_disp_sessions.find_one(
        {'context.call_id': {'$eq': utils.EXT_CALL_ID}},
    )

    assert 'created' in db_session_doc
    assert db_session_doc['worker_id'] == utils.WORKER_ID
    assert 'context' in db_session_doc
    assert mock_tanya.tanya.times_called == 1
    worker_context = db_session_doc['context']
    assert (
        worker_context['actions'][0]['originate']['yandex_uid']
        == 'BAD_OPERATOR'
    )
    session_id = db_session_doc['_id']
    request = {
        'session_id': session_id,
        'action_result': {
            'type': 'initial',
            'base_url': utils.TANYA_BASE_URL,
            'direction': 'outbound',
        },
    }

    response = await taxi_ivr_dispatcher.post(
        '/external/v1/action', json=request,
    )
    assert response.status == 200, response.text
    response = response.json()
    assert response == HANGUP_ACTION


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'cc-authproxy', 'dst': 'ivr-dispatcher'}],
    TVM_SERVICES=utils.MOCK_TVM_SERVICES,
    IVR_FRAMEWORK_FLOW_CONFIG=utils.LOCAL_FLOW_CONFIG,
)
async def test_dial_flow_originate_failed(
        mockserver,
        mock_personal_store,
        mock_tanya,
        taxi_ivr_dispatcher,
        mongodb,
        tvm2_client,
        load,
):
    tvm2_client.set_ticket(json.dumps({'30': {'ticket': 'some_ticket'}}))

    data = {
        'project': utils.PROJECT_ID,
        'call_external_id': utils.EXT_CALL_ID,
        'ivr_flow_id': utils.FLOW_ID,
        'flow_args': {'phone_number': '+79991234567', 'deflect_to_ext': True},
    }
    my_headers = {
        utils.TICKET_HEADER: utils.read_tvm_ticket(
            'proxy_to_disp_ticket.txt', load,
        ),
    }

    my_headers[utils.USER_UID_HEADER] = utils.OPERATOR_UID
    my_headers[utils.USER_LOGIN_HEADER] = utils.OPERATOR_LOGIN

    response = await taxi_ivr_dispatcher.post(
        '/cc/v1/ivr-dispatcher/v1/ivr-framework/form-create-call',
        json=data,
        headers=my_headers,
    )

    body = response.json()
    assert 'call_external_id' in body
    assert body['call_external_id'] == utils.EXT_CALL_ID

    db_session_doc = mongodb.ivr_disp_sessions.find_one(
        {'context.call_id': {'$eq': utils.EXT_CALL_ID}},
    )

    assert 'created' in db_session_doc
    assert db_session_doc['worker_id'] == utils.WORKER_ID
    assert 'context' in db_session_doc
    assert mock_tanya.tanya.times_called == 1
    worker_context = db_session_doc['context']
    assert (
        worker_context['actions'][0]['originate']['yandex_uid']
        == utils.OPERATOR_UID
    )
    session_id = db_session_doc['_id']
    request = {
        'session_id': session_id,
        'action_result': {
            'type': 'initial',
            'base_url': utils.TANYA_BASE_URL,
            'direction': 'outbound',
        },
    }

    response = await taxi_ivr_dispatcher.post(
        '/external/v1/action', json=request,
    )
    assert response.status == 200, response.text
    response = response.json()
    assert (
        response['action']['params']['call_external_id'] == utils.EXT_CALL_ID
    )
    assert response['action']['params']['call_to'] == '1000000111'
    request = {
        'session_id': session_id,
        'action_result': {
            'status': 'ERROR',
            'error': {'code': 'ABONENT_HANGUP'},
            'type': 'originate',
        },
    }

    response = await taxi_ivr_dispatcher.post(
        '/external/v1/action', json=request,
    )
    assert response.status == 200, response.text
    response = response.json()
    assert response == HANGUP_ACTION


FLOW_CONFIG_WITHOUT_LOCAL_ACTIONS = {
    'base_url': utils.BASE_URL,
    'tvm_name': utils.TVM_NAME,
    'asr_config': utils.ASR_CONFIG,
    'local_vad_config': utils.LOCAL_VAD_CONFIG,
    'outbound_number': '+74992296688',
    'outbound_routes': {
        '__default__': 'taxi_external',
        'to_operator': 'taxi_phonecall',
    },
    'record_call': True,
    'tts_config': utils.TTS_CONFIG,
    'use_tanya_backend': True,
    'is_form_flow': True,
    'project': utils.PROJECT_ID,
}
ORIGINATE_ACTION = {
    'external_id': 'originate_to_operator',
    'originate': {'yandex_uid': '1111111', 'route': 'to_operator'},
}
FORWARD_ACTION = {
    'external_id': 'forward_to_external',
    'forward': {
        'phone_number': '+79991234567',
        'enable_provision': True,
        'timeout_sec': 30,
        'use_deflect': False,
    },
}


@pytest.fixture(name='dial_client')
def mock_dial_client_dialog(mockserver):
    class DialClient:
        @staticmethod
        @mockserver.json_handler('/v1/ivr-framework/call-notify')
        async def notify_handler(request):
            last_action = request.json['last_action']
            if last_action == -1:
                return {'actions': [ORIGINATE_ACTION]}
            else:
                return {'actions': [FORWARD_ACTION]}

    return DialClient()


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'cc-authproxy', 'dst': 'ivr-dispatcher'}],
    TVM_SERVICES=utils.MOCK_TVM_SERVICES,
    IVR_FRAMEWORK_FLOW_CONFIG={
        utils.FLOW_ID: FLOW_CONFIG_WITHOUT_LOCAL_ACTIONS,
    },
)
async def test_dial_flow_without_local_actions(
        mockserver,
        mock_personal_store,
        dial_client,
        mock_tanya,
        taxi_ivr_dispatcher,
        mongodb,
        tvm2_client,
        load,
):
    tvm2_client.set_ticket(json.dumps({'30': {'ticket': 'some_ticket'}}))

    data = {
        'project': utils.PROJECT_ID,
        'call_external_id': utils.EXT_CALL_ID,
        'ivr_flow_id': utils.FLOW_ID,
        'flow_args': {'phone_number': '+79991234567', 'deflect_to_ext': True},
    }
    my_headers = {
        utils.TICKET_HEADER: utils.read_tvm_ticket(
            'proxy_to_disp_ticket.txt', load,
        ),
    }

    my_headers[utils.USER_UID_HEADER] = utils.OPERATOR_UID
    my_headers[utils.USER_LOGIN_HEADER] = utils.OPERATOR_LOGIN

    response = await taxi_ivr_dispatcher.post(
        '/cc/v1/ivr-dispatcher/v1/ivr-framework/form-create-call',
        json=data,
        headers=my_headers,
    )

    body = response.json()
    assert 'call_external_id' in body
    assert body['call_external_id'] == utils.EXT_CALL_ID

    db_session_doc = mongodb.ivr_disp_sessions.find_one(
        {'context.call_id': {'$eq': utils.EXT_CALL_ID}},
    )

    assert 'created' in db_session_doc
    assert db_session_doc['worker_id'] == utils.WORKER_ID
    assert 'context' in db_session_doc
    assert mock_tanya.tanya.times_called == 1

    session_id = db_session_doc['_id']
    request = {
        'session_id': session_id,
        'action_result': {
            'type': 'initial',
            'base_url': utils.TANYA_BASE_URL,
            'direction': 'outbound',
        },
    }

    response = await taxi_ivr_dispatcher.post(
        '/external/v1/action', json=request,
    )
    assert response.status == 200, response.text
    response = response.json()
    assert (
        response['action']['params']['call_external_id'] == utils.EXT_CALL_ID
    )
    assert response['action']['params']['call_to'] == '1000000111'
    request = {
        'session_id': session_id,
        'action_result': {'status': 'OK', 'type': 'originate'},
    }

    response = await taxi_ivr_dispatcher.post(
        '/external/v1/action', json=request,
    )
    assert response.status == 200, response.text
    response = response.json()
    assert (
        response['action']['params']['call_external_id'] == utils.EXT_CALL_ID
    )
    assert response['action']['params']['call_to'] == '+79991234567'
    assert response['action']['params']['enable_provision']
