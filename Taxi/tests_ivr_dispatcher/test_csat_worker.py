from aiohttp import web
import pytest

from tests_ivr_dispatcher import utils

CSAT_DEFAULT_VAD_CONFIG = {
    'no-input-timeout-ms': 10000,
    'speech-complete-timeout-ms': 2000,
    'speech-timeout-ms': 10000,
    'vad-silence-ms': 20,
    'vad-threshold': 40,
    'vad-voice-ms': 20,
}

OCTONODE_INITIAL_RESULT = {
    'called_number': utils.DEFAULT_TAXI_PHONE,  # call_from
    'caller_number': utils.DEFAULT_USER_PHONE,  # call_to
    'call_guid': 'some_call_guid',
    'status': 'ok',
    'type': 'initial',
}

CSAT_WORKER_ASK_RATING_REPLY = {
    'params': {
        'allowed_dtmf': 'any',
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'no-input-timeout-ms': CSAT_DEFAULT_VAD_CONFIG['no-input-timeout-ms'],
        'speech-complete-timeout-ms': CSAT_DEFAULT_VAD_CONFIG[
            'speech-complete-timeout-ms'
        ],
        'speech-timeout-ms': CSAT_DEFAULT_VAD_CONFIG['speech-timeout-ms'],
        'start-input-timers': True,
        'relative_path': 'csat_worker/csat.hello_request.wav',
        'vad-silence-ms': CSAT_DEFAULT_VAD_CONFIG['vad-silence-ms'],
        'vad-threshold': CSAT_DEFAULT_VAD_CONFIG['vad-threshold'],
        'vad-voice-ms': CSAT_DEFAULT_VAD_CONFIG['vad-voice-ms'],
        'no-local-vad': False,
    },
    'type': 'ask',
}

CSAT_WORKER_PLAY_BYE_REPLY = {
    'params': {'relative_path': 'csat_worker/csat.rating_cancelled.wav'},
    'type': 'play',
}

OCTONODE_ASK_RATING_RESULT = {
    'user_input': 'Без проблем, работу оцениваю на 5 баллов',
    'status': 'ok',
    'type': 'ask',
}

OCTONODE_ASK_RATING_BAD_RESULT = {'status': 'error', 'type': 'ask'}

CSAT_WORKER_REPEAT_ASK_REPLY = {
    'params': {
        'allowed_dtmf': 'any',
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'no-input-timeout-ms': CSAT_DEFAULT_VAD_CONFIG['no-input-timeout-ms'],
        'speech-complete-timeout-ms': CSAT_DEFAULT_VAD_CONFIG[
            'speech-complete-timeout-ms'
        ],
        'speech-timeout-ms': CSAT_DEFAULT_VAD_CONFIG['speech-timeout-ms'],
        'start-input-timers': True,
        'relative_path': 'csat_worker/csat.repeat_request.wav',
        'vad-silence-ms': CSAT_DEFAULT_VAD_CONFIG['vad-silence-ms'],
        'vad-threshold': CSAT_DEFAULT_VAD_CONFIG['vad-threshold'],
        'vad-voice-ms': CSAT_DEFAULT_VAD_CONFIG['vad-voice-ms'],
        'no-local-vad': False,
    },
    'type': 'ask',
}

CSAT_MAIN_SCENARIO = [
    (OCTONODE_INITIAL_RESULT, utils.DISPATCHER_ANSWER_REPLY, None),
    (utils.OCTONODE_ANSWER_OK_RESULT, CSAT_WORKER_ASK_RATING_REPLY, None),
    (OCTONODE_ASK_RATING_RESULT, CSAT_WORKER_PLAY_BYE_REPLY, None),
    (utils.OCTONODE_PLAY_OK_RESULT, utils.DISPATCHER_HANGUP_REPLY, None),
]

CSAT_REPEAT_ASK_SCENARIO = [
    (OCTONODE_INITIAL_RESULT, utils.DISPATCHER_ANSWER_REPLY, None),
    (utils.OCTONODE_ANSWER_OK_RESULT, CSAT_WORKER_ASK_RATING_REPLY, None),
    (OCTONODE_ASK_RATING_BAD_RESULT, CSAT_WORKER_REPEAT_ASK_REPLY, None),
    (OCTONODE_ASK_RATING_RESULT, CSAT_WORKER_PLAY_BYE_REPLY, None),
    (utils.OCTONODE_PLAY_OK_RESULT, utils.DISPATCHER_HANGUP_REPLY, None),
]

CSAT_REPEAT_FAILED_ASK_SCENARIO = [
    (OCTONODE_INITIAL_RESULT, utils.DISPATCHER_ANSWER_REPLY, None),
    (utils.OCTONODE_ANSWER_OK_RESULT, CSAT_WORKER_ASK_RATING_REPLY, None),
    (OCTONODE_ASK_RATING_BAD_RESULT, CSAT_WORKER_REPEAT_ASK_REPLY, None),
    (OCTONODE_ASK_RATING_BAD_RESULT, utils.DISPATCHER_HANGUP_REPLY, None),
]

CSAT_FAILED_TO_SAVE = [
    (OCTONODE_INITIAL_RESULT, utils.DISPATCHER_ANSWER_REPLY, None),
    (utils.OCTONODE_ANSWER_OK_RESULT, CSAT_WORKER_ASK_RATING_REPLY, None),
    (OCTONODE_ASK_RATING_RESULT, CSAT_WORKER_PLAY_BYE_REPLY, None),
    (utils.OCTONODE_PLAY_OK_RESULT, utils.DISPATCHER_HANGUP_REPLY, None),
]


@pytest.mark.now('2021-07-30T19:00:00.00Z')
@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'csat_worker',
                'type': 'native_worker',
            },
        },
        'public_numbers': {},
    },
    IVR_DISPATCHER_CSAT_REG_EXP={
        'patterns_map': {
            '1': ['\\W(1)\\W'],
            '2': ['\\W(2)\\W'],
            '3': ['\\W(3)\\W'],
            '4': ['\\W(4)\\W'],
            '5': ['\\W(5)\\W'],
        },
    },
)
@pytest.mark.parametrize(
    ['scenario', 'expected_support_ratings'],
    [
        pytest.param(CSAT_MAIN_SCENARIO, [('5', 'some_call_guid')]),
        pytest.param(CSAT_REPEAT_ASK_SCENARIO, [('5', 'some_call_guid')]),
        pytest.param(
            CSAT_REPEAT_FAILED_ASK_SCENARIO, [(None, 'some_call_guid')],
        ),
    ],
    ids=('csat_main_scenario', 'csat_repeat_scenario', 'failed_ask_scenario'),
)
async def test_scenarios(
        taxi_ivr_dispatcher,
        mongodb,
        scenario,
        expected_support_ratings,
        mockserver,
        mock_user_api,
        mock_int_authproxy,
        mock_personal,
        mock_callcenter_qa,
):
    for action, reply, _ in scenario:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
    assert [
        (row[1], row[2]) for row in mock_callcenter_qa.support_ratings
    ] == expected_support_ratings


@pytest.mark.now('2021-07-30T19:00:00.00Z')
@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'csat_worker',
                'type': 'native_worker',
            },
        },
        'public_numbers': {},
    },
    IVR_DISPATCHER_CSAT_REG_EXP={
        'patterns_map': {
            '1': ['\\W(1)\\W'],
            '2': ['\\W(2)\\W'],
            '3': ['\\W(3)\\W'],
            '4': ['\\W(4)\\W'],
            '5': ['\\W(5)\\W'],
        },
    },
)
async def test_bad_client(
        taxi_ivr_dispatcher,
        mongodb,
        mockserver,
        mock_user_api,
        mock_int_authproxy,
        mock_personal,
):
    @mockserver.json_handler('/callcenter-qa/v1/rating/save', prefix=True)
    async def _handle(request):
        return web.Response(status=500)

    for action, reply, _ in CSAT_FAILED_TO_SAVE:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
