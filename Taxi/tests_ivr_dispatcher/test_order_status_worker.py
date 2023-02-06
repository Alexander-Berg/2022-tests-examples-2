# pylint: disable=C0302, C0103
import functools

import pytest

from tests_ivr_dispatcher import utils

INITIATING = 'initiating'
ANSWERING = 'answering'
ERROR_SPEAKING = 'error'
ORDER_INFO_SPEAKING = 'order_info_speaking'
PARTNER_INFO_SPEAKING = 'partner_info_speaking'
CANCELLED = 'cancelled'
CANCELLING_ERROR = 'cancelling_error'
MAIN_MENU_WAITING_FOR_INPUT = 'main_menu_waiting_for_input'
ON_SEARCH_MENU_WAITING_FOR_INPUT = 'menu_on_search_waiting_for_input'
ON_TRANSPORTING_MENU_WAITING_FOR_INPUT = (
    'menu_on_transporting_waiting_for_input'
)
CAR_NOT_FOUND_MENU_WAITING_FOR_INPUT = 'menu_car_not_found_waiting_for_input'
SWITCHING_TO_OPERATOR = 'switching_to_operator'
SWITCHING_TO_DRIVER = 'switching_to_driver'
DRIVER_SWITCHING_ERROR = 'driver_switch_error_speaking'
FINISHED = 'finished'
FINISHED_WITH_ERRORS = 'finished_with_errors'


def context_assert_final_state(state, db):
    db_session_doc = db.ivr_disp_sessions.find_one(
        {'_id': utils.DEFAULT_SESSION_ID},
    )
    assert 'context' in db_session_doc
    assert 'state' in db_session_doc['context']
    assert db_session_doc['context']['state'] == state


# Octonode action results
OCTONODE_INITIAL_RESULT_OK = {
    'caller_number': utils.DEFAULT_USER_PHONE,  # call_from
    'called_number': utils.DEFAULT_TAXI_PHONE,  # call_to
    'status': 'ok',
    'type': 'initial',
    'call_guid': 'SOME_CALL_GUID',
    'origin_called_number': utils.DEFAULT_TAXI_PHONE,
}
OCTONODE_INITIAL_RESULT_ERROR = {
    'caller_number': utils.DEFAULT_USER_PHONE,  # call_from
    'called_number': utils.DEFAULT_TAXI_PHONE,  # call_to
    'status': 'error',
    'type': 'initial',
    'call_guid': 'SOME_CALL_GUID',
    'origin_called_number': utils.DEFAULT_TAXI_PHONE,
}

OCTONODE_ANSWER_RESULT_OK = {'status': 'ok', 'type': 'answer'}
OCTONODE_ANSWER_RESULT_ERROR = {'status': 'error', 'type': 'answer'}

OCTONODE_SPEAK_RESULT_OK = {'status': 'ok', 'type': 'speak'}
OCTONODE_SPEAK_RESULT_ERROR = {'status': 'error', 'type': 'speak'}

OCTONODE_PLAY_RESULT_OK = {'status': 'ok', 'type': 'play'}

OCTONODE_PLAY_RESULT_ERROR = {'status': 'error', 'type': 'play'}

OCTONODE_INPUT_1 = {'type': 'input', 'status': 'ok', 'numbers': '1'}

OCTONODE_INPUT_2 = {'type': 'input', 'status': 'ok', 'numbers': '2'}

OCTONODE_INPUT_3 = {'type': 'input', 'status': 'ok', 'numbers': '3'}
OCTONODE_INPUT_4 = {'type': 'input', 'status': 'ok', 'numbers': '4'}
OCTONODE_INPUT_5 = {'type': 'input', 'status': 'ok', 'numbers': '5'}
OCTONODE_INPUT_6 = {'type': 'input', 'status': 'ok', 'numbers': '6'}
OCTONODE_INPUT_7 = {'type': 'input', 'status': 'ok', 'numbers': '7'}
OCTONODE_INPUT_8 = {'type': 'input', 'status': 'ok', 'numbers': '8'}
OCTONODE_INPUT_9 = {'type': 'input', 'status': 'ok', 'numbers': '9'}
OCTONODE_INPUT_RESULT_OPERATOR_SWITCH = {
    'type': 'input',
    'status': 'ok',
    'numbers': '0',
}
OCTONODE_INPUT_RESULT_ERROR = {'type': 'input', 'status': 'error'}

OCTONODE_SWITCH_RESULT_OK = {'type': 'switch', 'status': 'ok'}
OCTONODE_SWITCH_RESULT_ERROR = {'type': 'switch', 'status': 'error'}

# Dispatcher possible answers
DISPATCHER_ANSWER_REPLY = {
    'type': 'answer',
    'params': {'start_recording': False},
}


def octonode_input_result_order_info():
    return OCTONODE_INPUT_2


def octonode_input_result_driver_switch():
    return OCTONODE_INPUT_1


def dispatcher_input_reply():
    return {
        'params': {
            'relative_path': (
                'order_status_worker_2_0/'
                'osw.main_menu_with_to_driver_first.wav'
            ),
            'timeout': 10,
        },
        'type': 'input',
    }


DISPATCHER_ON_SEARCH_INPUT_REPLY = {
    'params': {
        'relative_path': 'order_status_worker_2_0/osw.menu_on_search.wav',
        'timeout': 10,
    },
    'type': 'input',
}


def dispatcher_on_transporting_input_reply():
    return {
        'params': {
            'relative_path': (
                'order_status_worker_2_0/'
                'osw.menu_on_transporting_with_to_driver.wav'
            ),
            'timeout': 10,
        },
        'type': 'input',
    }


DISPATCHER_CAR_NOT_FOUND_INPUT_REPLY = {
    'params': {
        'relative_path': 'order_status_worker_2_0/osw.menu_car_not_found.wav',
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
        'text': (
            'Здравствуйте. В 22:40 приедет синий Audi A8. Номер A666MP77.'
            'Цена поездки 75 рублей.'
        ),
        'voice': 'alena',
    },
    'type': 'speak',
}

DISPATCHER_ON_SEARCH_SPEAK_REPLY = {
    'params': {
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'speed': 0.9,
        'text': 'Ищем машину',
        'voice': 'alena',
    },
    'type': 'speak',
}
DISPATCHER_ON_TRANSPORTING_SPEAK_REPLY = {
    'params': {
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'speed': 0.9,
        'text': (
            'Вы едете на синий Audi A8. Номер A666MP77.. '
            'Желаем Вам приятной поездки.Цена поездки 75 рублей.'
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
        'text': (
            'К сожалению, не удалось найти такси. '
            'Пожалуйста, закажите повторно.'
        ),
        'voice': 'alena',
    },
    'type': 'speak',
}

DISPATCHER_SWITCH_TO_DRIVER_REPLY = {
    'type': 'switch',
    'params': {
        'answer_timeout': 30,
        'call_from': '2128610',
        'early_answer': 1,
        'gateways': 'ivr_customer_to_driver',
        'progress_timeout': 65,
        'start_recording': False,
        'call_to': utils.DEFAULT_DRIVER_PHONE,
    },
}


DISPATCHER_SWITCH_TO_OPERATOR_REPLY = {
    'type': 'switch',
    'params': {'use_deflect_switch': True, 'call_to': '123'},
}

DISPATCHER_PLAY_CANCELLATION_PROMPT = {
    'params': {'relative_path': 'order_status_worker_2_0/osw.cancelled.wav'},
    'type': 'play',
}

DISPATCHER_PLAY_ERROR_PROMPT = {
    'params': {'relative_path': 'order_status_worker_2_0/osw.error.wav'},
    'type': 'play',
}

DISPATCHER_PLAY_CANCELLATION_ERROR_PROMPT = {
    'params': {
        'relative_path': 'order_status_worker_2_0/osw.cancellation_error.wav',
    },
    'type': 'play',
}


DISPATCHER_PLAY_DRIVER_ERROR_PROMPT = {
    'params': {
        'relative_path': 'order_status_worker_2_0/osw.driver_switch_error.wav',
    },
    'type': 'play',
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

DISPATCHER_PLAY_NO_PARTNER_INFO_PROMPT = {
    'params': {
        'relative_path': 'order_status_worker_2_0/oiw.partner_not_found.wav',
    },
    'type': 'play',
}

# Scenarios
def simple_call_scenario():
    return [
        (
            OCTONODE_INITIAL_RESULT_OK,
            DISPATCHER_ANSWER_REPLY,
            [functools.partial(context_assert_final_state, ANSWERING)],
        ),
        (
            OCTONODE_ANSWER_RESULT_OK,
            DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
            [
                functools.partial(
                    context_assert_final_state, ORDER_INFO_SPEAKING,
                ),
            ],
        ),
        (
            OCTONODE_SPEAK_RESULT_OK,
            dispatcher_input_reply(),
            [
                functools.partial(
                    context_assert_final_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            octonode_input_result_order_info(),
            DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
            [
                functools.partial(
                    context_assert_final_state, ORDER_INFO_SPEAKING,
                ),
            ],
        ),
        (
            OCTONODE_SPEAK_RESULT_OK,
            dispatcher_input_reply(),
            [
                functools.partial(
                    context_assert_final_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            OCTONODE_INPUT_4,
            DISPATCHER_PARTNER_INPUT_SPEAK_REPLY,
            [
                functools.partial(
                    context_assert_final_state, PARTNER_INFO_SPEAKING,
                ),
            ],
        ),
        (
            OCTONODE_SPEAK_RESULT_OK,
            dispatcher_input_reply(),
            [
                functools.partial(
                    context_assert_final_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        # etc
    ]


ON_SEARCH_SCENARIO = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ANSWER_REPLY,
        [functools.partial(context_assert_final_state, ANSWERING)],
    ),
    (
        OCTONODE_ANSWER_RESULT_OK,
        DISPATCHER_ON_SEARCH_SPEAK_REPLY,
        [functools.partial(context_assert_final_state, ORDER_INFO_SPEAKING)],
    ),
    (
        OCTONODE_SPEAK_RESULT_OK,
        DISPATCHER_ON_SEARCH_INPUT_REPLY,
        [
            functools.partial(
                context_assert_final_state, ON_SEARCH_MENU_WAITING_FOR_INPUT,
            ),
        ],
    ),
]


def all_kinds_of_input_number_on_search_scenario():
    return [
        *[
            (
                INPUT,
                {
                    'params': {'call_to': '123', 'use_deflect_switch': True},
                    'type': 'switch',
                },
                [
                    functools.partial(
                        context_assert_final_state, SWITCHING_TO_OPERATOR,
                    ),
                ],
            )
            for INPUT in (
                octonode_input_result_order_info(),
                octonode_input_result_driver_switch(),
                OCTONODE_INPUT_4,
                OCTONODE_INPUT_5,
                OCTONODE_INPUT_6,
                OCTONODE_INPUT_7,
                OCTONODE_INPUT_8,
                OCTONODE_INPUT_9,
                OCTONODE_INPUT_RESULT_OPERATOR_SWITCH,
            )
        ],
        (
            OCTONODE_INPUT_3,
            DISPATCHER_PLAY_CANCELLATION_PROMPT,
            [functools.partial(context_assert_final_state, CANCELLED)],
        ),
    ]


def on_transporting_scenario():
    return [
        (
            OCTONODE_INITIAL_RESULT_OK,
            DISPATCHER_ANSWER_REPLY,
            [functools.partial(context_assert_final_state, ANSWERING)],
        ),
        (
            OCTONODE_ANSWER_RESULT_OK,
            DISPATCHER_ON_TRANSPORTING_SPEAK_REPLY,
            [
                functools.partial(
                    context_assert_final_state, ORDER_INFO_SPEAKING,
                ),
            ],
        ),
        (
            OCTONODE_SPEAK_RESULT_OK,
            dispatcher_on_transporting_input_reply(),
            [
                functools.partial(
                    context_assert_final_state,
                    ON_TRANSPORTING_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
    ]


def on_transporting_order_info_scenario():
    return [
        (
            OCTONODE_INITIAL_RESULT_OK,
            DISPATCHER_ANSWER_REPLY,
            [functools.partial(context_assert_final_state, ANSWERING)],
        ),
        (
            OCTONODE_ANSWER_RESULT_OK,
            DISPATCHER_ON_TRANSPORTING_SPEAK_REPLY,
            [
                functools.partial(
                    context_assert_final_state, ORDER_INFO_SPEAKING,
                ),
            ],
        ),
        (
            OCTONODE_SPEAK_RESULT_OK,
            dispatcher_on_transporting_input_reply(),
            [
                functools.partial(
                    context_assert_final_state,
                    ON_TRANSPORTING_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            {'type': 'input', 'status': 'ok', 'numbers': '1'},
            DISPATCHER_ON_TRANSPORTING_SPEAK_REPLY,
            [
                functools.partial(
                    context_assert_final_state, ORDER_INFO_SPEAKING,
                ),
            ],
        ),
    ]


def on_transporting_switch_to_driver_scenario():
    result = [
        (
            OCTONODE_INITIAL_RESULT_OK,
            DISPATCHER_ANSWER_REPLY,
            [functools.partial(context_assert_final_state, ANSWERING)],
        ),
        (
            OCTONODE_ANSWER_RESULT_OK,
            DISPATCHER_ON_TRANSPORTING_SPEAK_REPLY,
            [
                functools.partial(
                    context_assert_final_state, ORDER_INFO_SPEAKING,
                ),
            ],
        ),
        (
            OCTONODE_SPEAK_RESULT_OK,
            dispatcher_on_transporting_input_reply(),
            [
                functools.partial(
                    context_assert_final_state,
                    ON_TRANSPORTING_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            OCTONODE_INPUT_2,
            DISPATCHER_SWITCH_TO_DRIVER_REPLY,
            [
                functools.partial(
                    context_assert_final_state, SWITCHING_TO_DRIVER,
                ),
            ],
        ),
        (
            OCTONODE_SWITCH_RESULT_OK,
            DISPATCHER_HANGUP_REPLY,
            [functools.partial(context_assert_final_state, FINISHED)],
        ),
    ]
    return result


def on_transporting_switch_to_operator_scenario():
    return [
        (
            OCTONODE_INITIAL_RESULT_OK,
            DISPATCHER_ANSWER_REPLY,
            [functools.partial(context_assert_final_state, ANSWERING)],
        ),
        (
            OCTONODE_ANSWER_RESULT_OK,
            DISPATCHER_ON_TRANSPORTING_SPEAK_REPLY,
            [
                functools.partial(
                    context_assert_final_state, ORDER_INFO_SPEAKING,
                ),
            ],
        ),
        (
            OCTONODE_SPEAK_RESULT_OK,
            dispatcher_on_transporting_input_reply(),
            [
                functools.partial(
                    context_assert_final_state,
                    ON_TRANSPORTING_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            OCTONODE_INPUT_RESULT_OPERATOR_SWITCH,
            {
                'params': {'call_to': '123', 'use_deflect_switch': True},
                'type': 'switch',
            },
            [
                functools.partial(
                    context_assert_final_state, SWITCHING_TO_OPERATOR,
                ),
            ],
        ),
        (
            OCTONODE_SWITCH_RESULT_OK,
            DISPATCHER_HANGUP_REPLY,
            [functools.partial(context_assert_final_state, FINISHED)],
        ),
    ]


CAR_NOT_FOUND_SCENARIO = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ANSWER_REPLY,
        [functools.partial(context_assert_final_state, ANSWERING)],
    ),
    (
        OCTONODE_ANSWER_RESULT_OK,
        DISPATCHER_CAR_NOT_FOUND_SPEAK_REPLY,
        [functools.partial(context_assert_final_state, ORDER_INFO_SPEAKING)],
    ),
    (
        OCTONODE_SPEAK_RESULT_OK,
        DISPATCHER_CAR_NOT_FOUND_INPUT_REPLY,
        [
            functools.partial(
                context_assert_final_state,
                CAR_NOT_FOUND_MENU_WAITING_FOR_INPUT,
            ),
        ],
    ),
]


def cancellation_scenario():
    return [
        (
            OCTONODE_INITIAL_RESULT_OK,
            DISPATCHER_ANSWER_REPLY,
            [functools.partial(context_assert_final_state, ANSWERING)],
        ),
        (
            OCTONODE_ANSWER_RESULT_OK,
            DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
            [
                functools.partial(
                    context_assert_final_state, ORDER_INFO_SPEAKING,
                ),
            ],
        ),
        (
            OCTONODE_SPEAK_RESULT_OK,
            dispatcher_input_reply(),
            [
                functools.partial(
                    context_assert_final_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            OCTONODE_INPUT_3,
            DISPATCHER_PLAY_CANCELLATION_PROMPT,
            [functools.partial(context_assert_final_state, CANCELLED)],
        ),
        (
            OCTONODE_PLAY_RESULT_OK,
            DISPATCHER_HANGUP_REPLY,
            [functools.partial(context_assert_final_state, FINISHED)],
        ),
    ]


def cancellation_error_scenario():
    return [
        (
            OCTONODE_INITIAL_RESULT_OK,
            DISPATCHER_ANSWER_REPLY,
            [functools.partial(context_assert_final_state, ANSWERING)],
        ),
        (
            OCTONODE_ANSWER_RESULT_OK,
            DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
            [
                functools.partial(
                    context_assert_final_state, ORDER_INFO_SPEAKING,
                ),
            ],
        ),
        (
            OCTONODE_SPEAK_RESULT_OK,
            dispatcher_input_reply(),
            [
                functools.partial(
                    context_assert_final_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            OCTONODE_INPUT_3,
            DISPATCHER_PLAY_CANCELLATION_ERROR_PROMPT,
            [functools.partial(context_assert_final_state, CANCELLING_ERROR)],
        ),
        (
            OCTONODE_PLAY_RESULT_OK,
            dispatcher_input_reply(),
            [
                functools.partial(
                    context_assert_final_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        # etc
    ]


def driver_switch_scenario():
    return [
        (
            OCTONODE_INITIAL_RESULT_OK,
            DISPATCHER_ANSWER_REPLY,
            [functools.partial(context_assert_final_state, ANSWERING)],
        ),
        (
            OCTONODE_ANSWER_RESULT_OK,
            DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
            [
                functools.partial(
                    context_assert_final_state, ORDER_INFO_SPEAKING,
                ),
            ],
        ),
        (
            OCTONODE_SPEAK_RESULT_OK,
            dispatcher_input_reply(),
            [
                functools.partial(
                    context_assert_final_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            octonode_input_result_driver_switch(),
            DISPATCHER_SWITCH_TO_DRIVER_REPLY,
            [
                functools.partial(
                    context_assert_final_state, SWITCHING_TO_DRIVER,
                ),
            ],
        ),
        (
            OCTONODE_SWITCH_RESULT_OK,
            DISPATCHER_HANGUP_REPLY,
            [functools.partial(context_assert_final_state, FINISHED)],
        ),
    ]


def driver_switch_error_scenario():
    return [
        (
            OCTONODE_INITIAL_RESULT_OK,
            DISPATCHER_ANSWER_REPLY,
            [functools.partial(context_assert_final_state, ANSWERING)],
        ),
        (
            OCTONODE_ANSWER_RESULT_OK,
            DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
            [
                functools.partial(
                    context_assert_final_state, ORDER_INFO_SPEAKING,
                ),
            ],
        ),
        (
            OCTONODE_SPEAK_RESULT_OK,
            dispatcher_input_reply(),
            [
                functools.partial(
                    context_assert_final_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            octonode_input_result_driver_switch(),
            DISPATCHER_SWITCH_TO_DRIVER_REPLY,
            [
                functools.partial(
                    context_assert_final_state, SWITCHING_TO_DRIVER,
                ),
            ],
        ),
        (
            OCTONODE_SWITCH_RESULT_ERROR,
            DISPATCHER_PLAY_DRIVER_ERROR_PROMPT,
            [
                functools.partial(
                    context_assert_final_state, DRIVER_SWITCHING_ERROR,
                ),
            ],
        ),
        (
            OCTONODE_PLAY_RESULT_OK,
            dispatcher_input_reply(),
            [
                functools.partial(
                    context_assert_final_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        # etc
    ]


def operator_switch_scenario():
    return [
        (
            OCTONODE_INITIAL_RESULT_OK,
            DISPATCHER_ANSWER_REPLY,
            [functools.partial(context_assert_final_state, ANSWERING)],
        ),
        (
            OCTONODE_ANSWER_RESULT_OK,
            DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
            [
                functools.partial(
                    context_assert_final_state, ORDER_INFO_SPEAKING,
                ),
            ],
        ),
        (
            OCTONODE_SPEAK_RESULT_OK,
            dispatcher_input_reply(),
            [
                functools.partial(
                    context_assert_final_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            OCTONODE_INPUT_RESULT_OPERATOR_SWITCH,
            DISPATCHER_SWITCH_TO_OPERATOR_REPLY,
            [
                functools.partial(
                    context_assert_final_state, SWITCHING_TO_OPERATOR,
                ),
            ],
        ),
        (
            OCTONODE_SWITCH_RESULT_OK,
            DISPATCHER_HANGUP_REPLY,
            [functools.partial(context_assert_final_state, FINISHED)],
        ),
    ]


ERROR_SCENARIO_1 = [
    (
        OCTONODE_INITIAL_RESULT_ERROR,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_final_state, FINISHED_WITH_ERRORS)],
    ),
]

ERROR_SCENARIO_2 = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ANSWER_REPLY,
        [functools.partial(context_assert_final_state, ANSWERING)],
    ),
    (
        OCTONODE_ANSWER_RESULT_ERROR,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_final_state, FINISHED_WITH_ERRORS)],
    ),
]

ERROR_SCENARIO_3 = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ANSWER_REPLY,
        [functools.partial(context_assert_final_state, ANSWERING)],
    ),
    (
        OCTONODE_ANSWER_RESULT_OK,
        DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
        [functools.partial(context_assert_final_state, ORDER_INFO_SPEAKING)],
    ),
    (
        OCTONODE_SPEAK_RESULT_ERROR,
        DISPATCHER_PLAY_ERROR_PROMPT,
        [functools.partial(context_assert_final_state, ERROR_SPEAKING)],
    ),
    (
        OCTONODE_PLAY_RESULT_OK,
        DISPATCHER_SWITCH_TO_OPERATOR_REPLY,
        [functools.partial(context_assert_final_state, SWITCHING_TO_OPERATOR)],
    ),
    (
        OCTONODE_SWITCH_RESULT_OK,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_final_state, FINISHED)],
    ),
]

ERROR_SCENARIO_4 = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ANSWER_REPLY,
        [functools.partial(context_assert_final_state, ANSWERING)],
    ),
    (
        OCTONODE_ANSWER_RESULT_OK,
        DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
        [functools.partial(context_assert_final_state, ORDER_INFO_SPEAKING)],
    ),
    (
        OCTONODE_SPEAK_RESULT_ERROR,
        DISPATCHER_PLAY_ERROR_PROMPT,
        [functools.partial(context_assert_final_state, ERROR_SPEAKING)],
    ),
    (
        OCTONODE_PLAY_RESULT_ERROR,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_final_state, FINISHED_WITH_ERRORS)],
    ),
]

NO_ORDER_SCENARIO = [
    (
        OCTONODE_INITIAL_RESULT_OK,
        DISPATCHER_ANSWER_REPLY,
        [functools.partial(context_assert_final_state, ANSWERING)],
    ),
    (
        OCTONODE_ANSWER_RESULT_OK,
        DISPATCHER_SWITCH_TO_OPERATOR_REPLY,
        [functools.partial(context_assert_final_state, SWITCHING_TO_OPERATOR)],
    ),
    (
        OCTONODE_SWITCH_RESULT_OK,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_final_state, FINISHED)],
    ),
]


def no_partner_info_scenario():
    return [
        (
            OCTONODE_INITIAL_RESULT_OK,
            DISPATCHER_ANSWER_REPLY,
            [functools.partial(context_assert_final_state, ANSWERING)],
        ),
        (
            OCTONODE_ANSWER_RESULT_OK,
            DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
            [
                functools.partial(
                    context_assert_final_state, ORDER_INFO_SPEAKING,
                ),
            ],
        ),
        (
            OCTONODE_SPEAK_RESULT_OK,
            dispatcher_input_reply(),
            [
                functools.partial(
                    context_assert_final_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            octonode_input_result_order_info(),
            DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY,
            [
                functools.partial(
                    context_assert_final_state, ORDER_INFO_SPEAKING,
                ),
            ],
        ),
        (
            OCTONODE_SPEAK_RESULT_OK,
            dispatcher_input_reply(),
            [
                functools.partial(
                    context_assert_final_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            OCTONODE_INPUT_4,
            DISPATCHER_PLAY_NO_PARTNER_INFO_PROMPT,
            [
                functools.partial(
                    context_assert_final_state, PARTNER_INFO_SPEAKING,
                ),
            ],
        ),
        (
            OCTONODE_PLAY_RESULT_OK,
            dispatcher_input_reply(),
            [
                functools.partial(
                    context_assert_final_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        # etc
    ]


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.DEFAULT_TAXI_PHONE: {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '__default__': {'metaqueue': utils.DEFAULT_METAQUEUE},
        utils.DEFAULT_TAXI_PHONE: {'metaqueue': utils.DEFAULT_METAQUEUE},
    },
    IVR_DISPATCHER_ROUTING_METAQUEUE_MAP=utils.DEFAULT_REROUTE_METAQUEUES,
    CALLCENTER_METAQUEUES=[
        {
            'name': utils.DEFAULT_METAQUEUE_ECONOMY,
            'number': '123',
            'allowed_clusters': ['1'],
        },
    ],
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'order_status_worker_2_0',
                'type': 'native_worker',
            },
        },
    },
)
@pytest.mark.parametrize(
    'scenario',
    [
        simple_call_scenario(),
        cancellation_scenario(),
        driver_switch_scenario(),
        driver_switch_error_scenario(),
        cancellation_error_scenario(),
        operator_switch_scenario(),
        on_transporting_scenario(),
        on_transporting_switch_to_operator_scenario(),
        on_transporting_order_info_scenario(),
        on_transporting_switch_to_driver_scenario(),
        ON_SEARCH_SCENARIO,
        ERROR_SCENARIO_1,
        ERROR_SCENARIO_2,
        ERROR_SCENARIO_3,
        ERROR_SCENARIO_4,
        no_partner_info_scenario(),
    ],
    ids=(
        'simple_call_scenario',
        'cancellation_scenario',
        'switch_to_driver',
        'driver_switch_error',
        'cancellation_error',
        'operator_switch',
        'on_transporting',
        'on_transporting_switch_to_operator',
        'on_transporting_order_info',
        'on_transporting_fail_to_switch_to_driver',
        'on_search',
        'error_scenario_1',
        'error_scenario_2',
        'error_scenario_3',
        'error_scenario_4',
        'no_partner_info_scenario',
    ),
)
async def test_order_status(
        taxi_ivr_dispatcher,
        mongodb,
        scenario,
        mock_int_authproxy,
        mock_personal,
        mock_user_api,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
        mock_parks,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        if scenario == ON_SEARCH_SCENARIO:
            response['fields']['candidates'] = list()
            response['fields']['order']['status'] = 'pending'
        if str(scenario) in [
                str(on_transporting_scenario()),
                str(on_transporting_switch_to_operator_scenario()),
                str(on_transporting_order_info_scenario()),
                str(on_transporting_switch_to_driver_scenario()),
        ]:
            response['fields']['order']['taxi_status'] = 'transporting'
        return response

    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        if scenario == ON_SEARCH_SCENARIO:
            status = 'search'
        elif str(scenario) in [
            str(on_transporting_scenario()),
            str(on_transporting_switch_to_operator_scenario()),
            str(on_transporting_order_info_scenario()),
            str(on_transporting_switch_to_driver_scenario()),
        ]:
            status = 'transporting'
        else:
            status = 'driving'
        return {
            'orders': [
                {
                    'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                    'status': status,
                },
            ],
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/cancel')
    def _order_cancel(request):
        if str(scenario) == str(cancellation_error_scenario()):
            return mockserver.make_response(status=500)
        return {}

    # Simulate no partner data for one particular test case
    if str(scenario) == str(no_partner_info_scenario()):

        @mockserver.json_handler('/parks/cars/legal-entities')
        async def no_parks(request):  # pylint: disable=W0612
            return mockserver.make_response(status=404)

    for action, reply, checks in scenario:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.DEFAULT_TAXI_PHONE: {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '__default__': {'metaqueue': utils.DEFAULT_METAQUEUE},
        utils.DEFAULT_TAXI_PHONE: {'metaqueue': utils.DEFAULT_METAQUEUE},
    },
    IVR_DISPATCHER_ROUTING_METAQUEUE_MAP=utils.DEFAULT_REROUTE_METAQUEUES,
    CALLCENTER_METAQUEUES=[
        {
            'name': utils.DEFAULT_METAQUEUE_ECONOMY,
            'number': '123',
            'allowed_clusters': ['1'],
        },
    ],
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'order_status_worker_2_0',
                'type': 'native_worker',
            },
        },
    },
)
@pytest.mark.parametrize(
    'input_number',
    all_kinds_of_input_number_on_search_scenario(),
    ids=[
        el[0]['numbers']
        for el in all_kinds_of_input_number_on_search_scenario()
    ],
)
async def test_on_serch_scenario_input_number(
        taxi_ivr_dispatcher,
        mongodb,
        input_number,
        mock_int_authproxy,
        mock_personal,
        mock_user_api,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
        mock_parks,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['candidates'] = list()
        response['fields']['order']['status'] = 'pending'
        return response

    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        return {
            'orders': [
                {
                    'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                    'status': 'search',
                },
            ],
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/cancel')
    def _order_cancel(request):
        return {}

    for action, reply, checks in [*ON_SEARCH_SCENARIO, input_number]:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.DEFAULT_TAXI_PHONE: {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '__default__': {'metaqueue': utils.DEFAULT_METAQUEUE},
        utils.DEFAULT_TAXI_PHONE: {'metaqueue': utils.DEFAULT_METAQUEUE},
    },
    IVR_DISPATCHER_ROUTING_METAQUEUE_MAP=utils.DEFAULT_REROUTE_METAQUEUES,
    CALLCENTER_METAQUEUES=[
        {
            'name': utils.DEFAULT_METAQUEUE_ECONOMY,
            'number': '123',
            'allowed_clusters': ['1'],
        },
    ],
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'order_status_worker_2_0',
                'type': 'native_worker',
            },
        },
    },
)
async def test_order_status_no_order(
        taxi_ivr_dispatcher,
        mongodb,
        mock_int_authproxy,
        mock_user_api,
        mock_personal,
        mockserver,
):
    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        return {'orders': []}

    for action, reply, checks in NO_ORDER_SCENARIO:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.DEFAULT_TAXI_PHONE: {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '__default__': {'metaqueue': utils.DEFAULT_METAQUEUE},
        utils.DEFAULT_TAXI_PHONE: {'metaqueue': utils.DEFAULT_METAQUEUE},
    },
    IVR_DISPATCHER_ROUTING_METAQUEUE_MAP=utils.DEFAULT_REROUTE_METAQUEUES,
    CALLCENTER_METAQUEUES=[
        {
            'name': utils.DEFAULT_METAQUEUE_ECONOMY,
            'number': '123',
            'allowed_clusters': ['1'],
        },
    ],
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'order_status_worker_2_0',
                'type': 'native_worker',
            },
        },
    },
)
async def test_order_change_status_to_cancelled_via_call(
        taxi_ivr_dispatcher,
        mongodb,
        mock_int_authproxy,
        mock_personal,
        mock_user_api,
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
        response['fields']['order']['status'] = 'cancelled'
        response['fields']['order']['taxi_status'] = None
        return response

    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        return {
            'orders': [
                {
                    'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                    'status': 'driving',
                    # return here driving to emulate has_order = True
                },
            ],
        }

    for action, reply, checks in CAR_NOT_FOUND_SCENARIO:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)
