import pytest


async def test_external_calls(
        _prepare, mocks, stq, _create_order, _close_order,
):
    order_external_ref = await _create_order()
    status = await _close_order(order_external_ref)
    assert status == 200

    topic = list(mocks.events_service.topics.values())[0]
    events = list(topic['known_events'])
    assert [i for i, v in enumerate(events) if v[0] == 'order_closed']
    assert mocks.events_post.times_called == 2
    assert mocks.events_topics.times_called == 4

    assert stq.corp_sync_tanker_order.times_called == 2
    for _ in range(stq.corp_sync_tanker_order.times_called):
        call = stq.corp_sync_tanker_order.next_call()
        assert call['kwargs']['order_id'] == '111111-222222'


async def test_already_closed(_prepare, mocks, _create_order, _close_order):
    order_external_ref = await _create_order()
    status = await _close_order(order_external_ref)
    assert status == 200
    status = await _close_order(order_external_ref)
    topic = list(mocks.events_service.topics.values())[0]
    events = list(topic['known_events'])
    assert (
        len([i for i, v in enumerate(events) if v[0] == 'order_closed']) == 1
    )
    assert status == 200


async def test_unknown_topic(_prepare, mocks, _create_order, _close_order):
    status = await _close_order('unknown_topic')
    assert status == 404


@pytest.fixture
async def _close_order(_close_request):
    async def _wrapper(order_external_ref):
        body = {
            'order': {
                'external_ref': order_external_ref,
                'amount': '1400.0000',
                'currency': 'RUB',
                'fuel_type': 'a95',
            },
        }
        response = await _close_request(body)
        return response.status_code

    return _wrapper


@pytest.fixture
async def _prepare(mocks, int_api_tanker_checks_mock, sync_with_corp_cabinet):
    await sync_with_corp_cabinet()


@pytest.fixture
async def _close_request(taxi_corp_billing):
    async def _wrapper(order):
        url = '/v1/close-order/tanker'
        response = await taxi_corp_billing.post(url, json=order)
        return response

    return _wrapper


@pytest.fixture
async def _create_order(
        load_json, int_api_tanker_checks_mock, pay_order_tanker_request, mocks,
):
    async def _wrapper():
        order = load_json('order_request_tanker.json')
        response = await pay_order_tanker_request(order)
        assert response.status_code == 200
        return order['order']['external_ref']

    return _wrapper
