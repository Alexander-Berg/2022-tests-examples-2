import copy

import pytest

from tests_ivr_dispatcher import fwo_utils
from tests_ivr_dispatcher import utils


ABONENT_NUMBER = copy.copy(utils.DEFAULT_USER_PHONE)
CALLCENTER_NUMBER = copy.copy(utils.DEFAULT_TAXI_PHONE)
CALL_GUID = 'some_call_guid'
SHORT_NUMBER = 'short_number'
UNDEFINED = 'undefined'

PERFORMER_TAG = 'performer_tag'
COURIER_TARIFF = 'courier'
SUPPORT_NUMBER = '444444'  # should be not more than 6 symbols
CALL_FROM = '+79152608765'
NEAREST_ZONE = 'moscow'

WORKER_ID = fwo_utils.WORKER_ID
FLOW_ID = 'cargo_support_flow'

OCTONODE_INITIATING = {
    'called_number': SHORT_NUMBER,
    'origin_called_number': CALLCENTER_NUMBER,
    'caller_number': ABONENT_NUMBER,
    'call_guid': CALL_GUID,
    'status': 'ok',
    'type': 'initial',
}
OCTONODE_ANSWER_RESULT_OK = {'status': 'ok', 'type': 'answer'}
OCTONODE_PLAY_RESULT_OK = {'status': 'ok', 'type': 'play'}
OCTONODE_SWITCH_OK_RESULT = {'status': 'ok', 'type': 'switch'}

DISPATCHER_INITIATING_REPLY = {
    'params': {'start_recording': False},
    'type': 'answer',
}
DISPATCHER_PLAY_INAPPROPRIATE_PERFORMER_REPLY = {
    'params': {
        'relative_path': (
            f'{WORKER_ID}/{FLOW_ID}/csf.inappropriate_performer.wav'
        ),
    },
    'type': 'play',
}
DISPATCHER_PLAY_CALLCENTER_WORKTIME_FROM_9_TO_21_REPLY = {
    'params': {
        'text': (
            'Спасибо за ваш звонок! Наша служба голосовой поддержки '
            'работает с 09:00 до 21:00 по местному времени. Для '
            'решения вашего вопроса, напишите, пожалуйста, ваше '
            'обращение в приложении Яндекс Пр+о и мы обязательно '
            'поможем вам.'
        ),
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'speed': 1.3,
        'voice': 'alena',
        'use_grpc': True,
    },
    'type': 'speak',
}
DISPATCHER_HANGUP_REPLY = {'type': 'hangup'}
DISPATCHER_SWITCH_TO_SUPPORT_REPLY = {
    'params': {
        'answer_timeout': fwo_utils.NO_ANSWER_TO,
        'call_from': CALL_FROM,
        'call_to': SUPPORT_NUMBER,
        'gateways': 'operators',
        'progress_timeout': fwo_utils.NO_ANSWER_TO,
        'send_events': False,
    },
    'type': 'switch',
}

SWITCH_TO_SUPPORT_SCENARIO = [
    (OCTONODE_INITIATING, DISPATCHER_INITIATING_REPLY),
    (OCTONODE_ANSWER_RESULT_OK, DISPATCHER_SWITCH_TO_SUPPORT_REPLY),
    (OCTONODE_SWITCH_OK_RESULT, DISPATCHER_HANGUP_REPLY),
]
CALLCENTER_WORKTIME_FROM_9_TO_21_SCENARIO = [
    (OCTONODE_INITIATING, DISPATCHER_INITIATING_REPLY),
    (
        OCTONODE_ANSWER_RESULT_OK,
        DISPATCHER_PLAY_CALLCENTER_WORKTIME_FROM_9_TO_21_REPLY,
    ),
    (OCTONODE_PLAY_RESULT_OK, DISPATCHER_HANGUP_REPLY),
]
INAPPROPRIATE_PERFORMER_SCENARIO = [
    (OCTONODE_INITIATING, DISPATCHER_INITIATING_REPLY),
    (OCTONODE_ANSWER_RESULT_OK, DISPATCHER_PLAY_INAPPROPRIATE_PERFORMER_REPLY),
    (OCTONODE_PLAY_RESULT_OK, DISPATCHER_HANGUP_REPLY),
]

SCENARIO_CONFIGS = pytest.mark.config(
    CARGO_SUPPORT_PHONES={
        'rus': {
            'cities': {
                NEAREST_ZONE: {
                    'phone': CALLCENTER_NUMBER,
                    'formatted_phone': CALLCENTER_NUMBER,
                    'working_time': {'from': '9:00', 'to': '21:00'},
                },
            },
            'default_callback': ['test'],
        },
    },
    IVR_DISPATCHER_CARGO_SUPPORT_CONFIG={
        'allowed_performer_tags': [PERFORMER_TAG],
        'allowed_tariff_classes': [COURIER_TARIFF],
        'support_number': SUPPORT_NUMBER,
    },
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {
            SHORT_NUMBER: {'name': FLOW_ID, 'type': 'flow_worker'},
        },
        'public_numbers': {},
    },
    IVR_FRAMEWORK_FLOW_CONFIG={
        FLOW_ID: {
            'base_url': fwo_utils.BASE_URL,
            'tvm_name': fwo_utils.TVM_NAME,
            'outbound_number': UNDEFINED,
            'outbound_routes': {'__default__': fwo_utils.OPERATOR_GW},
            'record_call': False,
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
