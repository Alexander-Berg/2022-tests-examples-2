import copy

from aiohttp import web
import pytest

from tests_ivr_dispatcher import fwt_utils
from tests_ivr_dispatcher import utils

ABONENT_NUMBER = copy.copy(utils.DEFAULT_USER_PHONE)
CALLCENTER_NUMBER = copy.copy(utils.DEFAULT_TAXI_PHONE)
CALL_GUID = 'some_call_guid'
SHORT_NUMBER = 'short_number'
UNDEFINED = 'undefined'

WORKER_ID = 'ivr_flow_worker'
FLOW_ID = 'taxi_disp_luring_flow'
TVM_NAME = 'ivr_dispatcher'

SOME_ASK_WAV = 'taxi_disp_luring_flow.ask'
OPERATOR_SWITCH_WAV = 'taxi_disp_luring_flow.operator_switch'
NOTIFY_SMS_SENDING_WAV = 'taxi_disp_luring_flow.notify_sms_sending'
BAD_USER_INPUT_WAV = 'taxi_disp_luring_flow.bad_user_input.wav'

FLOWS_CONFIG = {
    FLOW_ID: {
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
    },
}

TANYA_INITIAL_RESULT = {
    'caller_number': ABONENT_NUMBER,
    'called_number': SHORT_NUMBER,
    'origin_called_number': CALLCENTER_NUMBER,
    'call_guid': CALL_GUID,
    'base_url': 'http://tanya_url',
    'direction': 'inbound',
    'type': 'initial',
}

TANYA_ANSWER_OK_RESULT = {'type': 'answer', 'status': 'OK'}

TANYA_PLAYBACK_OK_RESULT = {'type': 'playback', 'status': 'OK'}

TANYA_SWITCH_OK_RESULT = {
    'type': 'forward',
    'status': 'OK',
    'transferee_id': fwt_utils.LEG_ID,
}

ANSWER_REPLY = {
    'action': {
        'type': 'answer',
        'params': {'enable_recording': fwt_utils.RECORD_CALL},
    },
    'action_id': 'answer',
}

ASK_FOR_SMS_SENDING_REPLY = {
    'action': {
        'params': {
            'dtmf_config': {
                'allowed_dtmf': 'any',
                'interdigit_timeout_ms': 5000,
                'max_digits': 1,
                'min_digits': 1,
            },
            'immediate_input': False,
            'no_input_timeout_ms': 5000,
            'play': {
                'prompt_url': (
                    f'http://ivr-dispatcher.s3.url/'
                    f'{WORKER_ID}/{FLOW_ID}/{SOME_ASK_WAV}.wav'
                ),
            },
        },
        'type': 'ask',
    },
    'action_id': 'ask_send_sms',
}

PLAY_NOTIFY_SMS_SENDING = {
    'action': {
        'params': {
            'play': {
                'prompt_url': (
                    f'http://ivr-dispatcher.s3.url/'
                    f'{WORKER_ID}/{FLOW_ID}/{NOTIFY_SMS_SENDING_WAV}.wav'
                ),
            },
        },
        'type': 'playback',
    },
    'action_id': 'notify_to_send_sms',
}

PLAY_OPERATOR_SWITCH_REPLY = {
    'action': {
        'params': {
            'play': {
                'prompt_url': (
                    f'http://ivr-dispatcher.s3.url/'
                    f'{WORKER_ID}/{FLOW_ID}/{OPERATOR_SWITCH_WAV}.wav'
                ),
            },
        },
        'type': 'playback',
    },
    'action_id': 'tell_about_operator_switch',
}

PLAY_BAD_USER_INPUT_REPLY = {
    'action': {
        'params': {
            'play': {
                'prompt_url': (
                    f'http://ivr-dispatcher.s3.url/'
                    f'{WORKER_ID}/{FLOW_ID}/{BAD_USER_INPUT_WAV}.wav'
                ),
            },
        },
        'type': 'playback',
    },
    'action_id': 'bad_user_input_playback',
}

ASK_FOR_SMS_SENDING_CONFIRM = {
    'error_cause': None,
    'status': 'OK',
    'type': 'ask',
    'numbers': '1',
    'user_input': '1',
}

ASK_FOR_SMS_SENDING_NOT_CONFIRM = {
    'error_cause': None,
    'status': 'OK',
    'type': 'ask',
    'numbers': '1',
    'user_input': '2',
}

ASK_FOR_SMS_SENDING_TIMEOUT = {
    'error_cause': None,
    'status': 'OK',
    'type': 'ask',
    'numbers': '1',
    'user_input': '-1',
}

ASK_FOR_SMS_SENDING_ERROR = {
    'error_cause': 'unexpected_error',
    'status': 'ERROR',
    'type': 'ask',
}

HANGUP_REPLY = {
    'action': {'type': 'hangup', 'params': {'cause': 'NORMAL_CALL_CLEARING'}},
    'action_id': 'hangup',
}

HANGUP_REPLY_WITHOUT_ACTION_ID = {
    'action': {'type': 'hangup', 'params': {'cause': 'NORMAL_CALL_CLEARING'}},
}

SWITCH_REPLY = {
    'action': {
        'params': {
            'answer_timeout': fwt_utils.NO_ANSWER_TO,
            'call_external_id': CALL_GUID,
            'call_from': utils.DEFAULT_TAXI_PHONE,
            'call_guid': CALL_GUID,
            'call_to': SHORT_NUMBER,
            'distributor': 'ivr_via_noc',
            'use_deflect': True,
            'leg_id': fwt_utils.LEG_ID,
        },
        'type': 'forward',
    },
    'action_id': 'operator_switch',
}

PLAY_MAIN_SCENARIO = [
    (TANYA_INITIAL_RESULT, ANSWER_REPLY, None),
    (TANYA_ANSWER_OK_RESULT, ASK_FOR_SMS_SENDING_REPLY, None),
    (ASK_FOR_SMS_SENDING_CONFIRM, PLAY_NOTIFY_SMS_SENDING, None),
    (TANYA_PLAYBACK_OK_RESULT, HANGUP_REPLY, None),
]

PLAY_SCENARIO_WITHOUT_MENU_HANGUP = [
    (TANYA_INITIAL_RESULT, ANSWER_REPLY, None),
    (TANYA_ANSWER_OK_RESULT, HANGUP_REPLY, None),
]

PLAY_SCENARIO_WITHOUT_MENU_SWITCH = [
    (TANYA_INITIAL_RESULT, ANSWER_REPLY, None),
    (TANYA_ANSWER_OK_RESULT, SWITCH_REPLY, None),
    (TANYA_SWITCH_OK_RESULT, HANGUP_REPLY, None),
]

PLAY_SCENARIO_NO_TANKER_KEY = [
    (TANYA_INITIAL_RESULT, ANSWER_REPLY, None),
    (TANYA_ANSWER_OK_RESULT, SWITCH_REPLY, None),
    (TANYA_SWITCH_OK_RESULT, HANGUP_REPLY, None),
]

PLAY_SCENARIO_SWITCH = [
    (TANYA_INITIAL_RESULT, ANSWER_REPLY, None),
    (TANYA_ANSWER_OK_RESULT, ASK_FOR_SMS_SENDING_REPLY, None),
    (ASK_FOR_SMS_SENDING_NOT_CONFIRM, SWITCH_REPLY, None),
    (TANYA_SWITCH_OK_RESULT, HANGUP_REPLY, None),
]

PLAY_SCENARIO_ASK_TIMEOUT_SWITCH = [
    (TANYA_INITIAL_RESULT, ANSWER_REPLY, None),
    (TANYA_ANSWER_OK_RESULT, ASK_FOR_SMS_SENDING_REPLY, None),
    (ASK_FOR_SMS_SENDING_TIMEOUT, SWITCH_REPLY, None),
    (TANYA_SWITCH_OK_RESULT, HANGUP_REPLY, None),
]

PLAY_SCENARIO_ASK_ERROR = [
    (TANYA_INITIAL_RESULT, ANSWER_REPLY, None),
    (TANYA_ANSWER_OK_RESULT, ASK_FOR_SMS_SENDING_REPLY, None),
    (ASK_FOR_SMS_SENDING_ERROR, HANGUP_REPLY, None),
]

PLAY_SCENARIO_WITH_REQUIRED_CHOICE_MAIN = [
    (TANYA_INITIAL_RESULT, ANSWER_REPLY, None),
    (TANYA_ANSWER_OK_RESULT, ASK_FOR_SMS_SENDING_REPLY, None),
    (
        ASK_FOR_SMS_SENDING_NOT_CONFIRM,
        SWITCH_REPLY,
        None,
    ),  # USER INPUT: 2 -> switch
    (TANYA_SWITCH_OK_RESULT, HANGUP_REPLY, None),
]

PLAY_SCENARIO_WITH_REQUIRED_CHOICE_SWITCH_AFTER_BAD_USER_INPUTS = [
    (TANYA_INITIAL_RESULT, ANSWER_REPLY, None),
    (TANYA_ANSWER_OK_RESULT, ASK_FOR_SMS_SENDING_REPLY, None),
    (ASK_FOR_SMS_SENDING_TIMEOUT, PLAY_BAD_USER_INPUT_REPLY, None),  # 1
    (TANYA_PLAYBACK_OK_RESULT, ASK_FOR_SMS_SENDING_REPLY, None),
    (ASK_FOR_SMS_SENDING_TIMEOUT, PLAY_BAD_USER_INPUT_REPLY, None),  # 2
    (TANYA_PLAYBACK_OK_RESULT, ASK_FOR_SMS_SENDING_REPLY, None),
    (ASK_FOR_SMS_SENDING_TIMEOUT, SWITCH_REPLY, None),  # 3 -> switch
    (TANYA_SWITCH_OK_RESULT, HANGUP_REPLY, None),
]

PLAY_SCENARIO_WITH_REQUIRED_CHOICE_SMS_AFTER_SECOND_TRY = [
    (TANYA_INITIAL_RESULT, ANSWER_REPLY, None),
    (TANYA_ANSWER_OK_RESULT, ASK_FOR_SMS_SENDING_REPLY, None),
    (
        ASK_FOR_SMS_SENDING_TIMEOUT,
        PLAY_BAD_USER_INPUT_REPLY,
        None,
    ),  # First try
    (TANYA_PLAYBACK_OK_RESULT, ASK_FOR_SMS_SENDING_REPLY, None),
    (
        ASK_FOR_SMS_SENDING_CONFIRM,
        PLAY_NOTIFY_SMS_SENDING,
        None,
    ),  # Second try -> success
    (TANYA_PLAYBACK_OK_RESULT, HANGUP_REPLY, None),
]

PLAY_SCENARIO_BAD_FLOW_CONTEXT = [
    (TANYA_INITIAL_RESULT, HANGUP_REPLY_WITHOUT_ACTION_ID, None),
]

PLAY_SCENARIO_PASSENGER_TAGS_TEST = [
    (TANYA_INITIAL_RESULT, ANSWER_REPLY, None),
    (TANYA_ANSWER_OK_RESULT, ASK_FOR_SMS_SENDING_REPLY, None),
    (ASK_FOR_SMS_SENDING_CONFIRM, PLAY_NOTIFY_SMS_SENDING, None),
    (TANYA_PLAYBACK_OK_RESULT, HANGUP_REPLY, None),
]

PLAY_SCENARIO_PASSENGER_TAGS_TEST_BAD_RESPONSE = [
    (TANYA_INITIAL_RESULT, HANGUP_REPLY_WITHOUT_ACTION_ID, None),
]


@pytest.mark.config(
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        utils.DEFAULT_TAXI_PHONE: {'metaqueue': utils.DEFAULT_METAQUEUE},
    },
    CALLCENTER_METAQUEUES=[
        {
            'name': utils.DEFAULT_METAQUEUE,
            'number': SHORT_NUMBER,
            'allowed_clusters': ['1'],
        },
    ],
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '+74959999999': {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
    IVR_FRAMEWORK_FLOW_CONFIG=FLOWS_CONFIG,
)
@pytest.mark.parametrize(
    ('scenario', 'flow_worker_args', 'sms_text', 'sms_sent'),
    (
        (
            PLAY_MAIN_SCENARIO,
            {
                'should_ask_menu': True,
                'should_switch_to_operator': True,
                'ask_wav_path': SOME_ASK_WAV,
                'sms_text_path': 'some_sms_text',
                'notify_sms_wav_path': NOTIFY_SMS_SENDING_WAV,
            },
            'Ты куда звонишь?',
            True,
        ),
        (
            PLAY_SCENARIO_WITHOUT_MENU_HANGUP,
            {
                'should_ask_menu': False,
                'should_switch_to_operator': False,
                'ask_wav_path': SOME_ASK_WAV,
                'sms_text_path': 'some_sms_text',
                'notify_sms_wav_path': NOTIFY_SMS_SENDING_WAV,
            },
            'Ты куда звонишь?',
            True,
        ),
        (
            PLAY_SCENARIO_WITHOUT_MENU_SWITCH,
            {
                'should_ask_menu': False,
                'should_switch_to_operator': True,
                'ask_wav_path': SOME_ASK_WAV,
                'sms_text_tanker_key': 'some_sms_text',
                'notify_sms_wav_path': NOTIFY_SMS_SENDING_WAV,
            },
            'Ты куда звонишь?',
            False,
        ),
        (
            PLAY_SCENARIO_SWITCH,
            {
                'should_ask_menu': True,
                'ask_wav_path': SOME_ASK_WAV,
                'sms_text_path': 'some_sms_text',
                'notify_sms_wav_path': NOTIFY_SMS_SENDING_WAV,
            },
            'Ты куда звонишь?',
            False,
        ),
        (
            PLAY_SCENARIO_ASK_TIMEOUT_SWITCH,
            {
                'should_ask_menu': True,
                'ask_wav_path': SOME_ASK_WAV,
                'sms_text_path': 'some_sms_text',
                'wait_time': 5000,
                'notify_sms_wav_path': NOTIFY_SMS_SENDING_WAV,
            },
            'Ты куда звонишь?',
            False,
        ),
        (
            PLAY_SCENARIO_NO_TANKER_KEY,
            {
                'should_ask_menu': True,
                'ask_wav_path': SOME_ASK_WAV,
                'sms_text_path': 'some_sms_text',
            },
            'Ты куда звонишь?',
            False,
        ),
        (
            PLAY_SCENARIO_ASK_ERROR,
            {
                'should_ask_menu': True,
                'ask_wav_path': SOME_ASK_WAV,
                'sms_text_path': 'some_sms_text',
                'notify_sms_wav_path': NOTIFY_SMS_SENDING_WAV,
            },
            'Ты куда звонишь?',
            False,
        ),
        (
            PLAY_SCENARIO_WITH_REQUIRED_CHOICE_MAIN,
            {
                'should_ask_menu': True,
                'ask_wav_path': SOME_ASK_WAV,
                'sms_text_path': 'some_sms_text',
                'notify_sms_wav_path': NOTIFY_SMS_SENDING_WAV,
                'ask_amount': 3,
                'bad_user_input_wav_path': BAD_USER_INPUT_WAV,
            },
            'Ты куда звонишь?',
            False,
        ),
        (
            PLAY_SCENARIO_WITH_REQUIRED_CHOICE_SWITCH_AFTER_BAD_USER_INPUTS,
            {
                'should_ask_menu': True,
                'ask_wav_path': SOME_ASK_WAV,
                'sms_text_path': 'some_sms_text',
                'notify_sms_wav_path': NOTIFY_SMS_SENDING_WAV,
                'ask_amount': 3,
                'bad_user_input_wav_path': BAD_USER_INPUT_WAV,
            },
            'Ты куда звонишь?',
            False,
        ),
        (
            PLAY_SCENARIO_WITH_REQUIRED_CHOICE_SMS_AFTER_SECOND_TRY,
            {
                'should_ask_menu': True,
                'ask_wav_path': SOME_ASK_WAV,
                'sms_text_path': 'some_sms_text',
                'notify_sms_wav_path': NOTIFY_SMS_SENDING_WAV,
                'ask_amount': 3,
                'bad_user_input_wav_path': BAD_USER_INPUT_WAV,
            },
            'Ты куда звонишь?',
            True,
        ),
        (
            PLAY_SCENARIO_BAD_FLOW_CONTEXT,
            {
                'should_ask_menu': True,
                'ask_wav_path': SOME_ASK_WAV,
                'sms_text_path': 'some_sms_text',
                'notify_sms_wav_path': NOTIFY_SMS_SENDING_WAV,
                'ask_amount': 3,
            },
            'Ты куда звонишь?',
            False,
        ),
        (
            PLAY_SCENARIO_BAD_FLOW_CONTEXT,
            {
                'should_ask_menu': True,
                'ask_wav_path': SOME_ASK_WAV,
                'sms_text_path': 'some_sms_text',
                'notify_sms_wav_path': NOTIFY_SMS_SENDING_WAV,
                'bad_user_input_wav_path': BAD_USER_INPUT_WAV,
            },
            'Ты куда звонишь?',
            False,
        ),
    ),
    ids=[
        'main_scenario',
        'scenario_without_menu_hangup',
        'scenario_without_menu_switch',
        'scenario_switch',
        'scenario_timeout_switch',
        'scenario_no_tanker_key',
        'scenario_ask_error',
        'scenario_with_required_choice_main',
        'switch_after_bad_user_inputs',
        'sms_after_second_try',
        'bad_flow_context_1',
        'bad_flow_context_2',
    ],
)
async def test_scenarios(
        taxi_ivr_dispatcher,
        mongodb,
        scenario,
        flow_worker_args,
        sms_text,
        sms_sent,
        stq,
        taxi_config,
        testpoint,
        mockserver,
        mock_user_api,
        mock_int_authproxy,
        mock_personal,
):
    @testpoint('set-dial-parameters-leg-id')
    def set_dial_parameters_leg_id(data):
        return {'leg_id': fwt_utils.LEG_ID}

    taxi_config.set_values(
        {
            'IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP': {
                'private_numbers': {
                    SHORT_NUMBER: {
                        'name': FLOW_ID,
                        'type': 'flow_worker',
                        'args': flow_worker_args,
                    },
                },
                'public_numbers': {},
            },
        },
    )

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

    if sms_sent:
        assert stq.ivr_sms_sending.times_called
        args = stq.ivr_sms_sending.next_call()
        args = args['kwargs']
        assert sms_text in args['text']
    else:
        assert not stq.ivr_sms_sending.times_called


@pytest.mark.config(
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        utils.DEFAULT_TAXI_PHONE: {'metaqueue': utils.DEFAULT_METAQUEUE},
    },
    CALLCENTER_METAQUEUES=[
        {
            'name': utils.DEFAULT_METAQUEUE,
            'number': SHORT_NUMBER,
            'allowed_clusters': ['1'],
        },
    ],
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '+74959999999': {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
    IVR_FRAMEWORK_FLOW_CONFIG=FLOWS_CONFIG,
)
@pytest.mark.parametrize(
    (
        'scenario',
        'flow_worker_args',
        'sms_text',
        'sms_sent',
        'v2_upload_response',
    ),
    (
        (
            PLAY_SCENARIO_PASSENGER_TAGS_TEST,
            {
                'should_ask_menu': True,
                'should_switch_to_operator': True,
                'ask_wav_path': SOME_ASK_WAV,
                'sms_text_path': 'some_sms_text',
                'notify_sms_wav_path': NOTIFY_SMS_SENDING_WAV,
                'passenger_tags': ['test_tag'],
            },
            'Ты куда звонишь?',
            True,
            None,
        ),
        (
            PLAY_SCENARIO_PASSENGER_TAGS_TEST_BAD_RESPONSE,
            {
                'should_ask_menu': True,
                'should_switch_to_operator': True,
                'ask_wav_path': SOME_ASK_WAV,
                'sms_text_path': 'some_sms_text',
                'notify_sms_wav_path': NOTIFY_SMS_SENDING_WAV,
                'passenger_tags': ['test_tag'],
            },
            'Ты куда звонишь?',
            False,
            {'code': '400', 'message': 'something bad happen'},
        ),
    ),
    ids=['good_response', '400_response'],
)
async def test_passenger_tags(
        taxi_ivr_dispatcher,
        mongodb,
        scenario,
        flow_worker_args,
        sms_text,
        sms_sent,
        v2_upload_response,
        stq,
        taxi_config,
        mockserver,
        mock_user_api,
        mock_int_authproxy,
        mock_personal,
):
    @mockserver.json_handler('/passenger-tags/v2/upload')
    def _upload(_request):
        assert _request.json['append'][0]['tags'][0]['name'] == 'test_tag'
        if v2_upload_response:
            return web.Response(status=400)
        return {}

    taxi_config.set_values(
        {
            'IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP': {
                'private_numbers': {
                    SHORT_NUMBER: {
                        'name': FLOW_ID,
                        'type': 'flow_worker',
                        'args': flow_worker_args,
                    },
                },
                'public_numbers': {},
            },
        },
    )

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

    if sms_sent:
        assert stq.ivr_sms_sending.times_called
        args = stq.ivr_sms_sending.next_call()
        args = args['kwargs']
        assert sms_text in args['text']
    else:
        assert not stq.ivr_sms_sending.times_called
