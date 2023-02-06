import copy

import pytest

from tests_ivr_dispatcher import fwt_utils
from tests_ivr_dispatcher import utils

ABONENT_NUMBER = copy.copy(utils.DEFAULT_USER_PHONE)
CALLCENTER_NUMBER = copy.copy(utils.DEFAULT_TAXI_PHONE)
CALL_GUID = 'some_call_guid'
SHORT_NUMBER = 'short_number'
UNDEFINED = 'undefined'

WORKER_ID = 'ivr_flow_worker'
FLOW_ID = 'taxi_disp_queue_emulation_flow'
TAXI_DISP_LURING_FLOW_ID = 'taxi_disp_luring_flow'
TVM_NAME = 'ivr_dispatcher'

MOH_WAV = 'taxi_disp_queue_emulation.queue_waiting'
ASK_FOR_SMS_SENDING_WAV = 'taxi_disp_queue_emulation.ask_for_sms_sending'
OPERATORS_BUSY_WAV = 'taxi_disp_queue_emulation.operators_busy'
INVALID_INPUT_WAV = 'taxi_disp_queue_emulation.invalid_input'
PLAY_BYE_DUE_TO_SMS_WAV = 'taxi_disp_queue_emulation.bye_due_to_sms'
PLAY_BACK_DUE_TO_FORWARD_WAV = 'taxi_disp_queue_emulation.forward_to_queue'
PLAY_BACK_DUE_TO_FORWARD_INVALID_INPUT_WAV = (
    'taxi_disp_queue_emulation.switch_after_invalid_input'
)
PLAY_PRE_HANGUP_WAV = 'taxi_disp_queue_emulation.pre_hangup'

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
    TAXI_DISP_LURING_FLOW_ID: {
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
                'interdigit_timeout_ms': 10000,
                'max_digits': 1,
                'min_digits': 1,
            },
            'immediate_input': False,
            'no_input_timeout_ms': 10000,
            'play': {
                'prompt_url': (
                    f'http://ivr-dispatcher.s3.url/'
                    f'{WORKER_ID}/{TAXI_DISP_LURING_FLOW_ID}'
                    f'/{ASK_FOR_SMS_SENDING_WAV}.wav'
                ),
            },
        },
        'type': 'ask',
    },
    'action_id': 'ask_send_sms',
}

ANOTHER_ASK = {
    'action': {
        'params': {
            'dtmf_config': {
                'allowed_dtmf': 'any',
                'interdigit_timeout_ms': 10000,
                'max_digits': 1,
                'min_digits': 1,
            },
            'immediate_input': False,
            'no_input_timeout_ms': 10000,
            'play': {
                'prompt_url': (
                    f'http://ivr-dispatcher.s3.url/'
                    f'{WORKER_ID}/{TAXI_DISP_LURING_FLOW_ID}'
                    f'/ANOTHER_ASK.wav'
                ),
            },
        },
        'type': 'ask',
    },
    'action_id': 'ask_send_sms',
}

ASK_FOR_SMS_SENDING_MOH_REPLY = {
    'action': {
        'params': {
            'dtmf_config': {
                'allowed_dtmf': 'any',
                'interdigit_timeout_ms': 10000,
                'max_digits': 1,
                'min_digits': 1,
            },
            'immediate_input': True,
            'no_input_timeout_ms': 10000,
            'play': {
                'prompt_url': (
                    f'http://ivr-dispatcher.s3.url/'
                    f'{WORKER_ID}/{FLOW_ID}/{MOH_WAV}.wav'
                ),
            },
        },
        'type': 'ask',
    },
    'action_id': 'queue_waiting',
}

PLAY_AFTER_ITERATION_REPLY = {
    'action': {
        'params': {
            'play': {
                'prompt_url': (
                    f'http://ivr-dispatcher.s3.url/'
                    f'{WORKER_ID}/{FLOW_ID}/{ASK_FOR_SMS_SENDING_WAV}.wav'
                ),
            },
        },
        'type': 'playback',
    },
    'action_id': 'playback_after_iteration',
}

PLAY_MOH_REPLY = {
    'action': {
        'params': {
            'play': {
                'prompt_url': (
                    f'http://ivr-dispatcher.s3.url/'
                    f'{WORKER_ID}/{FLOW_ID}/{MOH_WAV}.wav'
                ),
            },
        },
        'type': 'playback',
    },
    'action_id': 'queue_waiting',
}

PLAY_OPERATORS_BUSY_REPLY = {
    'action': {
        'params': {
            'play': {
                'prompt_url': (
                    f'http://ivr-dispatcher.s3.url/'
                    f'{WORKER_ID}/{FLOW_ID}/{OPERATORS_BUSY_WAV}.wav'
                ),
            },
        },
        'type': 'playback',
    },
    'action_id': 'hello_request',
}

ASK_INVALID_INPUT_REPLY = {
    'action': {
        'params': {
            'dtmf_config': {
                'allowed_dtmf': 'any',
                'interdigit_timeout_ms': 5000,
                'max_digits': 1,
                'min_digits': 1,
            },
            'immediate_input': True,
            'no_input_timeout_ms': 5000,
            'play': {
                'prompt_url': (
                    f'http://ivr-dispatcher.s3.url/'
                    f'{WORKER_ID}/{FLOW_ID}/{INVALID_INPUT_WAV}.wav'
                ),
            },
        },
        'type': 'ask',
    },
    'action_id': 'invalid_input',
}

PLAY_PRE_HANGUP_REPLY = {
    'action': {
        'params': {
            'play': {
                'prompt_url': (
                    f'http://ivr-dispatcher.s3.url/'
                    f'{WORKER_ID}/{FLOW_ID}/{PLAY_PRE_HANGUP_WAV}.wav'
                ),
            },
        },
        'type': 'playback',
    },
    'action_id': 'pre_hangup_playback',
}

# TDLF = Taxi Disp Luring Flow
PLAY_BYE_DUE_TO_SMS_FROM_TDLF_REPLY = {
    'action': {
        'params': {
            'play': {
                'prompt_url': (
                    f'http://ivr-dispatcher.s3.url/'
                    f'{WORKER_ID}/{TAXI_DISP_LURING_FLOW_ID}'
                    f'/{PLAY_BYE_DUE_TO_SMS_WAV}.wav'
                ),
            },
        },
        'type': 'playback',
    },
    'action_id': 'notify_to_send_sms',
}

PLAY_BYE_DUE_TO_SMS_REPLY = {
    'action': {
        'params': {
            'play': {
                'prompt_url': (
                    f'http://ivr-dispatcher.s3.url/'
                    f'{WORKER_ID}/{FLOW_ID}/{PLAY_BYE_DUE_TO_SMS_WAV}.wav'
                ),
            },
        },
        'type': 'playback',
    },
    'action_id': 'playback_due_to_sms',
}

PLAY_OPERATOR_SWITCH_REPLY = {
    'action': {
        'params': {
            'play': {
                'prompt_url': (
                    f'http://ivr-dispatcher.s3.url/'
                    f'{WORKER_ID}/{FLOW_ID}/{PLAY_BACK_DUE_TO_FORWARD_WAV}.wav'
                ),
            },
        },
        'type': 'playback',
    },
    'action_id': 'playback_due_to_forward',
}

PLAY_OPERATOR_SWITCH_INVALID_INPUT = {
    'action': {
        'params': {
            'play': {
                'prompt_url': (
                    f'http://ivr-dispatcher.s3.url/'
                    f'{WORKER_ID}/{FLOW_ID}/'
                    f'{PLAY_BACK_DUE_TO_FORWARD_INVALID_INPUT_WAV}.wav'
                ),
            },
        },
        'type': 'playback',
    },
    'action_id': 'playback_due_to_switch_after_invalid_input',
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

HANGUP_DUE_TO_SMS_REPLY = {
    'action': {'type': 'hangup', 'params': {'cause': 'NORMAL_CALL_CLEARING'}},
    'action_id': 'hangup_due_to_sms',
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
    (
        TANYA_ANSWER_OK_RESULT,
        PLAY_OPERATORS_BUSY_REPLY,
        None,
    ),  # Все операторы заняты
    (
        TANYA_PLAYBACK_OK_RESULT,
        ASK_FOR_SMS_SENDING_REPLY,
        None,
    ),  # Дочернее флоу с IVR на отправку смс
    (
        ASK_FOR_SMS_SENDING_CONFIRM,
        PLAY_BYE_DUE_TO_SMS_FROM_TDLF_REPLY,
        None,
    ),  # (Получили 1) Спасибо, мы отправим смс
    (TANYA_PLAYBACK_OK_RESULT, HANGUP_DUE_TO_SMS_REPLY, None),
]

PLAY_MAIN_SCENARIO_ANOTHER_ASK = [
    (TANYA_INITIAL_RESULT, ANSWER_REPLY, None),
    (
        TANYA_ANSWER_OK_RESULT,
        PLAY_OPERATORS_BUSY_REPLY,
        None,
    ),  # Все операторы заняты
    (
        TANYA_PLAYBACK_OK_RESULT,
        ANOTHER_ASK,
        None,
    ),  # Дочернее флоу с IVR на отправку смс
    (
        ASK_FOR_SMS_SENDING_CONFIRM,
        PLAY_BYE_DUE_TO_SMS_FROM_TDLF_REPLY,
        None,
    ),  # (Получили 1) Спасибо, мы отправим смс
    (TANYA_PLAYBACK_OK_RESULT, HANGUP_DUE_TO_SMS_REPLY, None),
]

PLAY_USER_INPUT_WHILE_MOH_SCENARIO = [
    (TANYA_INITIAL_RESULT, ANSWER_REPLY, None),
    (
        TANYA_ANSWER_OK_RESULT,
        PLAY_OPERATORS_BUSY_REPLY,
        None,
    ),  # Все операторы заняты
    (
        TANYA_PLAYBACK_OK_RESULT,
        ASK_FOR_SMS_SENDING_REPLY,
        None,
    ),  # Дочернее флоу с IVR на отправку смс
    (
        ASK_FOR_SMS_SENDING_TIMEOUT,
        ASK_FOR_SMS_SENDING_MOH_REPLY,
        None,
    ),  # (Не получили 1) MoH
    (
        ASK_FOR_SMS_SENDING_CONFIRM,
        PLAY_BYE_DUE_TO_SMS_REPLY,
        None,
    ),  # (Получили 1) Спасибо, отправим смс
    (TANYA_PLAYBACK_OK_RESULT, HANGUP_DUE_TO_SMS_REPLY, None),
]

PLAY_SWITCH_TO_OPERATOR_SCENARIO = [
    (TANYA_INITIAL_RESULT, ANSWER_REPLY, None),
    (
        TANYA_ANSWER_OK_RESULT,
        PLAY_OPERATORS_BUSY_REPLY,
        None,
    ),  # Все операторы заняты
    (
        TANYA_PLAYBACK_OK_RESULT,
        ASK_FOR_SMS_SENDING_REPLY,
        None,
    ),  # Дочернее флоу с IVR на отправку смс
    (
        ASK_FOR_SMS_SENDING_TIMEOUT,
        ASK_FOR_SMS_SENDING_MOH_REPLY,
        None,
    ),  # (Не получили 1) MoH
    (
        ASK_FOR_SMS_SENDING_TIMEOUT,
        PLAY_OPERATORS_BUSY_REPLY,
        None,
    ),  # (Не получили 1) Все операторы заняты
    (
        TANYA_PLAYBACK_OK_RESULT,
        ASK_FOR_SMS_SENDING_REPLY,
        None,
    ),  # Дочернее флоу с IVR на отправку смс
    (
        ASK_FOR_SMS_SENDING_TIMEOUT,
        ASK_FOR_SMS_SENDING_MOH_REPLY,
        None,
    ),  # (Не получили 1) MoH
    (ASK_FOR_SMS_SENDING_TIMEOUT, SWITCH_REPLY, None),  # Свитчим
    (TANYA_SWITCH_OK_RESULT, HANGUP_REPLY, None),
]

PLAY_SMS_IN_SECOND_ITERATION_SCENARIO = [
    (TANYA_INITIAL_RESULT, ANSWER_REPLY, None),
    (
        TANYA_ANSWER_OK_RESULT,
        PLAY_OPERATORS_BUSY_REPLY,
        None,
    ),  # Все операторы заняты
    (
        TANYA_PLAYBACK_OK_RESULT,
        ASK_FOR_SMS_SENDING_REPLY,
        None,
    ),  # Дочернее флоу с IVR на отправку смс
    (
        ASK_FOR_SMS_SENDING_TIMEOUT,
        ASK_FOR_SMS_SENDING_MOH_REPLY,
        None,
    ),  # (Не получили 1) MoH
    (
        ASK_FOR_SMS_SENDING_TIMEOUT,
        PLAY_OPERATORS_BUSY_REPLY,
        None,
    ),  # (Не получили 1) Все операторы заняты
    (
        TANYA_PLAYBACK_OK_RESULT,
        ASK_FOR_SMS_SENDING_REPLY,
        None,
    ),  # Дочернее флоу с IVR на отправку смс
    (
        ASK_FOR_SMS_SENDING_CONFIRM,
        PLAY_BYE_DUE_TO_SMS_FROM_TDLF_REPLY,
        None,
    ),  # (Получили 1) Спасибо, отправим смс
    (TANYA_PLAYBACK_OK_RESULT, HANGUP_DUE_TO_SMS_REPLY, None),
]

PLAY_NOT_SWITCH_TO_OPERATOR_SCENARIO = [
    (TANYA_INITIAL_RESULT, ANSWER_REPLY, None),
    (
        TANYA_ANSWER_OK_RESULT,
        PLAY_OPERATORS_BUSY_REPLY,
        None,
    ),  # Все операторы заняты
    (
        TANYA_PLAYBACK_OK_RESULT,
        ASK_FOR_SMS_SENDING_REPLY,
        None,
    ),  # Дочернее флоу с IVR на отправку смс
    (
        ASK_FOR_SMS_SENDING_TIMEOUT,
        ASK_FOR_SMS_SENDING_MOH_REPLY,
        None,
    ),  # (Не получили 1) MoH
    (
        ASK_FOR_SMS_SENDING_TIMEOUT,
        PLAY_OPERATORS_BUSY_REPLY,
        None,
    ),  # (Не получили 1) Все операторы заняты
    (
        TANYA_PLAYBACK_OK_RESULT,
        ASK_FOR_SMS_SENDING_REPLY,
        None,
    ),  # Дочернее флоу с IVR на отправку смс
    (
        ASK_FOR_SMS_SENDING_TIMEOUT,
        ASK_FOR_SMS_SENDING_MOH_REPLY,
        None,
    ),  # (Не получили 1) MoH
    (ASK_FOR_SMS_SENDING_TIMEOUT, PLAY_PRE_HANGUP_REPLY, None),
    (TANYA_PLAYBACK_OK_RESULT, HANGUP_REPLY, None),
]

PLAY_ANTIFRAUD_SCENARIO = [
    (TANYA_INITIAL_RESULT, ANSWER_REPLY, None),
    (
        TANYA_ANSWER_OK_RESULT,
        PLAY_OPERATORS_BUSY_REPLY,
        None,
    ),  # Все операторы заняты
    (
        TANYA_PLAYBACK_OK_RESULT,
        ASK_FOR_SMS_SENDING_REPLY,
        None,
    ),  # Дочернее флоу с IVR на отправку смс
    (
        ASK_FOR_SMS_SENDING_TIMEOUT,
        ASK_FOR_SMS_SENDING_MOH_REPLY,
        None,
    ),  # (Не получили 1) MoH [ask_attempts - 1]
    (
        ASK_FOR_SMS_SENDING_NOT_CONFIRM,
        ASK_INVALID_INPUT_REPLY,
        None,
    ),  # (Получили 2) Неверный ввод, нажмите 1 ... [ask_attempts - 2]
    (
        ASK_FOR_SMS_SENDING_NOT_CONFIRM,
        ASK_FOR_SMS_SENDING_MOH_REPLY,
        None,
    ),  # (Получили 2)Неверный ввод, нажмите 1 ... [ask_attempts - 3]
    (
        ASK_FOR_SMS_SENDING_NOT_CONFIRM,
        PLAY_OPERATOR_SWITCH_INVALID_INPUT,
        None,
    ),  # (Получили 2) Неверный ввод.
    (TANYA_PLAYBACK_OK_RESULT, SWITCH_REPLY, None),  # Свитчим
    (TANYA_SWITCH_OK_RESULT, HANGUP_REPLY, None),
]

PLAY_HARD_SCENARIO = [
    (TANYA_INITIAL_RESULT, ANSWER_REPLY, None),
    (TANYA_ANSWER_OK_RESULT, PLAY_AFTER_ITERATION_REPLY, None),
    (TANYA_PLAYBACK_OK_RESULT, PLAY_MOH_REPLY, None),
    (TANYA_PLAYBACK_OK_RESULT, PLAY_AFTER_ITERATION_REPLY, None),
    (TANYA_PLAYBACK_OK_RESULT, PLAY_MOH_REPLY, None),
    (TANYA_PLAYBACK_OK_RESULT, SWITCH_REPLY, None),
    (TANYA_SWITCH_OK_RESULT, HANGUP_REPLY, None),
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
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {
            SHORT_NUMBER: {'name': FLOW_ID, 'type': 'flow_worker'},
        },
        'public_numbers': {},
    },
)
@pytest.mark.parametrize(
    ('scenario', 'sms_sent', 'flow_worker_args', 'sms_text'),
    (
        (
            PLAY_MAIN_SCENARIO,
            True,
            {},
            'В приложении заказать такси дешевле <link>',
        ),
        (
            PLAY_USER_INPUT_WHILE_MOH_SCENARIO,
            True,
            {},
            'В приложении заказать такси дешевле <link>',
        ),
        (PLAY_SWITCH_TO_OPERATOR_SCENARIO, False, {}, None),
        (
            PLAY_SMS_IN_SECOND_ITERATION_SCENARIO,
            True,
            {},
            'В приложении заказать такси дешевле <link>',
        ),
        (
            PLAY_NOT_SWITCH_TO_OPERATOR_SCENARIO,
            False,
            {'should_switch_to_operator': False},
            None,
        ),
        (PLAY_ANTIFRAUD_SCENARIO, False, {'ask_attempts': 3}, None),
        (
            PLAY_HARD_SCENARIO,
            False,
            {'should_send_sms': False, 'should_play_operators_busy': False},
            None,
        ),
    ),
    ids=[
        'main_scenario',
        'user_input_while_moh_scenario',
        'switch_to_operator_scenario',
        'sms_in_second_iteration_scenario',
        'hard_scenario',
        'antifraud_scenario',
        'hard_scenario',
    ],
)
async def test_scenarios(
        taxi_ivr_dispatcher,
        mongodb,
        scenario,
        sms_sent,
        flow_worker_args,
        sms_text,
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
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {
            SHORT_NUMBER: {'name': FLOW_ID, 'type': 'flow_worker'},
        },
        'public_numbers': {},
    },
)
@pytest.mark.parametrize(
    ('scenario', 'flow_worker_args'),
    ((PLAY_MAIN_SCENARIO_ANOTHER_ASK, {'ask_wav_path': 'ANOTHER_ASK'}),),
    ids=['main_scenario_another_ask'],
)
async def test_scenarios_another_ask(
        taxi_ivr_dispatcher,
        mongodb,
        scenario,
        flow_worker_args,
        stq,
        taxi_config,
        mockserver,
        mock_user_api,
        mock_int_authproxy,
        mock_personal,
):
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
