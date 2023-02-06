# pylint: disable=redefined-outer-name

import pytest

from eats_automation_places.generated.cron import run_cron


@pytest.fixture
def eats_vendor(mockserver, load_json):
    class EatsVendor:
        @mockserver.json_handler('/4.0/restapp-front/api/v1/client/login')
        def login(self):
            return mockserver.make_response(
                json=load_json('token_response.json'),
            )

        @mockserver.json_handler(
            r'/4.0/restapp-front/api/v1/client/orders/\S+/accept', regex=True,
        )
        def accept_order(self):
            return mockserver.make_response()

        @mockserver.json_handler(
            r'/4.0/restapp-front/api/v1/client/orders/\S+/cancel', regex=True,
        )
        def cancel_order(self):
            return mockserver.make_response()

        @mockserver.json_handler(
            r'/4.0/restapp-front/api/v1/client/orders/\S+/deliver', regex=True,
        )
        def deliver_order(self):
            return mockserver.make_response()

        @mockserver.json_handler(
            r'/4.0/restapp-front/api/v1/client/orders/\S+/release', regex=True,
        )
        def release_order(self):
            return mockserver.make_response()

    return EatsVendor()


@pytest.mark.config(VENDOR_POLLING={'polling_attempts_per_minute': 1})
@pytest.mark.parametrize(
    'orders_json,'
    'accept_times_called,'
    'cancel_times_called,'
    'deliver_times_called,'
    'release_times_called',
    [
        ('active_orders_response.json', 0, 0, 0, 0),
        ('active_accept_orders_response.json', 3, 0, 0, 0),
        ('active_cancel_orders_response.json', 2, 2, 0, 0),
        ('active_deliver_orders_response.json', 2, 0, 2, 0),
        ('active_release_orders_response.json', 1, 0, 1, 1),
    ],
)
async def test_orders_without_comment(
        eats_vendor,
        mockserver,
        load_json,
        orders_json,
        accept_times_called,
        cancel_times_called,
        deliver_times_called,
        release_times_called,
):
    @mockserver.json_handler('/4.0/restapp-front/api/v1/client/orders/active')
    def active_orders():
        return mockserver.make_response(json=load_json(orders_json))

    await run_cron.main(
        ['eats_automation_places.crontasks.run_rest_emu', '-t', '0'],
    )
    assert active_orders.times_called == 1
    assert eats_vendor.login.times_called == 1
    assert eats_vendor.accept_order.times_called == accept_times_called
    assert eats_vendor.cancel_order.times_called == cancel_times_called
    assert eats_vendor.deliver_order.times_called == deliver_times_called
    assert eats_vendor.release_order.times_called == release_times_called
