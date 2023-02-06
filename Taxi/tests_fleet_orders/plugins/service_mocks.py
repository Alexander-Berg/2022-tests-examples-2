import pytest


class TransactionsContext:
    def __init__(self):
        self.transactions = []

    def set_transactions(self, transactions):
        self.transactions = transactions


@pytest.fixture(name='mock_fleet_transactions_api')
def _mock_fleet_transactions_api(mockserver):

    context = TransactionsContext()

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/orders/transactions/list',
    )
    def _v1_parks_orders_transactions_list(request):
        return {
            'transactions': [
                t
                for t in context.transactions
                if t['order_id']
                in request.json['query']['park']['order']['ids']
            ],
        }

    return context


class FleetParksContext:
    def __init__(self):
        self.parks = []

    def set_parks(self, parks):
        self.parks = parks


@pytest.fixture(name='mock_fleet_parks')
def _mock_fleet_parks(mockserver):

    context = FleetParksContext()

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _v1_parks_list(request):
        return {'parks': [t for t in context.parks]}

    return context


class VehiclesContext:
    def __init__(self):
        self.vehicles = []

    def set_vehicles(self, vehicles):
        self.vehicles = vehicles


@pytest.fixture(name='mock_fleet_vehicles')
def _mock_fleet_vehicles(mockserver):

    context = VehiclesContext()

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _v1_vehicles_cache_retrieve(request):
        return {'vehicles': [t for t in context.vehicles]}

    return context


class DriverProfilesContext:
    def __init__(self):
        self.profiles = []

    def set_profiles(self, profiles):
        self.profiles = profiles


@pytest.fixture(name='mock_driver_profiles')
def _mock_driver_profiles(mockserver):

    context = DriverProfilesContext()

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _v1_driver_profiles_retrieve(request):
        return {'profiles': [t for t in context.profiles]}

    return context


class UniqueDriversContext:
    def __init__(self):
        self.uniques = []

    def set_uniques(self, uniques):
        self.uniques = uniques


@pytest.fixture(name='mock_unique_drivers')
def _mock_unique_drivers(mockserver):

    context = UniqueDriversContext()

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _v1_driver_uniques_retrieve_by_profiles(request):
        return {'uniques': [t for t in context.uniques]}

    return context


class DriverPhotosContext:
    def __init__(self):
        self.actual_photos = []

    def set_actual_photos(self, actual_photos):
        self.actual_photos = actual_photos


@pytest.fixture(name='mock_udriver_photos')
def _mock_udriver_photos(mockserver):

    context = DriverPhotosContext()

    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _driver_photos_v1_fleet_photos(request):
        return {'actual_photos': [t for t in context.actual_photos]}

    return context
