# pylint: disable=redefined-outer-name
import pytest

import taxi_selfreg.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_selfreg.generated.service.pytest_plugins']


@pytest.fixture  # noqa: F405
def gambling_response_maker(mockserver):
    def gambling_error_handler(gambling_response):
        if gambling_response == 400:
            error_data = {
                'code': 'INVALID_REQUEST',
                'message': '',
                'details': [
                    {'code': 'INCOMPLETE_REQUEST_DATA', 'message': ''},
                ],
            }
            response = {'status': 400, 'json': error_data}
        elif gambling_response == 500:
            response = {'status': 500, 'json': {}}
        elif gambling_response == 'timeout_error':
            raise mockserver.TimeoutError()
        elif gambling_response == 'network_error':
            raise mockserver.NetworkError()
        return mockserver.make_response(**response)

    return gambling_error_handler


@pytest.fixture  # noqa: F405
def mock_personal(mockserver):
    class CallContext:
        def __init__(self) -> None:
            self.phone_pd_id_found = True
            self.license_pd_id_found = True
            self.store_licenses = None
            self.store_phone = None

        def set_phone_pd_id_found(self, found: bool):
            self.phone_pd_id_found = found

        def set_license_pd_id_found(self, found: bool):
            self.license_pd_id_found = found

    context = CallContext()

    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def _store_licenses(request):
        assert request.method == 'POST'
        body = request.json
        driver_license = body['value']

        license_pd_id = (
            f'personal_{driver_license}'
            if context.license_pd_id_found
            else None
        )
        return {'id': license_pd_id, 'value': driver_license}

    @mockserver.json_handler('/personal/v1/phones/store')
    def _store_phone(request):
        assert request.method == 'POST'
        body = request.json
        phone = body['value']
        phone_pd_id = (
            f'{phone}_personal' if context.phone_pd_id_found else None
        )
        return {'id': phone_pd_id, 'value': phone}

    context.store_licenses = _store_licenses
    context.store_phone = _store_phone

    return context


@pytest.fixture  # noqa: F405
def mock_driver_profiles_maker(mockserver, mock_driver_profiles):
    def context(expect_license, park_id):
        class CallContext:
            @mock_driver_profiles('/v1/driver/profiles/retrieve_by_license')
            @staticmethod
            def retrieve_by_license_handler(request):
                assert request.method == 'POST'
                body = request.json
                default_license_pd_id = f'personal_{expect_license}'
                assert default_license_pd_id in body['driver_license_in_set']
                assert body['projection'] == ['data.park_id']
                response_data = {
                    'profiles_by_license': [
                        {
                            'driver_license': default_license_pd_id,
                            'profiles': [
                                {
                                    'data': {'park_id': park_id},
                                    'park_driver_profile_id': (
                                        f'{park_id}_drvr'
                                    ),
                                },
                            ],
                        },
                    ],
                }
                return mockserver.make_response(status=200, json=response_data)

        return CallContext()

    return context


@pytest.fixture
def mock_fleet_vehicles_default(mockserver, mock_fleet_vehicles):
    class FleetVehiclesContext:
        def __init__(self):
            self.response = {'vehicles': []}
            self.handler = None
            self.error_code = None

        def set_response(self, resp):
            self.response = resp
            self.error_code = None

        def set_error(self, code):
            self.error_code = code

    context = FleetVehiclesContext()

    @mock_fleet_vehicles('/v1/vehicles/retrieve_by_number_with_normalization')
    def handler(request):
        if context.error_code:
            return mockserver.make_response(status=context.error_code)
        return context.response

    context.handler = handler
    return context


@pytest.fixture(autouse=True)
def mock_fleet_synchronizer(mockserver):
    class Context:
        def __init__(self):
            self.park_pairs = []
            self.login_allowed = False
            self.mock_park_mapping = None
            self.check_login_city_park = None

        def add_mapping(self, original_id, mapped_id):
            self.park_pairs.append((original_id, mapped_id))

        def reset_mappings(self):
            self.park_pairs = []

        def set_login_allowed(self, allowed: bool):
            self.login_allowed = allowed

    context = Context()

    @mockserver.json_handler('/fleet-synchronizer/v1/mapping/park')
    def _mock_park_mapping(request):
        park_id = request.query['park_id']
        found = [pair for pair in context.park_pairs if park_id in pair]
        return {
            'mapping': (
                [
                    {'app_family': 'taximeter', 'park_id': found[0][0]},
                    {'app_family': 'uberdriver', 'park_id': found[0][1]},
                ]
                if found
                else []
            ),
        }

    @mockserver.json_handler(
        '/fleet-synchronizer/fleet-synchronizer/v1/check-login-city-park',
    )
    def _mock_check_login_city_park(request):
        return {'allowed': context.login_allowed}

    context.mock_park_mapping = _mock_park_mapping
    context.check_login_city_park = _mock_check_login_city_park
    return context


@pytest.fixture
def service_client_default_headers():
    return {'User-Agent': 'Taximeter 9.60'}


@pytest.fixture
def mock_get_nearest_zone(mock_superapp_misc):
    @mock_superapp_misc('/4.0/mlutp/v1/nearest_zone')
    async def _nearest_zone(request):
        assert request.method == 'POST'
        body = request.json
        assert body['services'][0]['service'] == 'taxi'
        return {
            'services': [
                {
                    'service': 'taxi',
                    'payload': {'nearest_zone': 'moscow'},
                    'status': 'found',
                },
            ],
        }

    return _nearest_zone


@pytest.fixture
def mock_internal_v1_eda_data(mock_hiring_selfreg_forms):
    @mock_hiring_selfreg_forms('/internal/v1/eda/data')
    def _handler():
        return {'code': 'ok', 'message': 'Form submitted'}

    return _handler


@pytest.fixture
def mock_suggests_vehicle_citizen(mock_hiring_selfreg_forms):
    @mock_hiring_selfreg_forms(
        '/v1/eda/suggests/citizenships-and-vehicle-types',
    )
    def _handler():
        return {
            'citizenships': [{'id': 'RU', 'name': 'Российская Федерация'}],
            'vehicle_types': [
                {'id': 'car'},
                {'id': 'bicycle'},
                {'id': 'pedestrian'},
            ],
        }

    return _handler


@pytest.fixture
def mock_hsf_vacancy_choose(mock_hiring_selfreg_forms):
    @mock_hiring_selfreg_forms('/internal/v1/eda/vacancy/choose')
    def _handler():
        return {
            'success': True,
            'vacancy': 'eda_pedestrian',
            'service': 'eda',
            'vehicle_type': 'pedestrian',
        }

    return _handler


@pytest.fixture
def mock_hiring_api_v2_leads_create(
        mockserver,
        mock_hiring_api,
        mock_suggests_vehicle_citizen,
        mock_internal_v1_eda_data,
):
    def _wrapper(response, status=200, expected_body=None):
        @mock_hiring_api('/v2/leads/create')
        async def _handler(request):
            assert request.method == 'POST'
            if expected_body:
                assert expected_body == request.json
            return mockserver.make_response(status=status, json=response)

        return _handler

    return _wrapper


@pytest.fixture
def mock_eda_core_courier_create(mockserver):
    @mockserver.json_handler(
        '/eda_core/api/v1/general-information/couriers/create-or-update',
    )
    def _handler(reqeust):
        return mockserver.make_response(status=200, json={'id': 1234567})

    return _handler


@pytest.fixture
def stq_mock_taxi_selfreg(mockserver):
    @mockserver.json_handler(
        '/stq-agent/queues/api/add/taxi_selfreg_create_courier_and_lead',
    )
    async def _wrapper(*args, **kwargs):
        request = args[0].json
        info = _wrapper.calls_data
        info.append(request)
        return {}

    _wrapper.calls_data = []


@pytest.fixture
def mock_hiring_api_v2_leads_upsert(mockserver, mock_hiring_api):
    def _wrapper(responses, status=200):
        @mock_hiring_api('/v2/leads/upsert')
        async def _handler(request):
            response = responses.pop(0)
            return mockserver.make_response(
                status=response['status'], json=response['body'],
            )

        return _handler

    return _wrapper


@pytest.fixture  # noqa: F405
def mock_fleet_vehicles_create(mockserver):
    def context(response):
        class CallContext:
            @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
            @staticmethod
            def handler(request):
                assert request.method == 'POST'
                return response

        return CallContext()

    return context


@pytest.fixture  # noqa: F405
def mock_driver_profiles_create(mockserver):
    def context(response, phone=None, passport_uid=None, license_number=None):
        class CallContext:
            @mockserver.json_handler(
                '/driver-profiles/v1/driver/profiles/retrieve',
            )
            @staticmethod
            def handler(request):
                assert request.method == 'POST'
                if phone:
                    response['profiles'][0]['data']['phone_pd_ids'] = [
                        {'pd_id': f'{phone}_id'},
                    ]
                if passport_uid:
                    response['profiles'][0]['data'][
                        'platform_uid'
                    ] = passport_uid
                if license_number:
                    response['profiles'][0]['data']['license'][
                        'pd_id'
                    ] = f'{license_number}_id'
                return response

        return CallContext()

    return context


@pytest.fixture  # noqa: F405
def mock_driver_order_misc_create(mockserver):
    def context(response, is_on_order=False):
        class CallContext:
            @mockserver.json_handler(
                '/driver-order-misc/driver-order-misc/v1/check-on-order',
            )
            @staticmethod
            def handler(request):
                response['drivers'][0]['on_order'] = is_on_order
                return response

        return CallContext()

    return context


@pytest.fixture  # noqa: F405
def mock_fleet_parks_create(mockserver):
    def context(response):
        class CallContext:
            @mockserver.json_handler('/fleet-parks/v1/parks')
            @staticmethod
            def handler(request):
                return response

        return CallContext()

    return context


@pytest.fixture(autouse=True)
def _mock_personal_phones(mockserver):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def handler(request):
        phone_pd_id = request.json['id']
        return {'id': phone_pd_id, 'value': phone_pd_id[:-3]}

    return handler


@pytest.fixture(autouse=True)
def _mock_personal_licenses(mockserver):
    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def handler(request):
        phone_pd_id = request.json['id']
        return {'id': phone_pd_id, 'value': phone_pd_id[:-3]}

    return handler


@pytest.fixture
def mock_hiring_conditions_choose(mockserver, mock_hiring_taxiparks_gambling):
    def _wrapper(response, status):
        @mock_hiring_taxiparks_gambling('/v2/hiring-conditions/choose')
        def _handler(request):
            return mockserver.make_response(status=status, json=response)

        return _handler

    return _wrapper
