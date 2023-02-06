import pytest

from tests_ivr_dispatcher import fwt_utils
from tests_ivr_dispatcher import utils

WORKER_ID = 'ivr_flow_worker'
FLOW_ID = 'playback_flow'
TVM_NAME = 'ivr_dispatcher'
PLAYBACK_ID = 'playback'
HANGUP_ID = 'hangup'
PROMPT_ID = 'prompt1'
PROMPT_URL = (
    f'http://ivr-dispatcher.s3.url/{WORKER_ID}/{FLOW_ID}/{PROMPT_ID}.wav'
)

FLOW_CONFIG = {
    'base_url': fwt_utils.BASE_URL,
    'tvm_name': TVM_NAME,
    'outbound_number': utils.DEFAULT_TAXI_PHONE,
    'outbound_routes': {'__default__': fwt_utils.OUTBOUND_GW},
    'record_call': fwt_utils.RECORD_CALL,
    'no_answer_timeout_sec': fwt_utils.NO_ANSWER_TO,
    'tts_config': fwt_utils.TTS_CONFIG,
    'no_input_timeout_ms': fwt_utils.DEFAULT_NIT,
    'immediate_input': fwt_utils.DEFAULT_SIT,
    'asr_config': fwt_utils.ASR_CONFIG,
    'no_local_vad': fwt_utils.DEFAULT_NLV,
    'local_vad_config': fwt_utils.VAD_CONFIG,
}

IVR_FRAMEWORK_FLOW_CONFIG = {FLOW_ID: FLOW_CONFIG}

TANYA_INITIAL_RESULT = {
    'caller_number': utils.DEFAULT_USER_PHONE,
    'called_number': utils.DEFAULT_TAXI_PHONE,
    'origin_called_number': utils.DEFAULT_TAXI_PHONE,
    'call_guid': 'some_call_guid',
    'base_url': 'http://tanya_url',
    'direction': 'inbound',
    'type': 'initial',
}

TANYA_ANSWER_OK_RESULT = {'type': 'answer', 'status': 'OK'}

TANYA_PLAYBACK_OK_RESULT = {'type': 'playback', 'status': 'OK'}

PLAY_FLOW_ANSWER_REPLY = {
    'action': {
        'type': 'answer',
        'params': {'enable_recording': fwt_utils.RECORD_CALL},
    },
    'action_id': 'answer',
}

PLAY_FLOW_PLAY_REPLY = {
    'action': {
        'type': 'playback',
        'params': {'play': {'prompt_url': PROMPT_URL}},
    },
    'action_id': PLAYBACK_ID,
}

PLAY_FLOW_HANGUP_NC_REPLY = {
    'action': {'type': 'hangup', 'params': {'cause': 'NORMAL_CALL_CLEARING'}},
    'action_id': HANGUP_ID,
}

PLAY_MAIN_SCENARIO = [
    (TANYA_INITIAL_RESULT, PLAY_FLOW_ANSWER_REPLY, None),
    (TANYA_ANSWER_OK_RESULT, PLAY_FLOW_PLAY_REPLY, None),
    (TANYA_PLAYBACK_OK_RESULT, PLAY_FLOW_HANGUP_NC_REPLY, None),
]


@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {'name': FLOW_ID, 'type': 'flow_worker'},
        },
    },
    IVR_DISPATCHER_PLAY_FLOW={'prompt_url': PROMPT_ID},
    IVR_FRAMEWORK_FLOW_CONFIG=IVR_FRAMEWORK_FLOW_CONFIG,
)
@pytest.mark.parametrize(
    'scenario', [PLAY_MAIN_SCENARIO], ids=['playback_main_scenario'],
)
async def test_scenarios(
        taxi_ivr_dispatcher,
        mongodb,
        scenario,
        mockserver,
        mock_user_api,
        mock_int_authproxy,
        mock_personal,
):
    for action, reply, _ in scenario:
        request = {
            'session_id': utils.DEFAULT_SESSION_ID,
            'action_result': action,
        }
        response = await taxi_ivr_dispatcher.post(
            '/external/v1/action', json=request,
        )
        assert response.status == 200, response.text
        assert response.json() == reply


@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {'name': FLOW_ID, 'type': 'flow_worker'},
        },
    },
    IVR_DISPATCHER_PLAY_FLOW={},
    IVR_FRAMEWORK_FLOW_CONFIG=IVR_FRAMEWORK_FLOW_CONFIG,
)
async def test_no_config(
        taxi_ivr_dispatcher,
        mongodb,
        mockserver,
        mock_user_api,
        mock_int_authproxy,
        mock_personal,
):
    request = {
        'session_id': utils.DEFAULT_SESSION_ID,
        'action_result': TANYA_INITIAL_RESULT,
    }
    response = await taxi_ivr_dispatcher.post(
        '/external/v1/action', json=request,
    )
    assert response.status == 200, response.text
    assert response.json() == PLAY_FLOW_HANGUP_NC_REPLY
