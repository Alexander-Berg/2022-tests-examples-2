import pytest

from tests_ivr_dispatcher import fwt_utils as utils


@pytest.fixture(name='dial_client')
def mock_dial_client_dialog(mockserver):
    class DialClient:
        @staticmethod
        @mockserver.json_handler('/v1/ivr-framework/call-notify')
        async def notify_handler(request):
            msg = utils.Message(request.json)
            response = msg.response()
            if response:
                return response
            raise mockserver.TimeoutError()

    return DialClient()


# Checks
def check_answered_in_db(db):
    db_session_doc = db.ivr_disp_sessions.find_one({'_id': utils.SESSION_ID})
    assert 'context' in db_session_doc
    assert db_session_doc['context']['call_answered']


def check_hangup_in_db(db):
    db_session_doc = db.ivr_disp_sessions.find_one({'_id': utils.SESSION_ID})
    assert 'context' in db_session_doc
    assert not db_session_doc['context']['call_answered']


def check_wait_event_in_db(db):
    db_session_doc = db.ivr_disp_sessions.find_one({'_id': utils.SESSION_ID})
    assert 'context' in db_session_doc
    assert db_session_doc['context']['waiting_event']


# Test outgoing scenarios
OUTGOING_GOOD_CALL = [
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL, None),
    (
        utils.OUTGOING_TANYA_DIAL_OK,
        utils.DISPATCHER_ASK_PLAY_INTRO,
        check_answered_in_db,
    ),
    (utils.TANYA_ASK_REPLY_RABBIT, utils.DISPATCHER_ASK_PLAY_RABBIT, None),
    (utils.TANYA_ASK_REPLY_ANY, utils.DISPATCHER_ASK_SPEAK_SAID_ANY, None),
    (utils.TANYA_ASK_REPLY_CLOSE_ANY, utils.DISPATCHER_HANGUP, None),
]
OUTGOING_NO_ANSWER = [
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL, None),
    (
        utils.OUTGOING_TANYA_DIAL_ERROR,
        utils.DISPATCHER_HANGUP,
        check_hangup_in_db,
    ),
]
OUTGOING_RETRY_ACTION_RESULT = [
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL, None),
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL, None),
    (
        utils.OUTGOING_TANYA_DIAL_OK,
        utils.DISPATCHER_ASK_PLAY_INTRO,
        check_answered_in_db,
    ),
    (
        utils.TANYA_ASK_REPLY_RABBIT_RETRY,
        utils.DISPATCHER_PLAY_RABBIT_PROMPT,
        None,
    ),
    (
        utils.TANYA_PLAY_RABBIT_OK_RESULT,
        utils.DISPATCHER_ASK_PLAY_RABBIT,
        None,
    ),
    (
        utils.TANYA_PLAY_RABBIT_OK_RESULT,
        utils.DISPATCHER_ASK_PLAY_RABBIT,
        None,
    ),
    (utils.TANYA_ASK_REPLY_ANY, utils.DISPATCHER_ASK_SPEAK_SAID_ANY, None),
    (utils.TANYA_ASK_REPLY_CLOSE_ANY, utils.DISPATCHER_HANGUP, None),
]
OUTGOING_ASK_USER_HANGUP = [
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL, None),
    (
        utils.OUTGOING_TANYA_DIAL_OK,
        utils.DISPATCHER_ASK_PLAY_INTRO,
        check_answered_in_db,
    ),
    (utils.TANYA_ASK_USER_HANGUP, utils.DISPATCHER_FINISHED_HANGUP, None),
]
OUTGOING_ASK_SK_ERROR = [
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL, None),
    (utils.OUTGOING_TANYA_DIAL_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (utils.TANYA_ASK_ERROR_RESULT, utils.DISPATCHER_PLAY_ERROR_PROMPT, None),
    (utils.TANYA_PLAY_ERROR_OK_RESULT, utils.DISPATCHER_HANGUP, None),
]
OUTGOING_ASK_RETRY_ON_002 = [
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL, None),
    (utils.OUTGOING_TANYA_DIAL_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_INTRO_RESULT_NO_INPUT,
        utils.DISPATCHER_ASK_PLAY_INTRO,
        None,
    ),
]
OUTGOING_ASK_RETRY_ON_DTMF = [
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL, None),
    (utils.OUTGOING_TANYA_DIAL_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (utils.TANYA_ASK_REPLY_DTMF, utils.DISPATCHER_ASK_SPEAK_SAID_DTMF, None),
    (
        utils.TANYA_ASK_DTMF_RESULT_NO_INPUT,
        utils.DISPATCHER_ASK_PLAY_INTRO,
        None,
    ),
]
OUTGOING_OLD_STYLE_GOOD_FORWARD = [
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL, None),
    (utils.OUTGOING_TANYA_DIAL_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_FORWARD_INTRO,
        utils.DISPATCHER_FORWARD_REPLY,
        None,
    ),
    (utils.TANYA_BRIDGE_EVENT, utils.DISPATCHER_EMPTY_REPLY, None),
    (
        utils.TANYA_OLD_STYLE_FORWARDING_RESULT_OK,
        utils.DISPATCHER_PLAY_RABBIT_PROMPT,
        None,
    ),
    (utils.TANYA_PLAY_RABBIT_OK_RESULT, utils.DISPATCHER_HANGUP, None),
]
OUTGOING_GOOD_FORWARD = [
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL, None),
    (utils.OUTGOING_TANYA_DIAL_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_FORWARD_INTRO,
        utils.DISPATCHER_FORWARD_REPLY,
        None,
    ),
    (utils.TANYA_BRIDGE_EVENT, utils.DISPATCHER_EMPTY_REPLY, None),
    (
        utils.TANYA_FORWARDING_RESULT_TRANSFEREE_HUP,
        utils.DISPATCHER_PLAY_RABBIT_PROMPT,
        None,
    ),
    (utils.TANYA_PLAY_RABBIT_OK_RESULT, utils.DISPATCHER_HANGUP, None),
]
OUTGOING_FORWARD_INITIATOR_HUP = [
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL, None),
    (utils.OUTGOING_TANYA_DIAL_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_FORWARD_INTRO,
        utils.DISPATCHER_FORWARD_REPLY,
        None,
    ),
    (utils.TANYA_BRIDGE_EVENT, utils.DISPATCHER_EMPTY_REPLY, None),
    (
        utils.TANYA_FORWARDING_RESULT_INITIATOR_HUP,
        utils.DISPATCHER_FINISHED_HANGUP,
        None,
    ),
]
OUTGOING_FORWARD_TRANSFEREE_HUP = [
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL, None),
    (utils.OUTGOING_TANYA_DIAL_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_FORWARD_INTRO,
        utils.DISPATCHER_FORWARD_REPLY,
        None,
    ),
    (utils.TANYA_BRIDGE_EVENT, utils.DISPATCHER_EMPTY_REPLY, None),
    (
        utils.TANYA_FORWARDING_RESULT_TRANSFEREE_HUP,
        utils.DISPATCHER_PLAY_RABBIT_PROMPT,
        None,
    ),
    (utils.TANYA_PLAY_RABBIT_OK_RESULT, utils.DISPATCHER_HANGUP, None),
]
OUTGOING_ERROR_FORWARD_ABONENT_HANGUP = [
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL, None),
    (utils.OUTGOING_TANYA_DIAL_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_FORWARD_INTRO,
        utils.DISPATCHER_FORWARD_REPLY,
        None,
    ),
    (
        utils.TANYA_FORWARDING_RESULT_ERROR_ABONENT_HANGUP,
        utils.DISPATCHER_FINISHED_HANGUP,
        None,
    ),
]
OUTGOING_ERROR_FORWARD_TRANSFEREE_NO_ANSWER = [
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL, None),
    (utils.OUTGOING_TANYA_DIAL_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_FORWARD_INTRO,
        utils.DISPATCHER_FORWARD_REPLY,
        None,
    ),
    (
        utils.TANYA_FORWARDING_RESULT_ERROR_TRANSFEREE_NO_ANSWER,
        utils.DISPATCHER_FORWARD_BACKUP_REPLY,
        None,
    ),
    (utils.TANYA_BRIDGE_EVENT_BACKUP, utils.DISPATCHER_EMPTY_REPLY, None),
]
OUTGOING_UID_FORWARD = [
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL, None),
    (utils.OUTGOING_TANYA_DIAL_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_FORWARD_UID,
        utils.DISPATCHER_FORWARD_UID_REPLY,
        None,
    ),
    (
        utils.TANYA_FORWARDING_RESULT_TRANSFEREE_HUP,
        utils.DISPATCHER_PLAY_RABBIT_PROMPT,
        None,
    ),
    (utils.TANYA_PLAY_RABBIT_OK_RESULT, utils.DISPATCHER_HANGUP, None),
]
OUTGOING_UID_FORWARD_X_ROUTE = [
    (
        utils.OUTGOING_TANYA_INITIAL,
        utils.OUTGOING_DISPATCHER_DIAL_X_ROUTE,
        None,
    ),
    (utils.OUTGOING_TANYA_DIAL_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_FORWARD_UID,
        utils.DISPATCHER_FORWARD_UID_REPLY_X_ROUTE,
        None,
    ),
    (
        utils.TANYA_FORWARDING_RESULT_TRANSFEREE_HUP,
        utils.DISPATCHER_PLAY_RABBIT_PROMPT,
        None,
    ),
    (utils.TANYA_PLAY_RABBIT_OK_RESULT, utils.DISPATCHER_HANGUP, None),
]
OUTGOING_FALLBACK = [
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL, None),
    (utils.OUTGOING_TANYA_DIAL_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_FALLBACK,
        utils.DISPATCHER_PLAY_FALLBACK_PROMPT,
        None,
    ),
    (
        utils.TANYA_PLAY_FALLBACK_OK_RESULT,
        utils.DISPATCHER_FALLBACK_HANGUP,
        None,
    ),
]
OUTGOING_HOLD = [
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL, None),
    (utils.OUTGOING_TANYA_DIAL_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_HOLD,
        utils.DISPATCHER_HOLD,
        check_wait_event_in_db,
    ),
]
OUTGOING_SKIP_HOLDS = [
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL, None),
    (utils.OUTGOING_TANYA_DIAL_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_SKIP_HOLDS,
        utils.DISPATCHER_PLAY_RABBIT_PROMPT,
        None,
    ),
    (
        utils.TANYA_PLAY_RABBIT_OK_RESULT,
        utils.DISPATCHER_ASK_SPEAK_SAID_ANY,
        None,
    ),
    (
        utils.TANYA_PLAY_RABBIT_OK_RESULT,
        utils.DISPATCHER_ASK_SPEAK_SAID_ANY,
        None,
    ),
    (utils.TANYA_ASK_REPLY_CLOSE_ANY, utils.DISPATCHER_HANGUP, None),
]


@pytest.mark.config(IVR_FRAMEWORK_FLOW_CONFIG=utils.IVR_FRAMEWORK_FLOW_CONFIG)
@pytest.mark.parametrize(
    'scenario',
    [
        OUTGOING_GOOD_CALL,
        OUTGOING_NO_ANSWER,
        OUTGOING_RETRY_ACTION_RESULT,
        OUTGOING_ASK_USER_HANGUP,
        OUTGOING_ASK_SK_ERROR,
        OUTGOING_ASK_RETRY_ON_002,
        OUTGOING_ASK_RETRY_ON_DTMF,
        OUTGOING_OLD_STYLE_GOOD_FORWARD,
        OUTGOING_GOOD_FORWARD,
        OUTGOING_ERROR_FORWARD_ABONENT_HANGUP,
        OUTGOING_ERROR_FORWARD_TRANSFEREE_NO_ANSWER,
        OUTGOING_UID_FORWARD,
        OUTGOING_FORWARD_INITIATOR_HUP,
        OUTGOING_FORWARD_TRANSFEREE_HUP,
        OUTGOING_FALLBACK,
        OUTGOING_HOLD,
        OUTGOING_SKIP_HOLDS,
    ],
    ids=(
        'good_call',
        'done_on_no_answer',
        'retry_action_result',
        'hangup_on_hangup_on_ask',
        'hangup_on_error_on_ask',
        'retry_on_002',
        'retry_on_no_dtmf',
        'old_style_good_forward',
        'good_forward',
        'error_forward_abonent_hangup',
        'error_forward_transferee_no_answer',
        'uid_forward',
        'initiator_hup_forward',
        'transferee_hup_forward',
        'fallback_from_script',
        'hold',
        'skip_holds',
    ),
)
async def test_flow_worker_outgoing(
        taxi_ivr_dispatcher,
        mongodb,
        scenario,
        testpoint,
        dial_client,
        mock_user_api,
        mock_int_authproxy,
        mock_personal_phones,
):
    @testpoint('set-dial-parameters-leg-id')
    def set_dial_parameters_leg_id(data):
        return {'leg_id': utils.LEG_ID}

    mongodb.ivr_disp_sessions.insert_one(utils.NEW_CONTEXT)
    for action_request, dispatcher_reply, check in scenario:
        response = await taxi_ivr_dispatcher.post(
            '/external/v1/action', json=action_request,
        )
        assert response.status == 200, response.text
        assert response.json() == dispatcher_reply
        if check:
            check(mongodb)


@pytest.mark.config(
    IVR_FRAMEWORK_FLOW_CONFIG=utils.IVR_FRAMEWORK_FLOW_CONFIG_X_ROUTE,
)
async def test_x_route(
        taxi_ivr_dispatcher,
        mongodb,
        testpoint,
        dial_client,
        mock_user_api,
        mock_int_authproxy,
        mock_personal_phones,
):
    @testpoint('set-dial-parameters-leg-id')
    def set_dial_parameters_leg_id(data):
        return {'leg_id': utils.LEG_ID}

    mongodb.ivr_disp_sessions.insert_one(utils.NEW_CONTEXT)

    for (action_request, dispatcher_reply, _) in OUTGOING_UID_FORWARD_X_ROUTE:
        response = await taxi_ivr_dispatcher.post(
            '/external/v1/action', json=action_request,
        )
        assert response.status == 200, response.text
        assert response.json() == dispatcher_reply


# Test incoming scenarios
INCOMING_GOOD_CALL = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (
        utils.INCOMING_TANYA_ANSWER_OK,
        utils.DISPATCHER_ASK_PLAY_INTRO,
        check_answered_in_db,
    ),
    (utils.TANYA_ASK_REPLY_RABBIT, utils.DISPATCHER_ASK_PLAY_RABBIT, None),
    (utils.TANYA_ASK_REPLY_ANY, utils.DISPATCHER_ASK_SPEAK_SAID_ANY, None),
    (utils.TANYA_ASK_REPLY_CLOSE_ANY, utils.DISPATCHER_HANGUP, None),
]
INCOMING_NO_ANSWER = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (
        utils.INCOMING_TANYA_ANSWER_ERROR,
        utils.DISPATCHER_FINISHED_HANGUP,
        check_hangup_in_db,
    ),
]
INCOMING_RETRY_ACTION_RESULT = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (
        utils.INCOMING_TANYA_ANSWER_OK,
        utils.DISPATCHER_ASK_PLAY_INTRO,
        check_answered_in_db,
    ),
    (
        utils.TANYA_ASK_REPLY_RABBIT_RETRY,
        utils.DISPATCHER_PLAY_RABBIT_PROMPT,
        None,
    ),
    (
        utils.TANYA_PLAY_RABBIT_OK_RESULT,
        utils.DISPATCHER_ASK_PLAY_RABBIT,
        None,
    ),
    (
        utils.TANYA_PLAY_RABBIT_OK_RESULT,
        utils.DISPATCHER_ASK_PLAY_RABBIT,
        None,
    ),
    (utils.TANYA_ASK_REPLY_ANY, utils.DISPATCHER_ASK_SPEAK_SAID_ANY, None),
    (utils.TANYA_ASK_REPLY_CLOSE_ANY, utils.DISPATCHER_HANGUP, None),
]
INCOMING_ASK_USER_HANGUP = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (
        utils.INCOMING_TANYA_ANSWER_OK,
        utils.DISPATCHER_ASK_PLAY_INTRO,
        check_answered_in_db,
    ),
    (utils.TANYA_ASK_USER_HANGUP, utils.DISPATCHER_FINISHED_HANGUP, None),
]
INCOMING_ASK_SK_ERROR = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (utils.TANYA_ASK_ERROR_RESULT, utils.DISPATCHER_PLAY_ERROR_PROMPT, None),
    (utils.TANYA_PLAY_ERROR_OK_RESULT, utils.DISPATCHER_HANGUP, None),
]
INCOMING_ASK_RETRY_ON_002 = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_INTRO_RESULT_NO_INPUT,
        utils.DISPATCHER_ASK_PLAY_INTRO,
        None,
    ),
]
INCOMING_ASK_RETRY_ON_DTMF = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (utils.TANYA_ASK_REPLY_DTMF, utils.DISPATCHER_ASK_SPEAK_SAID_DTMF, None),
    (
        utils.TANYA_ASK_DTMF_RESULT_NO_INPUT,
        utils.DISPATCHER_ASK_PLAY_INTRO,
        None,
    ),
]
INCOMING_OLD_STYLE_GOOD_FORWARD = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_FORWARD_INTRO,
        utils.DISPATCHER_INCOMING_FORWARD_REPLY,
        None,
    ),
    (utils.TANYA_BRIDGE_EVENT, utils.DISPATCHER_EMPTY_REPLY, None),
    (
        utils.TANYA_OLD_STYLE_FORWARDING_RESULT_OK,
        utils.DISPATCHER_PLAY_RABBIT_PROMPT,
        None,
    ),
    (utils.TANYA_PLAY_RABBIT_OK_RESULT, utils.DISPATCHER_HANGUP, None),
]
INCOMING_GOOD_FORWARD = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_FORWARD_INTRO,
        utils.DISPATCHER_INCOMING_FORWARD_REPLY,
        None,
    ),
    (utils.TANYA_BRIDGE_EVENT, utils.DISPATCHER_EMPTY_REPLY, None),
    (
        utils.TANYA_FORWARDING_RESULT_TRANSFEREE_HUP,
        utils.DISPATCHER_PLAY_RABBIT_PROMPT,
        None,
    ),
    (utils.TANYA_PLAY_RABBIT_OK_RESULT, utils.DISPATCHER_HANGUP, None),
]
INCOMING_FORWARD_INITIATOR_HUP = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_FORWARD_INTRO,
        utils.DISPATCHER_INCOMING_FORWARD_REPLY,
        None,
    ),
    (utils.TANYA_BRIDGE_EVENT, utils.DISPATCHER_EMPTY_REPLY, None),
    (
        utils.TANYA_FORWARDING_RESULT_INITIATOR_HUP,
        utils.DISPATCHER_FINISHED_HANGUP,
        None,
    ),
]
INCOMING_FORWARD_TRANSFEREE_HUP = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_FORWARD_INTRO,
        utils.DISPATCHER_INCOMING_FORWARD_REPLY,
        None,
    ),
    (utils.TANYA_BRIDGE_EVENT, utils.DISPATCHER_EMPTY_REPLY, None),
    (
        utils.TANYA_FORWARDING_RESULT_TRANSFEREE_HUP,
        utils.DISPATCHER_PLAY_RABBIT_PROMPT,
        None,
    ),
    (utils.TANYA_PLAY_RABBIT_OK_RESULT, utils.DISPATCHER_HANGUP, None),
]
INCOMING_ERROR_FORWARD_ABONENT_HANGUP = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_FORWARD_INTRO,
        utils.DISPATCHER_INCOMING_FORWARD_REPLY,
        None,
    ),
    (
        utils.TANYA_FORWARDING_RESULT_ERROR_ABONENT_HANGUP,
        utils.DISPATCHER_FINISHED_HANGUP,
        None,
    ),
]
INCOMING_ERROR_FORWARD_TRANSFEREE_NO_ANSWER = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_FORWARD_INTRO,
        utils.DISPATCHER_INCOMING_FORWARD_REPLY,
        None,
    ),
    (
        utils.TANYA_FORWARDING_RESULT_ERROR_TRANSFEREE_NO_ANSWER,
        utils.DISPATCHER_INCOMING_FORWARD_BACKUP_REPLY,
        None,
    ),
    (utils.TANYA_BRIDGE_EVENT_BACKUP, utils.DISPATCHER_EMPTY_REPLY, None),
]
INCOMING_UID_FORWARD = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_FORWARD_UID,
        utils.DISPATCHER_INCOMING_FORWARD_UID_REPLY,
        None,
    ),
    (
        utils.TANYA_FORWARDING_RESULT_TRANSFEREE_HUP,
        utils.DISPATCHER_PLAY_RABBIT_PROMPT,
        None,
    ),
    (utils.TANYA_PLAY_RABBIT_OK_RESULT, utils.DISPATCHER_HANGUP, None),
]
INCOMING_FALLBACK = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_FALLBACK,
        utils.DISPATCHER_PLAY_FALLBACK_PROMPT,
        None,
    ),
    (
        utils.TANYA_PLAY_FALLBACK_OK_RESULT,
        utils.DISPATCHER_FALLBACK_HANGUP,
        None,
    ),
]
INCOMING_HOLD = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_HOLD,
        utils.DISPATCHER_HOLD,
        check_wait_event_in_db,
    ),
]
INCOMING_SKIP_HOLDS = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_SKIP_HOLDS,
        utils.DISPATCHER_PLAY_RABBIT_PROMPT,
        None,
    ),
    (
        utils.TANYA_PLAY_RABBIT_OK_RESULT,
        utils.DISPATCHER_ASK_SPEAK_SAID_ANY,
        None,
    ),
    (
        utils.TANYA_PLAY_RABBIT_OK_RESULT,
        utils.DISPATCHER_ASK_SPEAK_SAID_ANY,
        None,
    ),
    (utils.TANYA_ASK_REPLY_CLOSE_ANY, utils.DISPATCHER_HANGUP, None),
]
INCOMING_DEFLECT = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_DEFLECT_INTRO,
        utils.DISPATCHER_DEFLECT_REPLY,
        None,
    ),
    (utils.TANYA_FORWARDING_RESULT_DEFLECT, utils.DISPATCHER_HANGUP, None),
]
INCOMING_ASK_MULTIPLE_DTMF = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER, None),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_ASK_PLAY_INTRO, None),
    (
        utils.TANYA_ASK_REPLY_MULTI_DTMF,
        utils.DISPATCHER_ASK_SPEAK_SAID_MULTI_DTMF,
        None,
    ),
    (utils.TANYA_ASK_DTMF_RESULT_1234, utils.DISPATCHER_HOLD, None),
]


@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP=utils.WORKER_MAP_CONFIG,
    IVR_FRAMEWORK_FLOW_CONFIG=utils.IVR_FRAMEWORK_FLOW_CONFIG,
)
@pytest.mark.parametrize(
    'scenario',
    [
        INCOMING_GOOD_CALL,
        INCOMING_NO_ANSWER,
        INCOMING_RETRY_ACTION_RESULT,
        INCOMING_ASK_USER_HANGUP,
        INCOMING_ASK_SK_ERROR,
        INCOMING_ASK_RETRY_ON_002,
        INCOMING_ASK_RETRY_ON_DTMF,
        INCOMING_OLD_STYLE_GOOD_FORWARD,
        INCOMING_GOOD_FORWARD,
        INCOMING_ERROR_FORWARD_ABONENT_HANGUP,
        INCOMING_ERROR_FORWARD_TRANSFEREE_NO_ANSWER,
        INCOMING_UID_FORWARD,
        INCOMING_FORWARD_INITIATOR_HUP,
        INCOMING_FORWARD_TRANSFEREE_HUP,
        INCOMING_FALLBACK,
        INCOMING_HOLD,
        INCOMING_SKIP_HOLDS,
        INCOMING_DEFLECT,
        INCOMING_ASK_MULTIPLE_DTMF,
    ],
    ids=(
        'good_call',
        'done_on_no_answer',
        'retry_action_result',
        'hangup_on_hangup_on_ask',
        'hangup_on_error_on_ask',
        'retry_on_002',
        'retry_on_no_dtmf',
        'old_style_good_forward',
        'good_forward',
        'error_forward_abonent_hangup',
        'error_forward_transferee_no_answer',
        'uid_forward',
        'initiator_hup_forward',
        'transferee_hup_forward',
        'fallback_from_config',
        'hold',
        'skip_holds',
        'deflect',
        'multiple_dtmf',
    ),
)
async def test_flow_worker_incoming(
        taxi_ivr_dispatcher,
        mongodb,
        scenario,
        testpoint,
        dial_client,
        mock_user_api,
        mock_int_authproxy,
        mock_personal_phones,
):
    @testpoint('set-dial-parameters-leg-id')
    def set_dial_parameters_leg_id(data):
        return {'leg_id': utils.LEG_ID}

    for action_request, dispatcher_reply, check in scenario:
        response = await taxi_ivr_dispatcher.post(
            '/external/v1/action', json=action_request,
        )
        assert response.status == 200, response.text
        assert response.json() == dispatcher_reply
        if check:
            check(mongodb)


OUTGOING_METRICS = [
    (utils.OUTGOING_TANYA_INITIAL, utils.OUTGOING_DISPATCHER_DIAL),
    (utils.OUTGOING_TANYA_DIAL_OK, utils.DISPATCHER_ASK_PLAY_INTRO),
    (utils.TANYA_ASK_REPLY_RABBIT, utils.DISPATCHER_ASK_PLAY_RABBIT),
    (utils.TANYA_ASK_REPLY_ANY, utils.DISPATCHER_ASK_SPEAK_SAID_ANY),
    (utils.TANYA_ASK_REPLY_FORWARD_ANY, utils.DISPATCHER_FORWARD_REPLY),
    (utils.TANYA_BRIDGE_EVENT, utils.DISPATCHER_EMPTY_REPLY),
    (
        utils.TANYA_FORWARDING_RESULT_TRANSFEREE_HUP,
        utils.DISPATCHER_PLAY_RABBIT_PROMPT,
    ),
    (utils.TANYA_PLAY_RABBIT_OK_RESULT, utils.DISPATCHER_HANGUP),
]
INCOMING_METRICS = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_ASK_PLAY_INTRO),
    (utils.TANYA_ASK_REPLY_RABBIT, utils.DISPATCHER_ASK_PLAY_RABBIT),
    (utils.TANYA_ASK_REPLY_ANY, utils.DISPATCHER_ASK_SPEAK_SAID_ANY),
    (
        utils.TANYA_ASK_REPLY_FORWARD_ANY,
        utils.DISPATCHER_INCOMING_FORWARD_REPLY,
    ),
    (utils.TANYA_BRIDGE_EVENT, utils.DISPATCHER_EMPTY_REPLY),
    (
        utils.TANYA_FORWARDING_RESULT_TRANSFEREE_HUP,
        utils.DISPATCHER_PLAY_RABBIT_PROMPT,
    ),
    (utils.TANYA_PLAY_RABBIT_OK_RESULT, utils.DISPATCHER_HANGUP),
]


def sub_metrics(reduced_metrics, deducted_metrics):
    for key, deducted in deducted_metrics.items():
        if key in {'$meta', '$version'}:
            continue
        reduced = reduced_metrics.get(key)
        if reduced:
            if type(reduced) is type(deducted):
                if isinstance(reduced, dict):
                    sub_metrics(reduced, deducted)
                else:
                    reduced -= deducted
            if not reduced:
                del reduced_metrics[key]
            else:
                reduced_metrics[key] = reduced


def extract_flow_metrics(metrics, flow_id):
    return {
        key: value
        for key, value in metrics.items()
        if key in {'$meta', '$version', flow_id}
    }


@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP=utils.WORKER_MAP_CONFIG,
    IVR_FRAMEWORK_FLOW_CONFIG=utils.IVR_FRAMEWORK_FLOW_CONFIG,
)
@pytest.mark.parametrize(
    ['scenario', 'expected_metrics', 'is_outgoing'],
    [
        (OUTGOING_METRICS, 'outgoing_metrics.json', True),
        (INCOMING_METRICS, 'incoming_metrics.json', False),
    ],
    ids=('outgoing_metrics', 'incoming_metrics'),
)
async def test_metrics(
        taxi_ivr_dispatcher,
        taxi_ivr_dispatcher_monitor,
        mongodb,
        scenario,
        expected_metrics,
        is_outgoing,
        load_json,
        testpoint,
        dial_client,
        mock_user_api,
        mock_int_authproxy,
        mock_personal_phones,
):
    @testpoint('set-dial-parameters-leg-id')
    def set_dial_parameters_leg_id(data):
        return {'leg_id': utils.LEG_ID}

    prior_metrics = await taxi_ivr_dispatcher_monitor.get_metrics(
        f'{utils.WORKER_ID}.{utils.FLOW_ID}',
    )

    if is_outgoing:
        mongodb.ivr_disp_sessions.insert_one(utils.NEW_CONTEXT)

    for action_request, dispatcher_reply in scenario:
        response = await taxi_ivr_dispatcher.post(
            '/external/v1/action', json=action_request,
        )
        assert response.status == 200, response.text
        assert response.json() == dispatcher_reply

    metrics = await taxi_ivr_dispatcher_monitor.get_metrics(
        f'{utils.WORKER_ID}.{utils.FLOW_ID}',
    )
    sub_metrics(metrics, prior_metrics)
    metrics = extract_flow_metrics(metrics[utils.WORKER_ID], utils.FLOW_ID)
    assert metrics == load_json(expected_metrics)


CUSTOM_ASK_PARAMS = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_ASK_PLAY_INTRO),
    (utils.TANYA_ASK_REPLY_CUSTOM, utils.DISPATCHER_ASK_PLAY_CUSTOM),
    (utils.TANYA_ASK_REPLY_CUSTOM_LVC, utils.DISPATCHER_ASK_PLAY_CUSTOM_LVC),
]


@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP=utils.WORKER_MAP_CONFIG,
    IVR_FRAMEWORK_FLOW_CONFIG=utils.IVR_FRAMEWORK_FLOW_CONFIG,
)
async def test_ask_parameters(
        taxi_ivr_dispatcher,
        taxi_ivr_dispatcher_monitor,
        mongodb,
        testpoint,
        dial_client,
        mock_user_api,
        mock_int_authproxy,
        mock_personal_phones,
):
    for action_request, dispatcher_reply in CUSTOM_ASK_PARAMS:
        response = await taxi_ivr_dispatcher.post(
            '/external/v1/action', json=action_request,
        )
        assert response.status == 200, response.text
        assert response.json() == dispatcher_reply


@pytest.fixture(name='init_incoming_fallback_client')
def mock_incoming_fallback_client(mockserver):
    class DialClient:
        @staticmethod
        @mockserver.json_handler('/v1/ivr-framework/call-notify')
        async def notify_handler(request):
            if request.json['last_action'] == -1:
                raise mockserver.TimeoutError()
            return utils.RESPONSE_EMPTY

    return DialClient()


INIT_INCOMING_FALLBACK = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_PLAY_FALLBACK_PROMPT),
    (utils.TANYA_PLAY_FALLBACK_OK_RESULT, utils.DISPATCHER_FALLBACK_HANGUP),
]


@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP=utils.WORKER_MAP_CONFIG,
    IVR_FRAMEWORK_FLOW_CONFIG=utils.IVR_FRAMEWORK_FLOW_CONFIG,
)
async def test_init_incoming_fallback(
        taxi_ivr_dispatcher,
        mongodb,
        init_incoming_fallback_client,
        mock_user_api,
        mock_int_authproxy,
        mock_personal_phones,
):
    for action_request, dispatcher_reply in INIT_INCOMING_FALLBACK:
        response = await taxi_ivr_dispatcher.post(
            '/external/v1/action', json=action_request,
        )
        assert response.status == 200, response.text
        assert response.json() == dispatcher_reply


TANYA_PLAY_PLAYBACK_OK_RESULT = {
    'session_id': utils.SESSION_ID,
    'action_result': utils.TANYA_PLAY_OK_RESULT,
    'action_id': utils.PLAYBACK_ID,
}
TANYA_ASK_RATING_RESULT = {
    'session_id': utils.SESSION_ID,
    'action_result': utils.CSAT_FLOW_TANYA_ASK_RATING_RESULT,
    'action_id': utils.HELLO_REPLY_ID,
}
TANYA_BYE_PLAYBACK_OK_RESULT = {
    'session_id': utils.SESSION_ID,
    'action_result': utils.TANYA_PLAY_OK_RESULT,
    'action_id': utils.BYE_REPLY_ID,
}
INCOMING_SWITCH = [
    (utils.INCOMING_TANYA_INITIAL, utils.INCOMING_DISPATCHER_ANSWER),
    (utils.INCOMING_TANYA_ANSWER_OK, utils.DISPATCHER_ASK_PLAY_INTRO),
    (utils.TANYA_ASK_REPLY_SWITCH_INTRO, utils.PLAYBACK_FLOW_PLAY_REPLY),
    (utils.TANYA_ASK_REPLY_SWITCH_INTRO, utils.PLAYBACK_FLOW_PLAY_REPLY),
    (TANYA_PLAY_PLAYBACK_OK_RESULT, utils.DISPATCHER_ASK_HELLO_REPLY),
    (TANYA_PLAY_PLAYBACK_OK_RESULT, utils.DISPATCHER_ASK_HELLO_REPLY),
    (TANYA_ASK_RATING_RESULT, utils.DISPATCHER_PLAY_BYE_REPLY),
    (TANYA_BYE_PLAYBACK_OK_RESULT, utils.DISPATCHER_HANGUP),
]


@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP=utils.WORKER_MAP_CONFIG,
    IVR_DISPATCHER_PLAY_FLOW={'prompt_url': utils.PROMPT_ID},
    IVR_FRAMEWORK_FLOW_CONFIG={
        utils.CSAT_FLOW_ID: utils.FLOW_CONFIG,
        utils.PLAYBACK_FLOW_ID: utils.FLOW_CONFIG,
        utils.FLOW_ID: utils.FLOW_CONFIG,
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
async def test_incoming_switch(
        taxi_ivr_dispatcher,
        mongodb,
        dial_client,
        mock_user_api,
        mock_int_authproxy,
        mock_personal_phones,
        mock_callcenter_qa,
):
    for action_request, dispatcher_reply in INCOMING_SWITCH:
        response = await taxi_ivr_dispatcher.post(
            '/external/v1/action', json=action_request,
        )
        assert response.status == 200, response.text
        assert response.json() == dispatcher_reply


@pytest.fixture(name='call_notify_by_flow_id_client')
def mock_notify_by_flow_id_client(mockserver):
    class DialClient:
        @staticmethod
        @mockserver.json_handler(
            f'/v1/ivr-framework/call-notify/{utils.FLOW_ID}',
        )
        async def notify_handler(request):
            msg = utils.Message(request.json)
            response = msg.response()
            if response:
                return response
            raise mockserver.TimeoutError()

    return DialClient()


FLOW_CONFIG_NOTIFY_BY_FLOW_ID = utils.FLOW_CONFIG.copy()
FLOW_CONFIG_NOTIFY_BY_FLOW_ID['call_notify_by_flow_id'] = True


@pytest.mark.config(
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP=utils.WORKER_MAP_CONFIG,
    IVR_FRAMEWORK_FLOW_CONFIG={utils.FLOW_ID: FLOW_CONFIG_NOTIFY_BY_FLOW_ID},
)
async def test_call_notify_by_flow_id(
        taxi_ivr_dispatcher,
        mongodb,
        call_notify_by_flow_id_client,
        mock_user_api,
        mock_int_authproxy,
        mock_personal_phones,
):
    for action_request, dispatcher_reply, check in INCOMING_GOOD_CALL:
        response = await taxi_ivr_dispatcher.post(
            '/external/v1/action', json=action_request,
        )
        assert response.status == 200, response.text
        assert response.json() == dispatcher_reply
        if check:
            check(mongodb)
