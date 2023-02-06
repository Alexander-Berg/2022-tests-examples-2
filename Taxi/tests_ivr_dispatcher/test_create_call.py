import copy
import datetime


import pytest

from tests_ivr_dispatcher import fwo_utils as utils


NEW_CONTEXT = utils.NEW_CONTEXT.copy()


@pytest.fixture(name='dial_client')
def mock_dial_client_dialog(mockserver):
    class DialClient:
        @staticmethod
        @mockserver.json_handler('/v1/ivr-framework/call-notify')
        async def notify_handler(request):
            msg = utils.Message(request.json)
            return msg.response()

    return DialClient()


@pytest.mark.parametrize(
    'call_flow_id, flow_id, call_id, status',
    [
        (utils.CALL_FLOW_ID, utils.FLOW_ID, utils.CALL_ID, 200),
        (utils.CALL_FLOW_ID, 'nonexistent', utils.CALL_ID, 404),
    ],
    ids=('correct ivr_flow_id', 'nonexistent ivr_flow_id'),
)
@pytest.mark.parametrize(
    'use_tanya', [False, True], ids=('use_octonode', 'use_tanya'),
)
async def test_create_call(
        call_flow_id,
        flow_id,
        call_id,
        status,
        mockserver,
        dial_client,
        mock_personal_phones,
        taxi_ivr_dispatcher,
        mongodb,
        use_tanya,
        taxi_config,
):
    @mockserver.json_handler('/octonode/create_session')
    async def octonode(request):
        req_data = request.json
        assert (
            req_data['script']['steps']['start']['parameters'][
                'calling_number'
            ]
            == utils.OUTBOUND_NUMBER
        )
        assert (
            req_data['script']['steps']['start']['parameters']['call_to']
            == utils.ABONENT_NUMBER
        )
        assert (
            req_data['script']['steps']['start']['parameters']['gateways']
            == utils.OUTBOUND_GW
        )
        assert (
            req_data['script']['session_variables']['record_session']
            == utils.RECORD_CALL
        )
        assert req_data['script']['session_variables']['mrcp_config'] == {
            'engine': 'ya_speechkit',
            'language': utils.TTS_LANG,
            'voice': utils.TTS_VOICE,
            'speed': utils.TTS_SPEED,
        }
        return {'session_id': req_data.get('session_id', 'mocked_session_id')}

    @mockserver.json_handler('/tanya-telephony/create_leg')
    async def tanya(request):
        req_data = request.json
        assert 'session_id' in req_data
        return {'session_id': req_data.get('session_id', 'mocked_session_id')}

    config = copy.deepcopy(utils.IVR_FRAMEWORK_FLOW_CONFIG)
    config[utils.FLOW_ID]['base_url'] = mockserver.base_url
    if use_tanya:
        config[utils.FLOW_ID]['use_tanya_backend'] = use_tanya
    taxi_config.set_values({'IVR_FRAMEWORK_FLOW_CONFIG': config})
    data = {
        'call_external_id': call_id,
        'ivr_flow_id': flow_id,
        'personal_phone_id': utils.CALLED_PD_ID,
        'actions': [utils.ORIGINATE_ACTION],
        'context': utils.CLIENT_CONTEXT,
    }
    response = await taxi_ivr_dispatcher.post(
        '/v1/ivr-framework/create-call', json=data,
    )

    assert response.status == status
    if status != 200:
        return
    db_session_doc = mongodb.ivr_disp_sessions.find_one(
        {'context.call_flow_id': {'$eq': call_flow_id}},
    )
    assert 'created' in db_session_doc
    assert db_session_doc['worker_id'] == utils.WORKER_ID
    assert 'context' in db_session_doc
    worker_context = db_session_doc['context']
    if use_tanya:
        assert tanya.times_called == 1
        NEW_CONTEXT['context']['call_guid'] = worker_context['call_guid']
        NEW_CONTEXT['context']['call_record_id'] = worker_context['call_guid']
    else:
        assert octonode.times_called == 1
    assert worker_context == NEW_CONTEXT['context']


@pytest.mark.parametrize(
    'node_error, cr_response',
    [('500', 500), ('TO', 200), ('NE', 500)],
    ids=(
        '500 - 500',
        'response lost -- session alive',
        'network error -- 500',
    ),
)
@pytest.mark.parametrize(
    'use_tanya', [False, True], ids=('use_octonode', 'use_tanya'),
)
@pytest.mark.config(
    OCTONODE_CLIENT_QOS={
        '/octonode/create_session': {'attempts': 1, 'timeout-ms': 2000},
    },
    TANYA_TEL_CLIENT_QOS={
        '/tanya-telephony/create_leg': {'attempts': 1, 'timeout-ms': 2000},
    },
)
async def test_telephony_backend_error(
        mockserver,
        node_error,
        cr_response,
        mock_personal_phones,
        taxi_ivr_dispatcher,
        mongodb,
        use_tanya,
        taxi_config,
):
    @mockserver.json_handler('/octonode/create_session')
    async def octonode(request):
        if node_error == 'TO':
            # Simulate 200 response was lost, but session is alive
            mongodb.ivr_disp_sessions.update(
                {'context.call_id': utils.CALL_ID},
                {
                    '$set': {
                        'context.state': 'originating',
                        'updated': (
                            datetime.datetime.now()
                            + datetime.timedelta(seconds=3)
                        ),
                    },
                    '$inc': {'version': 1},
                },
            )
            raise mockserver.TimeoutError()
        if node_error == 'NE':
            raise mockserver.NetworkError()
        return mockserver.make_response(status=500)

    @mockserver.json_handler('/tanya-telephony/create_leg')
    async def tanya(request):
        if node_error == 'TO':
            # Simulate 200 response was lost, but session is alive
            mongodb.ivr_disp_sessions.update(
                {'context.call_id': utils.CALL_ID},
                {
                    '$set': {
                        'context.state': 'originating',
                        'updated': (
                            datetime.datetime.now()
                            + datetime.timedelta(seconds=3)
                        ),
                    },
                    '$inc': {'version': 1},
                },
            )
            raise mockserver.TimeoutError()
        if node_error == 'NE':
            raise mockserver.NetworkError()
        return mockserver.make_response(status=500)

    config = copy.deepcopy(utils.IVR_FRAMEWORK_FLOW_CONFIG)
    config[utils.FLOW_ID]['base_url'] = mockserver.base_url
    if use_tanya:
        config[utils.FLOW_ID]['use_tanya_backend'] = use_tanya
    taxi_config.set_values({'IVR_FRAMEWORK_FLOW_CONFIG': config})
    data = {
        'call_external_id': utils.CALL_ID,
        'ivr_flow_id': utils.FLOW_ID,
        'personal_phone_id': utils.CALLED_PD_ID,
        'actions': [utils.ORIGINATE_ACTION],
    }
    response = await taxi_ivr_dispatcher.post(
        '/v1/ivr-framework/create-call', json=data,
    )
    assert response.status == cr_response
    if use_tanya:
        assert tanya.times_called == 1
    else:
        assert octonode.times_called == 1

    if node_error == '500':
        db_session_doc = mongodb.ivr_disp_sessions.find_one(
            {'context.call_flow_id': {'$eq': utils.CALL_FLOW_ID}},
        )
        assert db_session_doc['context']['call_finished']
