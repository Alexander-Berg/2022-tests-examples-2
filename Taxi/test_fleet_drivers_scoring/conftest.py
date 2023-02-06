# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import json

import aiohttp
import pytest

import fleet_drivers_scoring.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['fleet_drivers_scoring.generated.service.pytest_plugins']


@pytest.fixture
def _mock_driver_profiles(mockserver):
    class DriverProfilesContext:
        def __init__(self):
            self.retrieve_by_license = None
            self.vehicle_bindings = None

            self.retrieve_by_license_response = {}
            self.vehicle_bindings_response = {}

        def set_retrieve_by_license_resp(self, response):
            self.retrieve_by_license_response = response

        def set_vehicle_bindings_response(self, response):
            self.vehicle_bindings_response = response

    context = DriverProfilesContext()

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_license',
    )
    def _retrieve_by_license(request):
        return context.retrieve_by_license_response

    @mockserver.json_handler(
        '/driver-profiles/v1/vehicle_bindings/cars/retrieve_by_driver_id',
    )
    def _vehicle_bindings(request):
        return context.vehicle_bindings_response

    context.retrieve_by_license = _retrieve_by_license
    context.vehicle_bindings = _vehicle_bindings

    return context


@pytest.fixture
def _mock_fleet_parks(mockserver):
    class FleetParksContext:
        def __init__(self):
            self.parks_list = None
            # in free scoring handler fleet_parks is called 2 times, so
            # parks_list_responses may contains several responses
            self.parks_list_responses = []
            self.current_response_number = 0

            self.cities_retrieve = None
            self.cities_retrieve_response = {}

        def set_parks_list_responses(self, response):
            self.parks_list_responses = response

        def set_cities_retrieve_response(self, response):
            self.cities_retrieve_response = response

    context = FleetParksContext()

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _park_list(request):
        try:
            request_park_ids = json.loads(request.get_data())['query']['park'][
                'ids'
            ]
            if len(context.parks_list_responses) > 1:
                parks_list_response = context.parks_list_responses[
                    context.current_response_number
                ]
            else:
                parks_list_response = context.parks_list_responses[0]
            context.current_response_number += 1
            park_id_to_response = {
                park_response['id']: park_response
                for park_response in parks_list_response['parks']
            }
            result = [
                park_id_to_response[park_id] for park_id in request_park_ids
            ]
        except KeyError:
            return {'parks': []}
        return {'parks': result}

    @mockserver.json_handler('/fleet-parks/v1/cities/retrieve_by_name')
    def _cities_retrieve(request):
        request.get_data()
        return context.cities_retrieve_response

    context.parks_list = _park_list
    context.cities_retrieve = _cities_retrieve

    return context


@pytest.fixture
def _mock_fleet_transactions_api(mockserver):
    class FleetTransactionsContext:
        def __init__(self):
            self.balances_list = None
            # {(park_id, driver_profile_id): balances_list, ...}
            self.balances_list_responses = {}

        def set_balances_list_responses(self, responses):
            self.balances_list_responses = responses

    context = FleetTransactionsContext()

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        park = request.json['query']['park']
        park_id = park['id']
        driver_profile_ids = park['driver_profile']['ids']
        assert len(driver_profile_ids) == 1
        balances_list_response = context.balances_list_responses[
            (park_id, driver_profile_ids[0])
        ]

        status = 200
        if 'code' in balances_list_response:
            status = balances_list_response['code']
        return aiohttp.web.json_response(
            status=status, data=balances_list_response,
        )

    context.balances_list = _balances_list

    return context


@pytest.fixture
def _mock_fleet_vehicles(mockserver):
    class FleetVehiclesContext:
        def __init__(self):
            self.vehicles_retrieve = None
            self.vehicles_retrieve_by_number = None
            self.vehicles_retrieve_response = {}
            self.vehicles_by_number_resp = {}

        def set_vehicles_retrieve_response(self, response):
            self.vehicles_retrieve_response = response

        def set_retrieve_by_number_resp(self, response):
            self.vehicles_by_number_resp = response

    context = FleetVehiclesContext()

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _vehicles_retrieve(request):
        request.get_data()
        return context.vehicles_retrieve_response

    @mockserver.json_handler(
        '/fleet-vehicles/v1/vehicles/retrieve_by_number_normalized',
    )
    def _vehicles_retrieve_by_number(request):
        request.get_data()
        return context.vehicles_by_number_resp

    context.vehicles_retrieve = _vehicles_retrieve
    context.vehicles_retrieve_by_number = _vehicles_retrieve_by_number

    return context


@pytest.fixture
def _mock_personal(mockserver):
    class Personal:
        def __init__(self):
            self.bulk_retrieve = None
            self.bulk_retrieve_response = {}

        def set_bulk_retrieve_response(self, response):
            self.bulk_retrieve_response = response

    personal = Personal()

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _bulk_retrieve(request):
        return personal.bulk_retrieve_response

    personal.bulk_retrieve = _bulk_retrieve

    return personal


@pytest.fixture
def _mock_taximeter_xservice(mockserver):
    class Context:
        def __init__(self):
            self.exams_retrieve = None
            # {(park_id, driver_profile_id1): exam1, ...}
            self.exams_retrieve_responses = {}

        def set_exams_retrieve_responses(self, responses):
            self.exams_retrieve_responses = responses

    context = Context()

    @mockserver.json_handler(
        '/taximeter-xservice/utils/qc/driver/exams/retrieve',
    )
    def _exams_retrieve(request):
        park = request.json['query']['park']
        park_id = park['id']
        driver_profile_id = park['driver_profile']['id']
        exams_retrieve_response = context.exams_retrieve_responses[
            (park_id, driver_profile_id)
        ]

        status = 200
        if 'code' in exams_retrieve_response:
            status = exams_retrieve_response['code']
        return aiohttp.web.json_response(
            status=status, data=exams_retrieve_response,
        )

    context.exams_retrieve = _exams_retrieve

    return context


@pytest.fixture
def _mock_territories(mockserver):
    class Territories:
        def __init__(self):
            self.countries_retrieve = None
            self.countries_retrieve_response = {}

        def set_countries_retrieve_response(self, response):
            self.countries_retrieve_response = response

    territories = Territories()

    @mockserver.json_handler('/territories/v1/countries/retrieve')
    def _countries_retrieve(request):
        return territories.countries_retrieve_response

    territories.countries_retrieve = _countries_retrieve

    return territories


@pytest.fixture
def _mock_unique_drivers(mockserver):
    class UniqueDriversContext:
        def __init__(self):
            self.retrieve_by_profiles = None
            self.retrieve_by_profiles_response = {}

        def set_retrieve_by_profiles_resp(self, response):
            self.retrieve_by_profiles_response = response

    context = UniqueDriversContext()

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _retrieve_by_profiles(request):
        return context.retrieve_by_profiles_response

    context.retrieve_by_profiles = _retrieve_by_profiles

    return context


@pytest.fixture
def _mock_driver_ratings(mockserver):
    class DriverRatingsContext:
        def __init__(self):
            self.driver_ratings = None
            self.driver_ratings_response = {}

        def set_driver_rating_response(self, response):
            self.driver_ratings_response = response

    context = DriverRatingsContext()

    @mockserver.json_handler('/driver-ratings/v2/driver/rating')
    def _driver_ratings(request):
        return context.driver_ratings_response

    context.driver_ratings = _driver_ratings
    return context


@pytest.fixture
def _mock_driver_photos(mockserver):
    class DriverPhotosContext:
        def __init__(self):
            self.get_photos = None
            self.get_photos_status = 200
            self.get_photos_response = {}

        def set_get_photos_resp(self, response, status=200):
            self.get_photos_status = status
            self.get_photos_response = response

    context = DriverPhotosContext()

    @mockserver.json_handler('/taxi-driver-photos/driver-photos/v2/photos')
    def _get_photos(request):
        return aiohttp.web.json_response(
            status=context.get_photos_status, data=context.get_photos_response,
        )

    context.get_photos = _get_photos

    return context


@pytest.fixture
def _mock_billing_replication(mockserver):
    class BillingReplicationContext:
        def __init__(self):
            self.billing_replication = None
            self.billing_replication_response = {}

        def set_billing_replication_resp(self, response):
            self.billing_replication_response = response

    context = BillingReplicationContext()

    @mockserver.json_handler('/billing-replication/contract/')
    def _billing_replication(request):
        return context.billing_replication_response

    context.billing_replication = _billing_replication

    return context


@pytest.fixture
def _mock_parks_replica(mockserver):
    class ParksReplicaContext:
        def __init__(self):
            self.parks_replica = None
            self.parks_replica_response = {}

        def set_parks_replica_response(self, response):
            self.parks_replica_response = response

    context = ParksReplicaContext()

    @mockserver.json_handler(
        '/parks-replica/v1/parks/billing_client_id/retrieve',
    )
    def _parks_replica(request):
        return context.parks_replica_response

    context.parks_replica = _parks_replica

    return context


@pytest.fixture
def _mock_tariffs(mockserver):
    class TariffsContext:
        def __init__(self):
            self.tariffs = None
            self.tariffs_response = {}

        def set_tariffs_response(self, response):
            self.tariffs_response = response

    context = TariffsContext()

    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    def _tariffs(request):
        return context.tariffs_response

    context.tariffs = _tariffs

    return context


@pytest.fixture
def _mock_agglomerations(mockserver):
    class AgglomerationsContext:
        def __init__(self):
            self.agglomerations = None
            self.agglomerations_response = {}

        def set_agglomerations_response(self, response):
            self.agglomerations_response = response

    context = AgglomerationsContext()

    @mockserver.json_handler(
        '/taxi-agglomerations/v1/geo_nodes/get_mvp_oebs_id',
    )
    def _agglomerations(request):
        return context.agglomerations_response

    context.agglomerations = _agglomerations

    return context


@pytest.fixture
def _mock_billing_orders(mockserver):
    class BillingOrdersContext:
        def __init__(self):
            self.billing_orders = None
            self.billing_orders_response = {}

        def set_billing_orders_response(self, response):
            self.billing_orders_response = response

    context = BillingOrdersContext()

    @mockserver.json_handler('/billing-orders/v2/process/async')
    def _billing_orders(request):
        return context.billing_orders_response

    context.billing_orders = _billing_orders

    return context


@pytest.fixture
def _mock_driver_orders(mockserver):
    class DriverOrdersContext:
        def __init__(self):
            self.orders = None
            # in free scoring handler driver_orders is called several times
            # for different parks, so orders_responses may contains several
            # responses like dict
            # {'park_id1': 'order1', 'park_id2': 'order2', ...}
            self.orders_responses = {}

        def set_orders_resp(self, response):
            self.orders_responses = response

    context = DriverOrdersContext()

    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    def _get_orders(request):
        park_id = request.json['query']['park']['id']
        return context.orders_responses[park_id]

    context.orders = _get_orders

    return context


@pytest.fixture
def _mock_parks_activation(mockserver):
    class ParksActivationContext:
        def __init__(self):
            self.parks_activation = None
            self.parks_activation_response = {}

        def set_parks_activation_response(self, response):
            self.parks_activation_response = response

    context = ParksActivationContext()

    @mockserver.json_handler('/parks-activation/v1/parks/activation/retrieve')
    def _parks_activation(request):
        return context.parks_activation_response

    context.parks_activation = _parks_activation

    return context


@pytest.fixture
def _mock_protocol(mockserver):
    class ProtocolContext:
        def __init__(self):
            self.nearestzone = None
            self.nearestzone_response = {}
            self.nearestzone_status_code = 200

        def set_nearestzone_response(self, response, status_code=200):
            self.nearestzone_response = response
            self.nearestzone_status_code = status_code

    context = ProtocolContext()

    @mockserver.json_handler('/protocol/3.0/nearestzone')
    def _nearestzone(request):
        request.get_data()
        return aiohttp.web.json_response(
            status=context.nearestzone_status_code,
            data=context.nearestzone_response,
        )

    context.nearestzone = _nearestzone

    return context


@pytest.fixture
def _mock_fleet_payouts(mockserver):
    class FleetPayoutsContext:
        def __init__(self):
            self.fleet_version = None
            self.fleet_version_response = {}

        def set_fleet_version_response(self, response):
            self.fleet_version_response = response

    context = FleetPayoutsContext()

    @mockserver.json_handler(
        '/fleet-payouts-py3/internal/payouts/v1/fleet-version',
    )
    def _fleet_version(request):
        return context.fleet_version_response

    context.fleet_version = _fleet_version

    return context


@pytest.fixture
def _mock_fleet_rent(mockserver):
    class FleetRentContext:
        def __init__(self):
            self.affiliation = None
            self.affiliation_response = {'records': []}

            self.debt = None
            self.debt_response = {}

        def set_affiliation(self, response):
            self.affiliation_response = response

        def set_debt(self, response):
            self.debt_response = response

    context = FleetRentContext()

    @mockserver.json_handler(
        '/fleet-rent-py3/v1/sys/affiliations/by-local-driver',
    )
    def _affiliation(request):
        return context.affiliation_response

    @mockserver.json_handler(
        '/fleet-rent-py3/fleet-rent/v1/sys/park/rent/drivers/debt',
    )
    def _debt(request):
        return context.debt_response

    context.affiliation = _affiliation
    context.debt = _debt

    return context
