from tests_fleet_antifraud.mock_api_impl import driver_orders
from tests_fleet_antifraud.mock_api_impl import driver_profiles
from tests_fleet_antifraud.mock_api_impl import fleet_transactions_api


_SERVICES = [driver_profiles, driver_orders, fleet_transactions_api]


def setup(load_json, mockserver):
    context = load_json('mock_api.json')
    return {s.NAME: s.setup(context, mockserver) for s in _SERVICES}
