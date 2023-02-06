# pylint: disable=too-many-lines

import functools

import pytest

from tests_ivr_dispatcher import utils

FINISHED_WITH_ERRORS = 'finished_with_errors'
ORIGINATING = 'originating'
FINISHED = 'finished'
ORDER_INFO_SPEAKING = 'order_info_speaking'
PARTNER_INFO_SPEAKING = 'partner_info_speaking'
PARTNER_INFO_MENU = 'partner_info_waiting_for_input'
OFFER_CONFIRMATION = 'offer_waiting_for_confirmation'


def context_assert_final_state(state, db):
    db_session_doc = db.ivr_disp_sessions.find_one(
        {'_id': utils.DEFAULT_SESSION_ID},
    )
    assert 'context' in db_session_doc
    assert 'state' in db_session_doc['context']
    assert db_session_doc['context']['state'] == state


def context_assert_final_state_kz(state, db):
    db_session_doc = db.ivr_disp_sessions.find_one(
        {'_id': utils.KZ_SESSION_ID},
    )
    assert 'context' in db_session_doc
    assert 'state' in db_session_doc['context']
    assert db_session_doc['context']['state'] == state


# Configs
IVR_DISPATCHER_PROMPT_SETS = {
    'ivr_workers': {
        'oiw.partner_dtmf': {
            'text': 'PDYA',
            'tts_speed': 1.1,
            'prompt_id': 'oiw.partner_dtmf.wav',
        },
        'oiw.partner_not_found': {
            'text': 'PNF',
            'prompt_id': 'oiw.partner_not_found.wav',
        },
        'oiw.bad_user_input': {
            'prompt_id': 'oiw.bad_user_input.wav',
            'text': (
                'Ввод не распознан, пожалуйста, перезвоните, '
                'если нужно оформить новый заказ.'
            ),
        },
        'oiw.confirm_offer': {
            'prompt_id': 'oiw.confirm_offer.wav',
            'text': 'Если хотите повторить заказ по этой цене - нажмите 1.',
            'tts_speed': 1.1,
        },
        'oiw.failed_order_creation': {
            'prompt_id': 'oiw.failed_order_creation.wav',
            'text': (
                'К сожалению, не удалось создать заказ. Пожалуйста, '
                'перезвоните, если нужно оформить новый заказ.'
            ),
        },
        'oiw.successful_order_creation': {
            'prompt_id': 'oiw.successful_order_creation.wav',
            'text': 'Спасибо, заказ принят, ищем машину, ожидайте звонка.',
        },
    },
    'override_kz_call_center': {
        'oiw.partner_dtmf': {
            'text': 'PDKZ',
            'tts_speed': 1.1,
            'prompt_id': 'oiw.partner_dtmf.wav',
        },
        'oiw.partner_not_found': {
            'text': 'PNFKZ',
            'prompt_id': 'oiw.partner_not_found.wav',
        },
    },
}
# Config variations for override tests
IVR_DISPATCHER_PROMPT_SETS_SAY_ONLY = {
    'ivr_workers': {
        'oiw.partner_dtmf': {'text': 'PDYA', 'tts_speed': 1.1},
        'oiw.partner_not_found': {'text': 'PNF'},
    },
    'override_kz_call_center': {
        'oiw.partner_dtmf': {'text': 'PDKZ', 'tts_speed': 1.1},
        'oiw.partner_not_found': {'text': 'PNFKZ'},
    },
}
IVR_DISPATCHER_PROMPT_SETS_SAY_ONLY_NO_OVERRIDE = {
    'ivr_workers': {
        'oiw.partner_dtmf': {'text': 'PDYA', 'tts_speed': 1.1},
        'oiw.partner_not_found': {'text': 'PNF'},
    },
    'override_kz_call_center': {
        'oiw.nonsence': {'text': 'NNS', 'tts_speed': 1.1},
    },
}
IVR_DISPATCHER_PROMPT_SETS_NO_OVERRIDE = {
    'ivr_workers': {
        'oiw.partner_dtmf': {
            'text': 'PDYA',
            'tts_speed': 1.1,
            'prompt_id': 'oiw.partner_dtmf.wav',
        },
        'oiw.partner_not_found': {
            'text': 'PNF',
            'prompt_id': 'oiw.partner_not_found.wav',
        },
    },
    'override_kz_call_center': {
        'oiw.nonsence': {'text': 'NNS', 'tts_speed': 1.1},
    },
}
IVR_DISPATCHER_PROMPT_SETS_NO_OVERRIDE_KEYSET = {
    'ivr_workers': {
        'oiw.partner_dtmf': {
            'text': 'PDYA',
            'tts_speed': 1.1,
            'prompt_id': 'oiw.partner_dtmf.wav',
        },
        'oiw.partner_not_found': {
            'text': 'PNF',
            'prompt_id': 'oiw.partner_not_found.wav',
        },
    },
}
IVR_DISPATCHER_PROMPT_SETS_NO_MAIN_KEYSET = {
    'nonsence': {'no_sence': {'text': 'NNS'}},
}
APPLICATION_MAP_TRANSLATION_KZ = {
    'kz_call_center': {
        'ivr_workers': 'override_kz_call_center',
        'notify': 'override_kz_call_center',
    },
}

# Octonode action results
OCTONODE_INITIAL_RESULT_OK = {
    'caller_number': utils.DEFAULT_TAXI_PHONE,  # call_from
    'called_number': utils.DEFAULT_USER_PHONE,  # call_to
    'status': 'ok',
    'type': 'initial',
}
OCTONODE_INITIAL_RESULT_KZ = {
    'caller_number': utils.KZ_NUMBER,  # call_from
    'called_number': utils.DEFAULT_USER_PHONE,
    'status': 'ok',
    'type': 'initial',
}
OCTONODE_INITIAL_RESULT_ERROR = {
    'called_number': utils.DEFAULT_TAXI_PHONE,
    'caller_number': utils.DEFAULT_USER_PHONE,
    'status': 'error',
    'type': 'initial',
}
OCTONODE_ORIGINATED_RESULT_OK = {'status': 'ok', 'type': 'originate'}
OCTONODE_ORIGINATED_RESULT_ERROR = {'status': 'error', 'type': 'originate'}
OCTONODE_SPEAK_RESULT_OK = {'status': 'ok', 'type': 'speak'}
OCTONODE_CREATE_ORDER_RESULT_OK = {'status': 'ok', 'type': 'speak'}
OCTONODE_PLAY_RESULT_OK = {'status': 'ok', 'type': 'play'}
OCTONODE_SPEAK_RESULT_INTERRUPTED_FAR = {
    'status': 'error',
    'type': 'speak',
    'error_cause': 'say_interrupted=initiator_hangup, speak_time=1000.123456',
}
OCTONODE_SPEAK_RESULT_INTERRUPTED_NEAR = {
    'status': 'error',
    'type': 'speak',
    'error_cause': 'say_interrupted=initiator_hangup, speak_time=0.123456',
}
OCTONODE_SPEAK_RESULT_NO_USER_ANSWER = {
    'status': 'error',
    'type': 'speak',
    'error_cause': 'no user answer',
}
OCTONODE_INPUT_RESULT_OK = {'type': 'input', 'status': 'ok', 'numbers': '1'}
OCTONODE_INPUT_RESULT_BAD_NUMBER = {
    'type': 'input',
    'status': 'ok',
    'numbers': '3',
}
OCTONODE_INPUT_RESULT_ERROR = {'type': 'input', 'status': 'error'}

# Dispatcher possible answers
DISPATCHER_ORIGINATE_REPLY = {
    'params': {
        'answer_timeout': 30,
        'call_from': utils.DEFAULT_TAXI_PHONE,
        'call_to': utils.DEFAULT_USER_PHONE,
        'early_answer': 1,
        'progress_timeout': 65,
        'start_recording': False,
        'gateways': 'ivr_order_informer',
    },
    'type': 'originate',
}

DISPATCHER_ORIGINATE_REPLY_KZ = {
    'params': {
        'answer_timeout': 30,
        'call_from': utils.KZ_NUMBER,
        'call_to': utils.DEFAULT_USER_PHONE,
        'early_answer': 1,
        'progress_timeout': 65,
        'start_recording': False,
        'gateways': 'ivr_via_noc_kz',
    },
    'type': 'originate',
}

DISPATCHER_REORDER_CONFIRMATION_REPLY = {
    'params': {
        'relative_path': 'ivr_workers/oiw.confirm_offer.wav',
        'timeout': 10,
    },
    'type': 'input',
}
DISPATCHER_CREATE_ORDER_REPLY = {
    'params': {
        'relative_path': 'ivr_workers/oiw.successful_order_creation.wav',
    },
    'type': 'play',
}

DISPATCHER_INPUT_REPLY = {
    'params': {
        'relative_path': 'ivr_workers/oiw.partner_dtmf.wav',
        'timeout': 10,
    },
    'type': 'input',
}
DISPATCHER_INPUT_REPLY_KZ = {
    'params': {
        'relative_path': 'override_kz_call_center/oiw.partner_dtmf.wav',
        'timeout': 10,
    },
    'type': 'input',
}
DISPATCHER_INPUT_REPLY_SAY_OVERRIDE = {
    'params': {
        'text': 'PDKZ',
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'speed': 0.9,
        'voice': 'alena',
        'timeout': 10,
    },
    'type': 'input',
}
DISPATCHER_INPUT_REPLY_SAY_NO_OVERRIDE = {
    'params': {
        'text': 'PDYA',
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'speed': 0.9,
        'voice': 'alena',
        'timeout': 10,
    },
    'type': 'input',
}
DISPATCHER_HANGUP_REPLY = {'type': 'hangup'}

DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY = {
    'params': {
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'speed': 0.9,
        'text': 'Здравствуйте. В 22:40 приедет синий Audi A8. Номер A666MP77.',
        'voice': 'alena',
    },
    'type': 'speak',
}

DISPATCHER_ON_ASSIGNED_PREORDER_SPEAK_REPLY = {
    'params': {
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'speed': 0.9,
        'text': (
            'Здравствуйте. В 22:40 приедет синий Audi A8. '
            'Номер A666MP77.Цена поездки 75 рублей.'
        ),
        'voice': 'alena',
    },
    'type': 'speak',
}

DISPATCHER_CAR_NOT_FOUND_SPEAK_REPLY = {
    'params': {
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'speed': 0.9,
        'text': 'Ищем машину',
        'voice': 'alena',
    },
    'type': 'speak',
}

DISPATCHER_CAR_NOT_FOUND_REORDER_ENABLE_SPEAK_REPLY = {
    'params': {
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'speed': 0.9,
        'text': (
            'К сожалению, машина по вашему заказу не найдена. '
            'Сейчас стоимость поездки от адреса Россия, Москва, '
            'ул.Льва Толстого, д.20 до адреса Россия, Москва, '
            'ул.Льва Толстого, д.12 составляет 363 рубля.'
        ),
        'voice': 'alena',
    },
    'type': 'speak',
}

DISPATCHER_PARTNER_INPUT_SPEAK_REPLY = {
    'params': {
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'speed': 0.9,
        'text': (
            'Вас обслуживает Партнёр  Ромашка,  1 2 3 4 5 6 7 8 , '
            'Рязанское шоссе,  Перевозчик  Иван,  1 2 3 4 5 6 , '
            'Варшавское шоссе, , 11-13 .'
        ),
        'voice': 'alena',
    },
    'type': 'speak',
}

DISPATCHER_NO_PARTNER_PLAY_REPLY = {
    'params': {'relative_path': 'ivr_workers/oiw.partner_not_found.wav'},
    'type': 'play',
}
DISPATCHER_NO_PARTNER_PLAY_REPLY_KZ = {
    'params': {
        'relative_path': 'override_kz_call_center/oiw.partner_not_found.wav',
    },
    'type': 'play',
}
DISPATCHER_NO_PARTNER_SPEAK_REPLY = {
    'params': {
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'speed': 0.9,
        'text': 'PNF',
        'voice': 'alena',
    },
    'type': 'speak',
}
DISPATCHER_NO_PARTNER_SPEAK_REPLY_KZ = {
    'params': {
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'speed': 0.9,
        'text': 'PNFKZ',
        'voice': 'alena',
    },
    'type': 'speak',
}

# Scenarios
SIMPLE_CALL_SCENARIO = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ORIGINATE_REPLY,
        [functools.partial(context_assert_final_state, ORIGINATING)],
    ),
    (
        OCTONODE_ORIGINATED_RESULT_OK,
        DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
        [functools.partial(context_assert_final_state, ORDER_INFO_SPEAKING)],
    ),
    (
        OCTONODE_SPEAK_RESULT_OK,
        DISPATCHER_INPUT_REPLY,
        [functools.partial(context_assert_final_state, PARTNER_INFO_MENU)],
    ),
    (
        OCTONODE_INPUT_RESULT_OK,
        DISPATCHER_PARTNER_INPUT_SPEAK_REPLY,
        [functools.partial(context_assert_final_state, PARTNER_INFO_SPEAKING)],
    ),
    (
        OCTONODE_SPEAK_RESULT_OK,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_final_state, FINISHED)],
    ),
]

PREORDER_CALL_SCENARIO = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ORIGINATE_REPLY,
        [functools.partial(context_assert_final_state, ORIGINATING)],
    ),
    (
        OCTONODE_ORIGINATED_RESULT_OK,
        DISPATCHER_ON_ASSIGNED_PREORDER_SPEAK_REPLY,
        [functools.partial(context_assert_final_state, ORDER_INFO_SPEAKING)],
    ),
]

SIMPLE_SMS_SCENARIO = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ORIGINATE_REPLY,
        [functools.partial(context_assert_final_state, ORIGINATING)],
    ),
    (
        OCTONODE_ORIGINATED_RESULT_ERROR,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_final_state, FINISHED_WITH_ERRORS)],
    ),
]

INITIAL_ERROR_SCENARIO = [
    (
        OCTONODE_INITIAL_RESULT_ERROR,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_final_state, FINISHED_WITH_ERRORS)],
    ),
]

ORIGINATED_ERROR_SCENARIO = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ORIGINATE_REPLY,
        [functools.partial(context_assert_final_state, ORIGINATING)],
    ),
    (
        OCTONODE_ORIGINATED_RESULT_ERROR,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_final_state, FINISHED_WITH_ERRORS)],
    ),
]

SPEAK_INTERRUPTED_FAR_SCENARIO = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ORIGINATE_REPLY,
        [functools.partial(context_assert_final_state, ORIGINATING)],
    ),
    (
        OCTONODE_ORIGINATED_RESULT_OK,
        DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
        [functools.partial(context_assert_final_state, ORDER_INFO_SPEAKING)],
    ),
    (
        OCTONODE_SPEAK_RESULT_INTERRUPTED_FAR,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_final_state, FINISHED)],
    ),
]

SPEAK_INTERRUPTED_NEAR_SCENARIO = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ORIGINATE_REPLY,
        [functools.partial(context_assert_final_state, ORIGINATING)],
    ),
    (
        OCTONODE_ORIGINATED_RESULT_OK,
        DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
        [functools.partial(context_assert_final_state, ORDER_INFO_SPEAKING)],
    ),
    (
        OCTONODE_SPEAK_RESULT_INTERRUPTED_NEAR,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_final_state, FINISHED_WITH_ERRORS)],
    ),
]

SPEAK_NO_USER_ANSWER_SCENARIO = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ORIGINATE_REPLY,
        [functools.partial(context_assert_final_state, ORIGINATING)],
    ),
    (
        OCTONODE_ORIGINATED_RESULT_OK,
        DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
        [functools.partial(context_assert_final_state, ORDER_INFO_SPEAKING)],
    ),
    (
        OCTONODE_SPEAK_RESULT_NO_USER_ANSWER,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_final_state, FINISHED_WITH_ERRORS)],
    ),
]

BAD_USER_INPUT_SCENARIO = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ORIGINATE_REPLY,
        [functools.partial(context_assert_final_state, ORIGINATING)],
    ),
    (
        OCTONODE_ORIGINATED_RESULT_OK,
        DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
        [functools.partial(context_assert_final_state, ORDER_INFO_SPEAKING)],
    ),
    (
        OCTONODE_SPEAK_RESULT_OK,
        DISPATCHER_INPUT_REPLY,
        [functools.partial(context_assert_final_state, PARTNER_INFO_MENU)],
    ),
    (
        OCTONODE_INPUT_RESULT_BAD_NUMBER,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_final_state, FINISHED)],
    ),
]

CAR_NOT_FOUND_REORDER_SCENARIO = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ORIGINATE_REPLY,
        [functools.partial(context_assert_final_state, ORIGINATING)],
    ),
    (
        OCTONODE_ORIGINATED_RESULT_OK,
        DISPATCHER_CAR_NOT_FOUND_REORDER_ENABLE_SPEAK_REPLY,
        [functools.partial(context_assert_final_state, ORDER_INFO_SPEAKING)],
    ),
    (
        OCTONODE_SPEAK_RESULT_OK,
        DISPATCHER_REORDER_CONFIRMATION_REPLY,
        [functools.partial(context_assert_final_state, OFFER_CONFIRMATION)],
    ),
    (
        OCTONODE_INPUT_RESULT_OK,
        DISPATCHER_CREATE_ORDER_REPLY,
        [functools.partial(context_assert_final_state, FINISHED)],
    ),
]

CAR_NOT_FOUND_SCENARIO = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ORIGINATE_REPLY,
        [functools.partial(context_assert_final_state, ORIGINATING)],
    ),
    (
        OCTONODE_ORIGINATED_RESULT_OK,
        DISPATCHER_CAR_NOT_FOUND_SPEAK_REPLY,
        [functools.partial(context_assert_final_state, ORDER_INFO_SPEAKING)],
    ),
    (
        OCTONODE_SPEAK_RESULT_OK,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_final_state, FINISHED)],
    ),
]

USER_INPUT_ERROR_SCENARIO = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ORIGINATE_REPLY,
        [functools.partial(context_assert_final_state, ORIGINATING)],
    ),
    (
        OCTONODE_ORIGINATED_RESULT_OK,
        DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
        [functools.partial(context_assert_final_state, ORDER_INFO_SPEAKING)],
    ),
    (
        OCTONODE_SPEAK_RESULT_OK,
        DISPATCHER_INPUT_REPLY,
        [functools.partial(context_assert_final_state, PARTNER_INFO_MENU)],
    ),
    (
        OCTONODE_INPUT_RESULT_ERROR,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_final_state, FINISHED)],
    ),
]

NO_PARTNER_CALL_SCENARIO = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ORIGINATE_REPLY,
        [functools.partial(context_assert_final_state, ORIGINATING)],
    ),
    (
        OCTONODE_ORIGINATED_RESULT_OK,
        DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
        [functools.partial(context_assert_final_state, ORDER_INFO_SPEAKING)],
    ),
    (
        OCTONODE_SPEAK_RESULT_OK,
        DISPATCHER_INPUT_REPLY,
        [functools.partial(context_assert_final_state, PARTNER_INFO_MENU)],
    ),
    (
        OCTONODE_INPUT_RESULT_OK,
        DISPATCHER_NO_PARTNER_PLAY_REPLY,
        [functools.partial(context_assert_final_state, PARTNER_INFO_SPEAKING)],
    ),
    (
        OCTONODE_PLAY_RESULT_OK,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_final_state, FINISHED)],
    ),
]

TEST_NEW_RECALLS = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ORIGINATE_REPLY,
        [functools.partial(context_assert_final_state, ORIGINATING)],
    ),
    (
        OCTONODE_ORIGINATED_RESULT_ERROR,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_final_state, FINISHED_WITH_ERRORS)],
    ),
]

PARTNER_INFO_KZ_SCENARIO = [
    (
        OCTONODE_INITIAL_RESULT_KZ,
        DISPATCHER_ORIGINATE_REPLY_KZ,
        [functools.partial(context_assert_final_state_kz, ORIGINATING)],
    ),
    (
        OCTONODE_ORIGINATED_RESULT_OK,
        DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
        [
            functools.partial(
                context_assert_final_state_kz, ORDER_INFO_SPEAKING,
            ),
        ],
    ),
    (
        OCTONODE_SPEAK_RESULT_OK,
        DISPATCHER_INPUT_REPLY_KZ,
        [functools.partial(context_assert_final_state_kz, PARTNER_INFO_MENU)],
    ),
]


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_OIW_SETTINGS={
        'originate_attempts': 1,
        'originate_retry_delay': 60,
        'sufficient_speak_time': 4,
        'speed': {'__default__': 0.9},
    },
    IVR_DISPATCHER_PROMPT_SETS=IVR_DISPATCHER_PROMPT_SETS,
    APPLICATION_MAP_TRANSLATIONS=APPLICATION_MAP_TRANSLATION_KZ,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.KZ_NUMBER: {
            'application': 'kz_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
)
@pytest.mark.parametrize(
    'scenario',
    [
        SIMPLE_CALL_SCENARIO,
        SIMPLE_SMS_SCENARIO,
        INITIAL_ERROR_SCENARIO,
        ORIGINATED_ERROR_SCENARIO,
        SPEAK_INTERRUPTED_FAR_SCENARIO,
        SPEAK_INTERRUPTED_NEAR_SCENARIO,
        SPEAK_NO_USER_ANSWER_SCENARIO,
        BAD_USER_INPUT_SCENARIO,
        USER_INPUT_ERROR_SCENARIO,
        PARTNER_INFO_KZ_SCENARIO,
    ],
    ids=(
        'simple_call_scenario',
        'simple_sms_scenario',
        'initial_error',
        'originated_error',
        'speak_interrupted_far',
        'speak_interrupted_near',
        'no_user_answer',
        'bad_user_input',
        'input_error',
        'partner_info_kz_override',
    ),
)
async def test_state_machine_no_retries(
        taxi_ivr_dispatcher,
        mongodb,
        scenario,
        mock_order_core,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
        mock_parks,
):
    for action, reply, checks in scenario:
        if scenario == PARTNER_INFO_KZ_SCENARIO:
            session_id = utils.KZ_SESSION_ID
        else:
            session_id = utils.DEFAULT_SESSION_ID
        request = {'session_id': session_id, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_OIW_SETTINGS={
        'originate_attempts': 1,
        'originate_retry_delay': 60,
        'sufficient_speak_time': 4,
    },
    IVR_DISPATCHER_PROMPT_SETS=IVR_DISPATCHER_PROMPT_SETS,
    APPLICATION_MAP_TRANSLATIONS=APPLICATION_MAP_TRANSLATION_KZ,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.KZ_NUMBER: {
            'application': 'kz_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
)
async def test_no_partner_info(
        mockserver,
        taxi_ivr_dispatcher,
        mongodb,
        mock_order_core,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
):
    @mockserver.json_handler('/parks/cars/legal-entities')
    async def no_parks(request):  # pylint: disable=W0612
        return mockserver.make_response(status=404)

    for action, reply, checks in NO_PARTNER_CALL_SCENARIO:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_OIW_SETTINGS={
        'originate_attempts': 1,
        'originate_retry_delay': 60,
        'sufficient_speak_time': 4,
    },
    IVR_DISPATCHER_PROMPT_SETS=IVR_DISPATCHER_PROMPT_SETS,
    APPLICATION_MAP_TRANSLATIONS=APPLICATION_MAP_TRANSLATION_KZ,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.KZ_NUMBER: {
            'application': 'kz_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
)
async def test_preorder_text(
        taxi_ivr_dispatcher,
        mongodb,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
        mock_parks,
        load_json,
        mockserver,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order']['preorder_request_id'] = 'tadada'
        return response

    for action, reply, checks in PREORDER_CALL_SCENARIO:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)


@pytest.mark.now('2019-01-01T00:00:00')
@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_OIW_SETTINGS={
        'originate_attempts': 1,
        'originate_retry_delay': 60,
        'sufficient_speak_time': 4,
        'speed': {'__default__': 0.9, 'partner_menu': 1.0},
    },
    IVR_DISPATCHER_PROMPT_SETS=IVR_DISPATCHER_PROMPT_SETS,
    APPLICATION_MAP_TRANSLATIONS=APPLICATION_MAP_TRANSLATION_KZ,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.KZ_NUMBER: {
            'application': 'kz_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
)
async def test_new_recalls_from_worker(
        taxi_ivr_dispatcher,
        mongodb,
        mock_order_core,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
        mock_parks,
        stq,
):
    for action, reply, checks in TEST_NEW_RECALLS:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_OIW_SETTINGS={
        'originate_attempts': 1,
        'originate_retry_delay': 60,
        'sufficient_speak_time': 4,
        'speed': {'__default__': 0.9, 'partner_menu': 1.0},
    },
    APPLICATION_MAP_TRANSLATIONS=APPLICATION_MAP_TRANSLATION_KZ,
)
@pytest.mark.parametrize(
    'promptset, dispatcher_response',
    [
        (IVR_DISPATCHER_PROMPT_SETS, DISPATCHER_INPUT_REPLY_KZ),
        (
            IVR_DISPATCHER_PROMPT_SETS_SAY_ONLY,
            DISPATCHER_INPUT_REPLY_SAY_OVERRIDE,
        ),
        (IVR_DISPATCHER_PROMPT_SETS_NO_OVERRIDE, DISPATCHER_INPUT_REPLY),
        (
            IVR_DISPATCHER_PROMPT_SETS_SAY_ONLY_NO_OVERRIDE,
            DISPATCHER_INPUT_REPLY_SAY_NO_OVERRIDE,
        ),
        (
            IVR_DISPATCHER_PROMPT_SETS_NO_OVERRIDE_KEYSET,
            DISPATCHER_INPUT_REPLY,
        ),
        (IVR_DISPATCHER_PROMPT_SETS_NO_MAIN_KEYSET, DISPATCHER_HANGUP_REPLY),
    ],
    ids=(
        'good_override',
        'say_only',
        'no_key_override',
        'say_only_no_key_override',
        'no_override_keyset',
        'no_main_keyset',
    ),
)
async def test_input_overrides(
        taxi_ivr_dispatcher,
        mongodb,
        mock_order_core,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
        mock_parks,
        stq,
        taxi_config,
        promptset,
        dispatcher_response,
):
    mongodb.ivr_disp_sessions.update_one(
        {'_id': utils.KZ_SESSION_ID},
        {
            '$set': {
                'context.state': ORDER_INFO_SPEAKING,
                'context.called_number': utils.DEFAULT_USER_PHONE,
                'context.caller_number': utils.KZ_NUMBER,
            },
        },
    )
    taxi_config.set_values({'IVR_DISPATCHER_PROMPT_SETS': promptset})
    request = {
        'session_id': utils.KZ_SESSION_ID,
        'action': OCTONODE_SPEAK_RESULT_OK,
    }
    response = await taxi_ivr_dispatcher.post('/action', json=request)
    assert response.status == 200, response.text
    assert response.json() == dispatcher_response


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_OIW_SETTINGS={
        'originate_attempts': 1,
        'originate_retry_delay': 60,
        'sufficient_speak_time': 4,
        'speed': {'__default__': 0.9, 'partner_menu': 1.0},
    },
    APPLICATION_MAP_TRANSLATIONS=APPLICATION_MAP_TRANSLATION_KZ,
)
@pytest.mark.parametrize(
    'promptset, dispatcher_response',
    [
        (IVR_DISPATCHER_PROMPT_SETS, DISPATCHER_NO_PARTNER_PLAY_REPLY_KZ),
        (
            IVR_DISPATCHER_PROMPT_SETS_SAY_ONLY,
            DISPATCHER_NO_PARTNER_SPEAK_REPLY_KZ,
        ),
        (
            IVR_DISPATCHER_PROMPT_SETS_NO_OVERRIDE,
            DISPATCHER_NO_PARTNER_PLAY_REPLY,
        ),
        (
            IVR_DISPATCHER_PROMPT_SETS_SAY_ONLY_NO_OVERRIDE,
            DISPATCHER_NO_PARTNER_SPEAK_REPLY,
        ),
        (
            IVR_DISPATCHER_PROMPT_SETS_NO_OVERRIDE_KEYSET,
            DISPATCHER_NO_PARTNER_PLAY_REPLY,
        ),
        (IVR_DISPATCHER_PROMPT_SETS_NO_MAIN_KEYSET, DISPATCHER_HANGUP_REPLY),
    ],
    ids=(
        'good_override',
        'say_only_override',
        'no_key_prompt_override',
        'say_only_no_key_override',
        'no_override_keyset',
        'no_main_keyset',
    ),
)
async def test_prompt_overrides(
        taxi_ivr_dispatcher,
        mongodb,
        mock_order_core,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
        mock_parks,
        stq,
        mockserver,
        taxi_config,
        promptset,
        dispatcher_response,
):
    @mockserver.json_handler('/parks/cars/legal-entities')
    async def no_parks(request):  # pylint: disable=W0612
        return mockserver.make_response(status=404)

    mongodb.ivr_disp_sessions.update_one(
        {'_id': utils.KZ_SESSION_ID},
        {
            '$set': {
                'context.state': PARTNER_INFO_MENU,
                'context.called_number': utils.DEFAULT_USER_PHONE,
                'context.caller_number': utils.KZ_NUMBER,
            },
        },
    )
    taxi_config.set_values({'IVR_DISPATCHER_PROMPT_SETS': promptset})
    request = {
        'session_id': utils.KZ_SESSION_ID,
        'action': OCTONODE_INPUT_RESULT_OK,
    }
    response = await taxi_ivr_dispatcher.post('/action', json=request)
    assert response.status == 200, response.text
    assert response.json() == dispatcher_response


@pytest.mark.experiments3(filename='experiments3_reorder.json')
@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_OIW_SETTINGS={
        'originate_attempts': 1,
        'originate_retry_delay': 60,
        'sufficient_speak_time': 4,
        'speed': {'__default__': 0.9},
    },
    IVR_DISPATCHER_PROMPT_SETS=IVR_DISPATCHER_PROMPT_SETS,
    APPLICATION_MAP_TRANSLATIONS=APPLICATION_MAP_TRANSLATION_KZ,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.KZ_NUMBER: {
            'application': 'kz_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
)
async def test_reorder(
        taxi_ivr_dispatcher,
        mongodb,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_int_authproxy,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
        mock_parks,
        mockserver,
        load_json,
):
    @staticmethod
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order']['status'] = 'handle_search_failed'
        response['fields']['order']['taxi_status'] = None
        return response

    @mockserver.json_handler('/user-api/v2/user_phones/get')
    async def _retrieve_personal_id(request):
        data = request.json
        return {
            'id': data['id'],
            'personal_phone_id': utils.DEFAULT_PERSONAL_PHONE_ID,
        }

    for action, reply, checks in CAR_NOT_FOUND_REORDER_SCENARIO:
        session_id = utils.DEFAULT_SESSION_ID
        request = {'session_id': session_id, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)
