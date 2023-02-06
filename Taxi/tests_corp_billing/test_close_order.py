import pytest

CLOSE_TRANSACTION_TIME = '2019-09-30T11:00:00.232200+0300'


async def test_external_calls(_prepare, mocks, _create_order, _close_order):
    order_external_ref = await _create_order()
    status = await _close_order(order_external_ref)
    assert status == 200

    topic = list(mocks.events_service.topics.values())[0]
    events = list(topic['known_events'])
    assert [i for i, v in enumerate(events) if v[0] == 'order_closed']
    assert mocks.events_post.times_called == 2
    assert mocks.events_topics.times_called == 4


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
            'order_external_ref': order_external_ref,
            'transaction_created_at': CLOSE_TRANSACTION_TIME,
        }
        response = await _close_request(body)
        return response.status_code

    return _wrapper


@pytest.fixture
async def _prepare(mocks, success_int_api_checks_mock, sync_with_corp_cabinet):
    await sync_with_corp_cabinet()


@pytest.fixture
async def _close_request(taxi_corp_billing):
    async def _wrapper(order):
        url = '/v1/close-order/eats'
        response = await taxi_corp_billing.post(url, json=order)
        return response

    return _wrapper


@pytest.fixture
async def _create_order(load_json, pay_order_request, mocks):
    async def _wrapper():
        order = load_json('order_request.json')
        response = await pay_order_request(order)
        assert response.status_code == 200
        return order['order']['external_ref']

    return _wrapper
