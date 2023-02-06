from asyncio import sleep
from freeswitch_testsuite.environment_config import (
    TS_DISTRIBUTOR, TS_OP_DISTRIBUTOR, MOD_IVRD_PORT)
from freeswitch_testsuite.freeswitch import (
    create_leg_and_assert, bad_create_leg_and_assert)
from freeswitch_testsuite.ivr_dispatcher import MockDispatcher
from freeswitch_testsuite.metrics import assert_metrics
from freeswitch_testsuite.sip_b2b_ua import B2BUA
from freeswitch_testsuite.sip_call import SipCall
from freeswitch_testsuite.speechkit import MockSk
from freeswitch_testsuite.ua_status import *
from socket import gethostname
from typing import Dict

CALL_GUID: str = '111-222-333-4567890'
NEW_SESSION_ID: str = 'aaa-bbb-cc-12345678'
ORIG_CALLED_NUM: str = '+78122128506'
DISP_CALLING_NUM: str = '+79999999'
CALLED_NUM: str = 'testsuite'
TEXT_TO_SAY: str = 'TEXTTOSAY'
TEXT_TO_ASK: str = 'TEXTTOASK'
TRANSFEREE_ID: str = 'xferee_id'
ANSWER_ACTION_ID = 'answer_id'
FORWARD_ACTION_ID = 'forward_id'
ENABLE_RECORDING = True
UA_CMD_ORIGINATE: Dict = {
    'command': 'originate',
    'parameters': {
        'uri': f'sip:{CALLED_NUM}@127.0.0.1:5060;transport=tcp',
        'headers': {
            'X-CC-OriginalDN': ORIG_CALLED_NUM,
            'X-TC-GUID': CALL_GUID,
        }
    }
}
UA_CMD_HANGUP: Dict = {
    'command': 'hangup',
    'parameters': {
        'cause': UA_CODE_NORMAL,
    }
}
UA_CMD_HANGUP_BUSY: Dict = {
    'command': 'hangup',
    'parameters': {
        'cause': UA_CODE_BUSY,
    }
}
UA_CMD_RINGING: Dict = {
    'command': 'ringing',
    'parameters': {}
}
UA_CMD_ANSWER: Dict = {
    'command': 'answer',
    'parameters': {
        'cause': UA_CODE_OK,
    }
}
MOD_INITIAL_INB_REQ_EVENT: Dict = {
    'type': 'initial',
    'base_url': f'http://{gethostname()}:{MOD_IVRD_PORT}',
    'call_guid': CALL_GUID,
    'direction': 'inbound',
    'origin_called_number': ORIG_CALLED_NUM,
    'called_number': 'testsuite',
    'caller_number': 'initiator'
}
MOD_TOUU_ORIG_NO_GW_EVENT: Dict = {
    'type': 'originate',
    'status': 'ERROR',
    'error': {
        'code': 'DESTINATION_UNAVALABLE'
    }
}
MOD_TOUB_ORIG_BUSY_EVENT: Dict = {
    'type': 'originate',
    'status': 'ERROR',
    'error': {
        'code': 'DESTINATION_BUSY'
    }
}
MOD_TOUB_ORIG_NO_ANSWER_EVENT: Dict = {
    'type': 'originate',
    'status': 'ERROR',
    'error': {
        'code': 'DESTINATION_NO_ANSWER'
    }
}
MOD_TOUB_ORIG_ANSWER_EVENT: Dict = {
    'type': 'originate',
    'status': 'OK'
}
MOD_INITIAL_OUT_REQ_EVENT: Dict = {
    'type': 'initial',
    'base_url': f'http://{gethostname()}:{MOD_IVRD_PORT}',
    'direction': 'outbound',
}
MOD_ANSWER_OK_EVENT: Dict = {
    'type': 'answer',
    'status': 'OK',
}
MOD_PLAYBACK_OK_EVENT: Dict = {
    'type': 'playback',
    'status': 'OK',
}
MOD_SPEAK_OK_EVENT: Dict = {
    'type': 'playback',
    'status': 'OK',
}
MOD_ASK_OK_EVENT: Dict = {
    'type': 'ask',
    'status': 'OK',
    'user_input': TEXT_TO_SAY
}
MOD_ASK_DTMF_8_EVENT: Dict = {
    'type': 'ask',
    'status': 'OK',
    'user_input': 'DIGIT: 8'
}
MOD_PLAYBACK_ERROR_EVENT: Dict = {
    'type': 'playback',
    'status': 'ERROR',
    'error': {
        'code': 'ABONENT_HANGUP'
    }
}
MOD_HOLD_OK_EVENT: Dict = {
    'type': 'hold',
    'status': 'OK',
}
MOD_HOLD_ERROR_HANGUP: Dict = {
    'type': 'hold',
    'status': 'ERROR',
    'error': {
        'code': 'ABONENT_HANGUP'
    }
}
MOD_WAIT_OK_EVENT: Dict = {
    'type': 'wait',
    'status': 'OK'
}
MOD_WAIT_ERROR_ABONENT_HUP: Dict = {
    'type': 'wait',
    'status': 'ERROR',
    'error': {
        'code': 'ABONENT_HANGUP'
    }
}
MOD_ORIGINATE_ERROR_EVENT: Dict = {
    'type': 'originate',
    'status': 'ERROR',
    'error': {
        'code': 'UNSUPPORTED_COMMAND'
    }
}
MOD_CHANNEL_BRIDGE_EVENT: Dict = {
    'type': 'channel_event',
    'status': 'OK',
    'event_type': 'BRIDGE_SUCCESS',
    'transferee_id': TRANSFEREE_ID,
}
MOD_HOLD_STARTED_EVENT: Dict = {
    'type': 'channel_event',
    'status': 'OK',
    'event_type': 'HOLD_STARTED'
}
MOD_FORWARD_OK_EVENT_TRANSFEREE_HUP: Dict = {
    'type': 'forward',
    'status': 'OK',
    'disconnect_side': 'transferee',
    'transferee_id': TRANSFEREE_ID
}
MOD_FORWARD_OK_EVENT_INITIATOR_HUP: Dict = {
    'type': 'forward',
    'status': 'OK',
    'disconnect_side': 'initiator',
    'transferee_id': TRANSFEREE_ID
}
MOD_FORWARD_OK_EVENT_DEFLECT: Dict = {
    'type': 'forward',
    'status': 'OK',
    'disconnect_side': 'deflect',
    'transferee_id': TRANSFEREE_ID
}
MOD_FORWARD_ERROR_EVENT_ABONENT_HANGUP: Dict = {
    'type': 'forward',
    'status': 'ERROR',
    'error': {
        'code': 'ABONENT_HANGUP'
    },
    'transferee_id': TRANSFEREE_ID,
}
MOD_FORWARD_ERROR_EVENT_TRANSFEREE_BUSY: Dict = {
    'type': 'forward',
    'status': 'ERROR',
    'error': {
        'code': 'DESTINATION_BUSY'
    },
    'transferee_id': TRANSFEREE_ID,
}
MOD_FORWARD_ERROR_EVENT_TRANSFEREE_NO_ANSWER: Dict = {
    'type': 'forward',
    'status': 'ERROR',
    'error': {
        'code': 'DESTINATION_NO_ANSWER'
    },
    'transferee_id': TRANSFEREE_ID,
}
MOD_UNKNOWN_CMD_REQ_EVENT: Dict = {
    'type': 'answerr',
    'status': 'ERROR',
    'error': {
        'code': 'UNSUPPORTED_COMMAND'
    }
}

DISP_404: Dict = {
    'status': 404
}
DISP_UNKNOWN: Dict = {
    'action': {
        'type': 'answerr',
        'params': {}
    }
}
DISP_ANSWER: Dict = {
    'action_id': ANSWER_ACTION_ID,
    'action': {
        'type': 'answer',
        'params': {
            'enable_recording': ENABLE_RECORDING,
        }
    }
}
DISP_ANSWER_WITH_FALLBACK: Dict = {
    'action_id': ANSWER_ACTION_ID,
    'action': {
        'type': 'answer',
        'params': {
            'enable_recording': ENABLE_RECORDING,
        }
    },
    'fallback_actions': [
        {
            'type': 'playback',
            'params': {
                'play': {
                    'prompt_url': 'http://127.0.0.1:4400/prompts/test.r8'
                }
            }
        },
        {
            'type': 'hangup',
            'params': {
                'cause': 'NORMAL_CALL_CLEARING'
            }
        }
    ]
}
DISP_ORIGINATE_UNAV: Dict = {
    'action': {
        'type': 'originate',
        'params': {
            'answer_timeout': 1,
            'call_guid': CALL_GUID,
            'call_from': DISP_CALLING_NUM,
            'call_to': 'responder',
            'distributor': 'shitty',
            'enable_recording': ENABLE_RECORDING,
        }
    }
}
DISP_ORIGINATE_BADPARAM: Dict = {
    'action': {
        'type': 'originate',
        'params': 'BAAD'
    }
}
DISP_ORIGINATE_OOO_COMMAND: Dict = {
    'action': {
        'type': 'playback',
        'params': {}
    }
}
DISP_ORIGINATE_UAS: Dict = {
    'action': {
        'type': 'originate',
        'params': {
            'answer_timeout': 3,
            'call_guid': CALL_GUID,
            'call_from': DISP_CALLING_NUM,
            'call_to': 'responder',
            'distributor': TS_DISTRIBUTOR,
            'enable_recording': ENABLE_RECORDING,
        }
    }
}
DISP_PLAYBACK_TEST_AL: Dict = {
    'action': {
        'type': 'playback',
        'params': {
            'play': {
                'prompt_url': 'http://127.0.0.1:4400/prompts/test.r8'
            }
        }
    }
}
DISP_HOLD: Dict = {
    'action': {
        'type': 'hold'
    }
}
DISP_WAIT_2S: Dict = {
    'action': {
        'type': 'wait',
        'params': {
            'duration_ms': 2000
        }
    }
}
DISP_SPEAK_HELLO: Dict = {
    'action': {
        'type': 'playback',
        'params': {
            'speak': {
                'text': 'THISISATESTSYNTHTHISISATESTSYNTH',
                'tts_config': {
                    'voice': 'alena',
                    'engine': 'ya_speechkit',
                    'language': 'ru-RU',
                    'speed': 1.0,
                    'use_grpc': True
                }
            }
        }
    }
}
DISP_SPEAK_GRPC_HELLO: Dict = {
    'action': {
        'type': 'playback',
        'params': {
            'speak': {
                'text': 'THISISATESTSYNTHTHISISATESTSYNTH',
                'tts_config': {
                    'voice': 'alena',
                    'engine': 'ya_speechkit',
                    'language': 'ru-RU',
                    'speed': 1.0,
                    'use_grpc': True,
                }
            }
        }
    }
}
DISP_ASK_PROMPT_TEXT_DTMF: Dict = {
    'action': {
        'type': 'ask',
        'params': {
            'play': {
                'prompt_url': 'http://127.0.0.1:4400/prompts/some_file.r8',
            },
            'asr_config': {
                'engine': 'ya_speechkit',
                'language_code': 'ru-RU',
                'model': 'general',
                'max_response_duration_ms': 3000,
            },
            'dtmf_config': {
                'min_digits': 1,
                'max_digits': 1,
                'interdigit_timeout_ms': 1000,
                'allowed_dtmf': 'any',
            },
            'immediate_input': 1,
            'no_input_timeout_ms': 1500,
        }
    }
}
DISP_ASK_PROMPT_DTMF: Dict = {
    'action': {
        'type': 'ask',
        'params': {
            'play': {
                'prompt_url': 'http://127.0.0.1:4400/prompts/some_file.r8',
            },
            'dtmf_config': {
                'min_digits': 1,
                'max_digits': 1,
                'interdigit_timeout_ms': 1000,
                'allowed_dtmf': 'none',
            },
            'immediate_input': 1,
            'no_input_timeout_ms': 3000,
        }
    }
}
DISP_ASK_SPEAK_TEXT: Dict = {
    'action': {
        'type': 'ask',
        'params': {
            'speak': {
                'text': TEXT_TO_ASK,
                'tts_config': {
                    'voice': 'alena',
                    'engine': 'ya_speechkit',
                    'language': 'ru-RU',
                    'speed': 1.0,
                    'use_grpc': True,
                }
            },
            'asr_config': {
                'engine': 'ya_speechkit',
                'language_code': 'ru-RU',
                'model': 'general',
                'max_response_duration_ms': 3000,
            },
            'immediate_input': 1,
            'no_input_timeout_ms': 4500,
        }
    }
}
DISP_HANGUP_NORMAL: Dict = {
    'action': {
        'type': 'hangup',
        'params': {
            'cause': 'NORMAL_CALL_CLEARING'
        }
    }
}
DISP_HANGUP_BUSY: Dict = {
    'action': {
        'type': 'hangup',
        'params': {
            'cause': 'USER_BUSY'
        }
    }
}
DISP_FORWARD_RESPONDER: Dict = {
    'action_id': FORWARD_ACTION_ID,
    'action': {
        'type': 'forward',
        'params': {
            'call_guid': CALL_GUID,
            'answer_timeout': 2,
            'call_from': '+78122128506',
            'call_to': 'responder',
            'distributor': TS_OP_DISTRIBUTOR,
            'leg_id': TRANSFEREE_ID,
        }
    }
}
DISP_FORWARD_INITIATOR: Dict = {
    'action_id': FORWARD_ACTION_ID,
    'action': {
        'type': 'forward',
        'params': {
            'call_guid': CALL_GUID,
            'answer_timeout': 2,
            'call_from': '+78122128506',
            'call_to': 'initiator',
            'distributor': TS_OP_DISTRIBUTOR,
            'leg_id': TRANSFEREE_ID,
        }
    }
}
DISP_FORWARD_DEFLECT: Dict = {
    'action_id': FORWARD_ACTION_ID,
    'action': {
        'type': 'forward',
        'params': {
            'call_guid': CALL_GUID,
            'answer_timeout': 2,
            'call_from': '+78122128506',
            'call_to': 'responder',
            'distributor': TS_OP_DISTRIBUTOR,
            'use_deflect': True,
            'leg_id': TRANSFEREE_ID,
        }
    }
}
DISP_200_OK: Dict = {}

TID404_METRICS: Dict = {
    'legs_inbound': 1,
    'curl.dispatcher_req.22': 1,
    'http.statistics.200': 1,
}
TIDF404_METRICS: Dict = {
    'legs_inbound': 1,
    'curl.dispatcher_req.22': 1,
    'http.statistics.200': 1,
    'fallbacks_count': 1,
}
TOBD_METRICS: Dict = {
    'http.create_leg.500': 1,
    'http.statistics.200': 1,
}
TOD404_METRICS: Dict = {
    'curl.dispatcher_req.22': 1,
    'http.create_leg.200': 1,
    'http.statistics.200': 1,
}
TOTS_METRICS: Dict = {
    'curl.dispatcher_req.0': 3,
    'http.create_leg.200': 2,
    'http.statistics.200': 1,
    'legs_outbound': 1,
}
TODBR_METRICS: Dict = {
    'originate_error.DIAL_PARAM_NOT_SET': 1,
    'curl.dispatcher_req.0': 2,
    'cmd.originate.ERROR': 1,
    'http.create_leg.200': 1,
    'http.statistics.200': 1,
}
TODOOO_METRICS: Dict = {
    'curl.dispatcher_req.0': 1,
    'cmd.playback.ERROR': 1,
    'http.create_leg.200': 1,
    'http.statistics.200': 1,
}
TODUC_METRICS: Dict = {
    'curl.dispatcher_req.0': 3,
    'command_unsupported': 1,
    'http.create_leg.200': 1,
    'http.statistics.200': 1,
}
TOUU_METRICS: Dict = {
    'curl.dispatcher_req.0': 2,
    'cmd.originate.ERROR': 1,
    'originate_error.NO_VIABLE_GATEWAY': 1,
    'http.create_leg.200': 1,
    'http.statistics.200': 1,
}
TOUB_METRICS: Dict = {
    'curl.dispatcher_req.0': 2,
    'cmd.originate.ERROR': 1,
    'originate_error.USER_BUSY': 1,
    'http.create_leg.200': 1,
    'http.statistics.200': 1,
}
TOUNA_METRICS: Dict = {
    'curl.dispatcher_req.0': 2,
    'cmd.originate.ERROR': 1,
    'originate_error.NO_ANSWER': 1,
    'http.create_leg.200': 1,
    'http.statistics.200': 1,
}
TOPDH_METRICS: Dict = {
    'curl.dispatcher_req.0': 3,
    'cmd.originate.OK': 1,
    'cmd.playback.OK': 1,
    'cmd.hangup.OK': 1,
    'http.create_leg.200': 1,
    'http.statistics.200': 1,
}
TIDU_METRICS: Dict = {
    'legs_inbound': 1,
    'curl.dispatcher_req.0': 2,
    'command_unsupported': 1,
    'http.statistics.200': 1,
}
TIHB_METRICS: Dict = {
    'legs_inbound': 1,
    'curl.dispatcher_req.0': 1,
    'cmd.hangup.OK': 1,
    'http.statistics.200': 1,
}
TIADH_METRICS: Dict = {
    'legs_inbound': 1,
    'curl.dispatcher_req.0': 2,
    'cmd.answer.OK': 1,
    'cmd.hangup.OK': 1,
    'http.statistics.200': 1,
}
TIAPDH_METRICS: Dict = {
    'legs_inbound': 1,
    'curl.dispatcher_req.0': 3,
    'cmd.answer.OK': 1,
    'cmd.playback.OK': 1,
    'cmd.hangup.OK': 1,
    'http.statistics.200': 1,
}
TIASDH_METRICS: Dict = {
    'legs_inbound': 1,
    'curl.dispatcher_req.0': 3,
    'cmd.answer.OK': 1,
    'cmd.playback.OK': 1,
    'cmd.hangup.OK': 1,
    'http.statistics.200': 1,
}
TIAAPDH_METRICS: Dict = {
    'legs_inbound': 1,
    'curl.dispatcher_req.0': 3,
    'cmd.answer.OK': 1,
    'cmd.ask.OK': 1,
    'cmd.hangup.OK': 1,
    'http.statistics.200': 1,
}
TIAPCH_METRICS: Dict = {
    'legs_inbound': 1,
    'curl.dispatcher_req.0': 3,
    'cmd.answer.OK': 1,
    'cmd.playback.ERROR': 1,
    'cmd.hangup.OK': 1,
    'http.statistics.200': 1,
}
TIAHCH_METRICS: Dict = {
    'legs_inbound': 1,
    'curl.dispatcher_req.0': 4,
    'cmd.answer.OK': 1,
    'cmd.hold.ERROR': 1,
    'cmd.hangup.OK': 1,
    'http.statistics.200': 1,
}
TIAWCH_METRICS: Dict = {
    'legs_inbound': 1,
    'curl.dispatcher_req.0': 3,
    'cmd.answer.OK': 1,
    'cmd.wait.ERROR': 1,
    'cmd.hangup.OK': 1,
    'http.statistics.200': 1,
}
TIAWDH_METRICS: Dict = {
    'legs_inbound': 1,
    'curl.dispatcher_req.0': 3,
    'cmd.answer.OK': 1,
    'cmd.wait.OK': 1,
    'cmd.hangup.OK': 1,
    'http.statistics.200': 1,
}
TIAD_METRICS: Dict = {
    'legs_inbound': 1,
    'curl.dispatcher_req.0': 3,
    'cmd.answer.OK': 1,
    'cmd.forward.OK': 1,
    'http.statistics.200': 1,
}
TIAHIF_METRICS: Dict = {
    'legs_inbound': 1,
    'curl.dispatcher_req.0': 5,
    'cmd.answer.OK': 1,
    'cmd.hold.ERROR': 1,
    'cmd.forward.OK': 1,
    'http.statistics.200': 1,
}


# Входящий, dispatcher отвечает ошибкой > 400
async def test_inb_dispatcher_404(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    call: SipCall = calls.make_outgoing()
    await call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_404)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_404)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_404)
    await call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_TEMP_UNAV)
    await assert_metrics(TID404_METRICS)
    call.stop()
    del call


# Входящий, ответ с fallback-сценарием и затем отвечает ошибкой
async def test_inb_answer_with_fallback_404(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    call: SipCall = calls.make_outgoing()
    await call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER_WITH_FALLBACK)
    await call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    dispatcher.respond(DISP_404)
    await dispatcher.assert_module_request(MOD_ANSWER_OK_EVENT)
    dispatcher.respond(DISP_404)
    await dispatcher.assert_module_request(MOD_ANSWER_OK_EVENT)
    dispatcher.respond(DISP_404)
    await call.assert_media_state(MEDIA_STATE_ACTIVE)
    await call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    await assert_metrics(TIDF404_METRICS)
    call.stop()
    del call


# Входящий, dispatcher возвращает неизвестную команду
async def test_inb_dispatcher_unknown(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    call: SipCall = calls.make_outgoing()
    await call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_UNKNOWN)
    await dispatcher.assert_module_request(MOD_UNKNOWN_CMD_REQ_EVENT)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_TEMP_UNAV)
    await assert_metrics(TIDU_METRICS)
    call.stop()
    del call


# Входящий, dispatcher отбивает со специфичным кодом
async def test_inb_hangup_busy(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    call: SipCall = calls.make_outgoing()
    await call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_HANGUP_BUSY)
    await call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_BUSY)
    await assert_metrics(TIHB_METRICS)
    call.stop()
    del call


# Входящий, dispatcher отвечает и сразу завершает звонок
async def test_inb_answer_dispatcher_hangup(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    call: SipCall = calls.make_outgoing()
    await call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER)
    await call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    await assert_metrics(TIADH_METRICS)
    call.stop()
    del call


# Входящий, ответ, playback, hangup со стороны dispatcher
async def test_inb_answer_playback_dispatcher_hangup(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    call: SipCall = calls.make_outgoing()
    await call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER)
    await call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    dispatcher.respond(DISP_PLAYBACK_TEST_AL)
    await call.assert_media_state(MEDIA_STATE_ACTIVE)
    await dispatcher.assert_module_request(MOD_PLAYBACK_OK_EVENT)
    call.assert_audio_and_reset(DISP_PLAYBACK_TEST_AL)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    await assert_metrics(TIAPDH_METRICS)
    call.stop()
    del call


# Входящий, ответ, speak, hangup со стороны dispatcher
async def test_inb_answer_speak_dispatcher_hangup(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    call: SipCall = calls.make_outgoing()
    await call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER)
    await call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    dispatcher.respond(DISP_SPEAK_HELLO)
    await call.assert_media_state(MEDIA_STATE_ACTIVE)
    await dispatcher.assert_module_request(MOD_SPEAK_OK_EVENT)
    call.assert_audio_and_reset(DISP_SPEAK_HELLO)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    await assert_metrics(TIASDH_METRICS)
    call.stop()
    del call


# Входящий, ответ, grpc_speak, hangup со стороны dispatcher
async def test_inb_answer_speak_grpc_dispatcher_hangup(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    call: SipCall = calls.make_outgoing()
    await call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER)
    await call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    dispatcher.respond(DISP_SPEAK_GRPC_HELLO)
    await call.assert_media_state(MEDIA_STATE_ACTIVE)
    await dispatcher.assert_module_request(MOD_SPEAK_OK_EVENT)
    call.assert_audio_and_reset(DISP_SPEAK_HELLO)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    await assert_metrics(TIASDH_METRICS)
    call.stop()
    del call


# Входящий, ответ, ask с промптом, hangup со стороны dispatcher
async def test_inb_answer_ask_prompt_dispatcher_hangup(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    call: SipCall = calls.make_outgoing()
    await call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER)
    await call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    await call.assert_media_state(MEDIA_STATE_ACTIVE)
    dispatcher.respond(DISP_ASK_PROMPT_TEXT_DTMF)
    await sk_mock.stt.initial_received
    call.speak(TEXT_TO_SAY)
    await sleep(0.5)  # sleep to fill audio buffer before check
    call.assert_audio(DISP_ASK_PROMPT_TEXT_DTMF)
    call.stop_speak()
    await dispatcher.assert_module_request(MOD_ASK_OK_EVENT)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    await assert_metrics(TIAAPDH_METRICS)
    call.stop()
    del call


# Входящий, ответ, ask с синтезом, hangup со стороны dispatcher
async def test_inb_answer_ask_synth_dispatcher_hangup(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    call: SipCall = calls.make_outgoing()
    await call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER)
    await call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    await call.assert_media_state(MEDIA_STATE_ACTIVE)
    dispatcher.respond(DISP_ASK_SPEAK_TEXT)
    await sk_mock.stt.initial_received
    call.speak(TEXT_TO_SAY)
    await sleep(0.5)  # sleep to fill audio buffer before check
    call.assert_audio(DISP_ASK_SPEAK_TEXT)
    call.stop_speak()
    await dispatcher.assert_module_request(MOD_ASK_OK_EVENT)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    await assert_metrics(TIAAPDH_METRICS)
    call.stop()
    del call


# Входящий, ответ, playback, hangup со стороны UAC
async def test_inb_answer_playback_caller_hangup(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    call: SipCall = calls.make_outgoing()
    await call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER)
    await call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    dispatcher.respond(DISP_PLAYBACK_TEST_AL)
    await call.assert_media_state(MEDIA_STATE_ACTIVE)
    await sleep(0.5)    # To fill audio buffer before check
    call.assert_audio_and_reset(DISP_PLAYBACK_TEST_AL)
    await call.send_and_assert(
        UA_CMD_HANGUP, UA_STATE_DISCONNECTED, UA_CODE_NORMAL)
    await dispatcher.assert_module_request(MOD_PLAYBACK_ERROR_EVENT)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await assert_metrics(TIAPCH_METRICS)
    call.stop()
    del call


# Входящий, ответ, ask с промптом, hangup со стороны dispatcher
async def test_inb_answer_ask_prompt_dtmf_reply(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    call: SipCall = calls.make_outgoing()
    await call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER)
    await call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    await call.assert_media_state(MEDIA_STATE_ACTIVE)
    dispatcher.respond(DISP_ASK_PROMPT_DTMF)
    await sleep(0.5)  # sleep to fill audio buffer before check
    call.assert_audio(DISP_ASK_PROMPT_DTMF)
    call.send_dtmf("8")
    await dispatcher.assert_module_request(MOD_ASK_DTMF_8_EVENT)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    await assert_metrics(TIAAPDH_METRICS)
    call.stop()
    del call


# Входящий, ответ, MoH, hangup со стороны UAC
async def test_inb_answer_hold_caller_hangup(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    call: SipCall = calls.make_outgoing()
    await call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER)
    await call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    dispatcher.respond(DISP_HOLD)
    await call.assert_media_state(MEDIA_STATE_ACTIVE)
    await dispatcher.assert_module_request(MOD_HOLD_STARTED_EVENT)
    dispatcher.respond(DISP_200_OK)
    await sleep(2)    # To fill audio buffer before check
    call.assert_audio_and_reset(DISP_HOLD)
    await call.send_and_assert(
        UA_CMD_HANGUP, UA_STATE_DISCONNECTED, UA_CODE_NORMAL)
    await dispatcher.assert_module_request(MOD_HOLD_ERROR_HANGUP)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await assert_metrics(TIAHCH_METRICS)
    call.stop()
    del call


# Входящий, ответ, wait, hangup со стороны UAC
async def test_inb_answer_wait_caller_hangup(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    call: SipCall = calls.make_outgoing()
    await call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER)
    await call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    dispatcher.respond(DISP_WAIT_2S)
    await call.assert_media_state(MEDIA_STATE_ACTIVE)
    await sleep(0.5)    # To fill audio buffer before hangup
    call.assert_audio_and_reset(DISP_WAIT_2S)
    await call.send_and_assert(
        UA_CMD_HANGUP, UA_STATE_DISCONNECTED, UA_CODE_NORMAL)
    await dispatcher.assert_module_request(MOD_WAIT_ERROR_ABONENT_HUP)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await assert_metrics(TIAWCH_METRICS)
    call.stop()
    del call


# Входящий, ответ, wait, hangup со стороны dispatcher
async def test_inb_answer_wait_dispatcher_hangup(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    call: SipCall = calls.make_outgoing()
    await call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER)
    await call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    dispatcher.respond(DISP_WAIT_2S)
    await call.assert_media_state(MEDIA_STATE_ACTIVE)
    await sleep(0.5)    # Sleep to fill buffer
    call.assert_audio_and_reset(DISP_WAIT_2S)
    await sleep(1.1)    # Sleep to allow wait to complete
    await dispatcher.assert_module_request(MOD_WAIT_OK_EVENT)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    await assert_metrics(TIAWDH_METRICS)
    call.stop()
    del call


# Входящий, ответ, wait, hangup со стороны dispatcher
async def test_inb_answer_deflect(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    call: SipCall = calls.make_outgoing()
    await call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER)
    await call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    dispatcher.respond(DISP_FORWARD_DEFLECT)
    await call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_DEFLECT)
    await dispatcher.assert_module_request(
        MOD_FORWARD_OK_EVENT_DEFLECT, action_id=FORWARD_ACTION_ID)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    await assert_metrics(TIAD_METRICS)
    call.stop()
    del call


# Входящий, ответ, MoH, interrupt, forward, initiator hangup во время дозвона
async def test_inb_answer_hold_interrupt_forward_initiator_hangup_dial(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    in_call: SipCall = calls.make_outgoing()
    await in_call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER)
    await in_call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await in_call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    dispatcher.respond(DISP_HOLD)
    await in_call.assert_media_state(MEDIA_STATE_ACTIVE)
    await dispatcher.assert_module_request(MOD_HOLD_STARTED_EVENT)
    dispatcher.respond(DISP_200_OK)
    await dispatcher.send_interrupt()
    await dispatcher.assert_module_request(MOD_HOLD_OK_EVENT)
    dispatcher.respond(DISP_FORWARD_RESPONDER)
    resp_call: SipCall = await calls.get_uas_incoming()
    await resp_call.assert_call_state(UA_STATE_INCOMING, UA_CODE_TRYING)
    resp_call.push_command(UA_CMD_RINGING)
    await resp_call.assert_call_state(UA_STATE_RINGING, UA_CODE_RINGING)
    await sleep(1)  # 1 second of progress, then hangup
    in_call.push_command(UA_CMD_HANGUP)
    await dispatcher.assert_module_request(
        MOD_FORWARD_ERROR_EVENT_ABONENT_HANGUP, action_id=FORWARD_ACTION_ID)
    await resp_call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_CANCEL)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    in_call.stop()
    resp_call.stop()
    del in_call
    del resp_call


# Входящий, ответ, MoH, interrupt, forward, transferee не отвечает
async def test_inb_answer_hold_interrupt_forward_transferee_no_answer(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    in_call: SipCall = calls.make_outgoing()
    await in_call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER)
    await in_call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await in_call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    dispatcher.respond(DISP_HOLD)
    await in_call.assert_media_state(MEDIA_STATE_ACTIVE)
    await dispatcher.assert_module_request(MOD_HOLD_STARTED_EVENT)
    dispatcher.respond(DISP_200_OK)
    await dispatcher.send_interrupt()
    await dispatcher.assert_module_request(MOD_HOLD_OK_EVENT)
    dispatcher.respond(DISP_FORWARD_RESPONDER)
    resp_call: SipCall = await calls.get_uas_incoming()
    await resp_call.assert_call_state(UA_STATE_INCOMING, UA_CODE_TRYING)
    resp_call.push_command(UA_CMD_RINGING)
    await resp_call.assert_call_state(UA_STATE_RINGING, UA_CODE_RINGING)
    await sleep(3)  # Answer timeout is 2 seconds, sleep longer for NO_ANSWER
    await resp_call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_CANCEL)
    await dispatcher.assert_module_request(
        MOD_FORWARD_ERROR_EVENT_TRANSFEREE_NO_ANSWER, action_id=FORWARD_ACTION_ID)
    dispatcher.respond(DISP_PLAYBACK_TEST_AL)
    await dispatcher.assert_module_request(MOD_PLAYBACK_OK_EVENT)
    in_call.assert_audio_and_reset(DISP_PLAYBACK_TEST_AL)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await in_call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    in_call.stop()
    resp_call.stop()
    del in_call
    del resp_call


# Входящий, ответ, MoH, interrupt, forward, transferee не отвечает,
# повторный дозвон
async def test_inb_answer_hold_interrupt_forward_transferee_no_answer_retry(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    in_call: SipCall = calls.make_outgoing()
    await in_call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER)
    await in_call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await in_call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    dispatcher.respond(DISP_HOLD)
    await in_call.assert_media_state(MEDIA_STATE_ACTIVE)
    await dispatcher.assert_module_request(MOD_HOLD_STARTED_EVENT)
    dispatcher.respond(DISP_200_OK)
    await dispatcher.send_interrupt()
    await dispatcher.assert_module_request(MOD_HOLD_OK_EVENT)
    dispatcher.respond(DISP_FORWARD_RESPONDER)
    resp_call: SipCall = await calls.get_uas_incoming()
    await resp_call.assert_call_state(UA_STATE_INCOMING, UA_CODE_TRYING)
    resp_call.push_command(UA_CMD_RINGING)
    await resp_call.assert_call_state(UA_STATE_RINGING, UA_CODE_RINGING)
    await sleep(3)  # Answer timeout is 2 seconds, sleep longer for NO_ANSWER
    await resp_call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_CANCEL)
    resp_call.stop()
    calls.uas_account.reset()
    await dispatcher.assert_module_request(
        MOD_FORWARD_ERROR_EVENT_TRANSFEREE_NO_ANSWER, action_id=FORWARD_ACTION_ID)
    dispatcher.respond(DISP_HOLD)
    await dispatcher.assert_module_request(MOD_HOLD_STARTED_EVENT)
    dispatcher.respond(DISP_200_OK)
    await dispatcher.send_interrupt()
    await dispatcher.assert_module_request(MOD_HOLD_OK_EVENT)
    dispatcher.respond(DISP_FORWARD_RESPONDER)
    resp_call: SipCall = await calls.get_uas_incoming()
    await resp_call.assert_call_state(UA_STATE_INCOMING, UA_CODE_TRYING)
    resp_call.push_command(UA_CMD_RINGING)
    await resp_call.assert_call_state(UA_STATE_RINGING, UA_CODE_RINGING)
    await sleep(0.5)
    resp_call.push_command(UA_CMD_ANSWER)
    await resp_call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await resp_call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(MOD_CHANNEL_BRIDGE_EVENT)
    dispatcher.respond(DISP_200_OK)
    await sleep(0.5)  # Talk a little, then hangup
    resp_call.push_command(UA_CMD_HANGUP)
    await dispatcher.assert_module_request(
        MOD_FORWARD_OK_EVENT_TRANSFEREE_HUP, action_id=FORWARD_ACTION_ID)
    dispatcher.respond(DISP_PLAYBACK_TEST_AL)
    await dispatcher.assert_module_request(MOD_PLAYBACK_OK_EVENT)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await in_call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    in_call.stop()
    resp_call.stop()
    del in_call
    del resp_call


# Входящий, ответ, MoH, interrupt, forward, transferee hangup во время дозвона
async def test_inb_answer_hold_interrupt_forward_transferee_hangup(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    in_call: SipCall = calls.make_outgoing()
    await in_call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER)
    await in_call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await in_call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    dispatcher.respond(DISP_HOLD)
    await in_call.assert_media_state(MEDIA_STATE_ACTIVE)
    await dispatcher.assert_module_request(MOD_HOLD_STARTED_EVENT)
    dispatcher.respond(DISP_200_OK)
    await dispatcher.send_interrupt()
    await dispatcher.assert_module_request(MOD_HOLD_OK_EVENT)
    dispatcher.respond(DISP_FORWARD_RESPONDER)
    resp_call: SipCall = await calls.get_uas_incoming()
    await resp_call.assert_call_state(UA_STATE_INCOMING, UA_CODE_TRYING)
    resp_call.push_command(UA_CMD_RINGING)
    await resp_call.assert_call_state(UA_STATE_RINGING, UA_CODE_RINGING)
    await sleep(0.5)  # Ring 0.5 second, then send BUSY
    resp_call.push_command(UA_CMD_HANGUP_BUSY)
    await resp_call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_BUSY)
    await dispatcher.assert_module_request(
        MOD_FORWARD_ERROR_EVENT_TRANSFEREE_BUSY, action_id=FORWARD_ACTION_ID)
    dispatcher.respond(DISP_PLAYBACK_TEST_AL)
    await dispatcher.assert_module_request(
        MOD_PLAYBACK_OK_EVENT)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await in_call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    in_call.stop()
    resp_call.stop()
    del in_call
    del resp_call


# Входящий, ответ, MoH, interrupt, forward, разговор, transferee hangup, play
async def test_inb_answer_hold_interrupt_forward_talk_transferee_hangup_play(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    in_call: SipCall = calls.make_outgoing()
    await in_call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER)
    await in_call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await in_call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    dispatcher.respond(DISP_HOLD)
    await in_call.assert_media_state(MEDIA_STATE_ACTIVE)
    await dispatcher.assert_module_request(MOD_HOLD_STARTED_EVENT)
    dispatcher.respond(DISP_200_OK)
    await sleep(0.5)  # Let him hang on hold a little
    await dispatcher.send_interrupt()
    await dispatcher.assert_module_request(MOD_HOLD_OK_EVENT)
    dispatcher.respond(DISP_FORWARD_RESPONDER)
    resp_call: SipCall = await calls.get_uas_incoming()
    await resp_call.assert_call_state(UA_STATE_INCOMING, UA_CODE_TRYING)
    resp_call.push_command(UA_CMD_RINGING)
    await resp_call.assert_call_state(UA_STATE_RINGING, UA_CODE_RINGING)
    await sleep(0.5)
    resp_call.push_command(UA_CMD_ANSWER)
    await resp_call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await resp_call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(MOD_CHANNEL_BRIDGE_EVENT)
    dispatcher.respond(DISP_200_OK)
    await sleep(0.5)  # Talk a little, then hangup
    resp_call.push_command(UA_CMD_HANGUP)
    await dispatcher.assert_module_request(
        MOD_FORWARD_OK_EVENT_TRANSFEREE_HUP, action_id=FORWARD_ACTION_ID)
    dispatcher.respond(DISP_PLAYBACK_TEST_AL)
    await dispatcher.assert_module_request(MOD_PLAYBACK_OK_EVENT)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await in_call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    in_call.stop()
    resp_call.stop()
    del in_call
    del resp_call


# Входящий, ответ, MoH, interrupt, forward, разговор, initiator hangup
async def test_inb_answer_hold_interrupt_forward_talk_initiator_hangup(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    in_call: SipCall = calls.make_outgoing()
    await in_call.send_and_assert(UA_CMD_ORIGINATE, UA_STATE_CALLING)
    await dispatcher.assert_module_request(MOD_INITIAL_INB_REQ_EVENT)
    dispatcher.respond(DISP_ANSWER)
    await in_call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await in_call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    dispatcher.respond(DISP_HOLD)
    await in_call.assert_media_state(MEDIA_STATE_ACTIVE)
    await dispatcher.assert_module_request(MOD_HOLD_STARTED_EVENT)
    dispatcher.respond(DISP_200_OK)
    await sleep(0.5)
    await dispatcher.send_interrupt()
    await dispatcher.assert_module_request(MOD_HOLD_OK_EVENT)
    dispatcher.respond(DISP_FORWARD_RESPONDER)
    resp_call: SipCall = await calls.get_uas_incoming()
    await resp_call.assert_call_state(UA_STATE_INCOMING, UA_CODE_TRYING)
    resp_call.push_command(UA_CMD_RINGING)
    await resp_call.assert_call_state(UA_STATE_RINGING, UA_CODE_RINGING)
    await sleep(0.5)
    resp_call.push_command(UA_CMD_ANSWER)
    await resp_call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await resp_call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(MOD_CHANNEL_BRIDGE_EVENT)
    dispatcher.respond(DISP_200_OK)
    await sleep(0.5)
    in_call.push_command(UA_CMD_HANGUP)
    await in_call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_NORMAL)
    await dispatcher.assert_module_request(
        MOD_FORWARD_OK_EVENT_INITIATOR_HUP, action_id=FORWARD_ACTION_ID)
    await resp_call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    in_call.stop()
    resp_call.stop()
    del in_call
    del resp_call


# Исходящий, не можем распарсить JSON в create_leg
async def test_out_bad_data(
        calls: B2BUA, dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    await bad_create_leg_and_assert()
    await assert_metrics(TOBD_METRICS)


# Исходящий, dispatcher отвечает ошибкой > 400 в ответ на initial
# Заказываем определённый session_id
async def test_out_dispatcher_404(
        calls: B2BUA, dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    await create_leg_and_assert(session_id=NEW_SESSION_ID)
    await dispatcher.assert_module_request(
        MOD_INITIAL_OUT_REQ_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_404)
    await dispatcher.assert_module_request(
        MOD_INITIAL_OUT_REQ_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_404)
    await dispatcher.assert_module_request(
        MOD_INITIAL_OUT_REQ_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_404)
    await assert_metrics(TOD404_METRICS)


# Заказываем определённый session_id дважды,
# создаётся только одна сессияе
async def test_out_twice_same_id(
        calls: B2BUA, dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    await create_leg_and_assert(session_id=NEW_SESSION_ID)
    await dispatcher.assert_module_request(
        MOD_INITIAL_OUT_REQ_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_ORIGINATE_UAS)
    call: SipCall = await calls.get_uas_incoming()
    await call.assert_call_state(UA_STATE_INCOMING, UA_CODE_TRYING)
    call.push_command(UA_CMD_ANSWER)
    await call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_TOUB_ORIG_ANSWER_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_PLAYBACK_TEST_AL)
    await create_leg_and_assert(session_id=NEW_SESSION_ID)
    await dispatcher.assert_module_request(MOD_PLAYBACK_OK_EVENT)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    await assert_metrics(TOTS_METRICS)
    call.stop()
    del call


# Исходящий, dispatcher отвечает на initial не originate
# Заказываем определённый session_id
async def test_out_dispatcher_ooo_response(
        calls: B2BUA, dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    await create_leg_and_assert(session_id=NEW_SESSION_ID)
    await dispatcher.assert_module_request(
        MOD_INITIAL_OUT_REQ_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_ORIGINATE_OOO_COMMAND)
    await assert_metrics(TODOOO_METRICS)


# Исходящий, dispatcher отвечает initial без нужных параметров
# Заказываем определённый session_id
async def test_out_dispatcher_bad_response(
        calls: B2BUA, dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    await create_leg_and_assert(session_id=NEW_SESSION_ID)
    await dispatcher.assert_module_request(
        MOD_INITIAL_OUT_REQ_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_ORIGINATE_BADPARAM)
    await dispatcher.assert_module_request(
        MOD_ORIGINATE_ERROR_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await assert_metrics(TODBR_METRICS)


# Исходящий, dispatcher отвечает ошибкой > 400 в ответ на initial
# Произвольный session_id
async def test_out_dispatcher_no_sid_404(
        calls: B2BUA, dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    await create_leg_and_assert()
    await dispatcher.assert_module_request(
        MOD_INITIAL_OUT_REQ_EVENT)
    dispatcher.respond(DISP_404)
    await dispatcher.assert_module_request(
        MOD_INITIAL_OUT_REQ_EVENT)
    dispatcher.respond(DISP_404)
    await dispatcher.assert_module_request(
        MOD_INITIAL_OUT_REQ_EVENT)
    dispatcher.respond(DISP_404)
    await assert_metrics(TOD404_METRICS)


# Исходящий, dispatcher возвращает неизвестную команду в ответ на initial
async def test_out_dispatcher_unknown_cmd(
        calls: B2BUA, dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    await create_leg_and_assert(session_id=NEW_SESSION_ID)
    await dispatcher.assert_module_request(
        MOD_INITIAL_OUT_REQ_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_ORIGINATE_UAS)
    call: SipCall = await calls.get_uas_incoming()
    await call.assert_call_state(UA_STATE_INCOMING, UA_CODE_TRYING)
    call.push_command(UA_CMD_ANSWER)
    await call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await call.assert_media_state(MEDIA_STATE_ACTIVE)
    await call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_TOUB_ORIG_ANSWER_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_UNKNOWN)
    await dispatcher.assert_module_request(MOD_UNKNOWN_CMD_REQ_EVENT)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    await assert_metrics(TODUC_METRICS)
    call.stop()
    del call


# Исходящий до sip-клиента, недоступен UAS
async def test_out_uas_unavailable(
        calls: B2BUA, dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    await create_leg_and_assert(session_id=NEW_SESSION_ID)
    await dispatcher.assert_module_request(
        MOD_INITIAL_OUT_REQ_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_ORIGINATE_UNAV)
    await dispatcher.assert_module_request(
        MOD_TOUU_ORIG_NO_GW_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await assert_metrics(TOUU_METRICS)


# Исходящий до sip-клиента, UAS отбивает со специфичным кодом
async def test_out_uas_busy(
        calls: B2BUA, dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    await create_leg_and_assert(session_id=NEW_SESSION_ID)
    await dispatcher.assert_module_request(
        MOD_INITIAL_OUT_REQ_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_ORIGINATE_UAS)
    call: SipCall = await calls.get_uas_incoming()
    await call.assert_call_state(UA_STATE_INCOMING, code=UA_CODE_TRYING)
    call.do_hangup(cause=UA_CODE_BUSY)
    await dispatcher.assert_module_request(
        MOD_TOUB_ORIG_BUSY_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await assert_metrics(TOUB_METRICS)
    call.stop()
    del call


# Исходящий до sip-клиента, UAS не отвечает
async def test_out_uas_no_answer(
        calls: B2BUA, dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    await create_leg_and_assert(session_id=NEW_SESSION_ID)
    await dispatcher.assert_module_request(
        MOD_INITIAL_OUT_REQ_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_ORIGINATE_UAS)
    call: SipCall = await calls.get_uas_incoming()
    await call.assert_call_state(UA_STATE_INCOMING, code=UA_CODE_TRYING)
    await sleep(4)
    await dispatcher.assert_module_request(
        MOD_TOUB_ORIG_NO_ANSWER_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await assert_metrics(TOUNA_METRICS)
    call.stop()
    del call


# Исходящий до sip-клиента, ответ, playback, hangup со стороны dispatcher
async def test_out_playback_dispatcher_hangup(
        calls: B2BUA, dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    await create_leg_and_assert(session_id=NEW_SESSION_ID)
    await dispatcher.assert_module_request(
        MOD_INITIAL_OUT_REQ_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_ORIGINATE_UAS)
    call: SipCall = await calls.get_uas_incoming()
    await call.assert_call_state(UA_STATE_INCOMING, UA_CODE_TRYING)
    call.push_command(UA_CMD_ANSWER)
    await call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await call.assert_media_state(MEDIA_STATE_ACTIVE)
    await call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_TOUB_ORIG_ANSWER_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_PLAYBACK_TEST_AL)
    await dispatcher.assert_module_request(MOD_PLAYBACK_OK_EVENT)
    call.assert_audio_and_reset(DISP_PLAYBACK_TEST_AL)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    await assert_metrics(TOPDH_METRICS)
    call.stop()
    del call


# Исходящий до sip-клиента, ответ, forward, transferee_hangup. ask
async def test_out_forward_xferee_hup_ask(
        calls: B2BUA, dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    await create_leg_and_assert(session_id=NEW_SESSION_ID)
    await dispatcher.assert_module_request(
        MOD_INITIAL_OUT_REQ_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_ORIGINATE_UAS)
    call: SipCall = await calls.get_uas_incoming()
    await call.assert_call_state(UA_STATE_INCOMING, UA_CODE_TRYING)
    call.push_command(UA_CMD_ANSWER)
    await call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await call.assert_media_state(MEDIA_STATE_ACTIVE)
    await call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(
        MOD_TOUB_ORIG_ANSWER_EVENT, session_id=NEW_SESSION_ID)
    dispatcher.respond(DISP_FORWARD_INITIATOR)
    resp_call: SipCall = await calls.get_uac_incoming()
    await resp_call.assert_call_state(UA_STATE_INCOMING, UA_CODE_TRYING)
    resp_call.push_command(UA_CMD_ANSWER)
    await resp_call.assert_call_state(UA_STATE_CONNECTING, UA_CODE_OK)
    await resp_call.assert_media_state(MEDIA_STATE_ACTIVE)
    await resp_call.assert_call_state(UA_STATE_CONFIRMED, UA_CODE_OK)
    await dispatcher.assert_module_request(MOD_CHANNEL_BRIDGE_EVENT)
    dispatcher.respond(DISP_200_OK)
    await sleep(0.5)
    resp_call.push_command(UA_CMD_HANGUP)
    await dispatcher.assert_module_request(MOD_FORWARD_OK_EVENT_TRANSFEREE_HUP)
    dispatcher.respond(DISP_ASK_PROMPT_DTMF)
    await sleep(0.5)  # sleep to fill audio buffer before check
    call.assert_audio(DISP_ASK_PROMPT_DTMF)
    call.send_dtmf("8")
    await dispatcher.assert_module_request(MOD_ASK_DTMF_8_EVENT)
    dispatcher.respond(DISP_HANGUP_NORMAL)
    await call.assert_call_state(UA_STATE_DISCONNECTED, UA_CODE_OK)
    call.stop()
    resp_call.stop()
    del call
    del resp_call


# Входящий, ручной ответ, ask с промптом, hangup со стороны dispatcher
async def man_inb_answer(
        calls: B2BUA,
        dispatcher: MockDispatcher,
        sk_mock: MockSk) -> None:
    forward: Dict = {
        'action': {
            'type': 'forward',
            'params': {
                'answer_timeout': 120,
                'call_guid': 'OLOLO',
                'call_from': '111111',
                'call_to': 'operator',
                'distributor': TS_OP_DISTRIBUTOR,
                'use_deflect': False,
                'enable_provision': True,
            },
        },
        'action_id': 'forward_id',
    }

    await dispatcher.print_module_request()
    dispatcher.respond(DISP_ANSWER)
    await dispatcher.assert_module_request(
        MOD_ANSWER_OK_EVENT, action_id=ANSWER_ACTION_ID)
    dispatcher.respond(forward)
    await dispatcher.print_module_request()
    dispatcher.respond(DISP_HANGUP_NORMAL)

