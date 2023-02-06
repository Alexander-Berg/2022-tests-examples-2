import json

import pytest

from tests_plugins import fastcgi

from . import utils

pytest_plugins = [
    # settings fixture
    'tests_plugins.settings',
    # Testsuite plugins
    'taxi_tests.environment.pytest_plugin',
    'taxi_tests.plugins.default',
    'taxi_tests.plugins.aliases',
    'taxi_tests.plugins.translations',
    'taxi_tests.plugins.mocks.configs_service',
    'taxi_tests.plugins.pgsql.deprecated',
    'tests_plugins.mock_driver_work_rules',
    'tests_plugins.daemons.plugins',
    'tests_plugins.testpoint',
    # Local mocks
    'tests_plugins.driver_categories_api',
    'tests_plugins.mock_experiments3_proxy',
    'tests_plugins.mock_taxi_exp',
    'tests_plugins.mock_territories',
    'tests_plugins.mock_tvm',
    'tests_plugins.mock_tvm2',
    'tests_plugins.config_service_defaults',
    'parks.personal_data_mocks',
    'parks.taximeter_xservice_mock',
]

taxi_parks = fastcgi.create_client_fixture(
    'taxi_parks', client_deps=('mock_personal_data',),
)


@pytest.fixture
def dispatcher_access_control(mockserver):
    @mockserver.json_handler('/dispatcher_access_control/v1/parks/users/list')
    def mock_callback(request):
        query = json.loads(request.get_data())['query']
        assert query['user'] == {'passport_uid': ['11']}
        return utils.make_users_list_response(display_name='Boss')

    return mock_callback


@pytest.fixture(autouse=True)
def fleet_rent(mockserver):
    @mockserver.json_handler('/fleet_rent/v1/sys/affiliations/all')
    def mock_callback(request):
        return {
            'records': [
                {
                    'record_id': 'f0201c13b0274180900025559b3d2cf8',
                    'park_id': '1488',
                    'original_driver_park_id': 'park_ie_1',
                    'original_driver_id': 'driver_ie_1_original',
                    'creator_uid': '1120000000185407',
                    'created_at': '2020-06-10T13:54:51.214211+03:00',
                    'modified_at': '2020-06-10T13:56:33.280892+03:00',
                    'state': 'active',
                    'local_driver_id': 'driver_ie_1_affiliation',
                },
                {
                    'record_id': '22d4b27fb0fa4fdeb1f676a63343754b',
                    'park_id': '1488',
                    'original_driver_park_id': 'park_ie_2',
                    'original_driver_id': 'driver_ie_2_original',
                    'creator_uid': '1120000000185407',
                    'created_at': '2020-06-10T15:56:26.786019+03:00',
                    'modified_at': '2020-06-10T18:56:26.786019+03:00',
                    'state': 'active',
                    'local_driver_id': 'driver_ie_2_affiliation',
                },
                {
                    'record_id': '22d4b27fb0fa4fdeb1f676a63343754e',
                    'park_id': '1488',
                    'original_driver_park_id': 'park_se_1',
                    'original_driver_id': 'driver_se_1_original',
                    'creator_uid': '1120000000185407',
                    'created_at': '2020-06-10T15:56:26.786019+03:00',
                    'modified_at': '2020-06-10T18:56:26.786019+03:00',
                    'state': 'accepted',
                    'local_driver_id': 'driver_se_1_affiliation',
                },
                {
                    'record_id': '22d4b27fb0fa4fdeb1f676a64343754e',
                    'park_id': '1488',
                    'original_driver_park_id': 'park_se_1',
                    'original_driver_id': 'driver_se_2_original',
                    'creator_uid': '1120000000185407',
                    'created_at': '2020-06-10T15:56:26.786019+03:00',
                    'modified_at': '2020-06-10T18:56:26.786019+03:00',
                    'state': 'new',
                    'local_driver_id': 'driver_se_2_affiliation',
                },
            ],
            'limit': 3000,
            'cursor': (
                '{\"latest_record_id\": \"22d4b27fb0fa4fdeb1f676a64343754e\",'
                ' \"latest_modified_at\": \"2020-06-10T15:56:26.786019\"}'
            ),
        }

    return mock_callback


@pytest.fixture
def contractor_profiles_manager(mockserver):
    @mockserver.json_handler(
        '/contractor_profiles_manager/v1/hiring-type-restriction/retrieve',
    )
    def mock_callback(request):
        return {'is_restricted': False, 'is_warning_expected': False}

    return mock_callback


@pytest.fixture
def contractor_profession(mockserver):
    class StaticMockContractorProfession:
        @mockserver.json_handler(
            '/contractor_profession/internal'
            '/v1/professions/initialize-contractors',
        )
        def initialize(request):
            return mockserver.make_response(status=200)

        @mockserver.json_handler(
            '/contractor_profession/internal/v1/professions/validate',
        )
        def validate(request):
            return mockserver.make_response(status=200)

    return StaticMockContractorProfession


@pytest.fixture(autouse=True)
def ext_drivematics_codegen(mockserver):
    @mockserver.json_handler('/ext_drivematics_codegen/v1/parks/car/list')
    def mock_callback(request):
        return {
            'tags_array': [
                {
                    'name': 'leasing_has_telematics_tag',
                    'cars_count_zero': 1,
                    'description': {
                        'name': 'leasing_has_telematics_tag',
                        'index': 11,
                        'comment': 'base object',
                        'display_name': 'leasing_has_telematics_tag',
                    },
                    'cars_count': 222,
                    'cars_count_prior': 0,
                },
                {
                    'name': 'brand_tag_test',
                    'cars_count_zero': 213,
                    'description': {
                        'name': 'brand_tag_test',
                        'index': 1111,
                        'tag_flow_priority': 0,
                        'taxi_companies_tins': ['111111111111'],
                        'tag_flow': '',
                        'display_name': 'Тег для бренда 000 Берёзка',
                        'id': '12387138f',
                    },
                    'cars_count': 213,
                    'cars_count_prior': 0,
                },
            ],
            'cars': [
                {
                    'number': 'NUMBER',
                    'imei': 'IMEI',
                    'vin': 'XXX',
                    'tags': [
                        {
                            'tag_id': 'ID',
                            'priority': 0,
                            'tag': 'brand_tag_test',
                            'display_name': 'Тег для бренда ООО Берёзка',
                            'object_id': 'OBJECT_ID',
                        },
                    ],
                },
            ],
            'can_get_more_pages': False,
            'page_size': 1000,
        }

    return mock_callback


@pytest.fixture(autouse=True)
def deptrans_driver_status(mockserver):
    @mockserver.json_handler(
        '/deptrans_driver_status/internal/v2/profiles/updates',
    )
    def mock_callback(request):
        return {
            'binding': [
                {
                    'deptrans_pd_id': 'id_valid_deptrans_id',
                    'driver_id': 'superDriver',
                    'park_id': '222333',
                    'status': 'approved',
                    'updated_ts': '2020-12-30T11:00:00+00:00',
                },
            ],
            'cursor': 'cursor',
        }

    return mock_callback


@pytest.fixture(autouse=True)
def selfemployed_fns_replica(mockserver):
    @mockserver.json_handler('/selfemployed_fns_replica/v1/profiles/updates')
    def mock_callback(request):
        return {
            'profiles': [
                {
                    'park_contractor_profile_id': (
                        '1489_driver_selfemployed_fns'
                    ),
                    'data': {
                        'park_id': '1489',
                        'contractor_profile_id': 'driver_selfemployed_fns',
                    },
                },
            ],
            'last_revision': 'revision',
        }

    return mock_callback


class DriverBalanceLimitUpdatedTrigger:
    def __init__(self, db):
        self.mock_callback = None
        self.return_error = False
        self.has_calls = False
        self.request_body = None
        self._db = db
        self._old_balance_limit = 0.0
        self._new_balance_limit = 0.0

    def _get_balance_limit(self, park_id, driver_id):
        driver = self._db.dbdrivers.find_one(
            {'park_id': park_id, 'driver_id': driver_id},
        )
        return 0.0 if driver is None else driver.pop('balance_limit', 0.0)

    def save_old_balance_limit(self, park_id, driver_id):
        self._old_balance_limit = self._get_balance_limit(park_id, driver_id)

    def save_new_balance_limit(self, park_id, driver_id):
        self._new_balance_limit = self._get_balance_limit(park_id, driver_id)

    def check_calls(self):
        assert self.has_calls == (
            not utils.equals(self._new_balance_limit, self._old_balance_limit)
        )

    def check_body(self, park_id, driver_id, datetime_now=None):
        body = self.request_body
        assert utils.equals(
            body.pop('new_balance_limit'), self._new_balance_limit,
        )
        assert utils.equals(
            body.pop('old_balance_limit'), self._old_balance_limit,
        )
        assert body.pop('park_id') == park_id
        assert body.pop('contractor_profile_id') == driver_id

        if datetime_now:
            assert body['balance_limit_updated_at'] == datetime_now

    def check(self, park_id, driver_id, datetime_now=None):
        self.save_new_balance_limit(park_id, driver_id)
        self.check_calls()
        if self.has_calls:
            self.check_body(park_id, driver_id, datetime_now)


@pytest.fixture
def driver_balance_limit_updated_trigger(db, mockserver):
    context = DriverBalanceLimitUpdatedTrigger(db)

    @mockserver.json_handler(
        '/contractor_balances/internal/v1/balance-limit-updated-trigger',
    )
    def _mock_callback(request):
        context.has_calls = True
        context.request_body = request.json
        if context.return_error:
            return mockserver.make_response(status=500)
        return {}

    context.mock_callback = _mock_callback
    return context
