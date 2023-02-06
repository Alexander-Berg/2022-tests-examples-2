import datetime

import pytest

from tests_corp_billing import util

SUCCESS = 'SUCCESS'
TRAN_ID_TPL = 'tanker/order/%s/%s'


async def test_external_calls(
        mocks, _prepare, pay_order_tanker_request, _request_body, stq,
):
    response = await pay_order_tanker_request(_request_body)
    assert response.status_code == 200

    assert mocks.events_post.times_called == 1
    assert mocks.events_topics.times_called == 2

    assert stq.corp_sync_tanker_order.times_called == 1
    call = stq.corp_sync_tanker_order.next_call()
    assert call['kwargs']['order_id'] == '111111-222222'


async def test_idempotency(
        mocks, _prepare, pay_order_tanker_request, _request_body,
):
    for _i in range(2):
        response = await pay_order_tanker_request(_request_body)
        assert response.status_code == 200
        assert response.json()['status']['code'] == SUCCESS
        assert response.json()['transaction_id'] == TRAN_ID_TPL % (
            _request_body['order']['external_ref'],
            1,
        )

    topics = list(mocks.events_service.topics.values())
    assert len(topics) == 1
    assert len(topics[0]['events']) == 1


async def test_first_created_rest_change_price(
        mocks,
        _prepare,
        pay_order_tanker_request,
        _request_body,
        taxi_corp_billing,
        taxi_corp_billing_monitor,
):
    await taxi_corp_billing.tests_control(reset_metrics=True)

    for index in range(3):
        body = _request_body.copy()
        body['transaction_created_at'] = util.to_timestring(
            datetime.datetime.utcnow() + datetime.timedelta(seconds=index),
        )
        response = await pay_order_tanker_request(body)
        assert response.status_code == 200
        assert response.json()['status']['code'] == 'SUCCESS'
        assert response.json()['transaction_id'] == TRAN_ID_TPL % (
            _request_body['order']['external_ref'],
            index + 1,
        )

    topics = list(mocks.events_service.topics.values())
    assert len(topics) == 1
    assert len(topics[0]['events']) == 3
    assert (
        len(
            [
                ev
                for ev in topics[0]['events']
                if ev['type'] == 'order_created'
            ],
        )
        == 1
    )
    assert (
        len(
            [
                ev
                for ev in topics[0]['events']
                if ev['type'] == 'price_changed'
            ],
        )
        == 2
    )

    metrics = await taxi_corp_billing_monitor.get_metrics('payment_method')
    metrics['payment_method']['tanker'].pop('$meta')
    assert len(metrics['payment_method']['tanker']) == 1
    assert metrics['payment_method']['tanker']['corp'] == 1


async def test_order_created_meta(
        mocks, _prepare, pay_order_tanker_request, _request_body, load_json,
):
    response = await pay_order_tanker_request(_request_body)
    assert response.status_code == 200

    topics = list(mocks.events_service.topics.values())
    assert len(topics) == 1
    assert len(topics[0]['events']) == 1
    meta = topics[0]['events'][0]['meta']

    pm_response = load_json('pm_eats_response.json')
    method = pm_response['payment_methods'][1]

    assert meta['client_external_ref'] == method['client_id']
    assert meta['employee_external_ref'] == method['user_id']
    assert meta['currency'] == method['currency']

    assert meta['payment_method'] == _request_body['type']
    assert meta['passport_uid'] == _request_body['user_info']['uid']
    assert (
        meta['personal_phone_id']
        == _request_body['user_info']['personal_phone_id']
    )

    price = _request_body['order']['amount']
    assert meta['prices']['consumer_price'] == price
    assert meta['prices']['performer_price'] == price

    assert meta['service'] == 'tanker'


async def test_order_sum_influence(
        _failed_int_api_tanker_checks_mock,
        mocks,
        pay_order_tanker_request,
        _request_body,
):
    body = _request_body
    body['order']['amount'] = '12500'
    response = await pay_order_tanker_request(body)
    assert response.status_code == 200
    assert response.json() == {
        'status': {
            'code': 'FAIL',
            'message': 'недостаточно средств для оплаты заказа',
        },
    }


@pytest.mark.parametrize(
    ['payment_method', 'expected_code'],
    [
        pytest.param(
            {
                'type': 'card',
                'card_info': {
                    'card_id': 'card-123',
                    'account': '500000****1111',
                    'yandex_uid': '44348071',
                },
            },
            200,
            id='card_success',
        ),
        pytest.param({'type': 'corp'}, 409, id='pm_type_mismatch'),
        pytest.param(
            {
                'type': 'card',
                'card_info': {
                    'card_id': 'card-234',
                    'account': '500000****1111',
                    'yandex_uid': '44348071',
                },
            },
            409,
            id='card_info_mismatch',
        ),
    ],
)
async def test_payment_method_card(
        _int_api_tanker_card_checks_mock,
        mocks,
        pay_order_tanker_request,
        _request_body,
        payment_method,
        expected_code,
):
    body = {**_request_body, **payment_method}
    response = await pay_order_tanker_request(body)
    assert response.status_code == expected_code

    if expected_code == 200:
        assert response.json()['status']['code'] == 'SUCCESS'
        topics = list(mocks.events_service.topics.values())
        assert len(topics) == 1
        meta = topics[0]['events'][0]['meta']
        assert meta['payment_method'] == payment_method['type']
    elif expected_code == 409:
        assert response.json()['code'] == 'INVALID_PAYMENT_METHOD'


@pytest.fixture
async def _prepare(mocks, int_api_tanker_checks_mock, sync_with_corp_cabinet):
    await sync_with_corp_cabinet()


@pytest.fixture
def _request_body(load_json):
    body = load_json('order_request_tanker.json')
    return body


@pytest.fixture
def _failed_int_api_tanker_checks_mock(mockserver, billing_replication):
    @mockserver.json_handler(
        '/taxi-corp-integration/v1/payment-methods/tanker',
    )
    def handler(request):
        assert request.json == {
            'currency': 'RUB',
            'order_id': '111111-222222',
            'order_sum': '12500',
            'fuel_type': 'a95',
        }
        return {
            'payment_methods': [
                {
                    'id': 'corp:yastation_rus_rkarlash:tanker/RUB',
                    'user_id': 'yastation_rus_rkarlash',
                    'client_id': 'yastation_rus',
                    'billing_id': '2000101',
                    'name': 'Команда Яндекс.Станции',
                    'type': 'corp',
                    'currency': 'RUB',
                    'availability': {
                        'available': False,
                        'disabled_reason': (
                            'недостаточно средств для оплаты заказа'
                        ),
                    },
                    'description': 'Осталось 4000 из 4000 ₽',
                },
                {
                    'id': 'corp:yataxi_rus_rkarlash:tanker/RUB',
                    'user_id': 'yataxi_rus_rkarlash',
                    'client_id': 'yataxi_rus',
                    'billing_id': '2000102',
                    'name': 'Команда Яндекс.Такси',
                    'type': 'corp',
                    'currency': 'RUB',
                    'availability': {
                        'available': False,
                        'disabled_reason': (
                            'недостаточно средств для оплаты заказа'
                        ),
                    },
                    'description': 'Осталось 10000 из 10000 ₽',
                },
            ],
        }

    return handler


@pytest.fixture
def _int_api_tanker_card_checks_mock(mockserver, billing_replication):
    @mockserver.json_handler(
        '/taxi-corp-integration/v1/payment-methods/tanker',
    )
    def handler(request):
        return {
            'payment_methods': [
                {
                    'id': 'corp:yataxi_rus_rkarlash:tanker/RUB',
                    'user_id': 'yataxi_rus_rkarlash',
                    'client_id': 'yataxi_rus',
                    'billing_id': '2000102',
                    'name': 'Команда Яндекс.Такси',
                    'type': 'card',
                    'card_info': {
                        'card_id': 'card-123',
                        'account': '500000****1111',
                        'yandex_uid': '44348071',
                    },
                    'currency': 'RUB',
                    'availability': {'available': True, 'disabled_reason': ''},
                    'description': 'Осталось 10000 из 10000 ₽',
                },
            ],
        }

    return handler
