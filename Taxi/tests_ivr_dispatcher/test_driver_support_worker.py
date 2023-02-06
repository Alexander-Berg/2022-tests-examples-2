# pylint: disable=C0302

import functools

import pytest

from tests_ivr_dispatcher import utils

FINISHED_WITH_ERRORS = 'finished_with_errors'
INITIALIZING = 'initializing'
ANSWERING = 'answering'
FINISHED = 'finished'
ERROR_SPEAKING = 'error'
SWITCHING_ERROR_SPEAKING = 'switching_error_speaking'
SWITCHING_TO_ADVERSE_DRIVER_IVR = 'switching_to_adverse_driver_ivr'
HELLO_SPEAKING = 'hello_speaking'
WAITING = 'waiting'
MAIN_MENU_WAITING_FOR_INPUT = 'main_menu_waiting_for_input'
BONUSES_MENU_WAITING_FOR_INPUT = 'bonuses_menu_waiting_for_input'
PROCESS_CHOOSED_NUMBER = 'process_choosed_number'

SWITCHING_TO_FINANCE = 'switching_to_finance_number'
SWITCHING_TO_ACCOUNTS = 'switching_to_accounts_number'
SWITCHING_TO_OTHER = 'switching_to_other_number'
SWITCHING_TO_PREMIUM_DRIVER_NUMBER = 'switching_to_premium_driver_number'
SWITCHING_TO_DRIVER_NUMBER_FOR_SELFEMPLOYED = (
    'switching_to_driver_number_for_selfemployed'
)
SWITCHING_TO_SUPPORT_DRIVER_ACTIVE_ORDER = (
    'switching_to_support_driver_active_order'
)
SWITCHING_TO = {
    '1': SWITCHING_TO_FINANCE,
    '2': SWITCHING_TO_ACCOUNTS,
    '3': SWITCHING_TO_ACCOUNTS,
    '5': SWITCHING_TO_OTHER,
}


def switching_to(
        number: str,
        premium: bool,
        selfemployed: bool = False,
        have_active_order: bool = False,
):
    if premium:
        return SWITCHING_TO_PREMIUM_DRIVER_NUMBER
    if have_active_order:
        return SWITCHING_TO_SUPPORT_DRIVER_ACTIVE_ORDER
    if selfemployed:
        return SWITCHING_TO_DRIVER_NUMBER_FOR_SELFEMPLOYED
    return SWITCHING_TO[number]


FINANCE_SUPPORT_NUMBER = 'some_finance_number'
ACCOUNTS_SUPPORT_NUMBER = 'some_accounts_number'
OTHER_SUPPORT_NUMBER = 'some_other_number'
PREMIUM_SUPPORT_NUMBER = 'some_premium_number'
SUPPORT_NUMBER_FOR_SELFEMPLOYED = 'some_number_for_selfemployed'
ACTIVE_ORDER_SUPPORT_NUMBER = 'active_order_number'
NUMBER_TO_CALLTO = {
    '1': FINANCE_SUPPORT_NUMBER,
    '2': ACCOUNTS_SUPPORT_NUMBER,
    '3': ACCOUNTS_SUPPORT_NUMBER,
    '5': OTHER_SUPPORT_NUMBER,
}


def number_to_callto(
        number: str,
        premium: bool,
        selfemployed: bool = False,
        have_active_order: bool = False,
):
    if premium:
        return PREMIUM_SUPPORT_NUMBER
    if have_active_order:
        return ACTIVE_ORDER_SUPPORT_NUMBER
    if selfemployed:
        return SUPPORT_NUMBER_FOR_SELFEMPLOYED
    return NUMBER_TO_CALLTO[number]


DRIVER_TAG = 'driver_tag'
ANOTHER_DRIVER_TAG = 'another_driver_tag'
SELFEMPLOYED_TAG = 'selfemployed'
DRIVER_TAG_FOR_SELFEMPLOYED = 'driver_tag_for_selfemployed'


def context_assert_current_state(state, db):
    db_session_doc = db.ivr_disp_sessions.find_one(
        {'_id': utils.DEFAULT_SESSION_ID},
    )
    assert 'context' in db_session_doc
    assert 'state' in db_session_doc['context']
    assert db_session_doc['context']['state'] == state


# Octonode action results
OCTONODE_INITIATING_RESULT_OK = {
    'called_number': utils.DEFAULT_TAXI_PHONE,  # call_from
    'caller_number': utils.DEFAULT_USER_PHONE,  # call_to
    'call_guid': 'some_call_guid',
    'status': 'ok',
    'type': 'initial',
}
OCTONODE_INITIATING_RESULT_ANONYMOUS_CALLER = {
    'called_number': utils.DEFAULT_TAXI_PHONE,
    'caller_number': 'Anonymous',
    'call_guid': 'some_call_guid',
    'status': 'ok',
    'type': 'initial',
}
OCTONODE_INITIATING_RESULT_ERROR = {
    'called_number': utils.DEFAULT_TAXI_PHONE,  # call_from
    'caller_number': utils.DEFAULT_USER_PHONE,  # call_to
    'call_guid': 'some_call_guid',
    'status': 'error',
    'type': 'initial',
}
OCTONODE_ANSWERING_RESULT_OK = {'status': 'ok', 'type': 'answer'}
OCTONODE_ANSWERING_RESULT_ERROR = {'status': 'error', 'type': 'answer'}
OCTONODE_PLAY_RESULT_OK = {'status': 'ok', 'type': 'play'}
OCTONODE_PLAY_RESULT_ERROR = {'status': 'error', 'type': 'play'}
OCTONODE_PLAY_RESULT_INTERRUPTED = {
    'status': 'error',
    'type': 'play',
    'error_cause': 'interrupted',
}
OCTONODE_WAIT_RESULT_OK = {'status': 'ok', 'type': 'wait'}


def octonode_input_result_ok(number: str):
    return {'status': 'ok', 'type': 'input', 'numbers': number}


OCTONODE_INPUT_RESULT_ERROR = {'status': 'error', 'type': 'input'}
OCTONODE_SWITCHING_RESULT_OK = {'status': 'ok', 'type': 'switch'}
OCTONODE_SWITCHING_RESULT_ERROR = {
    'status': 'error',
    'type': 'switch',
    'error_cause': 'n/a',
}

# Dispatcher possible answers
DISPATCHER_INITIATING_REPLY = {
    'params': {'start_recording': False},
    'type': 'answer',
}
DISPATCHER_HANGUP_REPLY = {'type': 'hangup'}


def dispatcher_hello_reply(key=None):
    key = 'dsw.hello0' if key is None else key
    return {
        'params': {'relative_path': f'driver_support_worker/{key}.wav'},
        'type': 'play',
    }


def dispatcher_wait_reply(delay=0):
    params = {}
    if delay:
        params.update({'delay': delay})
    return {'type': 'wait', 'params': params}


DISPATCHER_PLAY_ERROR = {
    'params': {'relative_path': 'driver_support_worker/dsw.error.wav'},
    'type': 'play',
}
DISPATCHER_PLAY_SWITCHING_ERROR = {
    'params': {
        'relative_path': 'driver_support_worker/dsw.switching_error.wav',
    },
    'type': 'play',
}


def dispatcher_main_menu_reply(premium: bool, is_auto_courier: bool = False):
    if is_auto_courier:
        prompt_id = 'dsw.auto_courier'
    elif premium:
        prompt_id = 'dsw.premium_main_menu'
    else:
        prompt_id = 'dsw.main_menu'
    return {
        'params': {
            'relative_path': f'driver_support_worker/{prompt_id}.wav',
            'timeout': 10,
        },
        'type': 'input',
    }


def dispatcher_bonuses_menu_reply(premium: bool):
    prompt_id = 'dsw.premium_bonuses_menu' if premium else 'dsw.bonuses_menu'
    return {
        'params': {
            'relative_path': f'driver_support_worker/{prompt_id}.wav',
            'timeout': 10,
        },
        'type': 'input',
    }


DISPATCHER_ADVERSE_DRIVER_SWITCH_REPLY = {
    'params': {'use_deflect_switch': True, 'call_to': '9944'},
    'type': 'switch',
}

BEFORE_SWITCH_PHRASE = {
    'params': {'relative_path': 'driver_support_worker/dsw.before_switch.wav'},
    'type': 'play',
}


def dispatcher_switch_reply(
        number: str,
        premium=False,
        selfemployed=False,
        have_active_order=False,
):
    return {
        'params': {
            'use_deflect_switch': True,
            'call_to': number_to_callto(
                number, premium, selfemployed, have_active_order,
            ),
        },
        'type': 'switch',
    }


# Scenarios
def adverse_driver_scenario(enable_switch_to_adverse_driver_ivr=True):
    return [
        (
            OCTONODE_INITIATING_RESULT_OK,
            DISPATCHER_INITIATING_REPLY,
            [functools.partial(context_assert_current_state, ANSWERING)],
        ),
        (
            OCTONODE_ANSWERING_RESULT_OK,
            DISPATCHER_ADVERSE_DRIVER_SWITCH_REPLY
            if enable_switch_to_adverse_driver_ivr
            else dispatcher_hello_reply('dsw.answer_for_adverse_driver'),
            [
                functools.partial(
                    context_assert_current_state,
                    SWITCHING_TO_ADVERSE_DRIVER_IVR,
                ),
            ]
            if enable_switch_to_adverse_driver_ivr
            else [
                functools.partial(
                    context_assert_current_state, HELLO_SPEAKING,
                ),
            ],
        ),
        (
            OCTONODE_SWITCHING_RESULT_OK,
            DISPATCHER_HANGUP_REPLY,
            [functools.partial(context_assert_current_state, FINISHED)],
        ),
    ]


ERROR_IN_PD_SCENARIO = [
    (
        {
            'called_number': utils.DEFAULT_TAXI_PHONE,
            'caller_number': utils.DEFAULT_USER_PHONE,
            'call_guid': 'some_call_guid',
            'status': 'ok',
            'type': 'initial',
        },
        DISPATCHER_INITIATING_REPLY,
        [functools.partial(context_assert_current_state, ANSWERING)],
    ),
    (
        OCTONODE_ANSWERING_RESULT_OK,
        dispatcher_hello_reply('dsw.hello_and_hangup_for_anonymous'),
        [functools.partial(context_assert_current_state, HELLO_SPEAKING)],
    ),
    (
        OCTONODE_PLAY_RESULT_OK,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_current_state, FINISHED)],
    ),
]

AGGRESSIVE_DRIVER_SCENARIO = [
    (
        OCTONODE_INITIATING_RESULT_OK,
        DISPATCHER_INITIATING_REPLY,
        [functools.partial(context_assert_current_state, ANSWERING)],
    ),
    (
        OCTONODE_ANSWERING_RESULT_OK,
        dispatcher_hello_reply('dsw.hello_and_hangup_for_aggressive_driver'),
        [functools.partial(context_assert_current_state, HELLO_SPEAKING)],
    ),
    (
        OCTONODE_PLAY_RESULT_OK,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_current_state, FINISHED)],
    ),
]


def main_scenario(
        number: str,
        premium=False,
        selfemployed=False,
        have_active_order=False,
):
    return [
        (
            OCTONODE_INITIATING_RESULT_OK,
            DISPATCHER_INITIATING_REPLY,
            [functools.partial(context_assert_current_state, ANSWERING)],
        ),
        (
            OCTONODE_ANSWERING_RESULT_OK,
            dispatcher_hello_reply(),
            [functools.partial(context_assert_current_state, HELLO_SPEAKING)],
        ),
        (
            OCTONODE_PLAY_RESULT_OK,
            dispatcher_wait_reply(),
            [functools.partial(context_assert_current_state, WAITING)],
        ),
        (
            OCTONODE_WAIT_RESULT_OK,
            dispatcher_main_menu_reply(premium),
            [
                functools.partial(
                    context_assert_current_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            octonode_input_result_ok('0'),
            dispatcher_main_menu_reply(premium),
            [
                functools.partial(
                    context_assert_current_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            octonode_input_result_ok(number),
            BEFORE_SWITCH_PHRASE,
            [
                functools.partial(
                    context_assert_current_state, PROCESS_CHOOSED_NUMBER,
                ),
            ],
        ),
        (
            OCTONODE_PLAY_RESULT_OK,
            dispatcher_switch_reply(
                number, premium, selfemployed, have_active_order,
            ),
            [
                functools.partial(
                    context_assert_current_state,
                    switching_to(
                        number, premium, selfemployed, have_active_order,
                    ),
                ),
            ],
        ),
        (
            OCTONODE_SWITCHING_RESULT_OK,
            DISPATCHER_HANGUP_REPLY,
            [functools.partial(context_assert_current_state, FINISHED)],
        ),
    ]


def bonuses_menu_scenario(premium: bool):
    return [
        (
            OCTONODE_INITIATING_RESULT_OK,
            DISPATCHER_INITIATING_REPLY,
            [functools.partial(context_assert_current_state, ANSWERING)],
        ),
        (
            OCTONODE_ANSWERING_RESULT_OK,
            dispatcher_hello_reply(),
            [functools.partial(context_assert_current_state, HELLO_SPEAKING)],
        ),
        (
            OCTONODE_PLAY_RESULT_OK,
            dispatcher_wait_reply(),
            [functools.partial(context_assert_current_state, WAITING)],
        ),
        (
            OCTONODE_WAIT_RESULT_OK,
            dispatcher_main_menu_reply(premium),
            [
                functools.partial(
                    context_assert_current_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            octonode_input_result_ok('4'),
            dispatcher_bonuses_menu_reply(premium),
            [
                functools.partial(
                    context_assert_current_state,
                    BONUSES_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            octonode_input_result_ok('0'),
            dispatcher_main_menu_reply(premium),
            [
                functools.partial(
                    context_assert_current_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            octonode_input_result_ok('4'),
            dispatcher_bonuses_menu_reply(premium),
            [
                functools.partial(
                    context_assert_current_state,
                    BONUSES_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            octonode_input_result_ok(''),
            DISPATCHER_HANGUP_REPLY,
            [functools.partial(context_assert_current_state, FINISHED)],
        ),
    ]


def scenario_for_auto_courier(
        first_number: str,
        second_number=None,
        premium=False,
        selfemployed=False,
        have_active_order=False,
):
    result = [
        (
            OCTONODE_INITIATING_RESULT_OK,
            DISPATCHER_INITIATING_REPLY,
            [functools.partial(context_assert_current_state, ANSWERING)],
        ),
        (
            OCTONODE_ANSWERING_RESULT_OK,
            dispatcher_hello_reply(),
            [functools.partial(context_assert_current_state, HELLO_SPEAKING)],
        ),
        (
            OCTONODE_PLAY_RESULT_OK,
            dispatcher_wait_reply(),
            [functools.partial(context_assert_current_state, WAITING)],
        ),
        (
            OCTONODE_WAIT_RESULT_OK,
            dispatcher_main_menu_reply(premium, True),
            [
                functools.partial(
                    context_assert_current_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
    ]

    if first_number == '1':
        result.append(
            (
                octonode_input_result_ok(first_number),
                dispatcher_main_menu_reply(premium),
                [
                    functools.partial(
                        context_assert_current_state,
                        MAIN_MENU_WAITING_FOR_INPUT,
                    ),
                ],
            ),
        )
        if second_number != '4':
            result.extend(
                [
                    (
                        octonode_input_result_ok(second_number),
                        BEFORE_SWITCH_PHRASE,
                        [
                            functools.partial(
                                context_assert_current_state,
                                PROCESS_CHOOSED_NUMBER,
                            ),
                        ],
                    ),
                    (
                        OCTONODE_PLAY_RESULT_OK,
                        dispatcher_switch_reply(
                            second_number,
                            premium,
                            selfemployed,
                            have_active_order,
                        ),
                        [
                            functools.partial(
                                context_assert_current_state,
                                switching_to(
                                    second_number,
                                    premium,
                                    selfemployed,
                                    have_active_order,
                                ),
                            ),
                        ],
                    ),
                ],
            )
        else:
            result.append(
                (
                    octonode_input_result_ok('4'),
                    dispatcher_bonuses_menu_reply(premium),
                    [
                        functools.partial(
                            context_assert_current_state,
                            BONUSES_MENU_WAITING_FOR_INPUT,
                        ),
                    ],
                ),
            )
    elif first_number == '2':
        result.append(
            (
                octonode_input_result_ok(first_number),
                dispatcher_hello_reply('dsw.say_and_hangup_for_auto_courier'),
                [
                    functools.partial(
                        context_assert_current_state, HELLO_SPEAKING,
                    ),
                ],
            ),
        )
    else:
        assert False, 'unexpected first_number in scenario_for_auto_courier'

    result.append(
        (
            OCTONODE_SWITCHING_RESULT_OK,
            DISPATCHER_HANGUP_REPLY,
            [functools.partial(context_assert_current_state, FINISHED)],
        ),
    )
    return result


INITIATING_ERROR_SCENARIO = [
    (
        OCTONODE_INITIATING_RESULT_ERROR,
        DISPATCHER_HANGUP_REPLY,
        [
            functools.partial(
                context_assert_current_state, FINISHED_WITH_ERRORS,
            ),
        ],
    ),
]

ANSWERING_ERROR_SCENARIO = [
    (
        OCTONODE_INITIATING_RESULT_OK,
        DISPATCHER_INITIATING_REPLY,
        [functools.partial(context_assert_current_state, ANSWERING)],
    ),
    (
        OCTONODE_ANSWERING_RESULT_ERROR,
        DISPATCHER_HANGUP_REPLY,
        [
            functools.partial(
                context_assert_current_state, FINISHED_WITH_ERRORS,
            ),
        ],
    ),
]


def adverse_driver_error_scenario(enable_switch_to_adverse_driver_ivr=True):
    return [
        (
            OCTONODE_INITIATING_RESULT_OK,
            DISPATCHER_INITIATING_REPLY,
            [functools.partial(context_assert_current_state, ANSWERING)],
        ),
        (
            OCTONODE_ANSWERING_RESULT_OK,
            DISPATCHER_ADVERSE_DRIVER_SWITCH_REPLY
            if enable_switch_to_adverse_driver_ivr
            else dispatcher_hello_reply('dsw.answer_for_adverse_driver'),
            [
                functools.partial(
                    context_assert_current_state,
                    SWITCHING_TO_ADVERSE_DRIVER_IVR,
                ),
            ]
            if enable_switch_to_adverse_driver_ivr
            else [
                functools.partial(
                    context_assert_current_state, HELLO_SPEAKING,
                ),
            ],
        ),
        (
            OCTONODE_SWITCHING_RESULT_ERROR,
            DISPATCHER_PLAY_SWITCHING_ERROR
            if enable_switch_to_adverse_driver_ivr
            else DISPATCHER_PLAY_ERROR,
            [
                functools.partial(
                    context_assert_current_state, SWITCHING_ERROR_SPEAKING,
                ),
            ]
            if enable_switch_to_adverse_driver_ivr
            else [
                functools.partial(
                    context_assert_current_state, ERROR_SPEAKING,
                ),
            ],
        ),
        (
            OCTONODE_PLAY_RESULT_ERROR,
            DISPATCHER_HANGUP_REPLY,
            [
                functools.partial(
                    context_assert_current_state, FINISHED_WITH_ERRORS,
                ),
            ],
        ),
    ]


HELLO_ERROR_SCENARIO = [
    (
        OCTONODE_INITIATING_RESULT_OK,
        DISPATCHER_INITIATING_REPLY,
        [functools.partial(context_assert_current_state, ANSWERING)],
    ),
    (
        OCTONODE_ANSWERING_RESULT_OK,
        dispatcher_hello_reply(),
        [functools.partial(context_assert_current_state, HELLO_SPEAKING)],
    ),
    (
        OCTONODE_PLAY_RESULT_ERROR,
        DISPATCHER_PLAY_ERROR,
        [functools.partial(context_assert_current_state, ERROR_SPEAKING)],
    ),
    (
        OCTONODE_PLAY_RESULT_OK,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_current_state, FINISHED)],
    ),
]

MAIN_MENU_ERROR_SCENARIO = [
    (
        OCTONODE_INITIATING_RESULT_OK,
        DISPATCHER_INITIATING_REPLY,
        [functools.partial(context_assert_current_state, ANSWERING)],
    ),
    (
        OCTONODE_ANSWERING_RESULT_OK,
        dispatcher_hello_reply(),
        [functools.partial(context_assert_current_state, HELLO_SPEAKING)],
    ),
    (
        OCTONODE_PLAY_RESULT_OK,
        dispatcher_wait_reply(),
        [functools.partial(context_assert_current_state, WAITING)],
    ),
    (
        OCTONODE_WAIT_RESULT_OK,
        dispatcher_main_menu_reply(premium=False),
        [
            functools.partial(
                context_assert_current_state, MAIN_MENU_WAITING_FOR_INPUT,
            ),
        ],
    ),
    (
        OCTONODE_INPUT_RESULT_ERROR,
        DISPATCHER_PLAY_ERROR,
        [functools.partial(context_assert_current_state, ERROR_SPEAKING)],
    ),
    (
        OCTONODE_PLAY_RESULT_ERROR,
        DISPATCHER_HANGUP_REPLY,
        [
            functools.partial(
                context_assert_current_state, FINISHED_WITH_ERRORS,
            ),
        ],
    ),
]


def switch_error_scenario(number: str):
    return [
        (
            OCTONODE_INITIATING_RESULT_OK,
            DISPATCHER_INITIATING_REPLY,
            [functools.partial(context_assert_current_state, ANSWERING)],
        ),
        (
            OCTONODE_ANSWERING_RESULT_OK,
            dispatcher_hello_reply(),
            [functools.partial(context_assert_current_state, HELLO_SPEAKING)],
        ),
        (
            OCTONODE_PLAY_RESULT_OK,
            dispatcher_wait_reply(),
            [functools.partial(context_assert_current_state, WAITING)],
        ),
        (
            OCTONODE_WAIT_RESULT_OK,
            dispatcher_main_menu_reply(premium=False),
            [
                functools.partial(
                    context_assert_current_state, MAIN_MENU_WAITING_FOR_INPUT,
                ),
            ],
        ),
        (
            octonode_input_result_ok(number),
            BEFORE_SWITCH_PHRASE,
            [
                functools.partial(
                    context_assert_current_state, PROCESS_CHOOSED_NUMBER,
                ),
            ],
        ),
        (
            OCTONODE_SWITCHING_RESULT_ERROR,
            DISPATCHER_PLAY_ERROR,
            [functools.partial(context_assert_current_state, ERROR_SPEAKING)],
        ),
        (
            OCTONODE_PLAY_RESULT_OK,
            DISPATCHER_HANGUP_REPLY,
            [functools.partial(context_assert_current_state, FINISHED)],
        ),
    ]


BONUSES_MENU_ERROR_SCENARIO = [
    (
        OCTONODE_INITIATING_RESULT_OK,
        DISPATCHER_INITIATING_REPLY,
        [functools.partial(context_assert_current_state, ANSWERING)],
    ),
    (
        OCTONODE_ANSWERING_RESULT_OK,
        dispatcher_hello_reply(),
        [functools.partial(context_assert_current_state, HELLO_SPEAKING)],
    ),
    (
        OCTONODE_PLAY_RESULT_OK,
        dispatcher_wait_reply(),
        [functools.partial(context_assert_current_state, WAITING)],
    ),
    (
        OCTONODE_WAIT_RESULT_OK,
        dispatcher_main_menu_reply(premium=False),
        [
            functools.partial(
                context_assert_current_state, MAIN_MENU_WAITING_FOR_INPUT,
            ),
        ],
    ),
    (
        octonode_input_result_ok('4'),
        dispatcher_bonuses_menu_reply(premium=False),
        [
            functools.partial(
                context_assert_current_state, BONUSES_MENU_WAITING_FOR_INPUT,
            ),
        ],
    ),
    (
        OCTONODE_INPUT_RESULT_ERROR,
        DISPATCHER_PLAY_ERROR,
        [functools.partial(context_assert_current_state, ERROR_SPEAKING)],
    ),
    (
        OCTONODE_PLAY_RESULT_OK,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_current_state, FINISHED)],
    ),
]

USER_INTERRUPT_SCENARIO = [
    (
        OCTONODE_INITIATING_RESULT_OK,
        DISPATCHER_INITIATING_REPLY,
        [functools.partial(context_assert_current_state, ANSWERING)],
    ),
    (
        OCTONODE_ANSWERING_RESULT_OK,
        dispatcher_hello_reply(),
        [functools.partial(context_assert_current_state, HELLO_SPEAKING)],
    ),
    (
        OCTONODE_PLAY_RESULT_INTERRUPTED,
        DISPATCHER_HANGUP_REPLY,
        [functools.partial(context_assert_current_state, FINISHED)],
    ),
]


def hello_experiment_scenario(key: str, delay: int, need_hangup: bool):
    result = [
        (
            OCTONODE_INITIATING_RESULT_OK,
            DISPATCHER_INITIATING_REPLY,
            [functools.partial(context_assert_current_state, ANSWERING)],
        ),
        (
            OCTONODE_ANSWERING_RESULT_OK,
            dispatcher_hello_reply(key),
            [functools.partial(context_assert_current_state, HELLO_SPEAKING)],
        ),
        (
            OCTONODE_PLAY_RESULT_OK,
            dispatcher_wait_reply(delay)
            if not need_hangup
            else DISPATCHER_HANGUP_REPLY,
            [
                functools.partial(
                    context_assert_current_state,
                    WAITING if not need_hangup else FINISHED,
                ),
            ],
        ),
    ]
    if not need_hangup:
        result.append(
            (
                OCTONODE_WAIT_RESULT_OK,
                dispatcher_main_menu_reply(premium=False),
                [
                    functools.partial(
                        context_assert_current_state,
                        MAIN_MENU_WAITING_FOR_INPUT,
                    ),
                ],
            ),
        )
    return result


@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'driver_support_worker',
                'type': 'native_worker',
            },
        },
    },
    IVR_DISPATCHER_DRIVER_SUPPORT_WORKER_SETTINGS={
        'allowed_driver_tags': [DRIVER_TAG],
        'premium_driver_tags': [ANOTHER_DRIVER_TAG],
        'adverse_driver_ivr_number': '9944',
        'premium_support_number': PREMIUM_SUPPORT_NUMBER,
        'finance_support_number': FINANCE_SUPPORT_NUMBER,
        'accounts_support_number': ACCOUNTS_SUPPORT_NUMBER,
        'other_support_number': OTHER_SUPPORT_NUMBER,
        'auto_courier_tags': ['auto_courier'],
        'active_order_rule': {
            'support_number': ACTIVE_ORDER_SUPPORT_NUMBER,
            'enable': True,
        },
    },
    IVR_DISPATCHER_PHRASE_BEFORE_SWITCH={'enabled': True, 'time_to_sleep': 10},
)
@pytest.mark.parametrize(
    ['scenario', 'driver_tags', 'orders'],
    [
        pytest.param(
            adverse_driver_scenario(),
            ['some_tag'],
            [],
            id='adverse_driver_scenario',
        ),
        pytest.param(
            main_scenario('1', have_active_order=True),
            [],
            [{'id': 'some_id', 'status': 'none'}],
            id='adverse_driver_with_active_order(#1)',
        ),
        pytest.param(
            main_scenario('2', have_active_order=True),
            [],
            [{'id': 'some_id', 'status': 'none'}],
            id='adverse_driver_with_active_order(#2)',
        ),
        pytest.param(
            main_scenario('3', have_active_order=True),
            [],
            [{'id': 'some_id', 'status': 'none'}],
            id='adverse_driver_with_active_order(#3)',
        ),
        pytest.param(
            main_scenario('5', have_active_order=True),
            [],
            [{'id': 'some_id', 'status': 'none'}],
            id='adverse_driver_with_active_order(#5)',
        ),
        pytest.param(
            main_scenario('1'),
            [DRIVER_TAG, 'some_tag'],
            [],
            id='main_scenario(#1)',
        ),
        pytest.param(
            main_scenario('2'),
            [DRIVER_TAG, 'some_tag'],
            [],
            id='main_scenario(#2)',
        ),
        pytest.param(
            main_scenario('3'),
            [DRIVER_TAG, 'some_tag'],
            [],
            id='main_scenario(#3)',
        ),
        pytest.param(
            main_scenario('5'),
            [DRIVER_TAG, 'some_tag'],
            [],
            id='main_scenario(#5)',
        ),
        pytest.param(
            main_scenario('1', have_active_order=True),
            [DRIVER_TAG, 'some_tag'],
            [{'id': 'some_id', 'status': 'none'}],
            id='main_scenario_for_active_order(#1)',
        ),
        pytest.param(
            main_scenario('2', have_active_order=True),
            [DRIVER_TAG, 'some_tag'],
            [{'id': 'some_id', 'status': 'none'}],
            id='main_scenario_for_active_order(#2)',
        ),
        pytest.param(
            main_scenario('3', have_active_order=True),
            [DRIVER_TAG, 'some_tag'],
            [{'id': 'some_id', 'status': 'none'}],
            id='main_scenario_for_active_order(#3)',
        ),
        pytest.param(
            main_scenario('5', have_active_order=True),
            [DRIVER_TAG, 'some_tag'],
            [{'id': 'some_id', 'status': 'none'}],
            id='main_scenario_for_active_order(#5)',
        ),
        pytest.param(
            main_scenario('1', True),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'some_tag'],
            [],
            id='premium_scenario(#1)',
        ),
        pytest.param(
            main_scenario('2', True),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'some_tag'],
            [],
            id='premium_scenario(#2)',
        ),
        pytest.param(
            main_scenario('3', True),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'some_tag'],
            [],
            id='premium_scenario(#3)',
        ),
        pytest.param(
            main_scenario('5', True),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'some_tag'],
            [],
            id='premium_scenario(#5)',
        ),
        pytest.param(
            main_scenario('1', premium=True, have_active_order=True),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'some_tag'],
            [{'id': 'some_id', 'status': 'none'}],
            id='main_scenario_premium_driver_with_active_order(#1)',
        ),
        pytest.param(
            main_scenario('2', premium=True, have_active_order=True),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'some_tag'],
            [{'id': 'some_id', 'status': 'none'}],
            id='main_scenario_premium_driver_with_active_order(#2)',
        ),
        pytest.param(
            main_scenario('3', premium=True, have_active_order=True),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'some_tag'],
            [{'id': 'some_id', 'status': 'none'}],
            id='main_scenario_premium_driver_with_active_order(#3)',
        ),
        pytest.param(
            main_scenario('5', premium=True, have_active_order=True),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'some_tag'],
            [{'id': 'some_id', 'status': 'none'}],
            id='main_scenario_premium_driver_with_active_order(#5)',
        ),
        pytest.param(
            bonuses_menu_scenario(False),
            [DRIVER_TAG, 'some_tag'],
            [],
            id='bonuses_menu_scenario(#4)',
        ),
        pytest.param(
            bonuses_menu_scenario(True),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'some_tag'],
            [],
            id='premium_bonuses_menu_scenario(#4)',
        ),
        pytest.param(
            INITIATING_ERROR_SCENARIO,
            [DRIVER_TAG, 'some_tag'],
            [],
            id='initiating_error_scenario',
        ),
        pytest.param(
            ANSWERING_ERROR_SCENARIO,
            [DRIVER_TAG, 'some_tag'],
            [],
            id='answering_error_scenario',
        ),
        pytest.param(
            adverse_driver_error_scenario(),
            ['some_tag'],
            [],
            id='adverse_driver_error_scenario',
        ),
        pytest.param(
            HELLO_ERROR_SCENARIO,
            [DRIVER_TAG, 'some_tag'],
            [],
            id='hello_error_scenario',
        ),
        pytest.param(
            MAIN_MENU_ERROR_SCENARIO,
            [DRIVER_TAG, 'some_tag'],
            [],
            id='main_menu_error_scenario',
        ),
        pytest.param(
            switch_error_scenario('1'),
            [DRIVER_TAG],
            [],
            id='switch_error_scenario(#1)',
        ),
        pytest.param(
            switch_error_scenario('2'),
            [DRIVER_TAG],
            [],
            id='switch_error_scenario(#2)',
        ),
        pytest.param(
            switch_error_scenario('3'),
            [DRIVER_TAG],
            [],
            id='switch_error_scenario(#3)',
        ),
        pytest.param(
            switch_error_scenario('5'),
            [DRIVER_TAG],
            [],
            id='switch_error_scenario(#5)',
        ),
        pytest.param(
            BONUSES_MENU_ERROR_SCENARIO,
            [DRIVER_TAG],
            [],
            id='bonuses_menu_error_scenario',
        ),
        pytest.param(
            USER_INTERRUPT_SCENARIO,
            [DRIVER_TAG],
            [],
            id='user_interrupt_scenario',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '1'),
            [DRIVER_TAG, 'auto_courier'],
            [],
            id='scenario_for_auto_courier(#1)',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '2'),
            [DRIVER_TAG, 'auto_courier'],
            [],
            id='scenario_for_auto_courier(#2)',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '3'),
            [DRIVER_TAG, 'auto_courier'],
            [],
            id='scenario_for_auto_courier(#3)',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '4'),
            [DRIVER_TAG, 'auto_courier'],
            [],
            id='scenario_for_auto_courier(#4)',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '5'),
            [DRIVER_TAG, 'auto_courier'],
            [],
            id='scenario_for_auto_courier(#5)',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '1', have_active_order=True),
            [DRIVER_TAG, 'auto_courier'],
            [{'id': 'some_id', 'status': 'none'}],
            id='scenario_for_auto_courier_with_active_order(#1)',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '2', have_active_order=True),
            [DRIVER_TAG, 'auto_courier'],
            [{'id': 'some_id', 'status': 'none'}],
            id='scenario_for_auto_courier_with_active_order(#2)',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '3', have_active_order=True),
            [DRIVER_TAG, 'auto_courier'],
            [{'id': 'some_id', 'status': 'none'}],
            id='scenario_for_auto_courier_with_active_order(#3)',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '4', have_active_order=True),
            [DRIVER_TAG, 'auto_courier'],
            [{'id': 'some_id', 'status': 'none'}],
            id='scenario_for_auto_courier_with_active_order(#4)',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '5', have_active_order=True),
            [DRIVER_TAG, 'auto_courier'],
            [{'id': 'some_id', 'status': 'none'}],
            id='scenario_for_auto_courier_with_active_order(#5)',
        ),
        pytest.param(
            scenario_for_auto_courier('2'),
            [DRIVER_TAG, 'auto_courier'],
            [],
            id='auto_courier_realy_auto_courier_with_active_order',
        ),
        pytest.param(
            scenario_for_auto_courier('2'),
            [DRIVER_TAG, 'auto_courier'],
            [{'id': 'some_id', 'status': 'none'}],
            id='scenario_for_auto_courier_realy_auto_courier',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '1', premium=True),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'auto_courier'],
            [],
            id='premium_driver_scenario_for_auto_courier(#1)',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '2', premium=True),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'auto_courier'],
            [],
            id='premium_driver_scenario_for_auto_courier(#2)',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '3', premium=True),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'auto_courier'],
            [],
            id='premium_driver_scenario_for_auto_courier(#3)',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '4', premium=True),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'auto_courier'],
            [],
            id='premium_driver_scenario_for_auto_courier(#4)',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '5', premium=True),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'auto_courier'],
            [],
            id='premium_driver_scenario_for_auto_courier(#5)',
        ),
        pytest.param(
            scenario_for_auto_courier('2', premium=True),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'auto_courier'],
            [],
            id='premium_driver_scenario_for_auto_courier_realy_auto_courier',
        ),
        pytest.param(
            scenario_for_auto_courier(
                '1', '1', premium=True, have_active_order=True,
            ),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'auto_courier'],
            [{'id': 'some_id', 'status': 'none'}],
            id='premium_driver_for_auto_courier_with_active_order(#1)',
        ),
        pytest.param(
            scenario_for_auto_courier(
                '1', '2', premium=True, have_active_order=True,
            ),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'auto_courier'],
            [{'id': 'some_id', 'status': 'none'}],
            id='premium_driver_for_auto_courier_with_active_order(#2)',
        ),
        pytest.param(
            scenario_for_auto_courier(
                '1', '3', premium=True, have_active_order=True,
            ),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'auto_courier'],
            [{'id': 'some_id', 'status': 'none'}],
            id='premium_driver_for_auto_courier_with_active_order(#3)',
        ),
        pytest.param(
            scenario_for_auto_courier(
                '1', '4', premium=True, have_active_order=True,
            ),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'auto_courier'],
            [{'id': 'some_id', 'status': 'none'}],
            id='premium_driver_for_auto_courier_with_active_order(#4)',
        ),
        pytest.param(
            scenario_for_auto_courier(
                '1', '5', premium=True, have_active_order=True,
            ),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'auto_courier'],
            [{'id': 'some_id', 'status': 'none'}],
            id='premium_driver_for_auto_courier_with_active_order(#5)',
        ),
        pytest.param(
            scenario_for_auto_courier(
                '2', premium=True, have_active_order=True,
            ),
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'auto_courier'],
            [{'id': 'some_id', 'status': 'none'}],
            id='premium_driver_scenario_for_auto_courier_with_active_order',
        ),
    ],
)
async def test_scenarios(
        taxi_ivr_dispatcher,
        mongodb,
        scenario,
        driver_tags,
        orders,
        mockserver,
        mock_driver_profiles,
):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_store(request, *args, **kwargs):
        assert request.json['validate'] is True
        assert request.json['value'] == utils.DEFAULT_USER_PHONE
        return mockserver.make_response(
            json={
                'id': utils.DEFAULT_PERSONAL_PHONE_ID,
                'value': request.json['value'],
            },
            status=200,
        )

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    async def _handle(request):
        return {
            'drivers': [
                {
                    'dbid': utils.DEFAULT_PARK_ID,
                    'uuid': utils.DEFAULT_DRIVER_ID,
                    'tags': driver_tags,
                },
            ],
        }

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return {
            'statuses': [
                {
                    'status': 'offline',
                    'park_id': utils.DEFAULT_PARK_ID,
                    'driver_id': utils.DEFAULT_DRIVER_ID,
                    'orders': orders,
                },
            ],
        }

    for action, reply, checks in scenario:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)


@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'driver_support_worker',
                'type': 'native_worker',
            },
        },
    },
    IVR_DISPATCHER_DRIVER_SUPPORT_WORKER_SETTINGS={
        'allowed_driver_tags': [DRIVER_TAG],
        'premium_driver_tags': [ANOTHER_DRIVER_TAG],
        'adverse_driver_ivr_number': '9944',
        'premium_support_number': PREMIUM_SUPPORT_NUMBER,
        'finance_support_number': FINANCE_SUPPORT_NUMBER,
        'accounts_support_number': ACCOUNTS_SUPPORT_NUMBER,
        'other_support_number': OTHER_SUPPORT_NUMBER,
        'auto_courier_tags': ['auto_courier'],
        'active_order_rule': {
            'support_number': ACTIVE_ORDER_SUPPORT_NUMBER,
            'enable': True,
        },
        'enable_switch_to_adverse_driver_ivr': False,
    },
    IVR_DISPATCHER_PHRASE_BEFORE_SWITCH={'enabled': True, 'time_to_sleep': 10},
)
@pytest.mark.parametrize(
    ['scenario', 'driver_tags', 'orders'],
    [
        pytest.param(
            adverse_driver_scenario(enable_switch_to_adverse_driver_ivr=False),
            ['some_tag'],
            [],
            id='adverse_driver_scenario',
        ),
        pytest.param(
            adverse_driver_error_scenario(
                enable_switch_to_adverse_driver_ivr=False,
            ),
            ['some_tag'],
            [],
            id='adverse_driver_error_scenario',
        ),
    ],
)
async def test_for_new_adverse_driver_scenario(
        taxi_ivr_dispatcher,
        mongodb,
        scenario,
        driver_tags,
        orders,
        mockserver,
        mock_driver_profiles,
):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_store(request, *args, **kwargs):
        assert request.json['validate'] is True
        assert request.json['value'] == utils.DEFAULT_USER_PHONE
        return mockserver.make_response(
            json={
                'id': utils.DEFAULT_PERSONAL_PHONE_ID,
                'value': request.json['value'],
            },
            status=200,
        )

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    async def _handle(request):
        return {
            'drivers': [
                {
                    'dbid': utils.DEFAULT_PARK_ID,
                    'uuid': utils.DEFAULT_DRIVER_ID,
                    'tags': driver_tags,
                },
            ],
        }

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return {
            'statuses': [
                {
                    'status': 'offline',
                    'park_id': utils.DEFAULT_PARK_ID,
                    'driver_id': utils.DEFAULT_DRIVER_ID,
                    'orders': orders,
                },
            ],
        }

    for action, reply, checks in scenario:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)


@pytest.mark.parametrize(
    (
        'exp3_json_file_name',
        'personal_phone_id',
        'prompt_id',
        'delay',
        'need_hangup',
    ),
    (
        pytest.param(
            'experiments3_ivr_hello_for_dsw.json',
            utils.DEFAULT_PERSONAL_PHONE_ID,
            'dsw.hello1',
            3,
            False,
            id='exp enabled',
        ),
        pytest.param(
            'experiments3_ivr_hello_for_dsw.json',
            utils.DEFAULT_DRIVER_PERSONAL_PHONE_ID,
            'dsw.hello0',
            0,
            False,
            id='exp disabled',
        ),
        pytest.param(
            'experiments3_hangup_after_hello.json',
            utils.DEFAULT_PERSONAL_PHONE_ID,
            'dsw.hello1',
            3,
            True,
            id='hangup after hello',
        ),
    ),
)
@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'driver_support_worker',
                'type': 'native_worker',
            },
        },
    },
    IVR_DISPATCHER_DRIVER_SUPPORT_WORKER_SETTINGS={
        'allowed_driver_tags': [DRIVER_TAG],
        'adverse_driver_ivr_number': '9944',
        'premium_support_number': PREMIUM_SUPPORT_NUMBER,
        'finance_support_number': FINANCE_SUPPORT_NUMBER,
        'accounts_support_number': ACCOUNTS_SUPPORT_NUMBER,
        'other_support_number': OTHER_SUPPORT_NUMBER,
        'active_order_rule': {
            'support_number': ACTIVE_ORDER_SUPPORT_NUMBER,
            'enable': False,
        },
    },
    IVR_DISPATCHER_PHRASE_BEFORE_SWITCH={'enabled': True, 'time_to_sleep': 10},
)
async def test_hello_experiment(
        taxi_ivr_dispatcher,
        mongodb,
        exp3_json_file_name,
        personal_phone_id,
        prompt_id,
        delay,
        need_hangup,
        mockserver,
        mock_driver_profiles,
        experiments3,
        load_json,
):
    experiments3.add_experiments_json(load_json(exp3_json_file_name))

    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_store(request, *args, **kwargs):
        assert request.json['validate'] is True
        assert request.json['value'] == utils.DEFAULT_USER_PHONE
        return mockserver.make_response(
            json={'id': personal_phone_id, 'value': request.json['value']},
            status=200,
        )

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    async def _handle(request):
        return {
            'drivers': [
                {
                    'dbid': utils.DEFAULT_PARK_ID,
                    'uuid': utils.DEFAULT_DRIVER_ID,
                    'tags': [DRIVER_TAG],
                },
            ],
        }

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return {
            'statuses': [
                {
                    'status': 'offline',
                    'park_id': utils.DEFAULT_PARK_ID,
                    'driver_id': utils.DEFAULT_DRIVER_ID,
                },
            ],
        }

    for action, reply, checks in hello_experiment_scenario(
            prompt_id, delay, need_hangup,
    ):
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)
    await taxi_ivr_dispatcher.invalidate_caches()


@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'driver_support_worker',
                'type': 'native_worker',
            },
        },
    },
    IVR_DISPATCHER_DRIVER_SUPPORT_WORKER_SETTINGS={
        'allowed_driver_tags': [DRIVER_TAG],
        'premium_driver_tags': [ANOTHER_DRIVER_TAG],
        'adverse_driver_ivr_number': '9944',
        'premium_support_number': PREMIUM_SUPPORT_NUMBER,
        'support_number_for_selfemployed': SUPPORT_NUMBER_FOR_SELFEMPLOYED,
        'finance_support_number': FINANCE_SUPPORT_NUMBER,
        'accounts_support_number': ACCOUNTS_SUPPORT_NUMBER,
        'other_support_number': OTHER_SUPPORT_NUMBER,
        'selfemployed_tags_rule': {
            'selfemployed_tags': [SELFEMPLOYED_TAG],
            'driver_tags_for_selfemployed': [DRIVER_TAG_FOR_SELFEMPLOYED],
        },
        'auto_courier_tags': ['auto_courier'],
        'active_order_rule': {
            'support_number': ACTIVE_ORDER_SUPPORT_NUMBER,
            'enable': True,
        },
    },
    IVR_DISPATCHER_PHRASE_BEFORE_SWITCH={'enabled': True, 'time_to_sleep': 10},
)
@pytest.mark.parametrize(
    ['scenario', 'driver_tags', 'orders'],
    [
        pytest.param(
            main_scenario('1', selfemployed=True),
            [DRIVER_TAG],
            [],
            id='main_scenario_for_selfemployed(#1)',
        ),
        pytest.param(
            main_scenario('2', selfemployed=True),
            [DRIVER_TAG],
            [],
            id='main_scenario_for_selfemployed(#2)',
        ),
        pytest.param(
            main_scenario('3', selfemployed=True),
            [DRIVER_TAG],
            [],
            id='main_scenario_for_selfemployed(#3)',
        ),
        pytest.param(
            main_scenario('5', selfemployed=True),
            [DRIVER_TAG],
            [],
            id='main_scenario_for_selfemployed(#5)',
        ),
        pytest.param(
            main_scenario('1', premium=True),
            [ANOTHER_DRIVER_TAG],
            [],
            id='premium_scenario_for_selfemployed(#1)',
        ),
        pytest.param(
            main_scenario('2', premium=True),
            [ANOTHER_DRIVER_TAG],
            [],
            id='premium_scenario_for_selfemployed(#2)',
        ),
        pytest.param(
            main_scenario('3', premium=True),
            [ANOTHER_DRIVER_TAG],
            [],
            id='premium_scenario_for_selfemployed(#3)',
        ),
        pytest.param(
            main_scenario('5', premium=True),
            [ANOTHER_DRIVER_TAG],
            [],
            id='premium_scenario_for_selfemployed(#5)',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '1', selfemployed=True),
            [DRIVER_TAG, 'auto_courier'],
            [],
            id='scenario_for_auto_courier(#1)',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '2', selfemployed=True),
            [DRIVER_TAG, 'auto_courier'],
            [],
            id='scenario_for_auto_courier(#2)',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '3', selfemployed=True),
            [DRIVER_TAG, 'auto_courier'],
            [],
            id='scenario_for_auto_courier(#3)',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '4', selfemployed=True),
            [DRIVER_TAG, 'auto_courier'],
            [],
            id='scenario_for_auto_courier(#4)',
        ),
        pytest.param(
            scenario_for_auto_courier('1', '5', selfemployed=True),
            [DRIVER_TAG, 'auto_courier'],
            [],
            id='scenario_for_auto_courier(#5)',
        ),
        pytest.param(
            scenario_for_auto_courier('2', selfemployed=True),
            [DRIVER_TAG, 'auto_courier'],
            [],
            id='scenario_for_auto_courier_realy_auto_courier',
        ),
        pytest.param(
            main_scenario('1', have_active_order=True),
            [DRIVER_TAG, 'some_tag'],
            [{'id': 'some_id', 'status': 'none'}],
            id='main_scenario(#1)',
        ),
        pytest.param(
            main_scenario('2', have_active_order=True),
            [DRIVER_TAG, 'some_tag'],
            [{'id': 'some_id', 'status': 'none'}],
            id='main_scenario(#2)',
        ),
        pytest.param(
            main_scenario('3', have_active_order=True),
            [DRIVER_TAG, 'some_tag'],
            [{'id': 'some_id', 'status': 'none'}],
            id='main_scenario(#3)',
        ),
        pytest.param(
            main_scenario('5', have_active_order=True),
            [DRIVER_TAG, 'some_tag'],
            [{'id': 'some_id', 'status': 'none'}],
            id='main_scenario(#5)',
        ),
    ],
)
async def test_scenarios_for_selfemployed(
        taxi_ivr_dispatcher,
        mongodb,
        scenario,
        driver_tags,
        orders,
        mockserver,
        mock_driver_profiles,
):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_store(request, *args, **kwargs):
        assert request.json['validate'] is True
        assert request.json['value'] == utils.DEFAULT_USER_PHONE
        return mockserver.make_response(
            json={
                'id': utils.DEFAULT_PERSONAL_PHONE_ID,
                'value': request.json['value'],
            },
            status=200,
        )

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    async def _handle(request):
        return {
            'drivers': [
                {
                    'dbid': utils.DEFAULT_PARK_ID,
                    'uuid': utils.DEFAULT_DRIVER_ID,
                    'tags': driver_tags,
                },
                {
                    'dbid': '-1',
                    'uuid': utils.DEFAULT_DRIVER_ID,
                    'tags': [SELFEMPLOYED_TAG, DRIVER_TAG_FOR_SELFEMPLOYED],
                },
            ],
        }

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return {
            'statuses': [
                {
                    'status': 'offline',
                    'park_id': utils.DEFAULT_PARK_ID,
                    'driver_id': utils.DEFAULT_DRIVER_ID,
                },
                {
                    'status': 'online',
                    'park_id': '-1',
                    'driver_id': utils.DEFAULT_DRIVER_ID,
                    'orders': orders,
                },
            ],
        }

    for action, reply, checks in scenario:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)


@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'driver_support_worker',
                'type': 'native_worker',
            },
        },
    },
    IVR_DISPATCHER_DRIVER_SUPPORT_WORKER_SETTINGS={
        'allowed_driver_tags': [DRIVER_TAG],
        'premium_driver_tags': [ANOTHER_DRIVER_TAG],
        'adverse_driver_ivr_number': '9944',
        'premium_support_number': PREMIUM_SUPPORT_NUMBER,
        'finance_support_number': FINANCE_SUPPORT_NUMBER,
        'accounts_support_number': ACCOUNTS_SUPPORT_NUMBER,
        'other_support_number': OTHER_SUPPORT_NUMBER,
        'active_order_rule': {
            'support_number': ACTIVE_ORDER_SUPPORT_NUMBER,
            'enable': False,
        },
    },
    IVR_DISPATCHER_PHRASE_BEFORE_SWITCH={'enabled': True, 'time_to_sleep': 10},
)
@pytest.mark.parametrize(
    ['scenario', 'driver_tags'],
    [
        pytest.param(
            ERROR_IN_PD_SCENARIO,
            ['some_tag'],
            id='error_in_pd_for_adverse_driver',
        ),
        pytest.param(
            ERROR_IN_PD_SCENARIO, [DRIVER_TAG, 'some_tag'], id='error_in_pd',
        ),
        pytest.param(
            ERROR_IN_PD_SCENARIO,
            [DRIVER_TAG, ANOTHER_DRIVER_TAG, 'some_tag'],
            id='error_in_pd_for_premium_driver',
        ),
    ],
)
async def test_if_error_in_pd(
        taxi_ivr_dispatcher,
        mongodb,
        scenario,
        driver_tags,
        mockserver,
        mock_driver_profiles,
):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_store(request, *args, **kwargs):
        assert request.json['validate'] is True
        assert request.json['value'] == utils.DEFAULT_USER_PHONE
        return {'code': 400, 'message': 'test'}

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    async def _handle(request):
        return {
            'drivers': [
                {
                    'dbid': utils.DEFAULT_PARK_ID,
                    'uuid': utils.DEFAULT_DRIVER_ID,
                    'tags': driver_tags,
                },
            ],
        }

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return {
            'statuses': [
                {
                    'status': 'offline',
                    'park_id': utils.DEFAULT_PARK_ID,
                    'driver_id': utils.DEFAULT_DRIVER_ID,
                },
            ],
        }

    for action, reply, checks in scenario:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)


@pytest.mark.parametrize(
    ('scenario', 'driver_tags', 'exp3_json_file_name', 'personal_phone_id'),
    (
        pytest.param(
            main_scenario('1', have_active_order=True),
            [],
            'experiments3_enable_support_for_active_order.json',
            utils.DEFAULT_PERSONAL_PHONE_ID,
            id='main_scenario(#1)',
        ),
        pytest.param(
            main_scenario('2', have_active_order=True),
            [],
            'experiments3_enable_support_for_active_order.json',
            utils.DEFAULT_PERSONAL_PHONE_ID,
            id='main_scenario(#2)',
        ),
        pytest.param(
            main_scenario('3', have_active_order=True),
            [],
            'experiments3_enable_support_for_active_order.json',
            utils.DEFAULT_PERSONAL_PHONE_ID,
            id='main_scenario(#3)',
        ),
        pytest.param(
            bonuses_menu_scenario(False),
            [],
            'experiments3_enable_support_for_active_order.json',
            utils.DEFAULT_PERSONAL_PHONE_ID,
            id='bonus_menu_scenario(#4)',
        ),
        pytest.param(
            main_scenario('5', have_active_order=True),
            [],
            'experiments3_enable_support_for_active_order.json',
            utils.DEFAULT_PERSONAL_PHONE_ID,
            id='main_scenario(#5)',
        ),
        pytest.param(
            adverse_driver_scenario(),
            [],
            'experiments3_disable_support_for_active_order.json',
            utils.DEFAULT_PERSONAL_PHONE_ID,
            id='scenario_for_adverse_driver_and_active_order_disable_by_exp',
        ),
        pytest.param(
            main_scenario('1', have_active_order=True),
            [DRIVER_TAG],
            'experiments3_enable_support_for_active_order.json',
            utils.DEFAULT_PERSONAL_PHONE_ID,
            id='main_scenario_for_allowed_driver(#1)',
        ),
        pytest.param(
            main_scenario('2', have_active_order=True),
            [DRIVER_TAG],
            'experiments3_enable_support_for_active_order.json',
            utils.DEFAULT_PERSONAL_PHONE_ID,
            id='main_scenario_for_allowed_driver(#2)',
        ),
        pytest.param(
            main_scenario('3', have_active_order=True),
            [DRIVER_TAG],
            'experiments3_enable_support_for_active_order.json',
            utils.DEFAULT_PERSONAL_PHONE_ID,
            id='main_scenario_for_allowed_driver(#3)',
        ),
        pytest.param(
            bonuses_menu_scenario(False),
            [DRIVER_TAG],
            'experiments3_enable_support_for_active_order.json',
            utils.DEFAULT_PERSONAL_PHONE_ID,
            id='bonus_menu_scenario_for_allowed_driver(#4)',
        ),
        pytest.param(
            main_scenario('5', have_active_order=True),
            [DRIVER_TAG],
            'experiments3_enable_support_for_active_order.json',
            utils.DEFAULT_PERSONAL_PHONE_ID,
            id='main_scenario_for_allowed_driver(#5)',
        ),
    ),
)
@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'driver_support_worker',
                'type': 'native_worker',
            },
        },
    },
    IVR_DISPATCHER_DRIVER_SUPPORT_WORKER_SETTINGS={
        'allowed_driver_tags': [DRIVER_TAG],
        'adverse_driver_ivr_number': '9944',
        'premium_support_number': PREMIUM_SUPPORT_NUMBER,
        'finance_support_number': FINANCE_SUPPORT_NUMBER,
        'accounts_support_number': ACCOUNTS_SUPPORT_NUMBER,
        'other_support_number': OTHER_SUPPORT_NUMBER,
        'active_order_rule': {
            'support_number': ACTIVE_ORDER_SUPPORT_NUMBER,
            'enable': False,
        },
    },
    IVR_DISPATCHER_PHRASE_BEFORE_SWITCH={'enabled': True, 'time_to_sleep': 10},
)
async def test_voice_support_for_driver_with_active_order(
        taxi_ivr_dispatcher,
        mongodb,
        scenario,
        driver_tags,
        exp3_json_file_name,
        personal_phone_id,
        mockserver,
        mock_driver_profiles,
        experiments3,
        load_json,
):
    experiments3.add_experiments_json(load_json(exp3_json_file_name))

    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_store(request, *args, **kwargs):
        assert request.json['validate'] is True
        assert request.json['value'] == utils.DEFAULT_USER_PHONE
        return mockserver.make_response(
            json={'id': personal_phone_id, 'value': request.json['value']},
            status=200,
        )

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    async def _handle(request):
        return {
            'drivers': [
                {
                    'dbid': utils.DEFAULT_PARK_ID,
                    'uuid': utils.DEFAULT_DRIVER_ID,
                    'tags': driver_tags,
                },
            ],
        }

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return {
            'statuses': [
                {
                    'status': 'offline',
                    'park_id': utils.DEFAULT_PARK_ID,
                    'driver_id': utils.DEFAULT_DRIVER_ID,
                    'orders': [{'id': 'some_id', 'status': 'none'}],
                },
            ],
        }

    for action, reply, checks in scenario:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)
    await taxi_ivr_dispatcher.invalidate_caches()


@pytest.mark.parametrize(
    ('scenario', 'driver_tags', 'exp3_json_file_name', 'personal_phone_id'),
    (
        pytest.param(
            adverse_driver_scenario(enable_switch_to_adverse_driver_ivr=False),
            [],
            'experiments3_disable_support_for_active_order.json',
            utils.DEFAULT_PERSONAL_PHONE_ID,
            id='scenario_for_adverse_driver_and_active_order_disable_by_exp',
        ),
    ),
)
@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'driver_support_worker',
                'type': 'native_worker',
            },
        },
    },
    IVR_DISPATCHER_DRIVER_SUPPORT_WORKER_SETTINGS={
        'allowed_driver_tags': [DRIVER_TAG],
        'adverse_driver_ivr_number': '9944',
        'premium_support_number': PREMIUM_SUPPORT_NUMBER,
        'finance_support_number': FINANCE_SUPPORT_NUMBER,
        'accounts_support_number': ACCOUNTS_SUPPORT_NUMBER,
        'other_support_number': OTHER_SUPPORT_NUMBER,
        'active_order_rule': {
            'support_number': ACTIVE_ORDER_SUPPORT_NUMBER,
            'enable': False,
        },
        'enable_switch_to_adverse_driver_ivr': False,
    },
    IVR_DISPATCHER_PHRASE_BEFORE_SWITCH={'enabled': True, 'time_to_sleep': 10},
)
async def test_for_new_adverse_driver_scenario_with_active_order(
        taxi_ivr_dispatcher,
        mongodb,
        scenario,
        driver_tags,
        exp3_json_file_name,
        personal_phone_id,
        mockserver,
        mock_driver_profiles,
        experiments3,
        load_json,
):
    experiments3.add_experiments_json(load_json(exp3_json_file_name))

    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_store(request, *args, **kwargs):
        assert request.json['validate'] is True
        assert request.json['value'] == utils.DEFAULT_USER_PHONE
        return mockserver.make_response(
            json={'id': personal_phone_id, 'value': request.json['value']},
            status=200,
        )

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    async def _handle(request):
        return {
            'drivers': [
                {
                    'dbid': utils.DEFAULT_PARK_ID,
                    'uuid': utils.DEFAULT_DRIVER_ID,
                    'tags': driver_tags,
                },
            ],
        }

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return {
            'statuses': [
                {
                    'status': 'offline',
                    'park_id': utils.DEFAULT_PARK_ID,
                    'driver_id': utils.DEFAULT_DRIVER_ID,
                    'orders': [{'id': 'some_id', 'status': 'none'}],
                },
            ],
        }

    for action, reply, checks in scenario:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)
    await taxi_ivr_dispatcher.invalidate_caches()


@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'driver_support_worker',
                'type': 'native_worker',
            },
        },
    },
    IVR_DISPATCHER_DRIVER_SUPPORT_WORKER_SETTINGS={
        'allowed_driver_tags': [DRIVER_TAG],
        'premium_driver_tags': [ANOTHER_DRIVER_TAG],
        'adverse_driver_ivr_number': '9944',
        'premium_support_number': PREMIUM_SUPPORT_NUMBER,
        'finance_support_number': FINANCE_SUPPORT_NUMBER,
        'accounts_support_number': ACCOUNTS_SUPPORT_NUMBER,
        'other_support_number': OTHER_SUPPORT_NUMBER,
        'active_order_rule': {
            'support_number': ACTIVE_ORDER_SUPPORT_NUMBER,
            'enable': False,
        },
        'operators_tags': {
            'aggressive_driver': {
                'enabled': True,
                'name': 'complaint_aggressive_driver',
            },
        },
    },
    IVR_DISPATCHER_PHRASE_BEFORE_SWITCH={'enabled': True, 'time_to_sleep': 10},
)
@pytest.mark.parametrize(
    'scenario',
    (
        pytest.param(
            AGGRESSIVE_DRIVER_SCENARIO, id='aggressive_driver_scenario',
        ),
    ),
)
async def test_aggressive_driver(
        taxi_ivr_dispatcher,
        mongodb,
        scenario,
        mockserver,
        mock_driver_profiles,
):
    @mockserver.json_handler('/callcenter-qa/v1/tags/info')
    def _mock_cc_qa_tags(request):
        return mockserver.make_response(
            json={
                'tags': [
                    {'reason': 'complaint_aggressive_driver', 'project': 'sp'},
                ],
            },
            status=200,
        )

    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_store(request, *args, **kwargs):
        assert request.json['validate'] is True
        assert request.json['value'] == utils.DEFAULT_USER_PHONE
        return mockserver.make_response(
            json={
                'id': utils.DEFAULT_PERSONAL_PHONE_ID,
                'value': request.json['value'],
            },
            status=200,
        )

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    async def _handle(request):
        return {
            'drivers': [
                {
                    'dbid': utils.DEFAULT_PARK_ID,
                    'uuid': utils.DEFAULT_DRIVER_ID,
                    'tags': [],
                },
            ],
        }

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return {
            'statuses': [
                {
                    'status': 'offline',
                    'park_id': utils.DEFAULT_PARK_ID,
                    'driver_id': utils.DEFAULT_DRIVER_ID,
                    'orders': [],
                },
            ],
        }

    for action, reply, checks in scenario:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        for check in checks:
            check(mongodb)
