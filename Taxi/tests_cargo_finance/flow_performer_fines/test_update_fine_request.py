import pytest


UID = '1111'
LOGIN = 'ya1111'


async def test_update_idempotency(
        recently,
        get_admin_fines_state,
        inject_events,
        send_request_409_json,
        mock_procaas_create,
):
    inject_events()
    state = await get_admin_fines_state()
    decision = state['pending_decisions'][1]
    request_body = {
        'decision': decision['decision'],
        'reason': decision['reason'],
    }
    await send_request_409_json(request_body)

    assert not mock_procaas_create.has_calls


async def test_happy_path(
        recently,
        send_request,
        load_json,
        request_body_from_payload,
        mock_procaas_create,
        check_payload,
):
    events = load_json('processing_events.json')
    update_req_event = events[1]
    await send_request(request_body_from_payload(update_req_event['payload']))

    assert mock_procaas_create.times_called == 3

    request = mock_procaas_create.next_call()['request']
    assert request.query['item_id'] == 'alias_id_1'
    check_payload(request.json, events[0]['payload'])

    # skip sum2pay dummy-init
    request = mock_procaas_create.next_call()['request']

    request = mock_procaas_create.next_call()['request']
    assert request.query['item_id'] == 'alias_id_1'
    check_payload(request.json, events[1]['payload'])


@pytest.fixture(name='request_auto_fine')
def _request_auto_fine(taxi_cargo_finance):
    async def _wrapper(request_body, order_id, yandex_uid, yandex_login):
        params = {'taxi_order_id': order_id}
        headers = {
            'X-Yandex-Uid': str(yandex_uid),
            'X-Yandex-Login': yandex_login,
        }
        response = await taxi_cargo_finance.post(
            '/internal/cargo-finance/performer/fines/automated-fine',
            params=params,
            headers=headers,
            json=request_body,
        )
        return response

    return _wrapper


@pytest.fixture(name='send_request')
def _send_request(request_auto_fine, order_proc):
    async def _wrapper(request_body):
        response = await request_auto_fine(
            request_body, order_proc['_id'], UID, LOGIN,
        )
        assert response.status_code == 200
        return response.json()

    return _wrapper


@pytest.fixture(name='send_request_409_json')
def _send_request_409_json(request_auto_fine, order_proc):
    async def _wrapper(request_body, order_id=None):
        if order_id is None:
            order_id = order_proc['_id']
        response = await request_auto_fine(request_body, order_id, UID, LOGIN)
        assert response.status_code == 409
        return response.json()

    return _wrapper
