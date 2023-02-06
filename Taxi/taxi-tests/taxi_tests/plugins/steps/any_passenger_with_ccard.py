import pytest


@pytest.fixture
def any_passenger_with_ccard(any_passenger_with_random_phone, billing):
    passenger = any_passenger_with_random_phone

    passenger.add_any_card()

    passenger.launch()
    passenger.paymentmethods()

    return passenger
