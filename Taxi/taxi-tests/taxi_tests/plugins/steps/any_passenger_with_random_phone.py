import random

import pytest

from taxi_tests.plugins import client


class Passenger(client.Client):

    def __init__(self, taximeter_control, *args, **kwargs):
        super(Passenger, self).__init__(*args, **kwargs)
        self.taximeter_control = taximeter_control
        self._driver_on_order = None

    @property
    def driver_on_order(self):
        if self._driver_on_order:
            return self._driver_on_order

        response = self.taxiontheway()
        self._driver_on_order = self.taximeter_control.find_by_phone(
            response['driver']['phone'],
        )
        return self._driver_on_order

    def add_any_card(self):
        self.card = self.billing.gen_any_success_card()
        self.add_card(card=self.card)

    def set_random_source(self, places):
        self.set_source(random.choice(places))

    def set_random_destinations(self, places, count=1):
        self.set_destinations([random.choice(places) for _ in range(count)])


@pytest.fixture
def any_passenger_with_random_phone(
        protocol, session_maker, search_maps, billing, taximeter_control,
):
    passenger = Passenger(
        taximeter_control, protocol, session_maker, search_maps, billing,
    )
    passenger.init_phone(phone='random')
    return passenger
