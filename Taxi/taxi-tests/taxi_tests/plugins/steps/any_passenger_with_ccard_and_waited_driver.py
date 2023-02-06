import pytest


# pylint: disable=invalid-name
@pytest.fixture
def any_passenger_with_ccard_and_waited_driver(
        any_passenger_with_ccard_and_route,
):
    passenger = any_passenger_with_ccard_and_route

    passenger.order(comment='manual_control-1,')
    passenger.wait_for_order_status(status='driving')

    driver = passenger.driver_on_order
    driver.move(passenger.source['geopoint'])
    driver.requestconfirm('waiting')

    return passenger
