# pylint: disable=wildcard-import, unused-wildcard-import, import-error, C0411
from driver_login_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(autouse=True, name='mock_client_notify')
def _mock_client_notify(mockserver):
    @mockserver.json_handler('/client-notify/v1/unsubscribe')
    def _mock_unsubscribe(request):
        return {}

    @mockserver.json_handler('/client-notify/v2/push')
    def _mock_v2_push(request):
        assert 'service' in request.json
        assert 'intent' in request.json
        assert 'client_id' in request.json
        return {'notification_id': '123123'}

    return _mock_unsubscribe


@pytest.fixture(autouse=True)
def _reposition_stop(mockserver):
    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/session/stop',
    )
    def _mock_post(request):
        return {}


@pytest.fixture(autouse=True)
def _driver_authorizer(mockserver):
    @mockserver.json_handler('/driver-authorizer/driver/sessions/expired')
    def _mock_driver_sessions_expired(request):
        return {'expired_sessions': []}

    @mockserver.json_handler('/driver-authorizer/driver/sessions')
    def _driver_authorizer(request):
        return mockserver.make_response(
            '{}', headers={'X-Driver-Session': 'session'},
        )


@pytest.fixture(name='parks', autouse=True)
def _parks(mockserver):
    class Context:
        def __init__(self):
            self.driver_to_park = {}
            self.mock_driver_profiles_search = None

        def set_parks(self, dictionary):
            self.driver_to_park = dictionary

    context = Context()

    @mockserver.json_handler('/parks/driver-profiles/search')
    def _search(request):
        assert 'fields' in request.json
        is_logout = request.json['fields'] == {
            'park': [
                'id',
                'integration_events',
                'provider_config',
                'providers',
            ],
            'driver': ['id', 'car_id', 'providers'],
        }

        if is_logout:
            assert 'query' in request.json
            assert 'driver' in request.json['query']
            assert 'id' in request.json['query']['driver']

        def _logout_response(request, context):
            profiles = []

            for driver_id in request.json['query']['driver']['id']:
                park_id = context.driver_to_park.get(driver_id, 'park_id_0')
                profile = {
                    'driver': {
                        'id': driver_id,
                        'providers': ['park', 'yandex'],
                        'car_id': 'some_car_id',
                    },
                    'park': {
                        'id': park_id,
                        'providers': ['park', 'yandex'],
                        'provider_config': {'yandex': {'clid': '100500'}},
                        'integration_events': [],
                    },
                }
                profiles.append(profile)

            response = {'profiles': profiles}
            return response

        def _login_response(request, context):
            return {
                'profiles': [
                    {
                        'park': {
                            'id': 'dbid',
                            'country_id': 'rus',
                            'city': 'Москва',
                            'is_active': True,
                            'name': 'Sea Bream',
                            'provider_config': {'yandex': {'clid': 'clid'}},
                        },
                        'driver': {
                            'id': 'uuid',
                            'car_id': 'car_id',
                            'first_name': 'John',
                            'middle_name': 'Howard',
                            'last_name': 'Doe',
                            'email': 'a@a.a',
                            'rule_id': 'rule',
                            'license_normalized': 'AABB101010',
                        },
                        'affiliation': {
                            'state': 'active',
                            'partner_source': 'self_employed',
                        },
                    },
                ],
            }

        return (
            _logout_response(request, context)
            if is_logout
            else _login_response(request, context)
        )

    context.mock_driver_profiles_search = _search
    return context


@pytest.fixture(name='driver_status', autouse=True)
def _driver_status(mockserver):
    class Handlers:
        def __init__(self):
            self.raise_on = []

        def set_raise_on(self, statuses):
            self.raise_on = statuses

        @staticmethod
        @mockserver.json_handler('/driver-status/v2/status/store')
        def mock_status_store(request):
            assert request.method == 'POST'
            assert 'park_id' in request.json
            assert 'driver_id' in request.json
            assert 'status' in request.json
            if request.json['status'] in handlers.raise_on:
                raise mockserver.TimeoutError()
            return {'status': request.json.get('status'), 'updated_ts': 1}

        @staticmethod
        @mockserver.json_handler('/driver-status/v1/internal/status/bulk')
        def mock_internal_status_bulk(request):
            assert request.method == 'POST'

            assert 'items' in request.json
            for item in request.json['items']:
                assert 'park_id' in item
                assert 'driver_id' in item
                assert 'status' in item

            return {}

    handlers = Handlers()
    return handlers


@pytest.fixture(name='fleet_synchronizer')
def _fleet_synchronizer(mockserver):
    class Context:
        def __init__(self):
            self.park_ids = [f'dbid{i}' for i in range(1, 7)]
            self.login_bulk_check = None

        def set_parks(self, park_ids):
            self.park_ids = park_ids

    context = Context()

    @mockserver.json_handler(
        '/fleet-synchronizer/fleet-synchronizer/v1/parks/login-bulk-check',
    )
    def _mock_login_bulk_check(request):
        return {
            'items': [{'park_id': park_id} for park_id in context.park_ids],
        }

    context.login_bulk_check = _mock_login_bulk_check
    return context


@pytest.fixture(name='driver_profiles_info')
def _driver_profiles(mockserver):
    class Context:
        def __init__(self):
            self.park_id = ''
            self.driver_id = ''
            self.taximeter_version = ''
            self.taximeter_brand = ''
            self.taximeter_build_type = ''
            self.taximeter_platform_version = ''
            self.do_raise = False

        def set_ids(self, park_id, driver_id):
            self.park_id = park_id
            self.driver_id = driver_id

        def set_do_raise(self, do_raise):
            self.do_raise = do_raise

        def set_taximeter_fields(
                self,
                taximeter_version,
                taximeter_brand,
                taximeter_build_type,
                taximeter_platform_version,
        ):
            self.taximeter_version = taximeter_version
            self.taximeter_brand = taximeter_brand
            self.taximeter_build_type = taximeter_build_type
            self.taximeter_platform_version = taximeter_platform_version

    context = Context()

    @mockserver.json_handler('/driver-profiles/v1/driver/login-info')
    def _driver_profiles_update(request):
        if context.do_raise:
            raise mockserver.TimeoutError()
        if context.taximeter_version:
            assert (
                request.json['taximeter_version'] == context.taximeter_version
            )
        if context.taximeter_brand:
            assert request.json['taximeter_brand'] == context.taximeter_brand
        if context.taximeter_build_type:
            assert (
                request.json['taximeter_build_type']
                == context.taximeter_build_type
            )
        if context.taximeter_platform_version:
            assert (
                request.json['taximeter_platform_version']
                == context.taximeter_platform_version
            )
        if context.park_id:
            assert request.query['park_id'] == context.park_id
        if context.driver_id:
            assert request.query['driver_profile_id'] == context.driver_id
        return {}

    return context


@pytest.fixture(autouse=True)
def _fleet_synchronizer_mapping(mockserver):
    @mockserver.json_handler('/fleet-synchronizer/v1/mapping/park')
    def _fleet_synchronizer_mapping_park(request):
        return {
            'mapping': [
                {'park_id': 'uber_dbid', 'app_family': 'uberdriver'},
                {'park_id': 'dbid', 'app_family': 'taximeter'},
            ],
        }


@pytest.fixture(autouse=True)
def _fleet_rent(mockserver):
    @mockserver.json_handler('/fleet-rent/v1/sys/affiliations/all')
    def _fleet_rent(request):
        return {'records': [], 'limit': 1, 'cursor': 'some_cursor'}


@pytest.fixture(name='contractor_random_bonus')
def _random_bonus(mockserver):
    @mockserver.json_handler(
        '/contractor-random-bonus/internal/random-bonus/v1/on-login',
    )
    def _on_login(request):
        return {}

    return _on_login


@pytest.fixture(autouse=True)
def _profession(mockserver):
    @mockserver.json_handler(
        '/contractor-profession/internal/v1/professions/get/active/bulk',
    )
    def _mock_contractor_profession(request):
        contractor_profile_id = request.json['contractors'][0][
            'contractor_profile_id'
        ]
        return {
            'contractors': [
                {
                    'contractor': {
                        'contractor_profile_id': contractor_profile_id,
                        'park_id': 'sample',
                    },
                    'profession': {'id': 'taxi_driver', 'groups': []},
                },
            ],
        }


@pytest.fixture(autouse=True)
def _personal(mockserver):
    """
    examples:
    value = '+70001234567', id = '+70001234567_id'
    value = 'a@b.c', id = 'a@b.c_id'
    """

    def _get_id(request) -> dict:
        value = request.json['value']
        return {'id': f'{value}_id', 'value': value}

    def _get_value(request) -> dict:
        entity_id = request.json['id']
        return {'id': entity_id, 'value': entity_id[:-3]}

    @mockserver.json_handler('/personal/v1/phones/store')
    def _get_phone_id(request):
        return _get_id(request)

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _get_phone_raw(request):
        return _get_value(request)

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _get_email_raw(request):
        return _get_value(request)

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def _get_license_raw(request):
        return _get_value(request)


@pytest.fixture(name='driver_profiles_courier')
def _driver_profiles_courier(mockserver):
    @mockserver.json_handler(
        '/driver-profiles/v1/eats-couriers-binding'
        '/retrieve_by_park_driver_profile_id',
    )
    def _driver_profiles_eats_courier_binding(request):
        return {
            'binding': [
                {
                    'taxi_id': request.json['id_in_set'][0],
                    'eats_id': None,
                    'courier_app': 'taximeter',
                },
            ],
        }


@pytest.fixture(name='fleet_vehicles')
def _fleet_vehicles(mockserver):
    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _retrieve(request):
        return {
            'vehicles': [
                {
                    'park_id_car_id': 'dbid_car_id',
                    'data': {
                        'callsign': 'callsign',
                        'brand': 'Audi',
                        'model': 'A8',
                        'number': 'A666MP77',
                    },
                },
            ],
        }


@pytest.fixture(name='driver_protocol')
def _driver_protocol(mockserver):
    @mockserver.json_handler('/driver-protocol/driver/polling/state/internal')
    def _polling_state(request):
        assert request.args.get('driver_mode_policy', None) == 'invalidate'
        return {
            'some': 'state',
            'driver_experiments': ['exp1', 'exp2', 'exp3'],
            'force_stop_apps': {'force': 'stop', 'apps': []},
        }


@pytest.fixture(name='driver_support')
def _driver_support(mockserver):
    @mockserver.json_handler(
        '/taxi-driver-support/v1/internal/support_chat/summary/',
    )
    def _chat_summaty(request):
        return {'new_messages_count': 0, 'updated': '2020-07-13T19:46:25+0500'}


@pytest.fixture(name='driver_modes')
def _driver_modes(mockserver):
    class Handlers:
        @staticmethod
        @mockserver.json_handler('/driver-mode-subscription/v1/mode/reset')
        def _mode_reset(request):
            assert request.headers['Accept-language'] == 'ru_RU'
            return {
                'active_mode': 'orders',
                'active_mode_type': 'orders_type',
                'active_since': '2019-05-01T12:00:00+0300',
            }

        @staticmethod
        @mockserver.json_handler('/driver-ui-profile/v1/mode')
        def driver_ui_profile(request):
            return {
                'display_profile': 'needs_to_be_reset',
                'display_mode': 'needs_to_be_reset',
            }

    return Handlers()


@pytest.fixture(name='driver_orders')
def _driver_orders(mockserver):
    @mockserver.json_handler('/driver-orders/v1/driver/orders/has-finished')
    def _has_finished(request):
        return {'has_finished': True}


@pytest.fixture(name='unique_drivers')
def _unique_drivers(mockserver):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _retrieve(request):
        request_id = request.json['profile_id_in_set'][0]
        assert request_id in ['dbid_uuid', 'uber_dbid_uber_uuid']
        return {
            'uniques': [
                {
                    'park_driver_profile_id': request_id,
                    'data': {'unique_driver_id': 'udid'},
                },
            ],
        }


@pytest.fixture
def login_last_step_fixtures(
        driver_orders,
        fleet_synchronizer,
        driver_profiles_info,
        driver_profiles_courier,
        fleet_vehicles,
        driver_protocol,
        driver_support,
        unique_drivers,
        driver_modes,
        mock_fleet_parks_list,
):
    pass


@pytest.fixture(name='mock_driver_order_misc')
def _mock_driver_order_misc(mockserver):
    class Context:
        def __init__(self):
            self.drivers_on_order = []
            self.check_on_order = None

        def set_on_order(self, drivers):
            self.drivers_on_order = drivers

    context = Context()

    @mockserver.json_handler(
        '/driver-order-misc/driver-order-misc/v1/check-on-order',
    )
    def _check_on_order(request):
        return {'drivers': context.drivers_on_order}

    context.check_on_order = _check_on_order
    return context


@pytest.fixture(name='mock_driver_authorizer')
def _mock_driver_authorizer(mockserver):
    class Content:
        def __init__(self):
            self.expected_drivers = set()
            self.response_data = {'sessions': []}
            self.sessions_bulk_retrieve = None
            self.sessions_retrieve_count = 0

        def set_expected_drivers(self, drivers):
            self.expected_drivers = drivers

        def set_sessions_response(self, response_data):
            self.response_data = response_data

    context = Content()

    @mockserver.json_handler(
        '/driver-authorizer/driver/sessions/bulk_retrieve',
    )
    def _da_bulk_retreive(request):
        if context.expected_drivers:
            requested_drivers = {
                (d['client_id'], d['park_id'], d['uuid'])
                for d in request.json['drivers']
            }
            assert requested_drivers == context.expected_drivers

        context.sessions_retrieve_count += len(request.json['drivers'])
        return context.response_data

    context.sessions_bulk_retrieve = _da_bulk_retreive
    return context


@pytest.fixture(name='blackbox')
def _blackbox(mockserver):
    class Context:
        def __init__(self):
            self.response = {
                'error': 'OK',
                'oauth': {
                    'client_id': '60b5d28c9fe84959ad7fb68b405591e7',
                    'issue_time': '2011-11-16 00:00:00',
                    'scope': 'taxi-driver:all',
                    'uid': '3000062912',
                },
                'phones': [
                    {
                        'attributes': {
                            '102': '+72222222222',
                            '107': '1',
                            '108': '0',
                            '4': '1624266000',  # 2021-06-21T09:00:00
                        },
                        'id': '2',
                    },
                    {
                        'attributes': {
                            '102': '+73333333333',
                            '107': '0',
                            '108': '0',
                            '4': '1624266030',  # 2021-06-21T09:00:30
                        },
                        'id': '3',
                    },
                    {
                        'attributes': {
                            '102': '+74444444444',
                            '107': '0',
                            '108': '1',
                            '4': '1624266060',  # 2021-06-21T09:01:00
                        },
                        'id': '4',
                    },
                ],
                'status': {'id': 0, 'value': 'VALID'},
                'uid': {'value': '3000062912'},
            }

        def clear_phones(self):
            self.response['phones'] = []

        def set_neophonish(self):
            self.response['aliases'] = {'21': 'neophonish-uid'}

        def add_phone(
                self, phone, is_default, is_secured, time_confirmed, phone_id,
        ):
            new_phone = {
                'attributes': {
                    '107': str(int(is_default)),
                    '108': str(int(is_secured)),
                    '102': phone,
                    '4': time_confirmed,
                },
                'id': phone_id,
            }
            self.response['phones'].append(new_phone)

        def add_phones(self, phones):
            for phone in phones:
                self.add_phone(**phone)

        def set_uid(self, uid):
            self.response['oauth']['uid'] = uid
            self.response['uid']['value'] = uid

        def set_response(self, response):
            self.response = response

    context = Context()

    @mockserver.json_handler('/blackbox')
    def _blackbox(request):
        return context.response

    return context


@pytest.fixture(name='parks_certifications')
def _parks_certifications(mockserver):
    @mockserver.json_handler(
        '/parks-certifications/v1/parks/certifications/list',
    )
    def _parks_certifications(request):
        return {
            'certifications': [
                {'park_id': 'dbid1', 'is_certified': False},
                {'park_id': 'dbid2', 'is_certified': True},
                {'park_id': 'dbid3', 'is_certified': False},
                {'park_id': 'dbid4', 'is_certified': False},
                {'park_id': 'dbid5', 'is_certified': True},
                {'park_id': 'dbid6', 'is_certified': False},
                {'park_id': 'dbid7', 'is_certified': True},
            ],
        }


@pytest.fixture(name='mock_parks')
def _mock_parks(mockserver):
    class Context:
        def __init__(self):
            self.response = {}

        def set_response(self, response):
            self.response = response

    context = Context()

    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        assert 'driver' in request.json['query']
        response = {'profiles': []}
        if 'platform_uid' in request.json['query']['driver']:
            platform_uid = request.json['query']['driver']['platform_uid'][0]
            for profile in context.response['profiles']:
                if (
                        'platform_uid' in profile['driver']
                        and profile['driver']['platform_uid'] == platform_uid
                ):
                    response['profiles'].append(profile)
        else:
            phone = request.json['query']['driver']['phone'][0]
            phone_pd_id = phone + '_id'
            for profile in context.response['profiles']:
                if profile['driver']['phone_pd_ids'][0] == phone_pd_id:
                    response['profiles'].append(profile)
        return response

    return context


@pytest.fixture(name='driver_profiles_puid')
def _mock_driver_profiles_puid(mockserver):
    class Context:
        def __init__(self):
            self.response = {}

        def set_response(self, response):
            self.response = response

    context = Context()

    @mockserver.json_handler('/driver-profiles/v1/driver/platform-uid-bulk')
    def _driver_profiles_search(request):
        assert request.json.get('reason') == 'login'
        assert 'passport_type' in request.json
        return context.response

    return context


@pytest.fixture(name='yagr_position_store')
def _mock_yagr_position_store(mockserver):
    @mockserver.json_handler('/yagr-raw/service/v2/position/store')
    def _yagr_position_store(request):
        assert 'positions' in request.json
        required_fields = ['lat', 'lon', 'unix_timestamp', 'source']
        for position in request.json['positions']:
            for field in required_fields:
                assert field in position
        return mockserver.make_response(
            content_type='application/json',
            headers={'X-Polling-Power-Policy': ''},
        )

    return _yagr_position_store


@pytest.fixture
def passport_step_fixtures(
        load_json,
        blackbox,
        mock_fleet_parks_list,
        mock_parks,
        parks_certifications,
):
    mock_fleet_parks_list.set_parks(load_json('fleet_parks_response.json'))
    mock_parks.set_response(load_json('parks_response.json'))


@pytest.fixture
def passport_login_step_fixtures(
        load_json,
        blackbox,
        mock_fleet_parks_list,
        mock_parks,
        parks_certifications,
        fleet_vehicles,
        driver_protocol,
        driver_modes,
        driver_support,
        driver_profiles_info,
        unique_drivers,
        yagr_position_store,
):
    mock_parks.set_response(load_json('parks_response.json'))
