import asyncio
import datetime
from unittest import mock

import pytest

from toll_roads import time_storage
from toll_roads.stq import toll_roads_order_save

ORDER_ID = '00234567890123456789abcdefGHIJKLMN'
USER_ID = '10234567890123456789abcdefGHIJKLMN'
OFFER_ID = '20234567890123456789abcdefGHIJKLMN'
OFFER_ID2 = '21234567890123456789abcdefGHIJKLMN'
DATETIME1 = datetime.datetime(2020, 1, 2, 3, 4, 5, 1000, datetime.timezone.utc)
DATETIME2 = DATETIME1 + datetime.timedelta(microseconds=1000)
NOW = DATETIME2


@pytest.mark.parametrize(
    'offer_id, offer_exists',
    [(OFFER_ID, True), (OFFER_ID, False), (None, False)],
)
@pytest.mark.parametrize(
    'order_exists, log_exists', [(True, True), (True, False), (False, False)],
)
@pytest.mark.parametrize('order_offer_id', [OFFER_ID, OFFER_ID2, None])
@pytest.mark.parametrize('order_can_switch_road', [False, True])
@pytest.mark.parametrize('user_had_choice', [False, True])
@pytest.mark.parametrize('user_chose_toll_roads', [False, True])
@pytest.mark.parametrize('autopayment', [False, True])
@pytest.mark.parametrize(
    'source, destination', [[(37.0, 55.0), (37.5, 55.5)], [None, None]],
)
@pytest.mark.parametrize('created', [DATETIME2, None])
@pytest.mark.parametrize(
    'antifraud_enabled',
    [
        pytest.param(
            enabled,
            marks=pytest.mark.config(
                TOLL_ROADS_ANTIFRAUD_ORDER_CANCEL_ENABLED=enabled,
            ),
        )
        for enabled in (False, True)
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_order_and_offer_save(
        stq_runner,
        db,
        offer_id,
        offer_exists,
        order_exists,
        log_exists,
        order_offer_id,
        order_can_switch_road,
        user_had_choice,
        user_chose_toll_roads,
        created,
        antifraud_enabled,
        mockserver,
        autopayment,
        source,
        destination,
):
    can_switch_road = (
        order_can_switch_road if order_exists else user_had_choice
    )

    @mockserver.json_handler('/order-core/v1/tc/order-cancel')
    def _order_cancel(request):
        return {}

    if offer_exists:
        await db.save_offer(offer_id)
    if order_exists:
        await db.save_order(
            ORDER_ID,
            DATETIME1,
            order_can_switch_road,
            order_offer_id,
            auto_payment=autopayment,
            source=source,
            destination=destination,
        )
    if log_exists:
        await db.save_log(ORDER_ID, DATETIME1, not user_chose_toll_roads)
        log = await db.fetch_last_log(ORDER_ID)
        assert log['created_at'] == DATETIME1

    await stq_runner.toll_roads_order_save.call(
        task_id='task1',
        args=(
            created,
            ORDER_ID,
            USER_ID,
            offer_id if offer_id is not None else '',
            user_had_choice,
            user_chose_toll_roads,
            autopayment,
            list(source) if source else None,
            list(destination) if destination else None,
        ),
    )

    order = await db.fetch_order(ORDER_ID)
    if user_chose_toll_roads or (user_had_choice and not offer_exists):
        assert order
        expected_order = {
            'order_id': ORDER_ID,
            'created_at': (
                DATETIME1 if order_exists else (created if created else NOW)
            ),
            'offer_id': order_offer_id if order_exists else offer_id,
            'can_switch_road': can_switch_road,
            'auto_payment': autopayment,
            'point_a': source,
            'point_b': destination,
        }
        assert dict(order) == expected_order

        log = await db.fetch_last_log(ORDER_ID)
        assert log
        expected_log = {
            'order_id': ORDER_ID,
            'created_at': DATETIME2,
            'has_toll_road': user_chose_toll_roads,
        }
        assert dict(log) == expected_log
    else:
        assert not order or order_exists

    if not offer_exists:
        offer = await db.fetch_offer(offer_id)
        assert bool(offer) == (user_chose_toll_roads and bool(offer_id))

    if not user_chose_toll_roads and offer_exists and antifraud_enabled:
        assert _order_cancel.times_called == 1
    else:
        assert _order_cancel.times_called == 0


async def test_cancel_invalid_order_state(stq_runner, db, mockserver):
    @mockserver.json_handler('/order-core/v1/tc/order-cancel')
    def _order_cancel(request):
        return mockserver.make_response(
            status=400,
            json={
                'code': 'INVALID_ORDER_STATE',
                'message': 'Order is in invalid state for cancellation',
            },
        )

    await db.save_offer(OFFER_ID)

    await stq_runner.toll_roads_order_save.call(
        task_id='task1',
        args=(
            DATETIME2,
            ORDER_ID,
            USER_ID,
            OFFER_ID,
            True,  # user_had_choice
            False,  # user_chose_toll_roads
        ),
    )
    assert _order_cancel.times_called == 1


def async_return(result=None):
    future = asyncio.Future()
    future.set_result(result)
    return future


@pytest.mark.parametrize('is_fraud', [False, True])
@pytest.mark.parametrize('fraud_reporting_enabled', [False, True])
@pytest.mark.parametrize('antifraud_enabled', [False, True])
async def test_fraud_reporting(
        is_fraud, fraud_reporting_enabled, antifraud_enabled,
):
    # pylint: disable=W0212
    order_saver = toll_roads_order_save.OrderSaver(
        toll_roads_order_save.Order(NOW, ORDER_ID, OFFER_ID),
        USER_ID,
        user_had_choice=True,
        user_chose_toll_road=False,
        context=mock.MagicMock(),
    )

    order_saver._load_offer = mock.MagicMock(return_value=async_return())
    order_saver._sync_offer_with_db = mock.MagicMock(
        return_value=async_return(),
    )
    order_saver._save_order = mock.MagicMock(return_value=async_return())
    order_saver._cancel_fraud_order = mock.MagicMock(
        return_value=async_return(),
    )

    type(order_saver)._is_fraud = mock.PropertyMock(return_value=is_fraud)
    type(order_saver)._is_fraud_reporting_enabled = mock.PropertyMock(
        return_value=fraud_reporting_enabled,
    )
    type(order_saver)._is_antifraud_enabled = mock.PropertyMock(
        return_value=antifraud_enabled,
    )

    with mock.patch('toll_roads.utils.metrics.Sender') as metrics_mock:
        send_mock = mock.MagicMock()
        metrics_mock.return_value.send_fraud_order_attempt = send_mock

        time_storage.init_time_storage('toll_roads_order_save')
        await order_saver.run()

        if is_fraud and fraud_reporting_enabled:
            send_mock.assert_called_once()
        else:
            send_mock.assert_not_called()
