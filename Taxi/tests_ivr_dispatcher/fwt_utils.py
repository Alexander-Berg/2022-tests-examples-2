# pylint: disable=C0302
WORKER_ID = 'ivr_flow_worker'
CALL_FLOW_ID = 'xT5n4mO/QeOa53FxYJOJnAqzE3E='
FLOW_ID = 'test_flow'
CSAT_FLOW_ID = 'csat_flow'
PLAYBACK_FLOW_ID = 'playback_flow'
PLAYBACK_ID = 'playback'
NO_FLOW_ID = 'no_flow'
CALL_ID = 'cw-test-call-id'
CALL_GUID = '111-222-333-444'
LEG_ID = 'fcc6f283217c4a7cb649ee24a0094b72'
INCOMING_CALL = 'incoming'
OUTGOING_CALL = 'outgoing'
BASE_URL = {'$mockserver': ''}
TANYA_BASE_URL = '$mockserver/tanya-telephony/'
TVM_NAME = 'callcenter-qa'
INBOUND_NUMBER = '+7495INBOUND'
OUTBOUND_NUMBER = '+7495OUTBOUND'
ABONENT_NUMBER = '+7495ABONENT'
CALLED_PD_ID = '+7495ABONENT_id'
FORWARD_NUMBER = '+7495FORWARD'
FORWARD_BACKUP_NUMBER = '+7495FORWARDBACKUP'
FORWARD_YANDEX_UID = '1001'
FORWARD_AGENT_ID = '111'
SWITCH_NUMBER = '+7495SWITCH'
ROUTE_CC_OPERATORS = 'cc_operators'
OUTBOUND_GW = 'ivr_via_noc'
OPERATOR_GW = 'operators'
OUTBOUND_X_ROUTE = 'x-provider'
OPERATOR_X_ROUTE = 'x-operator'
NO_ANSWER_TO = 100500
RECORD_CALL = True
USE_DEFLECT = False
ENABLE_PROVISION = True
RATING_RESULT = 'Без проблем, работу оцениваю на 5 баллов'
CSAT_FLOW_TANYA_ASK_RATING_RESULT = {
    'status': 'OK',
    'type': 'ask',
    'user_input': RATING_RESULT,
}

TTS_LANG = 'ru-RU'
TTS_VOICE = 'alena'
TTS_SPEED = 1.3
TTS_GRPC = True

ASR_LANG_CODE = 'ru-ru'
ASR_MODEL = 'general'

DEFAULT_NIT = 4000
DEFAULT_MRD = 10000
CUSTOM_MRD = 20000
DEFAULT_SIT = False
DEFAULT_NLV = False
DEFAULT_VT = 40
DEFAULT_VV = 20
DEFAULT_VS = 20
DEFAULT_SCT = 1000
DEFAULT_ST = 10000
CUSTOM_ST = 30000
CUSTOM_NIT = 500

SESSION_ID = 'cw-test-call-id'
INTRO_FILE_ID = 'intro'
INTRO_FILE_PATH = (
    f'http://ivr-dispatcher.s3.url/{WORKER_ID}/{FLOW_ID}/{INTRO_FILE_ID}.wav'
)
RABBIT_FILE_ID = 'rabbit'
RABBIT_FILE_PATH = (
    f'http://ivr-dispatcher.s3.url/{WORKER_ID}/{FLOW_ID}/{RABBIT_FILE_ID}.wav'
)
ERROR_FILE_ID = 'error'
ERROR_FILE_PATH = (
    f'http://ivr-dispatcher.s3.url/{WORKER_ID}/{FLOW_ID}/{ERROR_FILE_ID}.wav'
)
FALLB_FILE_ID = 'fallback'
FALLB_FILE_PATH = (
    f'http://ivr-dispatcher.s3.url/{WORKER_ID}/{FLOW_ID}/{FALLB_FILE_ID}.wav'
)
HELLO_REPLY_ID = 'csat.hello_request'
HELLO_REPLY_PATH = (
    f'http://ivr-dispatcher.s3.url/'
    f'{WORKER_ID}/{CSAT_FLOW_ID}/{HELLO_REPLY_ID}.wav'
)
BYE_REPLY_ID = 'csat.rating_cancelled'
BYE_REPLY_PATH = (
    f'http://ivr-dispatcher.s3.url/'
    f'{WORKER_ID}/{CSAT_FLOW_ID}/{BYE_REPLY_ID}.wav'
)
PROMPT_ID = 'prompt1'
PROMPT_PATH = (
    f'http://ivr-dispatcher.s3.url/'
    f'{WORKER_ID}/{PLAYBACK_FLOW_ID}/{PROMPT_ID}.wav'
)
ML_SAID = 'вы сказали'
INPUT_RABBIT = 'про заек'
INPUT_CUSTOM = 'custom_ask_params'
INPUT_CUSTOM_LVC = 'custom_ask_params_lvc'
INPUT_RABBIT_RETRY = 'про заек дважды'
INPUT_ANY = 'трололо'
INPUT_CLOSE = 'close'
INPUT_FORWARD = 'forward'
INPUT_FORWARD_UID = 'forward_to_uid'
INPUT_DEFLECT = 'deflect'
INPUT_SWITCH = 'switch'
INPUT_EMPTY = ''
INPUT_DTMF = 'dtmf'
INPUT_MULTI_DTMF = 'multi_dtmf'
INPUT_HOLD = 'hold'
INPUT_SKIP_HOLDS = 'skip_hold'
INPUT_FALLBACK = 'fallback'
DTMF_1234 = 'DIGIT: *1234#'

ORIGINATE_ACTION_ID = 'originate-action-id'
ANSWER_ACTION_ID = 'answer-action-id'
HANGUP_ACTION_ID = 'hangup-action-id'
HANGUP_FALLBACK_ACTION_ID = 'hangup-fallback-action-id'
HOLD_ACTION_ID = 'hold-action-id'
FORWARD_ACTION_ID = 'forward-action-id'
FORWARD_BACKUP_ACTION_ID = 'forward-backup-action-id'
SWITCH_ACTION_ID = 'switch-action-id'
PLAY_INTRO_ACTION_ID = 'play-intro-action-id'
PLAY_RABBIT_ACTION_ID = 'play-rabbit-action-id'
PLAY_ERROR_ACTION_ID = 'play-error-action-id'
PLAY_FALLBACK_ACTION_ID = 'play-fallback-action-id'
ASK_INTRO_ID = 'intro-id'
ASK_CUSTOM_ID = 'custom-id'
ASK_CUSTOM_LVC_ID = 'custom-lvc-id'
ASK_RABBIT_ID = 'rabbit-id'
ASK_ANY_ID = 'any-id'
ASK_DTMF_ID = 'any-id'
ASK_MULTI_DTMF_ID = 'multi-dtmf-id'
ASK_FALLBACK_ID = 'fallback-id'

PROJECT_ID = 'disp'
EXT_CALL_ID = '000-my-ext-call-id'
TICKET_HEADER = 'X-Ya-Service-Ticket'
USER_UID_HEADER = 'X-Yandex-UID'
USER_LOGIN_HEADER = 'X-Yandex-Login'
OPERATOR_UID = 'some_operator_uid'
OPERATOR_LOGIN = 'some_operator_login'

MOCK_TVM_SERVICES = {
    'ivr-dispatcher': 5,
    'statistics': 6,
    'yamaps': 7,
    'callcenter-operators': 8,
    'cars-catalog': 9,
    'driver-tags': 10,
    'communication-scenario': 11,
    'experiments3-proxy': 12,
    'callcenter-qa': 13,
    'order-core': 14,
    'driver-profiles': 15,
    'fleet-vehicles': 16,
    'driver-status': 17,
    'taxi-exp': 18,
    'fleet-parks': 19,
    'int-authproxy': 20,
    'parks': 21,
    'personal': 22,
    'plotva-ml': 23,
    'ucommunications': 24,
    'stq-agent': 25,
    'supportai-api': 26,
    'user-api': 27,
    'taxi_exp': 28,
    'tariffs': 29,
    'cc-authproxy': 30,
    'passenger-tags': 31,
}
ASR_CONFIG = {'language_code': 'ru-ru', 'model': 'general'}
TTS_CONFIG = {'language': 'ru-RU', 'speed': 1, 'voice': 'alena'}
LOCAL_VAD_CONFIG = {
    'speech_complete_timeout_ms': 1000,
    'speech_timeout_ms': 10000,
    'vad_silence_ms': 20,
    'vad_threshold': 40,
    'vad_voice_ms': 20,
}

LOCAL_FLOW_CONFIG = {
    'mock_flow': {
        'base_url': 'mock_url',
        'tvm_name': 'ivr-dispatcher',
        'asr_config': ASR_CONFIG,
        'local_vad_config': LOCAL_VAD_CONFIG,
        'outbound_number': '+74992296688',
        'outbound_routes': {
            '__default__': 'taxi_external',
            'to_operator': 'taxi_phonecall',
        },
        'record_call': True,
        'tts_config': TTS_CONFIG,
        'use_tanya_backend': True,
        'project': PROJECT_ID,
    },
    FLOW_ID: {
        'asr_config': ASR_CONFIG,
        'local_actions': [
            {
                'external_id': 'originate_to_operator',
                'originate': {
                    'yandex_uid': {
                        'value': '',
                        'override_name': 'operator_yandex_uid',
                    },
                    'route': {'value': 'to_operator'},
                },
            },
            {
                'external_id': 'forward_to_external',
                'forward': {
                    'phone_number': {
                        'value': '',
                        'override_name': 'phone_number',
                    },
                    'enable_provision': {'value': True},
                    'timeout_sec': {'value': 30},
                    'use_deflect': {
                        'value': False,
                        'override_name': 'deflect_to_ext',
                    },
                },
            },
        ],
        'local_vad_config': LOCAL_VAD_CONFIG,
        'outbound_number': '+74992296688',
        'outbound_routes': {
            '__default__': 'taxi_external',
            'to_operator': 'taxi_phonecall',
        },
        'record_call': True,
        'tts_config': TTS_CONFIG,
        'use_tanya_backend': True,
        'is_form_flow': True,
        'project': PROJECT_ID,
    },
}


def read_tvm_ticket(filename, load):
    try:
        for line in load(filename).splitlines():
            if not line.startswith('#'):
                return line.strip()
    except FileNotFoundError:
        pass
    return None


TTS_CONFIG = {
    'language': TTS_LANG,
    'voice': TTS_VOICE,
    'speed': TTS_SPEED,
    'use_grpc': TTS_GRPC,
}

ASR_CONFIG = {'language_code': ASR_LANG_CODE, 'model': ASR_MODEL}

VAD_CONFIG = {
    'vad_threshold': DEFAULT_VT,
    'vad_voice_ms': DEFAULT_VV,
    'vad_silence_ms': DEFAULT_VS,
    'speech_complete_timeout_ms': DEFAULT_SCT,
    'speech_timeout_ms': DEFAULT_ST,
}

VAD_CONFIG_CUSTOM = {
    'vad_threshold': DEFAULT_VT,
    'vad_voice_ms': DEFAULT_VV,
    'vad_silence_ms': DEFAULT_VS,
    'speech_complete_timeout_ms': DEFAULT_SCT,
    'speech_timeout_ms': CUSTOM_ST,
}

VAD_CONFIG_CUSTOM_TANYA = {
    'vad_threshold': DEFAULT_VT,
    'vad_voice_ms': DEFAULT_VV,
    'vad_silence_ms': DEFAULT_VS,
    'speech_complete_timeout_ms': DEFAULT_SCT,
}

FALLBACK_PLAYBACK_ACTION = {
    'external_id': PLAY_FALLBACK_ACTION_ID,
    'playback': {'playback': {'play': {'id': FALLB_FILE_ID}}},
}
FALLBACK_HANGUP_ACTION = {
    'external_id': HANGUP_FALLBACK_ACTION_ID,
    'hangup': {},
}

WORKER_MAP_CONFIG = {
    'public_numbers': {
        INBOUND_NUMBER: {
            'name': FLOW_ID,
            'type': 'flow_worker',
            'args': {
                'worker_arg1': 'test',
                'worker_arg2': False,
                'worker_arg3': 0.5,
            },
        },
        SWITCH_NUMBER: {
            'name': 'playback_flow',
            'type': 'flow_worker',
            'args': {'switch_to_csat': False},
        },
    },
    'private_numbers': {},
}

FLOW_CONFIG = {
    'base_url': BASE_URL,
    'tvm_name': TVM_NAME,
    'outbound_number': OUTBOUND_NUMBER,
    'outbound_routes': {
        '__default__': OUTBOUND_GW,
        ROUTE_CC_OPERATORS: OPERATOR_GW,
    },
    'record_call': RECORD_CALL,
    'no_answer_timeout_sec': NO_ANSWER_TO,
    'tts_config': TTS_CONFIG,
    'no_input_timeout_ms': DEFAULT_NIT,
    'max_response_duration_ms': DEFAULT_MRD,
    'immediate_input': DEFAULT_SIT,
    'asr_config': ASR_CONFIG,
    'no_local_vad': DEFAULT_NLV,
    'local_vad_config': VAD_CONFIG,
    'use_tanya_backend': True,
    'dtmf_as_text': True,
    'dispatcher_fallback_actions': [
        FALLBACK_PLAYBACK_ACTION,
        FALLBACK_HANGUP_ACTION,
    ],
}

FLOW_CONFIG_X_ROUTE = {
    'base_url': BASE_URL,
    'tvm_name': TVM_NAME,
    'outbound_number': OUTBOUND_NUMBER,
    'routes': {
        '__default__': {
            'distributor_name': OUTBOUND_GW,
            'x_route': OUTBOUND_X_ROUTE,
        },
        ROUTE_CC_OPERATORS: {
            'distributor_name': OPERATOR_GW,
            'x_route': OPERATOR_X_ROUTE,
        },
    },
    'record_call': RECORD_CALL,
    'no_answer_timeout_sec': NO_ANSWER_TO,
    'tts_config': TTS_CONFIG,
    'no_input_timeout_ms': DEFAULT_NIT,
    'max_response_duration_ms': DEFAULT_MRD,
    'immediate_input': DEFAULT_SIT,
    'asr_config': ASR_CONFIG,
    'no_local_vad': DEFAULT_NLV,
    'local_vad_config': VAD_CONFIG,
    'use_tanya_backend': True,
    'dtmf_as_text': True,
    'dispatcher_fallback_actions': [
        FALLBACK_PLAYBACK_ACTION,
        FALLBACK_HANGUP_ACTION,
    ],
}

IVR_FRAMEWORK_FLOW_CONFIG = {FLOW_ID: FLOW_CONFIG}
IVR_FRAMEWORK_FLOW_CONFIG_X_ROUTE = {FLOW_ID: FLOW_CONFIG_X_ROUTE}

CLIENT_CONTEXT = {
    'test1': 1,
    'test2': True,
    'test3': [1, 11, 101, 1001],
    'test4': {'test1': 1, 'test2': True},
}


class Message:
    def __init__(self, data):
        assert 'ivr_flow_id' in data
        assert 'call_external_id' in data
        assert 'abonent_number' in data
        assert 'service_number' in data
        assert 'direction' in data
        assert 'actions' in data
        assert 'last_action' in data

        self.ivr_flow_id = data['ivr_flow_id']
        assert self.ivr_flow_id
        self.call_external_id = data['call_external_id']
        assert self.call_external_id
        self.abonent_number = data['abonent_number']
        assert self.abonent_number
        self.service_number = data['service_number']
        assert self.service_number
        self.direction = data['direction']
        assert self.direction
        self.actions = data['actions']
        self.last_action = data['last_action']

    def get_action_state(self, action):
        assert 'status' in action
        status = action['status']
        assert status
        assert 'state' in status
        state = status['state']
        assert state
        return state

    def get_disconnect_side(self, action):
        assert 'status' in action
        status = action['status']
        assert status
        assert 'state' in status
        state = status['state']
        assert state
        return state

    def get_action_error_cause(self, action):
        assert 'status' in action
        status = action['status']
        assert status
        assert 'state' in status
        state = status['state']
        assert state == 'failed'
        assert 'error_cause' in status
        cause = status['error_cause']
        return cause

    def get_ask_action_value(self, action):
        assert 'status' in action
        status = action['status']
        assert status
        assert 'input_value' in status
        value = status['input_value']
        assert value
        return value

    def response(self):
        if self.last_action == -1:
            if self.direction == 'incoming':
                return RESPONSE_ANSWER
        else:
            call_action = self.actions[self.last_action]

            if 'originate' in call_action:
                action = call_action['originate']
                if self.get_action_state(action) == 'completed':
                    return RESPONSE_ASK_PLAY_INTRO_FALLBACK
            elif 'answer' in call_action:
                action = call_action['answer']
                if self.get_action_state(action) == 'completed':
                    return RESPONSE_ASK_PLAY_INTRO
                return RESPONSE_EMPTY
            elif 'ask' in call_action:
                action = call_action['ask']
                state = self.get_action_state(action)
                if state == 'completed':
                    input_value = self.get_ask_action_value(action)
                    if 'text' in input_value:
                        if input_value['text'] == INPUT_EMPTY:
                            return RESPONSE_ASK_PLAY_INTRO
                        if input_value['text'] == INPUT_RABBIT:
                            return RESPONSE_ASK_PLAY_RABBIT
                        if input_value['text'] == INPUT_RABBIT_RETRY:
                            return RESPONSE_ASK_PLAY_RABBIT_RETRY
                        if input_value['text'] == INPUT_CUSTOM:
                            return RESPONSE_ASK_PLAY_CUSTOM
                        if input_value['text'] == INPUT_CUSTOM_LVC:
                            return RESPONSE_ASK_PLAY_CUSTOM_LVC
                        if input_value['text'] == INPUT_ANY:
                            return RESPONSE_ASK_SPEAK_ANY
                        if input_value['text'] == INPUT_DTMF:
                            return RESPONSE_ASK_SPEAK_DTMF
                        if input_value['text'] == INPUT_MULTI_DTMF:
                            return RESPONSE_ASK_SPEAK_MULTI_DTMF
                        if input_value['text'] == DTMF_1234[7:]:
                            return RESPONSE_HOLD
                        if input_value['text'] == INPUT_FORWARD:
                            return RESPONSE_FORWARD
                        if input_value['text'] == INPUT_FORWARD_UID:
                            return RESPONSE_FORWARD_UID
                        if input_value['text'] == INPUT_DEFLECT:
                            return RESPONSE_DEFLECT
                        if input_value['text'] == INPUT_SWITCH:
                            return RESPONSE_SWITCH
                        if input_value['text'] == INPUT_CLOSE:
                            return RESPONSE_HANGUP
                        if input_value['text'] == INPUT_HOLD:
                            return RESPONSE_HOLD
                        if input_value['text'] == INPUT_SKIP_HOLDS:
                            return RESPONSE_SKIP_HOLDS
                        if input_value['text'] == INPUT_FALLBACK:
                            return None
                    if 'dtmf' in input_value:
                        if input_value['dtmf'] == -1:
                            return RESPONSE_HANGUP
                elif state == 'failed':
                    return RESPONSE_PLAY_ERROR
            elif 'forward' in call_action:
                action = call_action['forward']
                if self.get_action_state(action) == 'completed':
                    if action.get('use_deflect', False):
                        return RESPONSE_HANGUP
                    return RESPONSE_PLAY_RABBIT
                if self.get_action_state(action) == 'processing':
                    return RESPONSE_EMPTY
                if self.get_action_state(action) == 'failed':
                    cause = self.get_action_error_cause(action)
                    if 'DESTINATION' in cause:
                        return RESPONSE_FORWARD_BACKUP
                return RESPONSE_HANGUP

        return RESPONSE_HANGUP


# Tanya action results
OUTGOING_TANYA_INITIAL = {
    'session_id': SESSION_ID,
    'action_result': {
        'type': 'initial',
        'base_url': TANYA_BASE_URL,
        'direction': 'outbound',
    },
}
OUTGOING_TANYA_DIAL_OK = {
    'session_id': SESSION_ID,
    'action_result': {'status': 'OK', 'type': 'originate'},
    'action_id': ORIGINATE_ACTION_ID,
}
OUTGOING_TANYA_DIAL_ERROR = {
    'session_id': SESSION_ID,
    'action_result': {
        'type': 'originate',
        'status': 'ERROR',
        'ERROR': {'code': 'DESTINATION_NO_ANSWER'},
    },
    'action_id': ORIGINATE_ACTION_ID,
}
INCOMING_TANYA_INITIAL = {
    'session_id': SESSION_ID,
    'action_result': {
        'call_guid': CALL_GUID,
        'called_number': INBOUND_NUMBER,
        'caller_number': ABONENT_NUMBER,
        'origin_called_number': INBOUND_NUMBER,
        'base_url': 'http://tanya_url',
        'direction': 'inbound',
        'type': 'initial',
    },
}
INCOMING_TANYA_ANSWER_OK = {
    'session_id': SESSION_ID,
    'action_result': {'status': 'OK', 'type': 'answer'},
    'action_id': ANSWER_ACTION_ID,
}
INCOMING_TANYA_ANSWER_ERROR = {
    'session_id': SESSION_ID,
    'action_result': {
        'status': 'ERROR',
        'type': 'answer',
        'ERROR': {'code': 'OTHER_ERROR'},
    },
    'action_id': ANSWER_ACTION_ID,
}
TANYA_ASK_REPLY_RABBIT = {
    'session_id': SESSION_ID,
    'action_result': {
        'status': 'OK',
        'type': 'ask',
        'user_input': INPUT_RABBIT,
    },
    'action_id': ASK_INTRO_ID,
}
TANYA_ASK_REPLY_RABBIT_RETRY = {
    'session_id': SESSION_ID,
    'action_result': {
        'status': 'OK',
        'type': 'ask',
        'user_input': INPUT_RABBIT_RETRY,
    },
    'action_id': ASK_INTRO_ID,
}
TANYA_ASK_REPLY_ANY = {
    'session_id': SESSION_ID,
    'action_result': {'status': 'OK', 'type': 'ask', 'user_input': INPUT_ANY},
    'action_id': ASK_RABBIT_ID,
}
TANYA_ASK_REPLY_CUSTOM = {
    'session_id': SESSION_ID,
    'action_result': {
        'status': 'OK',
        'type': 'ask',
        'user_input': INPUT_CUSTOM,
    },
    'action_id': ASK_INTRO_ID,
}
TANYA_ASK_REPLY_CUSTOM_LVC = {
    'session_id': SESSION_ID,
    'action_result': {
        'status': 'OK',
        'type': 'ask',
        'user_input': INPUT_CUSTOM_LVC,
    },
    'action_id': ASK_CUSTOM_ID,
}
TANYA_ASK_REPLY_DTMF = {
    'session_id': SESSION_ID,
    'action_result': {'status': 'OK', 'type': 'ask', 'user_input': INPUT_DTMF},
    'action_id': ASK_INTRO_ID,
}
TANYA_ASK_REPLY_MULTI_DTMF = {
    'session_id': SESSION_ID,
    'action_result': {
        'status': 'OK',
        'type': 'ask',
        'user_input': INPUT_MULTI_DTMF,
    },
    'action_id': ASK_INTRO_ID,
}
TANYA_ASK_REPLY_CLOSE_ANY = {
    'session_id': SESSION_ID,
    'action_result': {
        'status': 'OK',
        'type': 'ask',
        'user_input': INPUT_CLOSE,
    },
    'action_id': ASK_ANY_ID,
}
TANYA_ASK_REPLY_CLOSE_INTRO = {
    'session_id': SESSION_ID,
    'action_result': {
        'status': 'OK',
        'type': 'ask',
        'user_input': INPUT_CLOSE,
    },
    'action_id': ASK_INTRO_ID,
}
TANYA_ASK_REPLY_HOLD = {
    'session_id': SESSION_ID,
    'action_result': {'status': 'OK', 'type': 'ask', 'user_input': INPUT_HOLD},
    'action_id': ASK_INTRO_ID,
}
TANYA_ASK_REPLY_SKIP_HOLDS = {
    'session_id': SESSION_ID,
    'action_result': {
        'status': 'OK',
        'type': 'ask',
        'user_input': INPUT_SKIP_HOLDS,
    },
    'action_id': ASK_INTRO_ID,
}
TANYA_ASK_REPLY_FORWARD_ANY = {
    'session_id': SESSION_ID,
    'action_result': {
        'status': 'OK',
        'type': 'ask',
        'user_input': INPUT_FORWARD,
    },
    'action_id': ASK_ANY_ID,
}
TANYA_ASK_REPLY_FORWARD_INTRO = {
    'session_id': SESSION_ID,
    'action_result': {
        'status': 'OK',
        'type': 'ask',
        'user_input': INPUT_FORWARD,
    },
    'action_id': ASK_INTRO_ID,
}
TANYA_ASK_REPLY_FORWARD_UID = {
    'session_id': SESSION_ID,
    'action_result': {
        'status': 'OK',
        'type': 'ask',
        'user_input': INPUT_FORWARD_UID,
    },
    'action_id': ASK_INTRO_ID,
}
TANYA_ASK_REPLY_DEFLECT_INTRO = {
    'session_id': SESSION_ID,
    'action_result': {
        'status': 'OK',
        'type': 'ask',
        'user_input': INPUT_DEFLECT,
    },
    'action_id': ASK_INTRO_ID,
}
TANYA_ASK_REPLY_SWITCH_INTRO = {
    'session_id': SESSION_ID,
    'action_result': {
        'status': 'OK',
        'type': 'ask',
        'user_input': INPUT_SWITCH,
    },
    'action_id': ASK_INTRO_ID,
}
TANYA_ASK_REPLY_FALLBACK = {
    'session_id': SESSION_ID,
    'action_result': {
        'status': 'OK',
        'type': 'ask',
        'user_input': INPUT_FALLBACK,
    },
    'action_id': ASK_INTRO_ID,
}
TANYA_ASK_USER_HANGUP = {
    'session_id': SESSION_ID,
    'action_result': {
        'error': {'code': 'ABONENT_HANGUP'},
        'status': 'ERROR',
        'type': 'ask',
    },
    'action_id': ASK_INTRO_ID,
}
TANYA_ASK_ERROR_RESULT = {
    'session_id': SESSION_ID,
    'action_result': {
        'error': {'code': 'RECOGNIZER_ERROR'},
        'status': 'ERROR',
        'type': 'ask',
    },
    'action_id': ASK_INTRO_ID,
}
TANYA_ASK_INTRO_RESULT_NO_INPUT = {
    'session_id': SESSION_ID,
    'action_result': {'status': 'OK', 'type': 'ask', 'user_input': ''},
    'action_id': ASK_INTRO_ID,
}
TANYA_ASK_DTMF_RESULT_NO_INPUT = {
    'session_id': SESSION_ID,
    'action_result': {'status': 'OK', 'type': 'ask', 'user_input': ''},
    'action_id': ASK_DTMF_ID,
}
TANYA_ASK_DTMF_RESULT_1234 = {
    'session_id': SESSION_ID,
    'action_result': {'status': 'OK', 'type': 'ask', 'user_input': DTMF_1234},
    'action_id': ASK_MULTI_DTMF_ID,
}
TANYA_PLAY_RABBIT_OK_RESULT = {
    'session_id': SESSION_ID,
    'action_result': {'status': 'OK', 'type': 'playback'},
    'action_id': PLAY_RABBIT_ACTION_ID,
}
TANYA_PLAY_ERROR_OK_RESULT = {
    'session_id': SESSION_ID,
    'action_result': {'status': 'OK', 'type': 'playback'},
    'action_id': PLAY_ERROR_ACTION_ID,
}
TANYA_PLAY_FALLBACK_OK_RESULT = {
    'session_id': SESSION_ID,
    'action_result': {'status': 'OK', 'type': 'playback'},
    'action_id': PLAY_FALLBACK_ACTION_ID,
}
TANYA_PLAY_OK_RESULT = {'type': 'playback', 'status': 'OK'}
TANYA_BRIDGE_EVENT = {
    'session_id': SESSION_ID,
    'action_result': {
        'transferee_id': LEG_ID,
        'status': 'OK',
        'event_type': 'BRIDGE_SUCCESS',
        'type': 'channel_event',
    },
    'action_id': FORWARD_ACTION_ID,
}
TANYA_BRIDGE_EVENT_BACKUP = {
    'session_id': SESSION_ID,
    'action_result': {
        'transferee_id': LEG_ID,
        'status': 'OK',
        'event_type': 'BRIDGE_SUCCESS',
        'type': 'channel_event',
    },
    'action_id': FORWARD_BACKUP_ACTION_ID,
}
TANYA_OLD_STYLE_FORWARDING_RESULT_OK = {
    'session_id': SESSION_ID,
    'action_result': {
        'transferee_id': LEG_ID,
        'status': 'OK',
        'type': 'forward',
    },
    'action_id': FORWARD_ACTION_ID,
}
TANYA_FORWARDING_RESULT_INITIATOR_HUP = {
    'session_id': SESSION_ID,
    'action_result': {
        'transferee_id': LEG_ID,
        'status': 'OK',
        'disconnect_side': 'initiator',
        'type': 'forward',
    },
    'action_id': FORWARD_ACTION_ID,
}
TANYA_FORWARDING_RESULT_DEFLECT = {
    'session_id': SESSION_ID,
    'action_result': {
        'transferee_id': LEG_ID,
        'status': 'OK',
        'disconnect_side': 'deflect',
        'type': 'forward',
    },
    'action_id': FORWARD_ACTION_ID,
}
TANYA_FORWARDING_RESULT_TRANSFEREE_HUP = {
    'session_id': SESSION_ID,
    'action_result': {
        'transferee_id': LEG_ID,
        'status': 'OK',
        'disconnect_side': 'transferee',
        'type': 'forward',
    },
    'action_id': FORWARD_ACTION_ID,
}
TANYA_FORWARDING_RESULT_ERROR_ABONENT_HANGUP = {
    'session_id': SESSION_ID,
    'action_result': {
        'transferee_id': LEG_ID,
        'status': 'ERROR',
        'type': 'forward',
        'error': {'code': 'ABONENT_HANGUP'},
    },
    'action_id': FORWARD_ACTION_ID,
}
TANYA_FORWARDING_RESULT_ERROR_TRANSFEREE_NO_ANSWER = {
    'session_id': SESSION_ID,
    'action_result': {
        'transferee_id': LEG_ID,
        'status': 'ERROR',
        'type': 'forward',
        'error': {'code': 'DESTINATION_NO_ANSWER'},
    },
    'action_id': FORWARD_ACTION_ID,
}

# Dispatcher replies
OUTGOING_DISPATCHER_DIAL = {
    'action': {
        'type': 'originate',
        'params': {
            'answer_timeout': NO_ANSWER_TO,
            'call_external_id': CALL_ID,
            'call_guid': CALL_GUID,
            'call_from': OUTBOUND_NUMBER,
            'call_to': ABONENT_NUMBER,
            'distributor': OUTBOUND_GW,
            'enable_recording': RECORD_CALL,
            'use_deflect': USE_DEFLECT,
        },
    },
    'action_id': ORIGINATE_ACTION_ID,
}
OUTGOING_DISPATCHER_DIAL_X_ROUTE = {
    'action': {
        'type': 'originate',
        'params': {
            'answer_timeout': NO_ANSWER_TO,
            'call_external_id': CALL_ID,
            'call_guid': CALL_GUID,
            'call_from': OUTBOUND_NUMBER,
            'call_to': ABONENT_NUMBER,
            'distributor': OUTBOUND_GW,
            'x_route': OUTBOUND_X_ROUTE,
            'enable_recording': RECORD_CALL,
            'use_deflect': USE_DEFLECT,
        },
    },
    'action_id': ORIGINATE_ACTION_ID,
}
INCOMING_DISPATCHER_ANSWER = {
    'action': {'type': 'answer', 'params': {'enable_recording': RECORD_CALL}},
    'action_id': ANSWER_ACTION_ID,
}
DISPATCHER_ASK_PLAY_INTRO = {
    'action': {
        'type': 'ask',
        'params': {
            'play': {'prompt_url': INTRO_FILE_PATH},
            'asr_config': {
                'engine': 'ya_speechkit',
                'language_code': ASR_LANG_CODE,
                'model': 'general',
                'max_response_duration_ms': DEFAULT_MRD,
            },
            'immediate_input': DEFAULT_SIT,
            'no_input_timeout_ms': DEFAULT_NIT,
        },
    },
    'action_id': ASK_INTRO_ID,
}
DISPATCHER_ASK_PLAY_RABBIT = {
    'action': {
        'type': 'ask',
        'params': {
            'play': {'prompt_url': RABBIT_FILE_PATH},
            'asr_config': {
                'engine': 'ya_speechkit',
                'language_code': ASR_LANG_CODE,
                'model': ASR_MODEL,
                'max_response_duration_ms': DEFAULT_MRD,
            },
            'immediate_input': DEFAULT_SIT,
            'no_input_timeout_ms': DEFAULT_NIT,
        },
    },
    'action_id': ASK_RABBIT_ID,
}
DISPATCHER_ASK_PLAY_CUSTOM = {
    'action': {
        'type': 'ask',
        'params': {
            'play': {'prompt_url': RABBIT_FILE_PATH},
            'asr_config': {
                'engine': 'ya_speechkit',
                'language_code': ASR_LANG_CODE,
                'model': ASR_MODEL,
                'max_response_duration_ms': CUSTOM_MRD,
            },
            'immediate_input': DEFAULT_SIT,
            'no_input_timeout_ms': DEFAULT_NIT,
        },
    },
    'action_id': ASK_CUSTOM_ID,
}
DISPATCHER_ASK_PLAY_CUSTOM_LVC = {
    'action': {
        'type': 'ask',
        'params': {
            'play': {'prompt_url': RABBIT_FILE_PATH},
            'asr_config': {
                'engine': 'ya_speechkit',
                'language_code': ASR_LANG_CODE,
                'model': ASR_MODEL,
                'max_response_duration_ms': CUSTOM_ST,
                'local_vad_config': VAD_CONFIG_CUSTOM_TANYA,
            },
            'immediate_input': DEFAULT_SIT,
            'no_input_timeout_ms': DEFAULT_NIT,
        },
    },
    'action_id': ASK_CUSTOM_LVC_ID,
}
DISPATCHER_ASK_SPEAK_SAID_ANY = {
    'action': {
        'type': 'ask',
        'params': {
            'speak': {
                'text': f'{ML_SAID} {INPUT_ANY}',
                'tts_config': {
                    'voice': TTS_VOICE,
                    'engine': 'ya_speechkit',
                    'language': TTS_LANG,
                    'speed': TTS_SPEED,
                    'use_grpc': TTS_GRPC,
                },
            },
            'asr_config': {
                'engine': 'ya_speechkit',
                'language_code': ASR_LANG_CODE,
                'model': ASR_MODEL,
                'max_response_duration_ms': DEFAULT_MRD,
            },
            'immediate_input': DEFAULT_SIT,
            'no_input_timeout_ms': DEFAULT_NIT,
        },
    },
    'action_id': ASK_ANY_ID,
}
DISPATCHER_ASK_SPEAK_SAID_DTMF = {
    'action': {
        'type': 'ask',
        'params': {
            'speak': {
                'text': f'{ML_SAID} {INPUT_DTMF}',
                'tts_config': {
                    'voice': TTS_VOICE,
                    'engine': 'ya_speechkit',
                    'language': TTS_LANG,
                    'speed': TTS_SPEED,
                    'use_grpc': TTS_GRPC,
                },
            },
            'dtmf_config': {
                'min_digits': 1,
                'max_digits': 1,
                'interdigit_timeout_ms': DEFAULT_NIT,
                'allowed_dtmf': 'any',
            },
            'immediate_input': DEFAULT_SIT,
            'no_input_timeout_ms': DEFAULT_NIT,
        },
    },
    'action_id': ASK_DTMF_ID,
}
DISPATCHER_ASK_SPEAK_SAID_MULTI_DTMF = {
    'action': {
        'type': 'ask',
        'params': {
            'speak': {
                'text': f'{ML_SAID} {INPUT_MULTI_DTMF}',
                'tts_config': {
                    'voice': TTS_VOICE,
                    'engine': 'ya_speechkit',
                    'language': TTS_LANG,
                    'speed': TTS_SPEED,
                    'use_grpc': TTS_GRPC,
                },
            },
            'dtmf_config': {
                'min_digits': 4,
                'max_digits': 5,
                'interdigit_timeout_ms': CUSTOM_NIT,
                'allowed_dtmf': 'any',
            },
            'immediate_input': DEFAULT_SIT,
            'no_input_timeout_ms': DEFAULT_NIT,
        },
    },
    'action_id': ASK_MULTI_DTMF_ID,
}
DISPATCHER_ASK_HELLO_REPLY = {
    'action': {
        'type': 'ask',
        'params': {
            'play': {'prompt_url': HELLO_REPLY_PATH},
            'asr_config': {
                'engine': 'ya_speechkit',
                'language_code': ASR_LANG_CODE,
                'model': ASR_MODEL,
                'max_response_duration_ms': DEFAULT_MRD,
            },
            'dtmf_config': {
                'min_digits': 1,
                'max_digits': 1,
                'interdigit_timeout_ms': DEFAULT_NIT,
                'allowed_dtmf': 'any',
            },
            'immediate_input': DEFAULT_SIT,
            'no_input_timeout_ms': DEFAULT_NIT,
        },
    },
    'action_id': HELLO_REPLY_ID,
}
DISPATCHER_PLAY_BYE_REPLY = {
    'action': {
        'type': 'playback',
        'params': {'play': {'prompt_url': BYE_REPLY_PATH}},
    },
    'action_id': BYE_REPLY_ID,
}
PLAYBACK_FLOW_PLAY_REPLY = {
    'action': {
        'type': 'playback',
        'params': {'play': {'prompt_url': PROMPT_PATH}},
    },
    'action_id': PLAYBACK_ID,
}
DISPATCHER_PLAY_ERROR_PROMPT = {
    'action': {
        'type': 'playback',
        'params': {'play': {'prompt_url': ERROR_FILE_PATH}},
    },
    'action_id': PLAY_ERROR_ACTION_ID,
}
DISPATCHER_PLAY_RABBIT_PROMPT = {
    'action': {
        'type': 'playback',
        'params': {'play': {'prompt_url': RABBIT_FILE_PATH}},
    },
    'action_id': PLAY_RABBIT_ACTION_ID,
}
DISPATCHER_PLAY_FALLBACK_PROMPT = {
    'action': {
        'type': 'playback',
        'params': {'play': {'prompt_url': FALLB_FILE_PATH}},
    },
    'action_id': PLAY_FALLBACK_ACTION_ID,
}
DISPATCHER_FORWARD_REPLY = {
    'action': {
        'type': 'forward',
        'params': {
            'call_guid': CALL_GUID,
            'call_external_id': CALL_ID,
            'answer_timeout': NO_ANSWER_TO,
            'call_from': OUTBOUND_NUMBER,
            'call_to': FORWARD_NUMBER,
            'distributor': OUTBOUND_GW,
            'use_deflect': USE_DEFLECT,
            'leg_id': LEG_ID,
        },
    },
    'action_id': FORWARD_ACTION_ID,
}
DISPATCHER_INCOMING_FORWARD_REPLY = {
    'action': {
        'type': 'forward',
        'params': {
            'call_guid': CALL_GUID,
            'call_external_id': CALL_GUID,
            'answer_timeout': NO_ANSWER_TO,
            'call_from': OUTBOUND_NUMBER,
            'call_to': FORWARD_NUMBER,
            'distributor': OUTBOUND_GW,
            'use_deflect': USE_DEFLECT,
            'leg_id': LEG_ID,
        },
    },
    'action_id': FORWARD_ACTION_ID,
}
DISPATCHER_DEFLECT_REPLY = {
    'action': {
        'type': 'forward',
        'params': {
            'call_guid': CALL_GUID,
            'call_external_id': CALL_GUID,
            'answer_timeout': NO_ANSWER_TO,
            'call_from': OUTBOUND_NUMBER,
            'call_to': FORWARD_NUMBER,
            'distributor': OUTBOUND_GW,
            'use_deflect': True,
            'leg_id': LEG_ID,
        },
    },
    'action_id': FORWARD_ACTION_ID,
}
DISPATCHER_FORWARD_BACKUP_REPLY = {
    'action': {
        'type': 'forward',
        'params': {
            'call_guid': CALL_GUID,
            'call_external_id': CALL_ID,
            'answer_timeout': NO_ANSWER_TO,
            'call_from': OUTBOUND_NUMBER,
            'call_to': FORWARD_BACKUP_NUMBER,
            'distributor': OUTBOUND_GW,
            'use_deflect': USE_DEFLECT,
            'leg_id': LEG_ID,
        },
    },
    'action_id': FORWARD_BACKUP_ACTION_ID,
}
DISPATCHER_INCOMING_FORWARD_BACKUP_REPLY = {
    'action': {
        'type': 'forward',
        'params': {
            'call_guid': CALL_GUID,
            'call_external_id': CALL_GUID,
            'answer_timeout': NO_ANSWER_TO,
            'call_from': OUTBOUND_NUMBER,
            'call_to': FORWARD_BACKUP_NUMBER,
            'distributor': OUTBOUND_GW,
            'use_deflect': USE_DEFLECT,
            'leg_id': LEG_ID,
        },
    },
    'action_id': FORWARD_BACKUP_ACTION_ID,
}
DISPATCHER_FORWARD_UID_REPLY = {
    'action': {
        'type': 'forward',
        'params': {
            'call_guid': CALL_GUID,
            'call_external_id': CALL_ID,
            'answer_timeout': NO_ANSWER_TO,
            'call_from': ABONENT_NUMBER,
            'call_to': FORWARD_AGENT_ID,
            'distributor': OPERATOR_GW,
            'use_deflect': USE_DEFLECT,
            'enable_provision': ENABLE_PROVISION,
            'leg_id': LEG_ID,
        },
    },
    'action_id': FORWARD_ACTION_ID,
}
DISPATCHER_FORWARD_UID_REPLY_X_ROUTE = {
    'action': {
        'type': 'forward',
        'params': {
            'call_guid': CALL_GUID,
            'call_external_id': CALL_ID,
            'answer_timeout': NO_ANSWER_TO,
            'call_from': ABONENT_NUMBER,
            'call_to': FORWARD_AGENT_ID,
            'distributor': OPERATOR_GW,
            'x_route': OPERATOR_X_ROUTE,
            'use_deflect': USE_DEFLECT,
            'enable_provision': ENABLE_PROVISION,
            'leg_id': LEG_ID,
        },
    },
    'action_id': FORWARD_ACTION_ID,
}
DISPATCHER_INCOMING_FORWARD_UID_REPLY = {
    'action': {
        'type': 'forward',
        'params': {
            'call_guid': CALL_GUID,
            'call_external_id': CALL_GUID,
            'answer_timeout': NO_ANSWER_TO,
            'call_from': ABONENT_NUMBER,
            'call_to': FORWARD_AGENT_ID,
            'distributor': OPERATOR_GW,
            'use_deflect': USE_DEFLECT,
            'enable_provision': ENABLE_PROVISION,
            'leg_id': LEG_ID,
        },
    },
    'action_id': FORWARD_ACTION_ID,
}
DISPATCHER_HOLD = {'action': {'type': 'hold'}, 'action_id': HOLD_ACTION_ID}
DISPATCHER_HANGUP = {
    'action': {'type': 'hangup', 'params': {'cause': 'NORMAL_CALL_CLEARING'}},
    'action_id': HANGUP_ACTION_ID,
}
DISPATCHER_FINISHED_HANGUP = {
    'action': {'type': 'hangup', 'params': {'cause': 'NORMAL_CALL_CLEARING'}},
}
DISPATCHER_FALLBACK_HANGUP = {
    'action': {'type': 'hangup', 'params': {'cause': 'NORMAL_CALL_CLEARING'}},
    'action_id': HANGUP_FALLBACK_ACTION_ID,
}
DISPATCHER_EMPTY_REPLY = {'action': {'type': 'empty'}}

# Context
INITIAL_CONTEXT_VALUES = {
    'string': 'test',
    'numeric': 2.5,
    'int': 0,
    'bool': True,
}
RESPONSE_CONTEXT_VALUES = {'string': 'test2'}

ORIGINATE_ACTION = {
    'external_id': ORIGINATE_ACTION_ID,
    'originate': {
        'phone_number': ABONENT_NUMBER,
        'outbound_number': OUTBOUND_NUMBER,
    },
}
ANSWER_ACTION = {'external_id': ANSWER_ACTION_ID, 'answer': {}}
HANGUP_ACTION = {'external_id': HANGUP_ACTION_ID, 'hangup': {}}
HOLD_ACTION = {'external_id': HOLD_ACTION_ID, 'hold': {}}
HOLD_ACTION1 = {'external_id': HOLD_ACTION_ID + '-1', 'hold': {}}
HOLD_ACTION2 = {'external_id': HOLD_ACTION_ID + '-2', 'hold': {}}
FORWARD_ACTION = {
    'external_id': FORWARD_ACTION_ID,
    'forward': {'phone_number': FORWARD_NUMBER},
}
FORWARD_BACKUP_ACTION = {
    'external_id': FORWARD_BACKUP_ACTION_ID,
    'forward': {'phone_number': FORWARD_BACKUP_NUMBER},
}
FORWARD_UID_ACTION = {
    'external_id': FORWARD_ACTION_ID,
    'forward': {
        'yandex_uid': FORWARD_YANDEX_UID,
        'route': ROUTE_CC_OPERATORS,
        'outbound_number': ABONENT_NUMBER,
        'enable_provision': ENABLE_PROVISION,
    },
}
DEFLECT_ACTION = {
    'external_id': FORWARD_ACTION_ID,
    'forward': {'phone_number': FORWARD_NUMBER, 'use_deflect': True},
}
SWITCH_ACTION = {
    'external_id': SWITCH_ACTION_ID,
    'switch': {
        'phone_number': SWITCH_NUMBER,
        'mode': 'transient',
        'args': {'switch_to_csat': True},
    },
}

PLAY_INTRO = {
    'external_id': PLAY_INTRO_ACTION_ID,
    'playback': {'playback': {'play': {'id': INTRO_FILE_ID}}},
}
PLAY_RABBIT = {
    'external_id': PLAY_RABBIT_ACTION_ID,
    'playback': {'playback': {'play': {'id': RABBIT_FILE_ID}}},
}
PLAY_ERROR = {
    'external_id': PLAY_ERROR_ACTION_ID,
    'playback': {'playback': {'play': {'id': ERROR_FILE_ID}}},
}
ASK_PLAY_INTRO = {
    'external_id': ASK_INTRO_ID,
    'ask': {'playback': {'play': {'id': INTRO_FILE_ID}}, 'input_mode': 'text'},
}
ASK_PLAY_RABBIT = {
    'external_id': ASK_RABBIT_ID,
    'ask': {
        'playback': {'play': {'id': RABBIT_FILE_ID}},
        'input_mode': 'text',
    },
}
ASK_PLAY_CUSTOM = {
    'external_id': ASK_CUSTOM_ID,
    'ask': {
        'playback': {'play': {'id': RABBIT_FILE_ID}},
        'input_mode': 'text',
        'max_response_duration_ms': CUSTOM_MRD,
    },
}
ASK_PLAY_CUSTOM_LVC = {
    'external_id': ASK_CUSTOM_LVC_ID,
    'ask': {
        'playback': {'play': {'id': RABBIT_FILE_ID}},
        'input_mode': 'text',
        'no_local_vad': False,
        'local_vad_config': VAD_CONFIG_CUSTOM,
    },
}
ASK_SPEAK_ANY = {
    'external_id': ASK_ANY_ID,
    'ask': {
        'playback': {'speak': {'text': f'{ML_SAID} {INPUT_ANY}'}},
        'input_mode': 'text',
    },
}
ASK_SPEAK_DTMF = {
    'external_id': ASK_DTMF_ID,
    'ask': {
        'playback': {'speak': {'text': f'{ML_SAID} {INPUT_DTMF}'}},
        'input_mode': 'dtmf',
    },
}
ASK_SPEAK_MULTI_DTMF = {
    'external_id': ASK_MULTI_DTMF_ID,
    'ask': {
        'playback': {'speak': {'text': f'{ML_SAID} {INPUT_MULTI_DTMF}'}},
        'input_mode': 'dtmf',
        'dtmf_config': {
            'min_digits': 4,
            'max_digits': 5,
            'interdigit_timeout_ms': CUSTOM_NIT,
        },
    },
}

CONTEXT_ORIGINATE_ACTION = {
    'external_id': ORIGINATE_ACTION_ID,
    'type': 'originate',
    'originate': {'phone_number': ABONENT_NUMBER},
}
CONTEXT_FALLBACK_PLAYBACK_ACTION = {
    'external_id': PLAY_FALLBACK_ACTION_ID,
    'type': 'playback',
    'playback': {'playback': {'play': {'id': FALLB_FILE_ID}}},
}
CONTEXT_FALLBACK_HANGUP_ACTION = {
    'external_id': HANGUP_FALLBACK_ACTION_ID,
    'type': 'hangup',
    'hangup': {'cause': 'normal-clearing'},
}
NEW_CONTEXT = {
    '_id': SESSION_ID,
    'context': {
        'call_flow_id': CALL_FLOW_ID,
        'flow_id': FLOW_ID,
        'call_id': CALL_ID,
        'call_guid': CALL_GUID,
        'service_number': OUTBOUND_NUMBER,
        'abonent_number': ABONENT_NUMBER,
        'abonent_phone_id': CALLED_PD_ID,
        'actions': [CONTEXT_ORIGINATE_ACTION],
        'fallback_actions': [
            CONTEXT_FALLBACK_PLAYBACK_ACTION,
            CONTEXT_FALLBACK_HANGUP_ACTION,
        ],
        'direction': OUTGOING_CALL,
        'call_answered': False,
        'call_finished': False,
        'waiting_event': False,
        'current_action': 0,
        'client_context': CLIENT_CONTEXT,
    },
    'created': '2020-07-20T15:10:00+0300',
    'version': 1,
    'worker_id': WORKER_ID,
}

# Client responses
RESPONSE_ORIGINATE = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [ORIGINATE_ACTION],
}
RESPONSE_ANSWER = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [ANSWER_ACTION],
}
RESPONSE_ASK_PLAY_INTRO = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [ASK_PLAY_INTRO],
}
RESPONSE_ASK_PLAY_INTRO_FALLBACK = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [ASK_PLAY_INTRO],
    'fallback_actions': [FALLBACK_PLAYBACK_ACTION, FALLBACK_HANGUP_ACTION],
}
RESPONSE_ASK_PLAY_RABBIT = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [ASK_PLAY_RABBIT],
}
RESPONSE_ASK_PLAY_RABBIT_RETRY = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [PLAY_RABBIT, ASK_PLAY_RABBIT],
}
RESPONSE_ASK_PLAY_CUSTOM = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [ASK_PLAY_CUSTOM],
}
RESPONSE_ASK_PLAY_CUSTOM_LVC = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [ASK_PLAY_CUSTOM_LVC],
}
RESPONSE_ASK_SPEAK_ANY = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [ASK_SPEAK_ANY],
}
RESPONSE_ASK_SPEAK_DTMF = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [ASK_SPEAK_DTMF],
}
RESPONSE_ASK_SPEAK_MULTI_DTMF = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [ASK_SPEAK_MULTI_DTMF],
}
RESPONSE_PLAY_ERROR = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [PLAY_ERROR],
}
RESPONSE_PLAY_RABBIT = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [PLAY_RABBIT],
}
RESPONSE_FORWARD = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [FORWARD_ACTION],
}
RESPONSE_FORWARD_BACKUP = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [FORWARD_BACKUP_ACTION],
}
RESPONSE_FORWARD_UID = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [FORWARD_UID_ACTION],
}
RESPONSE_DEFLECT = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [DEFLECT_ACTION],
}
RESPONSE_SWITCH = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [SWITCH_ACTION],
}
RESPONSE_HANGUP = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [HANGUP_ACTION],
}
RESPONSE_HOLD = {'context': RESPONSE_CONTEXT_VALUES, 'actions': [HOLD_ACTION]}
RESPONSE_SKIP_HOLDS = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [PLAY_RABBIT, HOLD_ACTION1, HOLD_ACTION2, ASK_SPEAK_ANY],
}
RESPONSE_EMPTY = {'context': RESPONSE_CONTEXT_VALUES}
