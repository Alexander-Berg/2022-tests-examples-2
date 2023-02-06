import pytest


# pylint: disable=invalid-name
@pytest.fixture
def any_passenger_with_ccard_and_route(any_passenger_with_ccard, places):
    passenger = any_passenger_with_ccard

    passenger.set_random_source(places.in_moscow)
    passenger.set_random_destinations(places.in_moscow)

    return passenger
