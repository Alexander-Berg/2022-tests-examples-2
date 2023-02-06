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
FLOW_ID = 'after_disp_call_flow'

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

OCTONODE_PLAY_OK_RESULT = {'status': 'ok', 'type': 'play'}

OCTONODE_ASK_RESULT_CONFIRM_CANCEL = {
    'error_cause': None,
    'status': 'ok',
    'type': 'input',
    'numbers': '1',
}

OCTONODE_ASK_RESULT_BAD_INPUT = {
    'error_cause': None,
    'status': 'ok',
    'type': 'input',
    'numbers': '2',
}

OCTONODE_ASK_RESULT_ERROR = {
    'error_cause': 'unexcpected_error',
    'status': 'error',
    'type': 'input',
}

OCTONODE_SWITCH_OK_RESULT = {'status': 'ok', 'type': 'switch'}

OCTONODE_SWITCH_ERROR_RESULT = {'status': 'error', 'type': 'switch'}

ANSWER_REPLY = {'type': 'answer', 'params': {'start_recording': True}}

HELLO_REPLY = {
    'params': {
        'relative_path': (
            f'ivr_flow_worker/{FLOW_ID}/disp_after_call.hello_request.wav'
        ),
    },
    'type': 'play',
}

ASK_FOR_CANCEL_ORDER_REPLY = {
    'params': {
        'relative_path': (
            f'ivr_flow_worker/{FLOW_ID}/disp_after_call.cancel_request.wav'
        ),
        'timeout': 4,
    },
    'type': 'input',
}

ORDER_CANCELLED_REPLY = {
    'params': {
        'relative_path': (
            f'ivr_flow_worker/{FLOW_ID}/disp_after_call.cancel_success.wav'
        ),
    },
    'type': 'play',
}

TELL_ABOUT_OPERATOR_SWITCH_REPLY = {
    'params': {
        'relative_path': (
            f'ivr_flow_worker/{FLOW_ID}/disp_after_call.operator_switch.wav'
        ),
    },
    'type': 'play',
}

ORDER_SKIPPED_REPLY = {
    'params': {
        'relative_path': (
            f'ivr_flow_worker/{FLOW_ID}/disp_after_call.cancel_skipped.wav'
        ),
    },
    'type': 'play',
}

CANCEL_ERROR_REPLY = {
    'params': {
        'relative_path': (
            f'ivr_flow_worker/{FLOW_ID}/disp_after_call.cancel_error.wav'
        ),
    },
    'type': 'play',
}

TRY_ONE_MORE_TIME_REPLY = {
    'params': {
        'relative_path': (
            f'ivr_flow_worker/{FLOW_ID}/disp_after_call.try_again.wav'
        ),
    },
    'type': 'play',
}

BAD_INPUT_REPLY = {
    'params': {
        'relative_path': (
            f'ivr_flow_worker/{FLOW_ID}/disp_after_call.bad_input.wav'
        ),
    },
    'type': 'play',
}

FORWARDING_ERROR_REPLY = {
    'params': {
        'relative_path': (
            f'ivr_flow_worker/{FLOW_ID}/disp_after_call.error_forwarding.wav'
        ),
    },
    'type': 'play',
}

HANGUP_REPLY = {'type': 'hangup'}

DONE_REPLY = {'type': 'done'}

SWITCH_REPLY = {
    'params': {'call_to': '123', 'use_deflect_switch': True},
    'type': 'switch',
}

FORCE_SWITCH_REPLY = {
    'params': {'call_to': '456', 'use_deflect_switch': True},
    'type': 'switch',
}

AFTER_DISP_CALL_MAIN_SCENARIO = [
    (OCTONODE_INITIAL, ANSWER_REPLY, None),
    (OCTONODE_ANSWER_RESULT_OK, HELLO_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, ASK_FOR_CANCEL_ORDER_REPLY, None),
    (OCTONODE_ASK_RESULT_CONFIRM_CANCEL, ORDER_CANCELLED_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, HANGUP_REPLY, None),
]

NO_ORDER_SCENARIO = [(OCTONODE_INITIAL, HANGUP_REPLY, None)]

TRANSPORTING_SCENARIO = [
    (OCTONODE_INITIAL, ANSWER_REPLY, None),
    (OCTONODE_ANSWER_RESULT_OK, HELLO_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, ASK_FOR_CANCEL_ORDER_REPLY, None),
    (OCTONODE_ASK_RESULT_CONFIRM_CANCEL, ORDER_SKIPPED_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, TELL_ABOUT_OPERATOR_SWITCH_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, SWITCH_REPLY, None),
    (OCTONODE_SWITCH_OK_RESULT, HANGUP_REPLY, None),
]

CANCEL_ERROR_SCENARIO = [
    (OCTONODE_INITIAL, ANSWER_REPLY, None),
    (OCTONODE_ANSWER_RESULT_OK, HELLO_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, ASK_FOR_CANCEL_ORDER_REPLY, None),
    (OCTONODE_ASK_RESULT_CONFIRM_CANCEL, CANCEL_ERROR_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, TRY_ONE_MORE_TIME_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, ASK_FOR_CANCEL_ORDER_REPLY, None),
    (OCTONODE_ASK_RESULT_CONFIRM_CANCEL, CANCEL_ERROR_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, TELL_ABOUT_OPERATOR_SWITCH_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, SWITCH_REPLY, None),
    (OCTONODE_SWITCH_OK_RESULT, HANGUP_REPLY, None),
]

BAD_INPUT_SCENARIO = [
    (OCTONODE_INITIAL, ANSWER_REPLY, None),
    (OCTONODE_ANSWER_RESULT_OK, HELLO_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, ASK_FOR_CANCEL_ORDER_REPLY, None),
    (OCTONODE_ASK_RESULT_BAD_INPUT, BAD_INPUT_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, TRY_ONE_MORE_TIME_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, ASK_FOR_CANCEL_ORDER_REPLY, None),
    (OCTONODE_ASK_RESULT_BAD_INPUT, BAD_INPUT_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, TELL_ABOUT_OPERATOR_SWITCH_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, SWITCH_REPLY, None),
    (OCTONODE_SWITCH_OK_RESULT, HANGUP_REPLY, None),
]

CANNOT_SWITCH_SCENARIO = [
    (OCTONODE_INITIAL, ANSWER_REPLY, None),
    (OCTONODE_ANSWER_RESULT_OK, HELLO_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, ASK_FOR_CANCEL_ORDER_REPLY, None),
    (OCTONODE_ASK_RESULT_BAD_INPUT, BAD_INPUT_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, TRY_ONE_MORE_TIME_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, ASK_FOR_CANCEL_ORDER_REPLY, None),
    (OCTONODE_ASK_RESULT_BAD_INPUT, BAD_INPUT_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, TELL_ABOUT_OPERATOR_SWITCH_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, SWITCH_REPLY, None),
    (OCTONODE_SWITCH_ERROR_RESULT, FORWARDING_ERROR_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, HANGUP_REPLY, None),
]

ASK_ERROR_SCENARIO = [
    (OCTONODE_INITIAL, ANSWER_REPLY, None),
    (OCTONODE_ANSWER_RESULT_OK, HELLO_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, ASK_FOR_CANCEL_ORDER_REPLY, None),
    (OCTONODE_ASK_RESULT_ERROR, ASK_FOR_CANCEL_ORDER_REPLY, None),
    (OCTONODE_ASK_RESULT_ERROR, HANGUP_REPLY, None),
]

TRANSPORTING_SCENARIO_SWITCH_DISABLED = [
    (OCTONODE_INITIAL, ANSWER_REPLY, None),
    (OCTONODE_ANSWER_RESULT_OK, HELLO_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, ASK_FOR_CANCEL_ORDER_REPLY, None),
    (OCTONODE_ASK_RESULT_CONFIRM_CANCEL, ORDER_SKIPPED_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, HANGUP_REPLY, None),
]

TRANSPORTING_SCENARIO_FORCE_SWITCH = [
    (OCTONODE_INITIAL, ANSWER_REPLY, None),
    (OCTONODE_ANSWER_RESULT_OK, HELLO_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, ASK_FOR_CANCEL_ORDER_REPLY, None),
    (OCTONODE_ASK_RESULT_CONFIRM_CANCEL, ORDER_SKIPPED_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, TELL_ABOUT_OPERATOR_SWITCH_REPLY, None),
    (OCTONODE_PLAY_OK_RESULT, FORCE_SWITCH_REPLY, None),
    (OCTONODE_SWITCH_OK_RESULT, HANGUP_REPLY, None),
]


@pytest.mark.now('2021-07-30T19:00:00.00Z')
@pytest.mark.config(
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        utils.DEFAULT_TAXI_PHONE: {'metaqueue': utils.DEFAULT_METAQUEUE},
    },
    IVR_DISPATCHER_ROUTING_METAQUEUE_MAP=utils.DEFAULT_REROUTE_METAQUEUES,
    CALLCENTER_METAQUEUES=[
        {
            'name': utils.DEFAULT_METAQUEUE,
            'number': '123',
            'allowed_clusters': ['1'],
        },
    ],
    IVR_DISPATCHER_AFTER_DISP_CALL_WORKER={
        'attempts': 2,
        'switch_enabled': True,
    },
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
            'outbound_number': UNDEFINED,
            'outbound_routes': {'__default__': fwo_utils.OPERATOR_GW},
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
    'scenario',
    (
        AFTER_DISP_CALL_MAIN_SCENARIO,
        NO_ORDER_SCENARIO,
        TRANSPORTING_SCENARIO,
        CANCEL_ERROR_SCENARIO,
        BAD_INPUT_SCENARIO,
        CANNOT_SWITCH_SCENARIO,
        ASK_ERROR_SCENARIO,
    ),
    ids=(
        'AFTER_DISP_CALL_MAIN_SCENARIO',
        'NO_ORDER_SCENARIO',
        'TRANSPORTING_SCENARIO',
        'CANCEL_ERROR_SCENARIO',
        'BAD_INPUT_SCENARIO',
        'CANNOT_SWITCH_SCENARIO',
        'ASK_ERROR_SCENARIO',
    ),
)
async def test_scenarios(
        taxi_ivr_dispatcher,
        mongodb,
        mockserver,
        mock_user_api,
        mock_int_authproxy,
        mock_personal,
        scenario,
        load_json,
):
    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        if scenario == NO_ORDER_SCENARIO:
            return {'orders': []}
        return {
            'orders': [
                {'orderid': utils.DEFAULT_ORDER_ID, 'status': 'driving'},
            ],
        }

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        if scenario == TRANSPORTING_SCENARIO:
            response['fields']['order']['taxi_status'] = 'transporting'
        return response

    @mockserver.json_handler('/int-authproxy/v1/orders/cancel')
    def _order_cancel(request):
        if scenario == CANCEL_ERROR_SCENARIO:
            return mockserver.make_response(status=500)
        return {}

    for action, reply, _ in scenario:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply


@pytest.mark.now('2021-07-30T19:00:00.00Z')
@pytest.mark.config(
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        utils.DEFAULT_TAXI_PHONE: {'metaqueue': utils.DEFAULT_METAQUEUE},
    },
    IVR_DISPATCHER_AFTER_DISP_CALL_WORKER={
        'attempts': 2,
        'switch_enabled': False,
    },
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
            'outbound_number': UNDEFINED,
            'outbound_routes': {'__default__': fwo_utils.OPERATOR_GW},
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
async def test_switch_disabled(
        taxi_ivr_dispatcher,
        mongodb,
        mockserver,
        mock_user_api,
        mock_int_authproxy,
        mock_personal,
        load_json,
):
    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        return {
            'orders': [
                {'orderid': utils.DEFAULT_ORDER_ID, 'status': 'driving'},
            ],
        }

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order']['taxi_status'] = 'transporting'
        return response

    @mockserver.json_handler('/int-authproxy/v1/orders/cancel')
    def _order_cancel(request):
        return {}

    for action, reply, _ in TRANSPORTING_SCENARIO_SWITCH_DISABLED:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply


@pytest.mark.now('2021-07-30T19:00:00.00Z')
@pytest.mark.config(
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        utils.DEFAULT_TAXI_PHONE: {'metaqueue': utils.DEFAULT_METAQUEUE},
    },
    IVR_DISPATCHER_AFTER_DISP_CALL_WORKER={
        'attempts': 2,
        'switch_enabled': True,
        'force_metaqueue_to_process_switch': 'force',
    },
    IVR_DISPATCHER_ROUTING_METAQUEUE_MAP=utils.DEFAULT_REROUTE_METAQUEUES,
    CALLCENTER_METAQUEUES=[
        {'name': 'force', 'number': '456', 'allowed_clusters': ['1']},
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
            'outbound_number': UNDEFINED,
            'outbound_routes': {'__default__': fwo_utils.OPERATOR_GW},
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
async def test_force_metaqueue_switch(
        taxi_ivr_dispatcher,
        mongodb,
        mockserver,
        mock_user_api,
        mock_int_authproxy,
        mock_personal,
        load_json,
):
    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        return {
            'orders': [
                {'orderid': utils.DEFAULT_ORDER_ID, 'status': 'driving'},
            ],
        }

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order']['taxi_status'] = 'transporting'
        return response

    @mockserver.json_handler('/int-authproxy/v1/orders/cancel')
    def _order_cancel(request):
        return {}

    for action, reply, _ in TRANSPORTING_SCENARIO_FORCE_SWITCH:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
