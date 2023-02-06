import datetime

import pytest

from tests_corp_billing import util

SUCCESS = 'SUCCESS'
TRAN_ID_TPL = 'eats/order/%s/%s'


async def test_external_calls(
        success_int_api_checks_mock, mocks, pay_order_request, _request_body,
):
    response = await pay_order_request(_request_body)
    assert response.status_code == 200

    assert mocks.events_post.times_called == 1
    assert mocks.events_topics.times_called == 2


async def test_idempotency(
        success_int_api_checks_mock, mocks, pay_order_request, _request_body,
):
    for _i in range(2):
        response = await pay_order_request(_request_body)
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
        success_int_api_checks_mock, mocks, pay_order_request, _request_body,
):
    for index in range(3):
        body = _request_body.copy()
        body['transaction_created_at'] = util.to_timestring(
            datetime.datetime.utcnow() + datetime.timedelta(seconds=index),
        )
        response = await pay_order_request(body)
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


async def test_order_created_meta(
        success_int_api_checks_mock,
        mocks,
        pay_order_request,
        _request_body,
        load_json,
):
    response = await pay_order_request(_request_body)
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

    assert meta['passport_uid'] == _request_body['user_info']['uid']
    assert (
        meta['personal_phone_id']
        == _request_body['user_info']['personal_phone_id']
    )

    price = sum(float(p['amount']) for p in _request_body['products'])
    assert float(meta['prices_without_vat']['consumer_price']) == price
    assert float(meta['prices_without_vat']['performer_price']) == price

    assert meta['service'] == 'eats'
    assert 'created_at' in meta
    assert 'tariff' in meta


async def test_order_sum_influence(
        _failed_int_api_checks_mock, mocks, pay_order_request, _request_body,
):
    body = dict(
        _request_body,
        products=[
            {'amount': '12500.00', 'currency': 'RUB', 'name': 'service'},
        ],
    )
    response = await pay_order_request(body)
    assert response.status_code == 200
    assert response.json() == {
        'status': {
            'code': 'FAIL',
            'message': 'недостаточно средств для оплаты заказа',
        },
    }


@pytest.fixture
def _request_body(load_json):
    body = load_json('order_request.json')
    return body


@pytest.fixture
def _failed_int_api_checks_mock(mockserver):
    @mockserver.json_handler('/taxi-corp-integration/v1/payment-methods/eats')
    def handler(request):
        assert request.json == {
            'currency': 'RUB',
            'order_id': '111111-222222',
            'order_sum': '12500',
        }
        return {
            'payment_methods': [
                {
                    'id': 'corp:yastation_rus_rkarlash:RUB',
                    'user_id': 'yastation_rus_rkarlash',
                    'client_id': 'yastation_rus',
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
                    'id': 'corp:yataxi_rus_rkarlash:RUB',
                    'user_id': 'yataxi_rus_rkarlash',
                    'client_id': 'yataxi_rus',
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
