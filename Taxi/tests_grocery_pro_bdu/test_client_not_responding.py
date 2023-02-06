# pylint: disable=W0612
import datetime
import json

import pytest

PERFORMER_ID = 'dbid0_uuid0'
CALL_EXTERNAL_ID = 'call_id_0'
IVR_FLOW_ID = 'ivr_flow_0'
PERSONAL_PHONE_ID = 'personal_phone_id_0'
ORDER_ID = 'order_id_0'

NOW = datetime.datetime(2020, 9, 14, 14, 15, 16)

CONTEXT = {
    'performer_id': PERFORMER_ID,
    'order_id': ORDER_ID,
    'scenario_name': 'client_not_responding',
}


def build_originate_action(state):
    return {
        'external_id': CALL_EXTERNAL_ID,
        'originate': {
            'phone_number': '+79260711354',
            'timeout_sec': 15,
            'status': {'state': state},
        },
    }


def build_wait_action(state):
    return {
        'external_id': CALL_EXTERNAL_ID,
        'wait': {'timeout_sec': 15, 'status': {'state': state}},
    }


def build_ask_action(state, dtmf_answer=None):
    action = {
        'external_id': CALL_EXTERNAL_ID,
        'ask': {
            'allowed_dtmf': '123',
            'immediate_input': False,
            'input_mode': 'text',
            'no_input_timeout_ms': 15000,
            'playback': {'speak': {'text': 'some text'}},
            'status': {'state': state},
        },
    }
    if dtmf_answer is not None:
        action['ask']['status']['input_value'] = {'dtmf': dtmf_answer}
    return action


def build_hangup_action():
    return {
        'external_id': CALL_EXTERNAL_ID,
        'hangup': {'cause': 'normal-clearing'},
    }


def build_action(action_type: str, state: str, dtmf_answer=None):
    if action_type == 'originate':
        return build_originate_action(state)
    if action_type == 'wait':
        return build_wait_action(state)
    if action_type == 'ask':
        return build_ask_action(state, dtmf_answer)
    if action_type == 'hangup':
        return build_hangup_action()
    return None


def build_call_notify_request(actions: list, last_action: int):
    return {
        'call_external_id': CALL_EXTERNAL_ID,
        'ivr_flow_id': IVR_FLOW_ID,
        'call_guid': '',
        'service_number': '+74950328686',
        'abonent_number': '+79260711354',
        'direction': 'outgoing',
        'actions': actions,
        'last_action': last_action,
        'context': CONTEXT,
    }


def insert_call(pgsql, status, user_dtmf_answer=None, call_result=None):
    cursor = pgsql['grocery_pro_bdu'].cursor()
    sql = """
        INSERT INTO grocery_pro_bdu.client_call_states(
            performer_id, status, updated, call_external_id,
            ivr_flow_id, context, personal_phone_id, user_dtmf_answer,
            call_result, call_number
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
    """  # noqa: W291
    cursor.execute(
        sql,
        (
            PERFORMER_ID,
            status,
            NOW.isoformat(),
            CALL_EXTERNAL_ID,
            IVR_FLOW_ID,
            json.dumps(CONTEXT),
            PERSONAL_PHONE_ID,
            user_dtmf_answer,
            call_result,
            1,
        ),
    )


def update_call_result(pgsql, call_result: str):
    cursor = pgsql['grocery_pro_bdu'].cursor()
    sql = """
        UPDATE grocery_pro_bdu.client_call_states
        SET call_result = %s
    """
    cursor.execute(sql, (call_result,))


def get_call(pgsql, performer_id):
    cursor = pgsql['grocery_pro_bdu'].cursor()
    sql = """
        SELECT performer_id, status, call_external_id,
        ivr_flow_id, context, personal_phone_id, call_result,
        user_dtmf_answer
        FROM grocery_pro_bdu.client_call_states WHERE performer_id = %s
    """  # noqa: W291
    cursor.execute(sql, (PERFORMER_ID,))
    return cursor.fetchone()


def action_state_to_call_result(action_state: str, action_type: str):
    if action_state == 'failed' and action_type == 'originate':
        return 'user_not_responded'
    if action_state in ('failed', 'timeout'):
        return 'fail'
    if action_state == 'completed':
        return 'completed'
    if action_state == 'abonent-hangup':
        return 'user_hangup'
    return None


@pytest.mark.experiments3(
    name='grocery_pro_bdu_client_call_settings',
    consumers=['grocery-pro-bdu/call'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'allowed_dtmf': '12',
        'immediate_input': True,
        'no_input_timeout_ms': 2000,
        'playback': {'text': 'some text'},
        'wait_action_timeout_sec': 2,
        'dtmf_answers_mapping': {'1': 'deliver', '2': 'cancel'},
        'call_try_count': 1,
    },
    is_config=True,
)
@pytest.mark.parametrize(
    'ivr_response_code, call_status',
    [(200, 'calling'), (500, 'call_failure'), (404, 'call_failure')],
)
async def test_create_call_basic(
        taxi_grocery_pro_bdu,
        pgsql,
        stq,
        stq_runner,
        mockserver,
        ivr_response_code,
        call_status,
):
    @mockserver.json_handler('/ivr-dispatcher/v1/ivr-framework/create-call')
    def create_call_(request):
        return mockserver.make_response(status=ivr_response_code)

    insert_call(pgsql, 'idle')
    await stq_runner.grocery_pro_bdu_process_client_call.call(
        task_id=PERFORMER_ID, kwargs={'performer_id': PERFORMER_ID},
    )

    call = get_call(pgsql, PERFORMER_ID)

    assert call == (
        PERFORMER_ID,
        call_status,
        CALL_EXTERNAL_ID,
        IVR_FLOW_ID,
        CONTEXT,
        PERSONAL_PHONE_ID,
        None,
        None,
    )


@pytest.mark.parametrize(
    'action_type, action_state',
    [
        ('originate', 'completed'),
        ('wait', 'completed'),
        ('originate', 'failed'),
        ('wait', 'failed'),
        ('originate', 'abonent-hangup'),
        ('wait', 'abonent-hangup'),
        ('originate', 'timeout'),
        ('wait', 'timeout'),
        ('ask', 'completed'),
        ('ask', 'failed'),
        ('ask', 'abonent-hangup'),
        ('ask', 'timeout'),
    ],
)
async def test_call_notify_basic(
        taxi_grocery_pro_bdu, pgsql, mockserver, action_type, action_state,
):
    insert_call(pgsql, 'calling')

    dtmf_answer = (
        1 if action_state == 'completed' and action_type == 'ask' else None
    )

    actions = [build_action(action_type, action_state, dtmf_answer)]
    request_body = build_call_notify_request(actions, len(actions) - 1)

    response = await taxi_grocery_pro_bdu.post(
        '/v1/ivr-framework/call-notify',
        headers={'X-Idempotency-Token': 'Random-Idempotency-Key'},
        json=request_body,
    )

    call_result = action_state_to_call_result(action_state, action_type)

    expected_response = (
        {'actions': [build_hangup_action()]}
        if call_result == 'completed'
        else {}
    )

    assert response.json() == expected_response

    user_dtmf_answer = (
        1 if action_state == 'completed' and action_type == 'ask' else None
    )

    call = get_call(pgsql, PERFORMER_ID)
    assert call == (
        PERFORMER_ID,
        'calling',
        CALL_EXTERNAL_ID,
        IVR_FLOW_ID,
        CONTEXT,
        PERSONAL_PHONE_ID,
        call_result,
        user_dtmf_answer,
    )


@pytest.mark.experiments3(
    name='grocery_pro_bdu_client_call_settings',
    consumers=['grocery-pro-bdu/call'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'allowed_dtmf': '12',
        'immediate_input': True,
        'no_input_timeout_ms': 2000,
        'playback': {'text': 'some text'},
        'wait_action_timeout_sec': 2,
        'dtmf_answers_mapping': {'1': 'deliver', '2': 'cancel'},
        'call_try_count': 1,
    },
    is_config=True,
)
@pytest.mark.parametrize(
    'user_dtmf_answer, new_state',
    [(1, 'deliver'), (2, 'cancel'), (3, 'deliver')],
)
async def test_process_client_answer(
        taxi_grocery_pro_bdu,
        pgsql,
        stq,
        stq_runner,
        mockserver,
        user_dtmf_answer,
        new_state,
):
    insert_call(pgsql, 'calling', user_dtmf_answer)

    await stq_runner.grocery_pro_bdu_process_client_call.call(
        task_id=PERFORMER_ID, kwargs={'performer_id': PERFORMER_ID},
    )

    call = get_call(pgsql, PERFORMER_ID)

    assert call == (
        PERFORMER_ID,
        new_state,
        CALL_EXTERNAL_ID,
        IVR_FLOW_ID,
        CONTEXT,
        PERSONAL_PHONE_ID,
        None,
        user_dtmf_answer,
    )


@pytest.mark.experiments3(
    name='grocery_pro_bdu_client_call_settings',
    consumers=['grocery-pro-bdu/call'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'allowed_dtmf': '12',
        'immediate_input': True,
        'no_input_timeout_ms': 2000,
        'playback': {'text': 'some text'},
        'wait_action_timeout_sec': 2,
        'dtmf_answers_mapping': {'1': 'deliver', '2': 'cancel'},
        'call_try_count': 2,
    },
    is_config=True,
)
async def test_client_not_responded_retry(
        taxi_grocery_pro_bdu, pgsql, stq, stq_runner, mockserver,
):
    insert_call(pgsql, 'calling', None, 'user_not_responded')

    await stq_runner.grocery_pro_bdu_process_client_call.call(
        task_id=PERFORMER_ID, kwargs={'performer_id': PERFORMER_ID},
    )

    call = get_call(pgsql, PERFORMER_ID)

    assert call == (
        PERFORMER_ID,
        'idle',
        CALL_EXTERNAL_ID,
        IVR_FLOW_ID,
        CONTEXT,
        PERSONAL_PHONE_ID,
        None,
        None,
    )

    task = stq.grocery_pro_bdu_process_client_call.next_call()
    assert task['id'] == PERFORMER_ID
    assert task['kwargs']['performer_id'] == PERFORMER_ID

    @mockserver.json_handler('/ivr-dispatcher/v1/ivr-framework/create-call')
    def create_call_(request):
        return mockserver.make_response(status=200)

    await stq_runner.grocery_pro_bdu_process_client_call.call(
        task_id=PERFORMER_ID, kwargs={'performer_id': PERFORMER_ID},
    )

    call = get_call(pgsql, PERFORMER_ID)

    assert call == (
        PERFORMER_ID,
        'calling',
        CALL_EXTERNAL_ID,
        IVR_FLOW_ID,
        CONTEXT,
        PERSONAL_PHONE_ID,
        None,
        None,
    )

    update_call_result(pgsql, 'user_not_responded')

    task = stq.grocery_pro_bdu_process_client_call.next_call()
    assert task['id'] == PERFORMER_ID
    assert task['kwargs']['performer_id'] == PERFORMER_ID

    await stq_runner.grocery_pro_bdu_process_client_call.call(
        task_id=PERFORMER_ID, kwargs={'performer_id': PERFORMER_ID},
    )

    call = get_call(pgsql, PERFORMER_ID)

    assert call == (
        PERFORMER_ID,
        'cancel',
        CALL_EXTERNAL_ID,
        IVR_FLOW_ID,
        CONTEXT,
        PERSONAL_PHONE_ID,
        'user_not_responded',
        None,
    )


async def test_cancel_order_processing_notification(
        pgsql, processing, stq_runner,
):

    insert_call(pgsql, 'cancel')

    await stq_runner.grocery_pro_bdu_process_client_call.call(
        task_id=PERFORMER_ID, kwargs={'performer_id': PERFORMER_ID},
    )

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert len(events) == 1
    event = events[0]

    assert event.item_id == ORDER_ID
    assert event.idempotency_token == ORDER_ID + '_' + 'client_not_responded'
    assert event.payload == {
        'code': 'client_not_responded',
        'order_id': ORDER_ID,
        'reason': 'order_notification',
        'payload': {},
    }
