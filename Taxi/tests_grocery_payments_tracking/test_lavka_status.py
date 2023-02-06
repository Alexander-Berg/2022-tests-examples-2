import datetime

# pylint: disable=import-error
from grocery_mocks import grocery_cibus as grocery_cibus_mock
import pytest

from tests_grocery_payments_tracking import consts
from tests_grocery_payments_tracking import experiments
from tests_grocery_payments_tracking import headers


CIBUS_RESPONSE_PAYLOAD = {
    'application_id': grocery_cibus_mock.DEFAULT_PAYMENT['application_id'],
    'token': grocery_cibus_mock.DEFAULT_PAYMENT['token'],
    'redirect_url': grocery_cibus_mock.DEFAULT_PAYMENT['redirect_url'],
    'finish_url': grocery_cibus_mock.DEFAULT_PAYMENT['finish_url'],
    'type': 'cibus',
}


@pytest.fixture(name='lavka_payment_status')
async def _lavka_payment_status(
        taxi_grocery_payments_tracking, experiments3, grocery_cibus,
):
    async def _inner(
            enabled=True,
            expected_status=200,
            payment_type=consts.CARD_PAYMENT_TYPE,
            checked_order_id=consts.ORDER_ID,
            expected_retry_header='10',
    ):
        experiments3.add_config(
            name='grocery_payments_tracking_enabled',
            consumers=['grocery-payments-tracking'],
            default_value={'enabled': enabled},
        )

        if checked_order_id is not None:
            grocery_cibus.cibus_status.check(order_id=checked_order_id)

        request = {'order_id': consts.ORDER_ID, 'payment_type': payment_type}

        response = await taxi_grocery_payments_tracking.post(
            '/lavka/v1/payments-tracking/v1/status',
            json=request,
            headers=headers.DEFAULT_HEADERS,
        )

        if expected_retry_header is not None and expected_status == 200:
            assert response.headers['Retry-After'] == expected_retry_header

        assert response.status_code == expected_status

        return response.json()

    return _inner


async def test_skip(lavka_payment_status):
    response = await lavka_payment_status(
        enabled=False, expected_retry_header=None,
    )

    assert response['status'] == 'need_to_skip'


async def test_init(lavka_payment_status, grocery_payments_tracking_db):
    response = await lavka_payment_status()

    assert response['status'] == 'init'

    payment = grocery_payments_tracking_db.get_payment()

    assert payment is not None
    assert payment.status == 'init'


async def test_mocked_response(
        lavka_payment_status, grocery_payments_tracking_configs,
):
    mocked_response = {
        'status': 'wait_user_action',
        'payload': {'purchase_token': 'xxx', 'type': 'sbp'},
    }
    grocery_payments_tracking_configs.set_mocked_status_response(
        mocked_response,
    )
    response = await lavka_payment_status(expected_retry_header=None)

    assert response == mocked_response


@experiments.RETRY_AFTER_SECONDS
@pytest.mark.parametrize(
    'lifetime, retry',
    [
        (datetime.timedelta(seconds=1), '1'),
        (datetime.timedelta(seconds=30000), '10'),
    ],
)
async def test_retry_header(
        lavka_payment_status, grocery_cibus, lifetime, retry, now,
):
    created = str((now - lifetime).strftime('%Y-%m-%dT%H:%M:%SZ'))

    grocery_cibus.cibus_status.mock_response(created=created)

    await lavka_payment_status(
        payment_type='cibus', expected_retry_header=retry,
    )


async def test_cibus_status_ok(lavka_payment_status, grocery_cibus):
    cibus_response = grocery_cibus_mock.DEFAULT_PAYMENT

    response = await lavka_payment_status(payment_type='cibus')

    assert grocery_cibus.cibus_status.times_called == 1
    assert response == {
        'status': 'wait_user_action',
        'payload': {
            'type': 'cibus',
            'redirect_url': cibus_response['redirect_url'],
            'finish_url': cibus_response['finish_url'],
            'token': cibus_response['token'],
            'application_id': cibus_response['application_id'],
        },
    }


async def test_cibus_status_fail(lavka_payment_status, grocery_cibus):
    cibus_response = grocery_cibus_mock.DEFAULT_PAYMENT_FAIL

    grocery_cibus.cibus_status.mock_response(**cibus_response)

    response = await lavka_payment_status(payment_type='cibus')

    assert grocery_cibus.cibus_status.times_called == 1
    assert response == {'status': cibus_response['status']}


@pytest.mark.parametrize('status_code', [400, 404])
async def test_cibus_status_error(
        lavka_payment_status, grocery_cibus, status_code,
):
    cibus_response = grocery_cibus_mock.DEFAULT_PAYMENT_ERROR

    grocery_cibus.cibus_status.mock_response(**cibus_response)
    grocery_cibus.cibus_status.status_code = status_code
    response = await lavka_payment_status(
        payment_type='cibus', expected_status=status_code,
    )

    assert grocery_cibus.cibus_status.times_called == 1
    assert response == {
        'code': cibus_response['code'],
        'message': cibus_response['message'],
    }


@pytest.mark.parametrize(
    'status, payload',
    [
        ('init', None),
        ('wait_user_action', {'type': 'card', 'redirect_url': 'some_url'}),
        ('fail', None),
    ],
)
async def test_card_status_from_db(
        lavka_payment_status, grocery_payments_tracking_db, status, payload,
):
    grocery_payments_tracking_db.insert_payment(status=status, payload=payload)

    response = await lavka_payment_status()

    assert response['status'] == status
    assert response.get('payload') == payload


@pytest.mark.parametrize(
    'status, payload',
    [
        ('wait_user_action', CIBUS_RESPONSE_PAYLOAD),
        ('need_to_skip', None),
        ('success', None),
        ('cancel', None),
        ('fail', None),
    ],
)
async def test_cibus_status_from_db(
        lavka_payment_status, grocery_payments_tracking_db, status, payload,
):
    grocery_payments_tracking_db.insert_payment(status=status, payload=None)

    response = await lavka_payment_status(payment_type='cibus')

    assert response['status'] == status
    assert response.get('payload') == payload
