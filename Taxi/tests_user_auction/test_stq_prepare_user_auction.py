import datetime

import bson
import pytest

SOME_DATETIME = datetime.datetime(
    2021, 6, 4, 13, 37, 2, 85130, tzinfo=datetime.timezone.utc,
)
SOME_DATETIME_STR = SOME_DATETIME.isoformat()

SOME_EARLIER_DATETIME = datetime.datetime(
    2020, 6, 4, 13, 37, 2, 85130, tzinfo=datetime.timezone.utc,
)
SOME_EARLIER_DATETIME_STR = SOME_EARLIER_DATETIME.isoformat()


PHONE_ID = '123412341234123412341234'

PASSENGER_PRICE = 2000

STQ_KWARGS = {
    'order_id': 'order_id1',
    'created': SOME_DATETIME_STR,
    'order_request': {'due': SOME_DATETIME_STR, 'is_delayed': False},
    'tariff_zone': 'spb',
    'phone_id': {'$oid': PHONE_ID},
}

STQ_KWARGS_FULL_AUCTION = {
    'order_id': 'order_id1',
    'created': SOME_DATETIME_STR,
    'order_request': {'due': SOME_DATETIME_STR, 'is_delayed': False},
    'tariff_zone': 'spb',
    'phone_id': {'$oid': PHONE_ID},
    'base_price': PASSENGER_PRICE,
}


def recal_order(order_price):
    return {
        'price': {
            'driver': {'meta': {}, 'total': order_price},
            'user': {
                'meta': {
                    'paid_cancel_in_waiting_price': 199.0,
                    'paid_cancel_price': 199.0,
                },
                'total': order_price,
            },
        },
    }


@pytest.mark.now('2018-08-05T00:00:00Z')
@pytest.mark.experiments3(filename='allowed_price_change_config.json')
async def test_stq_prepare_user_auction(
        taxi_user_auction, mockserver, testpoint, stq_runner,
):
    order_price = 1000

    @mockserver.json_handler('/pricing-data-preparer/v2/recalc_order')
    def pricing_data_preparer(request):
        return recal_order(order_price)

    @mockserver.handler(
        '/order-core/internal/processing/v1/event/user-auction-init-price',
    )
    def mock_processing_event(request):
        assert request.query['order_id'] == 'order_id1'
        assert (
            request.headers['X-Idempotency-Token'] == 'user-auction-init-price'
        )

        body = bson.BSON(request.get_data()).decode()
        assert body['event_arg'] == {
            'base_price': order_price,
            'allowed_price_change_fixed_steps': {
                'max_steps': 5,
                'step': 200.5,
            },
        }
        return mockserver.make_response(
            status=200, content_type='application/bson',
        )

    @testpoint('prepare_user_auction_stq')
    def testpoint_call(_):
        return {}

    await taxi_user_auction.enable_testpoints()

    await stq_runner.prepare_user_auction.call(
        task_id='task_id1', kwargs=STQ_KWARGS,
    )

    assert testpoint_call.times_called == 1
    assert mock_processing_event.times_called == 1
    assert pricing_data_preparer.times_called == 1


@pytest.mark.now('2018-08-05T00:00:00Z')
@pytest.mark.experiments3(filename='allowed_price_change_config.json')
async def test_stq_prepare_user_auction_with_full_auction(
        taxi_user_auction, mockserver, testpoint, stq_runner,
):
    @mockserver.json_handler('/pricing-data-preparer/v2/recalc_order')
    def pricing_data_preparer(request):
        return recal_order(1000)

    @mockserver.handler(
        '/order-core/internal/processing/v1/event/user-auction-init-price',
    )
    def mock_processing_event(request):
        assert request.query['order_id'] == 'order_id1'
        assert (
            request.headers['X-Idempotency-Token'] == 'user-auction-init-price'
        )

        body = bson.BSON(request.get_data()).decode()
        assert body['event_arg'] == {
            'base_price': PASSENGER_PRICE,
            'allowed_price_change_fixed_steps': {
                'max_steps': 5,
                'step': 200.5,
            },
        }
        return mockserver.make_response(
            status=200, content_type='application/bson',
        )

    @testpoint('prepare_user_auction_stq')
    def testpoint_call(_):
        return {}

    await taxi_user_auction.enable_testpoints()

    await stq_runner.prepare_user_auction.call(
        task_id='task_id1', kwargs=STQ_KWARGS_FULL_AUCTION,
    )

    assert testpoint_call.times_called == 1
    assert mock_processing_event.times_called == 1
    assert pricing_data_preparer.times_called == 0


async def test_disabled_auction_not_found_config3(
        taxi_user_auction, stq_runner, mockserver, testpoint,
):
    @mockserver.json_handler('/pricing-data-preparer/v2/recalc_order')
    def pricing_data_preparer(request):
        return recal_order(1000)

    @testpoint('prepare_user_auction_stq')
    def testpoint_call(_):
        return {}

    await taxi_user_auction.enable_testpoints()

    await stq_runner.prepare_user_auction.call(
        task_id='task_id1', kwargs=STQ_KWARGS,
    )

    assert testpoint_call.times_called == 1
    assert pricing_data_preparer.times_called == 1


@pytest.mark.experiments3(filename='allowed_price_change_config.json')
async def test_disabled_auction_by_price_change_config(
        taxi_user_auction, stq_runner, mockserver, testpoint,
):
    @mockserver.json_handler('/pricing-data-preparer/v2/recalc_order')
    def pricing_data_preparer(request):
        return recal_order(666)

    @testpoint('prepare_user_auction_stq')
    def testpoint_call(_):
        return {}

    await taxi_user_auction.enable_testpoints()

    await stq_runner.prepare_user_auction.call(
        task_id='task_id1', kwargs=STQ_KWARGS,
    )

    assert testpoint_call.times_called == 1
    assert pricing_data_preparer.times_called == 1


@pytest.mark.config(USER_AUCTION_PREPARE_USER_AUCTION_MAX_ATTEMPTS=3)
async def test_stq_prepare_user_auction_max_attempts(
        taxi_user_auction, stq_runner, testpoint,
):
    @testpoint('prepare_user_auction_stq')
    def testpoint_call(_):
        return {'inject_error': True}

    await taxi_user_auction.enable_testpoints()

    await stq_runner.prepare_user_auction.call(
        task_id='task_id1', kwargs=STQ_KWARGS, expect_fail=True,
    )
    await stq_runner.prepare_user_auction.call(
        task_id='task_id1', kwargs=STQ_KWARGS, expect_fail=False, exec_tries=3,
    )

    assert testpoint_call.times_called == 2


async def test_delayed_by_flag_order(taxi_user_auction, testpoint, stq_runner):
    @testpoint('prepare_user_auction_stq')
    def testpoint_call(_):
        return {}

    await taxi_user_auction.enable_testpoints()

    await stq_runner.prepare_user_auction.call(
        task_id='task_id1',
        kwargs={
            'order_id': 'order_id1',
            'created': SOME_DATETIME_STR,
            'order_request': {'due': SOME_DATETIME_STR, 'is_delayed': True},
            'tariff_zone': 'spb',
            'phone_id': {'$oid': PHONE_ID},
        },
    )

    assert testpoint_call.times_called == 0


@pytest.mark.config(DELAYED_ORDER_DETECTION_THRESHOLD_MIN=15)
async def test_delayed_by_due_order(taxi_user_auction, testpoint, stq_runner):
    @testpoint('prepare_user_auction_stq')
    def testpoint_call(_):
        return {}

    await taxi_user_auction.enable_testpoints()

    await stq_runner.prepare_user_auction.call(
        task_id='task_id1',
        kwargs={
            'order_id': 'order_id1',
            'created': SOME_EARLIER_DATETIME_STR,
            'order_request': {'due': SOME_DATETIME_STR, 'is_delayed': False},
            'tariff_zone': 'spb',
            'phone_id': {'$oid': PHONE_ID},
        },
    )

    assert testpoint_call.times_called == 0
