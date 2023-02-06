import datetime

import pytest

from tests_corp_billing import util

SUCCESS = 'SUCCESS'
TRAN_ID_TPL = 'claim/order/%s/%s'


@pytest.mark.config(
    CORP_BILLING_PAYMENT_KINDS_BY_CATEGORIES={
        'express': {
            'client': 'delivery_multi_client_b2b_trip_payment',
            'partner': 'delivery_multi_park_b2b_trip_payment',
        },
    },
)
async def test_external_calls(mocks, pay_cargo_request, _request_body):
    body = _request_body.copy()
    body['claim']['claim_id'] = 'failed'
    response = await pay_cargo_request(_request_body)
    assert response.status_code == 200

    assert mocks.events_post.times_called == 1
    assert mocks.events_topics.times_called == 2


@pytest.mark.config(
    CORP_BILLING_PAYMENT_KINDS_BY_CATEGORIES={
        'express': {
            'client': 'delivery_multi_client_b2b_trip_payment',
            'partner': 'delivery_multi_park_b2b_trip_payment',
        },
    },
)
async def test_idempotency(mocks, pay_cargo_request, _request_body):
    for _i in range(2):
        response = await pay_cargo_request(_request_body)
        assert response.status_code == 200
        assert response.json()['status']['code'] == SUCCESS
        assert response.json()['transaction_id'] == TRAN_ID_TPL % (
            _request_body['claim']['claim_id'],
            1,
        )

    topics = list(mocks.events_service.topics.values())
    assert len(topics) == 1
    assert len(topics[0]['events']) == 1


@pytest.mark.config(
    CORP_BILLING_PAYMENT_KINDS_BY_CATEGORIES={
        'express': {
            'client': 'delivery_multi_client_b2b_trip_payment',
            'partner': 'delivery_multi_park_b2b_trip_payment',
        },
    },
)
async def test_first_created_rest_change_price(
        mocks, pay_cargo_request, _request_body,
):
    body = _request_body.copy()
    body['transaction_created_at'] = util.to_timestring(
        datetime.datetime.utcnow() + datetime.timedelta(seconds=0),
    )
    response = await pay_cargo_request(body)
    assert response.status_code == 200
    assert response.json()['status']['code'] == 'SUCCESS'
    assert response.json()['transaction_id'] == TRAN_ID_TPL % (
        _request_body['claim']['claim_id'],
        1,
    )
    for index in range(2):
        body = _request_body.copy()
        body['claim']['claim_status'] = 'manual_price_correction/' + str(
            index + 1,
        )
        body['transaction_created_at'] = util.to_timestring(
            datetime.datetime.utcnow() + datetime.timedelta(seconds=index + 1),
        )
        response = await pay_cargo_request(body)
        assert response.status_code == 200
        assert response.json()['status']['code'] == 'SUCCESS'
        assert response.json()['transaction_id'] == TRAN_ID_TPL % (
            _request_body['claim']['claim_id'],
            index + 2,
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


@pytest.mark.config(
    CORP_BILLING_PAYMENT_KINDS_BY_CATEGORIES={
        'express': {
            'client': 'delivery_multi_client_b2b_trip_payment',
            'partner': 'delivery_multi_park_b2b_trip_payment',
        },
    },
)
async def test_order_created_meta(mocks, pay_cargo_request, _request_body):
    response = await pay_cargo_request(_request_body)
    assert response.status_code == 200

    topics = list(mocks.events_service.topics.values())
    assert len(topics) == 1
    assert len(topics[0]['events']) == 1


@pytest.fixture
def _request_body(load_json):
    body = load_json('claim_request.json')
    return body
