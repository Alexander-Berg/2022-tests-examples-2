import jwt
import pytest

from testsuite.utils import matching


def test_admin_state_example(load_json, admin_state_returning):
    assert admin_state_returning == load_json('admin_state_example.json')


async def test_state_with_invalid_flow(request_admin_state):
    response = await request_admin_state(flow='broken_flow')
    assert response.status_code == 400
    assert response.json()['code'] == 'unknown_flow'


def test_can_always_change_sum(admin_state_returning):
    assert 'token' in admin_state_returning['actions']['change_order_sum']


async def test_change_order_sum_event(
        admin_state_returning,
        load_json,
        mock_procaas_create,
        procaas_extract_token,
        claim_id,
        request_admin_change_order_sum,
):
    token = admin_state_returning['actions']['change_order_sum']['token']
    response = await request_admin_change_order_sum(token, '10.1000')
    assert response.status_code == 200

    token_payload = jwt.decode(token, options={'verify_signature': False})

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_pay_order/')
    assert request.query == {'item_id': 'claims/{}'.format(claim_id)}
    assert procaas_extract_token(request) == token_payload['operation_id']
    assert request.json == load_json('change_order_sum_payload.json')


async def test_change_billing_functions_sum_event(
        admin_state_returning,
        mock_procaas_create,
        procaas_extract_token,
        claim_id,
        request_admin_change_billing_functions_sum,
):
    token = admin_state_returning['actions']['change_billing_functions_sum'][
        'token'
    ]
    response = await request_admin_change_billing_functions_sum(
        token, '12.1000',
    )
    assert response.status_code == 200

    token_payload = jwt.decode(token, options={'verify_signature': False})

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_pay_order/')
    assert request.query == {'item_id': 'claims/{}'.format(claim_id)}
    assert procaas_extract_token(request) == token_payload['operation_id']
    assert (
        request.json['kind'] == 'manual_change_billing_functions_sum_request'
    )


async def test_change_sum_events_queue(
        admin_state_returning,
        mock_procaas_events,
        request_admin_change_order_sum,
        flush_all,
):
    flush_all()
    token = admin_state_returning['actions']['change_order_sum']['token']
    response = await request_admin_change_order_sum(token, '10.1000')
    assert response.status_code == 200

    assert mock_procaas_events.times_called == 1
    request = mock_procaas_events.next_call()['request']
    assert request.path.count('/cargo/finance_pay_order/')


async def test_change_sum_detect_races(
        admin_state_returning, request_admin_change_order_sum, append_event,
):
    token = admin_state_returning['actions']['change_order_sum']['token']
    append_event(token, known_state_revision=1)
    response = await request_admin_change_order_sum(token, '100.00')
    assert response.status_code == 409
    assert response.json()['code'] == 'race_condition'


async def test_change_sum_with_invalid_flow(request_admin_change_order_sum):
    response = await request_admin_change_order_sum(
        'token', '0.0', flow='broken_flow',
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'unknown_flow'


async def test_change_sum_to_invalid_value(request_admin_change_order_sum):
    response = await request_admin_change_order_sum('token', '-10.0')
    assert response.status_code == 400
    assert response.json()['code'] == 'invalid_sum'


async def test_change_sum_with_wrong_token(
        admin_state_unpaid, request_admin_change_order_sum,
):
    token = admin_state_unpaid['actions']['retry_hold']['token']
    response = await request_admin_change_order_sum(token, '0.0')
    assert response.status_code == 409
    assert response.json()['code'] == 'invalid_token'


def test_admin_state_with_compensation(admin_state_cleared):
    assert admin_state_cleared['actions']['change_compensation'] == {
        'token': matching.any_string,
    }


def test_compensation_is_hidden(load_json, admin_state_returning):
    assert 'change_compensation' not in admin_state_returning['actions']


@pytest.mark.parametrize('need_compensation', [True, False])
async def test_change_compensation_event(
        admin_state_cleared,
        request_admin_change_compensation,
        load_json,
        mock_procaas_create,
        need_compensation,
):
    token = admin_state_cleared['actions']['change_compensation']['token']
    response = await request_admin_change_compensation(
        token, need_compensation=need_compensation,
    )
    assert response.status_code == 200

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_pay_order/')
    compensation_request = load_json('change_compensation_payload.json')
    compensation_request['data']['new_value'][
        'need_compensation'
    ] = need_compensation
    assert request.json == compensation_request


async def test_compensation_with_invalid_extra_sum(
        request_admin_change_compensation,
):
    response = await request_admin_change_compensation(
        'token', need_compensation=True, extra_sum='-10.0',
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'invalid_sum'


async def test_compensation_detect_races(
        admin_state_cleared, request_admin_change_compensation, append_event,
):
    token = admin_state_cleared['actions']['change_compensation']['token']
    append_event(token, known_state_revision=1)
    response = await request_admin_change_compensation(
        token, need_compensation=True,
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'race_condition'


async def test_compensation_with_invalid_flow(
        request_admin_change_compensation,
):
    response = await request_admin_change_compensation(
        'token', need_compensation=True, flow='broken_flow',
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'unknown_flow'


async def test_compensation_with_wrong_token(
        admin_state_cleared, request_admin_change_compensation,
):
    token = admin_state_cleared['actions']['change_order_sum']['token']
    response = await request_admin_change_compensation(token, True)
    assert response.status_code == 409
    assert response.json()['code'] == 'invalid_token'


def test_can_retry_hold_if_unpaid(admin_state_unpaid):
    assert 'token' in admin_state_unpaid['actions']['retry_hold']


async def test_retry_hold_calls_stq(
        admin_state_unpaid, request_admin_retry_hold, flush_all, stq,
):
    flush_all()
    token = admin_state_unpaid['actions']['retry_hold']['token']
    response = await request_admin_retry_hold(token)
    assert response.status_code == 200
    assert stq.cargo_finance_pay_applying.times_called == 1


def test_retry_hold_is_hidden_otherwise(admin_state_returning):
    assert 'retry_hold' not in admin_state_returning['actions']


async def test_retry_hold_with_invalid_flow(request_admin_retry_hold):
    response = await request_admin_retry_hold('token', flow='broken_flow')
    assert response.status_code == 400
    assert response.json()['code'] == 'unknown_flow'


async def test_retry_hold_with_wrong_token(
        admin_state_returning, request_admin_retry_hold,
):
    token = admin_state_returning['actions']['change_order_sum']['token']
    response = await request_admin_retry_hold(token)
    assert response.status_code == 409
    assert response.json()['code'] == 'invalid_token'


#  #############################
#  System states with injections


@pytest.fixture(name='admin_state_returning')
async def _admin_state_returning(
        applying_state_held,
        set_transactions_response,
        set_applying_sum2pay,
        run_applying_stq,
        inject_all_events,
        get_admin_state,
        flush_all,
        load_json,
):
    sum2pay = load_json('sum2pay_can_hold.json')
    sum2pay['client']['agent']['sum'] = '500'
    await set_applying_sum2pay(sum2pay)
    set_transactions_response(load_json('transactions_in_progress.json'))
    await run_applying_stq()

    flush_all()
    return await get_admin_state()


@pytest.fixture(name='admin_state_cleared')
async def _admin_state_cleared(
        applying_state_held,
        set_transactions_response,
        set_applying_sum2pay,
        run_applying_stq,
        inject_all_events,
        get_admin_state,
        flush_all,
        load_json,
):
    sum2pay = load_json('sum2pay_can_hold.json')
    sum2pay['revision'] += 1
    sum2pay['is_service_complete'] = True
    await set_applying_sum2pay(sum2pay)
    await run_applying_stq()

    flush_all()
    return await get_admin_state()


@pytest.fixture(name='admin_state_unpaid')
async def _admin_state_unpaid(
        applying_state_held,
        set_transactions_response,
        run_applying_stq,
        inject_all_events,
        get_admin_state,
        flush_all,
        load_json,
):
    set_transactions_response(load_json('transactions_paid_less.json'))
    await run_applying_stq()

    flush_all()
    return await get_admin_state()


@pytest.fixture(name='admin_state_example')
async def _admin_state_example(
        inject_all_events, applying_state_held, get_admin_state, flush_all,
):
    flush_all()
    return await get_admin_state()


@pytest.fixture(name='inject_all_events')
def _inject_all_events(load_json, procaas_events_response):
    procaas_events_response.events = load_json(
        'cargo_finance_pay_order_events.json',
    )


@pytest.fixture(name='append_event')
def _append_event(load_json, procaas_events_response):
    def wrapper(token, known_state_revision=None):
        token_payload = jwt.decode(token, options={'verify_signature': False})
        revision = token_payload['state_revision']
        if known_state_revision is not None:
            revision = known_state_revision
        operation_id = token_payload['operation_id']

        event = {
            'created': '2021-07-01T11:30:15+00:00',
            'event_id': 'event_123',
            'handled': False,
            'payload': load_json('change_order_sum_payload.json'),
        }
        event['payload']['data']['known_state_revision'] = revision
        event['payload']['data']['operation_id'] = operation_id

        procaas_events_response.events.append(event)

    return wrapper
