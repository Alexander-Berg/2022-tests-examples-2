import pytest

from tests_ivr_dispatcher import utils


# Scenarios
GOOD_SCENARIO = [
    (
        utils.OCTONODE_INITIAL_RESULT_TEST_WORKER,
        utils.DISPATCHER_ANSWER_NOREC_REPLY,
    ),
    (utils.OCTONODE_ANSWER_OK_RESULT, utils.DISPATCHER_PLAY_TEST_REPLY),
    (
        utils.OCTONODE_PLAY_OK_RESULT,
        utils.DISPATCHER_ASK_TEST_INPUT_TEXT_REPLY,
    ),
    (
        utils.OCTONODE_ASK_DIGIT_1_REPLY,
        utils.DISPATCHER_ASK_TEST_INPUT_PLAY_REPLY,
    ),
    (
        utils.OCTONODE_ASK_TEXT_CHECK_REPLY,
        utils.DISPATCHER_ASK_TEST_INPUT_PLAY_REPLY,
    ),
    (utils.OCTONODE_ASK_TEXT_END_REPLY, utils.DISPATCHER_HANGUP_REPLY),
]
HANGUP_SCENARIO_PLAYBACK = [
    (
        utils.OCTONODE_INITIAL_RESULT_TEST_WORKER,
        utils.DISPATCHER_ANSWER_NOREC_REPLY,
    ),
    (utils.OCTONODE_ANSWER_OK_RESULT, utils.DISPATCHER_PLAY_TEST_REPLY),
    (utils.OCTONODE_PLAY_USER_HANGUP, utils.DISPATCHER_HANGUP_REPLY),
]
ERROR_SCENARIO_PLAYBACK = [
    (
        utils.OCTONODE_INITIAL_RESULT_TEST_WORKER,
        utils.DISPATCHER_ANSWER_NOREC_REPLY,
    ),
    (utils.OCTONODE_ANSWER_OK_RESULT, utils.DISPATCHER_PLAY_TEST_REPLY),
    (utils.OCTONODE_PLAY_ERR_RESULT, utils.DISPATCHER_HANGUP_REPLY),
]
HANGUP_SCENARIO_ASK = [
    (
        utils.OCTONODE_INITIAL_RESULT_TEST_WORKER,
        utils.DISPATCHER_ANSWER_NOREC_REPLY,
    ),
    (utils.OCTONODE_ANSWER_OK_RESULT, utils.DISPATCHER_PLAY_TEST_REPLY),
    (
        utils.OCTONODE_PLAY_OK_RESULT,
        utils.DISPATCHER_ASK_TEST_INPUT_TEXT_REPLY,
    ),
    (utils.OCTONODE_ASK_USER_HANGUP, utils.DISPATCHER_HANGUP_REPLY),
]


@pytest.mark.parametrize(
    'scenario',
    [
        GOOD_SCENARIO,
        ERROR_SCENARIO_PLAYBACK,
        HANGUP_SCENARIO_PLAYBACK,
        HANGUP_SCENARIO_ASK,
    ],
    ids=(
        'normal',
        'playback_error',
        'user_hangup_playback',
        'user_hangup_ask',
    ),
)
async def test_worker_scenarios(
        taxi_ivr_dispatcher,
        pgsql,
        scenario,
        mock_user_api,
        mock_int_authproxy,
        mock_personal_phones,
):
    for action, reply in scenario:
        request = {'session_id': utils.NEW_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        assert response.json() == reply
        db = pgsql['ivr_api']
        cursor = db.cursor()
        cursor.execute('SELECT * FROM ivr_api.worker_actions')
        result = list(cursor.fetchall())
        assert result
