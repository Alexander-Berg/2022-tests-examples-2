WORKER_ID = 'ivr_flow_worker'
CALL_FLOW_ID = 'xT5n4mO/QeOa53FxYJOJnAqzE3E='
FLOW_ID = 'test_project'
CALL_ID = 'cw-test-call-id'
CALL_GUID = ''
INCOMING_CALL = 'incoming'
OUTGOING_CALL = 'outgoing'
BASE_URL = {'$mockserver': ''}
TVM_NAME = 'callcenter-qa'
INBOUND_NUMBER = '+79999999999'
ABONENT_NUMBER = '+74959999999'
CALLED_PD_ID = '+74959999999_id'
FORWARD_NUMBER = '+74989999999'
FORWARD_YANDEX_UID = '1001'
FORWARD_AGENT_ID = '111'
FORWARD_SEND_EVENTS = True
OUTBOUND_NUMBER = '+79999999999'
ROUTE_CC_OPERATORS = 'cc_operators'
OUTBOUND_GW = 'ivr_via_noc'
OPERATOR_GW = 'operators'
NO_ANSWER_TO = 100500
PROGRESS_TO = NO_ANSWER_TO
RECORD_CALL = True

TTS_LANG = 'ru-RU'
TTS_VOICE = 'alena'
TTS_SPEED = 1.3
TTS_GRPC = True

ASR_LANG_CODE = 'ru-ru'
ASR_MODEL = 'general'

DEFAULT_NIT = 4000
DEFAULT_SIT = False
DEFAULT_NLV = False
DEFAULT_VT = 40
DEFAULT_VV = 20
DEFAULT_VS = 20
DEFAULT_SCT = 1000
DEFAULT_ST = 10000

SESSION_ID = 'cw-test-call-id'
INTRO_FILE = 'intro'
RABBIT_FILE = 'rabbit'
ERROR_FILE = 'error'
FALLBACK_FILE = 'fallback'
ML_SAID = 'вы сказали'
INPUT_RABBIT = 'про заек'
INPUT_ANY = 'трололо'
INPUT_CLOSE = 'close'
INPUT_FORWARD = 'switch'
INPUT_FORWARD_UID = 'switch_to_uid'
INPUT_EMPTY = ''
INPUT_DTMF = 'dtmf'
INPUT_HOLD = 'hold'
INPUT_SKIP_HOLDS = 'skip_hold'
INPUT_FALLBACK = 'fallback'

ORIGINATE_ACTION_ID = 'originate-action-id'
ANSWER_ACTION_ID = 'answer-action-id'
HANGUP_ACTION_ID = 'hangup-action-id'
HANGUP_FALLBACK_ACTION_ID = 'hangup-fallback-action-id'
HOLD_ACTION_ID = 'hold-action-id'
FORWARD_ACTION_ID = 'forward-action-id'
PLAY_INTRO_ACTION_ID = 'play-intro-action-id'
PLAY_RABBIT_ACTION_ID = 'play-rabbit-action-id'
PLAY_ERROR_ACTION_ID = 'play-error-action-id'
PLAY_FALLBACK_ACTION_ID = 'play-fallback-action-id'
ASK_INTRO_ID = 'intro-id'
ASK_RABBIT_ID = 'rabbit-id'
ASK_ANY_ID = 'any-id'
ASK_DTMF_ID = 'any-id'
ASK_FALLBACK_ID = 'fallback-id'

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

FALLBACK_PLAYBACK_ACTION = {
    'external_id': PLAY_FALLBACK_ACTION_ID,
    'playback': {'playback': {'play': {'id': FALLBACK_FILE}}},
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
    'immediate_input': DEFAULT_SIT,
    'asr_config': ASR_CONFIG,
    'no_local_vad': DEFAULT_NLV,
    'local_vad_config': VAD_CONFIG,
    'forward_bridge_notify': FORWARD_SEND_EVENTS,
    'dispatcher_fallback_actions': [
        FALLBACK_PLAYBACK_ACTION,
        FALLBACK_HANGUP_ACTION,
    ],
}

IVR_FRAMEWORK_FLOW_CONFIG = {FLOW_ID: FLOW_CONFIG}

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
                    return RESPONSE_ASK_INTRO_FALLBACK
            elif 'answer' in call_action:
                action = call_action['answer']
                if self.get_action_state(action) == 'completed':
                    return RESPONSE_ASK_INTRO
            elif 'ask' in call_action:
                action = call_action['ask']
                state = self.get_action_state(action)
                if state == 'completed':
                    input_value = self.get_ask_action_value(action)
                    if 'text' in input_value:
                        if input_value['text'] == INPUT_EMPTY:
                            return RESPONSE_ASK_INTRO
                        if input_value['text'] == INPUT_RABBIT:
                            return RESPONSE_ASK_RABBIT
                        if input_value['text'] == INPUT_ANY:
                            return RESPONSE_ASK_ANY
                        if input_value['text'] == INPUT_DTMF:
                            return RESPONSE_ASK_DTMF
                        if input_value['text'] == INPUT_FORWARD:
                            return RESPONSE_FORWARD
                        if input_value['text'] == INPUT_FORWARD_UID:
                            return RESPONSE_FORWARD_UID
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
                if self.get_action_state(action) == 'processing':
                    return RESPONSE_EMPTY
                if self.get_action_state(action) == 'completed':
                    return RESPONSE_PLAY_RABBIT
            elif 'hold' in call_action:
                action = call_action['hold']
                if self.get_action_state(action) == 'processing':
                    return RESPONSE_EMPTY

        return RESPONSE_HANGUP


# Octonode action results
OUTGOING_OCTONODE_INITIAL = {
    'brand': None,
    'call_guid': None,
    'origin_called_number': None,
    'status': 'ok',
    'type': 'initial',
}
OUTGOING_OCTONODE_INITIAL_ERROR = {
    'error_cause': 'badaboom!',
    'status': 'error',
    'type': 'initial',
}
INCOMING_OCTONODE_INITIAL = {
    'brand': None,
    'call_guid': None,
    'called_number': INBOUND_NUMBER,
    'caller_number': ABONENT_NUMBER,
    'origin_called_number': INBOUND_NUMBER,
    'status': 'ok',
    'type': 'initial',
}
INCOMING_OCTONODE_INITIAL_ERROR = {
    'called_number': INBOUND_NUMBER,
    'caller_number': ABONENT_NUMBER,
    'origin_called_number': INBOUND_NUMBER,
    'error_cause': 'badaboom!',
    'status': 'error',
    'type': 'initial',
}
OUTGOING_OCTONODE_DIAL_OK = {'status': 'ok', 'type': 'originate'}
OUTGOING_OCTONODE_DIAL_ERROR = {
    'error_cause': 'leg_hangup (CALL_REJECTED)',
    'status': 'error',
    'type': 'originate',
}
INCOMING_OCTONODE_DIAL_OK = {'status': 'ok', 'type': 'answer'}
INCOMING_OCTONODE_DIAL_ERROR = {
    'error_cause': 'leg_hangup (CALL_REJECTED)',
    'status': 'error',
    'type': 'answer',
}
OCTONODE_ASK_REPLY_RABBIT = {
    'error_cause': None,
    'status': 'ok',
    'type': 'ask',
    'user_input': INPUT_RABBIT,
}
OCTONODE_ASK_REPLY_ANY = {
    'error_cause': None,
    'status': 'ok',
    'type': 'ask',
    'user_input': INPUT_ANY,
}
OCTONODE_ASK_REPLY_DTMF = {
    'error_cause': None,
    'status': 'ok',
    'type': 'ask',
    'user_input': INPUT_DTMF,
}
OCTONODE_ASK_REPLY_CLOSE = {
    'error_cause': None,
    'status': 'ok',
    'type': 'ask',
    'user_input': INPUT_CLOSE,
}
OCTONODE_ASK_REPLY_HOLD = {
    'error_cause': None,
    'status': 'ok',
    'type': 'ask',
    'user_input': INPUT_HOLD,
}
OCTONODE_ASK_REPLY_SKIP_HOLDS = {
    'error_cause': None,
    'status': 'ok',
    'type': 'ask',
    'user_input': INPUT_SKIP_HOLDS,
}
OCTONODE_ASK_REPLY_FORWARD = {
    'error_cause': None,
    'status': 'ok',
    'type': 'ask',
    'user_input': INPUT_FORWARD,
}
OCTONODE_ASK_REPLY_FORWARD_UID = {
    'error_cause': None,
    'status': 'ok',
    'type': 'ask',
    'user_input': INPUT_FORWARD_UID,
}
OCTONODE_ASK_REPLY_FALLBACK = {
    'error_cause': None,
    'status': 'ok',
    'type': 'ask',
    'user_input': INPUT_FALLBACK,
}
OCTONODE_ASK_USER_HANGUP = {
    'error_cause': 'initiator_hangup',
    'status': 'error',
    'type': 'ask',
}
OCTONODE_ASK_ERROR_RESULT = {
    'error_cause': 'some_error',
    'status': 'error',
    'type': 'ask',
}
OCTONODE_ASK_RESULT_002 = {
    'error_cause': 'Completion-Cause:002',
    'status': 'error',
    'type': 'ask',
    'user_input': None,
}
OCTONODE_ASK_RESULT_DTMF = {
    'error_cause': None,
    'status': 'ok',
    'type': 'input',
    'numbers': None,
}
OCTONODE_PLAY_OK_RESULT = {'status': 'ok', 'type': 'play'}
OCTONODE_HOLD_OK_RESULT = {'status': 'ok', 'type': 'hold'}
OCTONODE_FORWARDING_BRIDGE_SUCCESS = {
    'status': 'ok',
    'type': 'channel_event',
    'event_type': 'BRIDGE_SUCCESS',
}
OCTONODE_OLD_STYLE_FORWARDING_RESULT_OK = {'status': 'ok', 'type': 'switch'}
OCTONODE_FORWARDING_RESULT_INITIATOR_HUP = {
    'status': 'ok',
    'disconnect_side': 'initiator',
    'type': 'switch',
}
OCTONODE_FORWARDING_RESULT_TRANSFEREE_HUP = {
    'status': 'ok',
    'disconnect_side': 'transferee',
    'type': 'switch',
}
OCTONODE_FORWARDING_RESULT_ERROR = {
    'status': 'error',
    'type': 'switch',
    'error_cause': 'n/a',
}

# Dispatcher replies
OUTGOING_DISPATCHER_DIAL = {
    'params': {
        'answer_timeout': NO_ANSWER_TO,
        'call_from': OUTBOUND_NUMBER,
        'call_to': ABONENT_NUMBER,
        'gateways': OUTBOUND_GW,
        'start_recording': RECORD_CALL,
    },
    'type': 'originate',
}
INCOMING_DISPATCHER_DIAL = {
    'params': {'start_recording': RECORD_CALL},
    'type': 'answer',
}
DISPATCHER_ASK_PLAY_INTRO = {
    'params': {
        'allowed_dtmf': 'any',
        'engine': 'ya_speechkit',
        'language': TTS_LANG,
        'relative_path': f'{WORKER_ID}/{FLOW_ID}/{INTRO_FILE}.wav',
        'no-input-timeout-ms': DEFAULT_NIT,
        'no-local-vad': DEFAULT_NLV,
        'speech-complete-timeout-ms': DEFAULT_SCT,
        'speech-timeout-ms': DEFAULT_ST,
        'start-input-timers': DEFAULT_SIT,
        'vad-silence-ms': DEFAULT_VS,
        'vad-threshold': DEFAULT_VT,
        'vad-voice-ms': DEFAULT_VV,
    },
    'type': 'ask',
}
DISPATCHER_ASK_PLAY_RABBIT = {
    'params': {
        'allowed_dtmf': 'any',
        'engine': 'ya_speechkit',
        'language': TTS_LANG,
        'relative_path': f'{WORKER_ID}/{FLOW_ID}/{RABBIT_FILE}.wav',
        'no-input-timeout-ms': DEFAULT_NIT,
        'no-local-vad': DEFAULT_NLV,
        'speech-complete-timeout-ms': DEFAULT_SCT,
        'speech-timeout-ms': DEFAULT_ST,
        'start-input-timers': DEFAULT_SIT,
        'vad-silence-ms': DEFAULT_VS,
        'vad-threshold': DEFAULT_VT,
        'vad-voice-ms': DEFAULT_VV,
    },
    'type': 'ask',
}
DISPATCHER_ASK_SPEAK_SAID_ANY = {
    'params': {
        'allowed_dtmf': 'any',
        'engine': 'ya_speechkit',
        'language': TTS_LANG,
        'voice': TTS_VOICE,
        'speed': TTS_SPEED,
        'use_grpc': TTS_GRPC,
        'text': f'{ML_SAID} {INPUT_ANY}',
        'no-input-timeout-ms': DEFAULT_NIT,
        'no-local-vad': DEFAULT_NLV,
        'speech-complete-timeout-ms': DEFAULT_SCT,
        'speech-timeout-ms': DEFAULT_ST,
        'start-input-timers': DEFAULT_SIT,
        'vad-silence-ms': DEFAULT_VS,
        'vad-threshold': DEFAULT_VT,
        'vad-voice-ms': DEFAULT_VV,
    },
    'type': 'ask',
}
DISPATCHER_ASK_SPEAK_SAID_DTMF = {
    'params': {
        'engine': 'ya_speechkit',
        'language': TTS_LANG,
        'voice': TTS_VOICE,
        'speed': TTS_SPEED,
        'use_grpc': TTS_GRPC,
        'text': f'{ML_SAID} {INPUT_DTMF}',
        'timeout': 4,
    },
    'type': 'input',
}
DISPATCHER_PLAY_ERROR_PROMPT = {
    'params': {'relative_path': f'{WORKER_ID}/{FLOW_ID}/{ERROR_FILE}.wav'},
    'type': 'play',
}
DISPATCHER_PLAY_RABBIT_PROMPT = {
    'params': {'relative_path': f'{WORKER_ID}/{FLOW_ID}/{RABBIT_FILE}.wav'},
    'type': 'play',
}
DISPATCHER_PLAY_FALLBACK_PROMPT = {
    'params': {'relative_path': f'{WORKER_ID}/{FLOW_ID}/{FALLBACK_FILE}.wav'},
    'type': 'play',
}
DISPATCHER_FORWARD_REPLY = {
    'params': {
        'answer_timeout': NO_ANSWER_TO,
        'call_from': OUTBOUND_NUMBER,
        'call_to': FORWARD_NUMBER,
        'gateways': OUTBOUND_GW,
        'progress_timeout': PROGRESS_TO,
        'send_events': FORWARD_SEND_EVENTS,
    },
    'type': 'switch',
}
DISPATCHER_FORWARD_UID_REPLY = {
    'params': {
        'answer_timeout': NO_ANSWER_TO,
        'call_from': ABONENT_NUMBER,
        'call_to': FORWARD_AGENT_ID,
        'gateways': OPERATOR_GW,
        'progress_timeout': PROGRESS_TO,
        'send_events': FORWARD_SEND_EVENTS,
    },
    'type': 'switch',
}
DISPATCHER_HOLD = {'type': 'hold'}
DISPATCHER_WAIT_EVENT = {'params': {}, 'type': 'wait_event'}
DISPATCHER_HANGUP = {'type': 'hangup'}
DISPATCHER_DONE = {'type': 'done'}

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
FORWARD_UID_ACTION = {
    'external_id': FORWARD_ACTION_ID,
    'forward': {
        'yandex_uid': FORWARD_YANDEX_UID,
        'route': ROUTE_CC_OPERATORS,
        'outbound_number': ABONENT_NUMBER,
    },
}
PLAY_INTRO = {
    'external_id': PLAY_INTRO_ACTION_ID,
    'playback': {'playback': {'play': {'id': INTRO_FILE}}},
}
PLAY_RABBIT = {
    'external_id': PLAY_RABBIT_ACTION_ID,
    'playback': {'playback': {'play': {'id': RABBIT_FILE}}},
}
PLAY_ERROR = {
    'external_id': PLAY_ERROR_ACTION_ID,
    'playback': {'playback': {'play': {'id': ERROR_FILE}}},
}
ASK_INTRO = {
    'external_id': ASK_INTRO_ID,
    'ask': {'playback': {'play': {'id': INTRO_FILE}}, 'input_mode': 'text'},
}
ASK_RABBIT = {
    'external_id': ASK_RABBIT_ID,
    'ask': {'playback': {'play': {'id': RABBIT_FILE}}, 'input_mode': 'text'},
}
ASK_ANY = {
    'external_id': ASK_ANY_ID,
    'ask': {
        'playback': {'speak': {'text': f'{ML_SAID} {INPUT_ANY}'}},
        'input_mode': 'text',
    },
}
ASK_DTMF = {
    'external_id': ASK_DTMF_ID,
    'ask': {
        'playback': {'speak': {'text': f'{ML_SAID} {INPUT_DTMF}'}},
        'input_mode': 'dtmf',
    },
}

CONTEXT_ORIGINATE_ACTION = {
    'external_id': ORIGINATE_ACTION_ID,
    'type': 'originate',
    'originate': {
        'phone_number': ABONENT_NUMBER,
        'outbound_number': OUTBOUND_NUMBER,
    },
}
CONTEXT_FALLBACK_PLAYBACK_ACTION = {
    'external_id': PLAY_FALLBACK_ACTION_ID,
    'type': 'playback',
    'playback': {'playback': {'play': {'id': FALLBACK_FILE}}},
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
RESPONSE_ASK_INTRO = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [ASK_INTRO],
}
RESPONSE_ASK_INTRO_FALLBACK = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [ASK_INTRO],
    'fallback_actions': [FALLBACK_PLAYBACK_ACTION, FALLBACK_HANGUP_ACTION],
}
RESPONSE_ASK_RABBIT = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [ASK_RABBIT],
}
RESPONSE_ASK_ANY = {'context': RESPONSE_CONTEXT_VALUES, 'actions': [ASK_ANY]}
RESPONSE_ASK_DTMF = {'context': RESPONSE_CONTEXT_VALUES, 'actions': [ASK_DTMF]}
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
RESPONSE_FORWARD_UID = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [FORWARD_UID_ACTION],
}
RESPONSE_HANGUP = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [HANGUP_ACTION],
}
RESPONSE_HOLD = {'context': RESPONSE_CONTEXT_VALUES, 'actions': [HOLD_ACTION]}
RESPONSE_SKIP_HOLDS = {
    'context': RESPONSE_CONTEXT_VALUES,
    'actions': [HOLD_ACTION1, HOLD_ACTION2, ASK_ANY],
}
RESPONSE_EMPTY = {'context': RESPONSE_CONTEXT_VALUES}
