from aiohttp import web
import pytest

from tests_ivr_dispatcher import fwt_utils
from tests_ivr_dispatcher import utils

WORKER_ID = 'ivr_flow_worker'
FLOW_ID = 'csat_flow'
TVM_NAME = 'ivr_dispatcher'
PLAYBACK_ID = 'playback'
HANGUP_ID = 'hangup'
HELLO_REPLY_ID = 'csat.hello_request'
HELLO_REPLY_URL = (
    f'http://ivr-dispatcher.s3.url/{WORKER_ID}/{FLOW_ID}/{HELLO_REPLY_ID}.wav'
)
REPEAT_REPLY_ID = 'csat.repeat_request'
REPEAT_REPLY_URL = (
    f'http://ivr-dispatcher.s3.url/{WORKER_ID}/{FLOW_ID}/{REPEAT_REPLY_ID}.wav'
)
BYE_REPLY_ID = 'csat.rating_cancelled'
BYE_REPLY_URL = (
    f'http://ivr-dispatcher.s3.url/{WORKER_ID}/{FLOW_ID}/{BYE_REPLY_ID}.wav'
)
RATING_RESULT = 'Без проблем, работу оцениваю на 5 баллов'
EMPTY_RESULT = ''

FLOW_CONFIG = {
    'base_url': fwt_utils.BASE_URL,
    'tvm_name': TVM_NAME,
    'outbound_number': utils.DEFAULT_TAXI_PHONE,
    'outbound_routes': {'__default__': fwt_utils.OUTBOUND_GW},
    'record_call': fwt_utils.RECORD_CALL,
    'no_answer_timeout_sec': fwt_utils.NO_ANSWER_TO,
    'tts_config': fwt_utils.TTS_CONFIG,
    'no_input_timeout_ms': fwt_utils.DEFAULT_NIT,
    'max_response_duration_ms': fwt_utils.DEFAULT_MRD,
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
TANYA_ASK_RATING_RESULT = {
    'status': 'OK',
    'type': 'ask',
    'user_input': RATING_RESULT,
}
TANYA_ASK_RATING_BAD_RESULT = {
    'status': 'OK',
    'type': 'ask',
    'user_input': EMPTY_RESULT,
}
TANYA_PLAYBACK_OK_RESULT = {'type': 'playback', 'status': 'OK'}

DISPATCHER_ANSWER_REPLY = {
    'action': {
        'type': 'answer',
        'params': {'enable_recording': fwt_utils.RECORD_CALL},
    },
    'action_id': 'answer',
}
DISPATCHER_ASK_HELLO_REPLY = {
    'action': {
        'type': 'ask',
        'params': {
            'play': {'prompt_url': HELLO_REPLY_URL},
            'asr_config': {
                'engine': 'ya_speechkit',
                'language_code': fwt_utils.ASR_LANG_CODE,
                'model': fwt_utils.ASR_MODEL,
                'max_response_duration_ms': fwt_utils.DEFAULT_MRD,
            },
            'dtmf_config': {
                'min_digits': 1,
                'max_digits': 1,
                'interdigit_timeout_ms': fwt_utils.DEFAULT_NIT,
                'allowed_dtmf': 'any',
            },
            'immediate_input': fwt_utils.DEFAULT_SIT,
            'no_input_timeout_ms': fwt_utils.DEFAULT_NIT,
        },
    },
    'action_id': HELLO_REPLY_ID,
}
DISPATCHER_ASK_REPEAT_REPLY = {
    'action': {
        'type': 'ask',
        'params': {
            'play': {'prompt_url': REPEAT_REPLY_URL},
            'asr_config': {
                'engine': 'ya_speechkit',
                'language_code': fwt_utils.ASR_LANG_CODE,
                'model': fwt_utils.ASR_MODEL,
                'max_response_duration_ms': fwt_utils.DEFAULT_MRD,
            },
            'dtmf_config': {
                'min_digits': 1,
                'max_digits': 1,
                'interdigit_timeout_ms': fwt_utils.DEFAULT_NIT,
                'allowed_dtmf': 'any',
            },
            'immediate_input': fwt_utils.DEFAULT_SIT,
            'no_input_timeout_ms': fwt_utils.DEFAULT_NIT,
        },
    },
    'action_id': REPEAT_REPLY_ID,
}
DISPATCHER_PLAY_BYE_REPLY = {
    'action': {
        'type': 'playback',
        'params': {'play': {'prompt_url': BYE_REPLY_URL}},
    },
    'action_id': BYE_REPLY_ID,
}
DISPATCHER_HANGUP = {
    'action': {'type': 'hangup', 'params': {'cause': 'NORMAL_CALL_CLEARING'}},
    'action_id': HANGUP_ID,
}

CSAT_MAIN_SCENARIO = [
    (TANYA_INITIAL_RESULT, DISPATCHER_ANSWER_REPLY, None),
    (TANYA_ANSWER_OK_RESULT, DISPATCHER_ASK_HELLO_REPLY, None),
    (TANYA_ASK_RATING_RESULT, DISPATCHER_PLAY_BYE_REPLY, None),
    (TANYA_PLAYBACK_OK_RESULT, DISPATCHER_HANGUP, None),
]
CSAT_REPEAT_ASK_SCENARIO = [
    (TANYA_INITIAL_RESULT, DISPATCHER_ANSWER_REPLY, None),
    (TANYA_ANSWER_OK_RESULT, DISPATCHER_ASK_HELLO_REPLY, None),
    (TANYA_ASK_RATING_BAD_RESULT, DISPATCHER_ASK_REPEAT_REPLY, None),
    (TANYA_ASK_RATING_RESULT, DISPATCHER_PLAY_BYE_REPLY, None),
    (TANYA_PLAYBACK_OK_RESULT, DISPATCHER_HANGUP, None),
]
CSAT_REPEAT_FAILED_ASK_SCENARIO = [
    (TANYA_INITIAL_RESULT, DISPATCHER_ANSWER_REPLY, None),
    (TANYA_ANSWER_OK_RESULT, DISPATCHER_ASK_HELLO_REPLY, None),
    (TANYA_ASK_RATING_BAD_RESULT, DISPATCHER_ASK_REPEAT_REPLY, None),
    (TANYA_ASK_RATING_BAD_RESULT, DISPATCHER_HANGUP, None),
]
CSAT_FAILED_TO_SAVE = [
    (TANYA_INITIAL_RESULT, DISPATCHER_ANSWER_REPLY, None),
    (TANYA_ANSWER_OK_RESULT, DISPATCHER_ASK_HELLO_REPLY, None),
    (TANYA_ASK_RATING_RESULT, DISPATCHER_PLAY_BYE_REPLY, None),
    (TANYA_PLAYBACK_OK_RESULT, DISPATCHER_HANGUP, None),
]


@pytest.mark.now('2021-07-30T19:00:00.00Z')
@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {'name': FLOW_ID, 'type': 'flow_worker'},
        },
    },
    IVR_DISPATCHER_CSAT_REG_EXP={
        'patterns_map': {
            '1': ['\\W(1)\\W'],
            '2': ['\\W(2)\\W'],
            '3': ['\\W(3)\\W'],
            '4': ['\\W(4)\\W'],
            '5': ['\\W(5)\\W'],
        },
    },
    IVR_FRAMEWORK_FLOW_CONFIG=IVR_FRAMEWORK_FLOW_CONFIG,
)
@pytest.mark.parametrize(
    ['scenario', 'expected_support_ratings'],
    [
        pytest.param(CSAT_MAIN_SCENARIO, [('5', 'some_call_guid')]),
        pytest.param(CSAT_REPEAT_ASK_SCENARIO, [('5', 'some_call_guid')]),
        pytest.param(
            CSAT_REPEAT_FAILED_ASK_SCENARIO, [(None, 'some_call_guid')],
        ),
    ],
    ids=('csat_main_scenario', 'csat_repeat_scenario', 'failed_ask_scenario'),
)
async def test_scenarios(
        taxi_ivr_dispatcher,
        mongodb,
        scenario,
        expected_support_ratings,
        mockserver,
        mock_user_api,
        mock_int_authproxy,
        mock_personal,
        mock_callcenter_qa,
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
    assert [
        (row[1], row[2]) for row in mock_callcenter_qa.support_ratings
    ] == expected_support_ratings


@pytest.mark.now('2021-07-30T19:00:00.00Z')
@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {'name': FLOW_ID, 'type': 'flow_worker'},
        },
    },
    IVR_DISPATCHER_CSAT_REG_EXP={
        'patterns_map': {
            '1': ['\\W(1)\\W'],
            '2': ['\\W(2)\\W'],
            '3': ['\\W(3)\\W'],
            '4': ['\\W(4)\\W'],
            '5': ['\\W(5)\\W'],
        },
    },
    IVR_FRAMEWORK_FLOW_CONFIG=IVR_FRAMEWORK_FLOW_CONFIG,
)
async def test_bad_client(
        taxi_ivr_dispatcher,
        mongodb,
        mockserver,
        mock_user_api,
        mock_int_authproxy,
        mock_personal,
):
    @mockserver.json_handler('/callcenter-qa/v1/rating/save', prefix=True)
    async def _handle(request):
        return web.Response(status=500)

    for action, reply, _ in CSAT_FAILED_TO_SAVE:
        request = {
            'session_id': utils.DEFAULT_SESSION_ID,
            'action_result': action,
        }
        response = await taxi_ivr_dispatcher.post(
            '/external/v1/action', json=request,
        )
        assert response.status == 200, response.text
        assert response.json() == reply
