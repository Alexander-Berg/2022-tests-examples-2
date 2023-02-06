DEFAULT_ORDER_ID = '9b0ef3c5398b3e07b59f03110563479d'
DEFAULT_ALIAS_ID = '09f24cb023842e86a05281f049689ae1'
DEFAULT_PHONE_ID = '581fe54e0779cf3c0cb61b70'
DEFAULT_PERSONAL_PHONE_ID = '9cc9e88b3aec4e699eb19c1cd54f23bc'
DEFAULT_USER_PHONE = '+79152608765'
DEFAULT_SESSION_ID = 'f0d7e65adbe24f7e9167c0ef857edede'
DEFAULT_LOCALE = 'ru'
DEFAULT_APPLICATION = 'call_center'
DEFAULT_NEAREST_ZONE = 'moscow'
DEFAULT_STQ_TASK_ID = 'test_task'
DEFAULT_INTENT = 'taxi_intent'
DEFAULT_SENDER = 'taxi_sender'
DEFAULT_DRIVER_PERSONAL_PHONE_ID = '9cc9e88b3aec4e699eb19c1cd54f23ad'
DEFAULT_DRIVER_PHONE = '+79998887766'
DEFAULT_CAR_ID = 'vehicle1'
DEFAULT_TARIFF_CATEGORY_ID = 'efb6584781884267b8d4769ff421a4af'
DEFAULT_TAXI_PHONE = '+74959999999'
DEFAULT_DRIVER_ID = '779556aa00b44c08b928e3cb23014b35'
DEFAULT_PARK_ID = '112ce41513984089a610465f36c8647e'
DEFAULT_METAQUEUE = 'disp_cc'
DEFAULT_METAQUEUE_ECONOMY = 'disp_economy'
DEFAULT_USER_ID = '581fe54e0779cf3c0cb61b71'

ON_ASSIGNED = 'on_assigned'
ON_WAITING = 'on_waiting'
ON_SEARCH = 'on_search'
HANDLE_DRIVING = 'handle_driving'
HANDLE_WAITING = 'handle_waiting'
HANDLE_CANCEL_BY_USER = 'handle_cancel_by_user'
CREATE_REASON = 'create'
KZ_INTENT = 'taxi_intent_kz'
KZ_SENDER = 'taxi_sender_kz'
KZ_NUMBER = '+77777654321'
KZ_SESSION_ID = 'kz_session_id'
ANOTHER_SESSION_ID = 'f0d7e65adbe24f7e9167c0ef857ededf'
ANOTHER_PARK_ID = '112ce41513984089a610465f36c8647f'

DEFAULT_IVR_SETTINGS = {
    'application_settings': {
        DEFAULT_APPLICATION: {
            'has_order_status': True,
            'gateway_settings': {
                '__default__': {
                    'name': 'ivr_via_noc',
                    'default_number': '2128510',
                    'numbers': ['2128500'],
                },
                'driver_switch': {
                    'name': 'ivr_customer_to_driver',
                    'default_number': '2128610',
                    'numbers': ['2128600'],
                },
                'ivr_order_informer': {
                    'name': 'ivr_order_informer',
                    'default_number': '2128710',
                    'numbers': ['2128700', DEFAULT_TAXI_PHONE],
                },
            },
            'locale': 'ru',
            'sms_settings': {
                'sms_enabled': True,
                'force_send_sms': False,
                'intent': DEFAULT_INTENT,
                'sender': DEFAULT_SENDER,
            },
        },
        '7220_call_center': {
            'has_order_status': True,
            'gateway_settings': {
                '__default__': {'name': 'ivr_via_noc', 'numbers': ['2128501']},
                'driver_switch': {
                    'name': 'ivr_customer_to_driver',
                    'numbers': ['2128601'],
                },
                'ivr_order_informer': {
                    'name': 'ivr_order_informer',
                    'numbers': ['2128701', DEFAULT_TAXI_PHONE],
                },
            },
            'locale': 'ru',
            'sms_settings': {
                'sms_enabled': True,
                'force_send_sms': False,
                'intent': DEFAULT_INTENT,
                'sender': DEFAULT_SENDER,
            },
        },
        'arm_call_center': {
            'has_order_status': False,
            'gateway_settings': {
                '__default__': {
                    'name': 'ivr_via_noc',
                    'default_number': '2128512',
                    'numbers': ['2128502'],
                },
                'driver_switch': {
                    'name': 'ivr_customer_to_driver',
                    'numbers': ['2128602'],
                },
                'ivr_order_informer': {
                    'name': 'ivr_order_informer',
                    'numbers': ['2128702', DEFAULT_TAXI_PHONE],
                },
            },
            'locale': 'ru',
            'sms_settings': {
                'sms_enabled': True,
                'force_send_sms': True,
                'intent': DEFAULT_INTENT,
                'sender': DEFAULT_SENDER,
                'driver_phone_enabled': True,
            },
        },
        'uber_az_call_center': {
            'has_order_status': False,
            'gateway_settings': {
                '__default__': {'name': 'ivr_via_noc', 'numbers': ['2128503']},
                'driver_switch': {
                    'name': 'ivr_customer_to_driver',
                    'numbers': ['2128603'],
                },
                'ivr_order_informer': {
                    'name': 'ivr_order_informer',
                    'numbers': ['2128703', DEFAULT_TAXI_PHONE],
                },
            },
            'locale': 'az',
            'sms_settings': {
                'sms_enabled': True,
                'force_send_sms': True,
                'intent': DEFAULT_INTENT,
                'sender': DEFAULT_SENDER,
                'driver_phone_enabled': True,
            },
        },
        'kz_call_center': {
            'has_order_status': False,
            'gateway_settings': {
                '__default__': {
                    'name': 'ivr_via_noc_kz',
                    'numbers': [KZ_NUMBER],
                },
                'driver_switch': {
                    'name': 'ivr_via_noc_kz',
                    'numbers': [KZ_NUMBER],
                },
                'ivr_order_informer': {
                    'name': 'ivr_via_noc_kz',
                    'numbers': [KZ_NUMBER],
                },
            },
            'locale': 'ru',
            'sms_settings': {
                'sms_enabled': True,
                'force_send_sms': True,
                'intent': KZ_INTENT,
                'sender': KZ_SENDER,
            },
        },
    },
}

DEFAULT_REROUTE_METAQUEUES = {
    'order_status_worker_2_0': {
        DEFAULT_METAQUEUE: {'metaqueue': DEFAULT_METAQUEUE_ECONOMY},
    },
}

CALLING_NUM_HARD = '+79009999988'
CALLING_NUM_ORDINARY = '+79009999999'
NEW_SESSION_ID = 'test_session_id'


# Octonode action results
OCTONODE_INITIAL_RESULT = {
    'brand': '+100',
    'call_guid': 'noc_call_guid',
    'called_number': '89900',
    'caller_number': CALLING_NUM_ORDINARY,
    'origin_called_number': '+78122128506',
    'status': 'ok',
    'type': 'initial',
}
OCTONODE_INITIAL_RESULT_TEST_WORKER = {
    'brand': '+100',
    'call_guid': 'noc_call_guid',
    'called_number': '77777',
    'caller_number': CALLING_NUM_ORDINARY,
    'origin_called_number': '+78122128506',
    'status': 'ok',
    'type': 'initial',
}
OCTONODE_ANSWER_OK_RESULT = {'status': 'ok', 'type': 'answer'}
OCTONODE_SWITCH_OK_RESULT = {'status': 'ok', 'type': 'switch'}
OCTONODE_PLAY_OK_RESULT = {'status': 'ok', 'type': 'play'}
OCTONODE_PLAY_ERR_RESULT = {
    'error_cause': 'FILE NOT FOUND',
    'status': 'error',
    'type': 'play',
}
OCTONODE_PLAY_USER_HANGUP = {
    'error_cause': 'initiator_hangup',
    'status': 'error',
    'type': 'play',
}
OCTONODE_ASK_USER_HANGUP = {
    'error_cause': 'initiator_hangup',
    'status': 'error',
    'type': 'ask',
}
OCTONODE_ASK_DIGIT_1_REPLY = {
    'user_input': 'DIGIT: 1',
    'status': 'ok',
    'type': 'ask',
}
OCTONODE_ASK_TEXT_CHECK_REPLY = {
    'user_input': 'Проверка',
    'status': 'ok',
    'type': 'ask',
}
OCTONODE_ASK_TEXT_END_REPLY = {
    'user_input': 'Довольно',
    'status': 'ok',
    'type': 'ask',
}
OCTONODE_SPEAK_RESULT_OK = {'status': 'ok', 'type': 'speak'}

# Dispatcher possible answers
DISPATCHER_ANSWER_REPLY = {
    'type': 'answer',
    'params': {'start_recording': True},
}
DISPATCHER_ANSWER_NOREC_REPLY = {
    'type': 'answer',
    'params': {'start_recording': False},
}
DISPATCHER_HANGUP_REPLY = {'type': 'hangup'}

DISPATCHER_PLAY_TEST_REPLY = {
    'params': {'relative_path': 'oiw/check.wav'},
    'type': 'play',
}
DISPATCHER_ASK_TEST_INPUT_TEXT_REPLY = {
    'params': {
        'allowed_dtmf': 'any',
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'no-input-timeout-ms': 10000,
        'no-local-vad': False,
        'speech-complete-timeout-ms': 2000,
        'speech-timeout-ms': 10000,
        'speed': 1.0,
        'start-input-timers': False,
        'text': (
            'Тест диалога. Нажмите 1 или скажите проверка чтобы повторить.'
        ),
        'vad-silence-ms': 20,
        'vad-threshold': 40,
        'vad-voice-ms': 20,
        'voice': 'alena',
    },
    'type': 'ask',
}
DISPATCHER_ASK_TEST_INPUT_PLAY_REPLY = {
    'params': {
        'allowed_dtmf': 'any',
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'no-input-timeout-ms': 10000,
        'no-local-vad': False,
        'speech-complete-timeout-ms': 2000,
        'speech-timeout-ms': 10000,
        'start-input-timers': False,
        'relative_path': 'tw/check.wav',
        'vad-silence-ms': 20,
        'vad-threshold': 40,
        'vad-voice-ms': 20,
    },
    'type': 'ask',
}

IVR_SETTINGS_GOOD = {
    'application_settings': {
        'call_center': {
            'gateway_settings': {
                '__default__': {
                    'name': 'ivr_via_noc',
                    'numbers': [DEFAULT_TAXI_PHONE],
                },
            },
            'locale': 'ru',
            'has_order_status': True,
            'sms_settings': {
                'force_send_sms': False,
                'intent': 'test_ntent',
                'sender': 'test',
                'sms_enabled': False,
            },
        },
    },
}
IVR_SETTINGS_NO_DISP = {
    'application_settings': {
        'call_center': {
            'gateway_settings': {
                '__default__': {
                    'name': 'ivr_via_noc',
                    'default_number': '2128710',
                    'numbers': [DEFAULT_TAXI_PHONE],
                },
            },
            'has_order_status': True,
            'locale': 'ru',
            'sms_settings': {
                'force_send_sms': False,
                'intent': 'test_ntent',
                'sender': 'test',
                'sms_enabled': False,
            },
        },
    },
}
