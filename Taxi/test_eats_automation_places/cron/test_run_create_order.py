import datetime

import pytest

from eats_automation_places.crontasks import exceptions
from eats_automation_places.crontasks import track_order
from eats_automation_places.generated.cron import run_cron


@pytest.mark.now(enabled=True)
@pytest.mark.parametrize(
    'crontask', ['run_create_retail_order', 'run_create_rest_order'],
)
async def test_create_order(mockserver, monkeypatch, load_json, crontask):
    @mockserver.json_handler('/api/v1/cart')
    def fill_cart():  # pylint: disable=W0612
        return mockserver.make_response(json=load_json('fill_cart.json'))

    @mockserver.json_handler('/api/v2/cart/go-checkout')
    def go_checkout():  # pylint: disable=W0612
        return mockserver.make_response(json=load_json('go_checkout.json'))

    @mockserver.json_handler('/api/v1/user/addresses')
    def get_addresses():  # pylint: disable=W0612
        return mockserver.make_response(json=load_json('get_addresses.json'))

    @mockserver.json_handler('/api/v1/orders')
    def create_order():  # pylint: disable=W0612
        return mockserver.make_response(json=load_json('create_order.json'))

    @mockserver.json_handler('/api/v2/cart')
    def delete_cart():  # pylint: disable=W0612
        return mockserver.make_response(json={}, status=204)

    @mockserver.json_handler('/api/v2/orders/tracking')
    def track_orders():  # pylint: disable=W0612
        return mockserver.make_response(json=load_json('tracking.json'))

    monkeypatch.setattr(
        track_order.OrderTracker,
        '_DEFAULT_TIMEOUT',
        datetime.timedelta(seconds=0),
    )

    await run_cron.main(
        [f'eats_automation_places.crontasks.{crontask}', '-t', '0'],
    )
    assert fill_cart.times_called == 1
    assert go_checkout.times_called == 1
    assert get_addresses.times_called == 1
    assert create_order.times_called == 1
    assert track_orders.times_called == 1
    assert delete_cart.times_called == 0


@pytest.mark.parametrize(
    'crontask', ['run_create_retail_order', 'run_create_rest_order'],
)
async def test_no_addresses(mockserver, load_json, crontask):
    @mockserver.json_handler('/api/v1/cart')
    def fill_cart():  # pylint: disable=W0612
        return mockserver.make_response(json=load_json('fill_cart.json'))

    @mockserver.json_handler('/api/v2/cart/go-checkout')
    def go_checkout():  # pylint: disable=W0612
        return mockserver.make_response(json=load_json('go_checkout.json'))

    @mockserver.json_handler('/api/v1/user/addresses')
    def get_addresses():  # pylint: disable=W0612
        return mockserver.make_response(json=load_json('empty_addresses.json'))

    @mockserver.json_handler('/api/v1/orders')
    def create_order():  # pylint: disable=W0612
        return mockserver.make_response(json=load_json('create_order.json'))

    @mockserver.json_handler('/api/v2/cart')
    def delete_cart():  # pylint: disable=W0612
        return mockserver.make_response(json={}, status=204)

    with pytest.raises(exceptions.MissingAddressException):
        await run_cron.main(
            [f'eats_automation_places.crontasks.{crontask}', '-t', '0'],
        )

    assert fill_cart.times_called == 1
    assert go_checkout.times_called == 1
    assert get_addresses.times_called == 1
    assert create_order.times_called == 0
    assert delete_cart.times_called == 1


@pytest.mark.parametrize(
    'crontask', ['run_create_retail_order', 'run_create_rest_order'],
)
async def test_no_offers(mockserver, load_json, crontask):
    @mockserver.json_handler('/api/v1/cart')
    def fill_cart():  # pylint: disable=W0612
        return mockserver.make_response(json=load_json('fill_cart.json'))

    @mockserver.json_handler('/api/v2/cart/go-checkout')
    def go_checkout():  # pylint: disable=W0612
        return mockserver.make_response(
            json=load_json('go_checkout_empty_offers.json'),
        )

    @mockserver.json_handler('/api/v1/user/addresses')
    def get_addresses():  # pylint: disable=W0612
        return mockserver.make_response(json=load_json('get_addresses.json'))

    @mockserver.json_handler('/api/v1/orders')
    def create_order():  # pylint: disable=W0612
        return mockserver.make_response(json=load_json('create_order.json'))

    @mockserver.json_handler('/api/v2/cart')
    def delete_cart():  # pylint: disable=W0612
        return mockserver.make_response(json={}, status=204)

    with pytest.raises(exceptions.EmptyOffersListException):
        await run_cron.main(
            [f'eats_automation_places.crontasks.{crontask}', '-t', '0'],
        )

    assert fill_cart.times_called == 1
    assert go_checkout.times_called == 1
    assert get_addresses.times_called == 0
    assert create_order.times_called == 0
    assert delete_cart.times_called == 1
