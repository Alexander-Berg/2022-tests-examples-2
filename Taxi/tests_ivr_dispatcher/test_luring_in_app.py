import copy

import pytest

from tests_ivr_dispatcher import fwo_utils
from tests_ivr_dispatcher import utils

ABONENT_NUMBER = copy.copy(utils.DEFAULT_USER_PHONE)
CALLCENTER_NUMBER = copy.copy(utils.DEFAULT_TAXI_PHONE)
CALL_GUID = 'some_call_guid'
SHORT_NUMBER = 'short_number'
UNDEFINED = 'undefined'

WORKER_ID = 'ivr_flow_worker'
FLOW_ID = 'taxi_disp_luring_in_app_flow'

OCTONODE_INITIAL = {
    'brand': None,
    'called_number': SHORT_NUMBER,
    'origin_called_number': CALLCENTER_NUMBER,
    'caller_number': ABONENT_NUMBER,
    'call_guid': CALL_GUID,
    'status': 'ok',
    'type': 'initial',
}
OCTONODE_ANSWER_RESULT_OK = {'status': 'ok', 'type': 'answer'}


OCTONODE_ASK_RESULT_CONFIRM_CANCEL = {
    'error_cause': None,
    'status': 'ok',
    'type': 'input',
    'numbers': '1',
}

OCTONODE_ASK_RESULT_ERROR = {
    'error_cause': 'unexcpected_error',
    'status': 'error',
    'type': 'input',
}

ANSWER_REPLY = {'type': 'answer', 'params': {'start_recording': True}}

ASK_FOR_LURING_REPLY = {
    'params': {
        'relative_path': (
            f'ivr_flow_worker/{FLOW_ID}/luring_in_app.ask_for_sms_sending.wav'
        ),
        'timeout': 4,
    },
    'type': 'input',
}

ASK_FOR_LURING_REPLY_CONFIRM = {
    'error_cause': None,
    'status': 'ok',
    'type': 'input',
    'numbers': '1',
}


ASK_FOR_LURING_REPLY_NOT_CONFIRM = {
    'error_cause': None,
    'status': 'ok',
    'type': 'input',
    'numbers': '1',
}

HANGUP_REPLY = {'type': 'hangup'}

LURING_IN_APP_MAIN_SCENARIO_1 = [
    (OCTONODE_INITIAL, ANSWER_REPLY, None),
    (OCTONODE_ANSWER_RESULT_OK, ASK_FOR_LURING_REPLY, None),
    (ASK_FOR_LURING_REPLY_CONFIRM, HANGUP_REPLY, None),
]

LURING_IN_APP_MAIN_SCENARIO_2 = [
    (OCTONODE_INITIAL, ANSWER_REPLY, None),
    (OCTONODE_ANSWER_RESULT_OK, ASK_FOR_LURING_REPLY, None),
    (ASK_FOR_LURING_REPLY_NOT_CONFIRM, HANGUP_REPLY, None),
]

NO_APP_SCENARIO = [
    (OCTONODE_INITIAL, ANSWER_REPLY, None),
    (OCTONODE_ANSWER_RESULT_OK, HANGUP_REPLY, None),
]

ASK_ERROR_SCENARIO = [
    (OCTONODE_INITIAL, ANSWER_REPLY, None),
    (OCTONODE_ANSWER_RESULT_OK, ASK_FOR_LURING_REPLY, None),
    (OCTONODE_ASK_RESULT_ERROR, HANGUP_REPLY, None),
]


@pytest.mark.now('2021-07-30T19:00:00.00Z')
@pytest.mark.config(
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        utils.DEFAULT_TAXI_PHONE: {'metaqueue': utils.DEFAULT_METAQUEUE},
    },
    CALLCENTER_METAQUEUES=[
        {
            'name': utils.DEFAULT_METAQUEUE,
            'number': '123',
            'allowed_clusters': ['1'],
        },
    ],
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {
            SHORT_NUMBER: {'name': FLOW_ID, 'type': 'flow_worker'},
        },
        'public_numbers': {},
    },
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '+74959999999': {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
)
@pytest.mark.config(
    IVR_FRAMEWORK_FLOW_CONFIG={
        FLOW_ID: {
            'base_url': fwo_utils.BASE_URL,
            'tvm_name': fwo_utils.TVM_NAME,
            'record_call': fwo_utils.RECORD_CALL,
            'no_answer_timeout_sec': fwo_utils.NO_ANSWER_TO,
            'tts_config': fwo_utils.TTS_CONFIG,
            'no_input_timeout_ms': fwo_utils.DEFAULT_NIT,
            'immediate_input': fwo_utils.DEFAULT_SIT,
            'asr_config': fwo_utils.ASR_CONFIG,
            'no_local_vad': fwo_utils.DEFAULT_NLV,
            'local_vad_config': fwo_utils.VAD_CONFIG,
        },
    },
)
@pytest.mark.parametrize(
    ('scenario', 'sms_sent'),
    (
        (LURING_IN_APP_MAIN_SCENARIO_1, True),
        (LURING_IN_APP_MAIN_SCENARIO_2, True),
        (NO_APP_SCENARIO, False),
        (ASK_ERROR_SCENARIO, False),
    ),
    ids=(
        'LURING_IN_APP_MAIN_SCENARIO_1',
        'LURING_IN_APP_MAIN_SCENARIO_2',
        'NO_APP_SCENARIO',
        'ASK_ERROR_SCENARIO',
    ),
)
async def test_scenarios(
        taxi_ivr_dispatcher,
        mongodb,
        mockserver,
        mock_user_api,
        mock_personal,
        scenario,
        load_json,
        taxi_config,
        sms_sent,
        stq,
):
    if scenario == NO_APP_SCENARIO:
        taxi_config.set_values(
            {'CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP': {}},
        )
    await taxi_ivr_dispatcher.invalidate_caches()

    for action, reply, _ in scenario:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply

    if sms_sent:
        assert stq.ivr_sms_sending.times_called
        args = stq.ivr_sms_sending.next_call()
        args = args['kwargs']
        assert 'Ссылка на приложение' in args['text']
    else:
        assert not stq.ivr_sms_sending.times_called
