# pylint: disable=wildcard-import, unused-wildcard-import, import-error, C0411
# pylint: disable=redefined-outer-name
import json
import uuid

import bson
from lookup_plugins import *  # noqa: F403 F401
import pytest

from tests_lookup import mock_candidates
from tests_lookup import order_core


@pytest.fixture(name='metadata_storage_json', autouse=True)
def _metadata_storage(mockserver):
    @mockserver.json_handler('/metadata-storage-json/v2/metadata/retrieve')
    def _metadata_for_order(request):
        return mockserver.make_response('', 404)


@pytest.fixture(name='candidates', autouse=True)
def _candidates(mockserver, load_json):
    class Context:
        @staticmethod
        @mockserver.json_handler('/candidates/order-search')
        def order_search(request):
            return mock_candidates.make_candidates()

        @staticmethod
        @mockserver.json_handler('/candidates/profiles')
        def profiles(request):
            driver = json.loads(request.get_data())['driver_ids'][0]
            return {
                'drivers': [
                    {
                        'uuid': driver['uuid'],
                        'dbid': driver['dbid'],
                        'position': [0, 0],
                        'classes': ['econom', 'business'],
                        'car_model': 'BMW X2',
                    },
                ],
            }

        @staticmethod
        @mockserver.json_handler('/candidates/order-satisfy')
        def order_satisfy(request):
            assert 'driver_ids' in request.json
            return mockserver.make_response('', 500)

    return Context()


@pytest.fixture(name='driver_scoring', autouse=True)
def _lookup_ordering(mockserver, load_json):
    class Context:
        @staticmethod
        @mockserver.json_handler('/driver_scoring/v2/score-candidates')
        def ordering(request):
            # do minimal sort by time
            body = json.loads(request.get_data())['request']
            candidates = [
                {
                    'id': candidate['id'],
                    'score': candidate['route_info']['time'],
                }
                for candidate in body['candidates']
            ]
            return {
                'candidates': sorted(
                    candidates, key=lambda candidate: candidate['score'],
                ),
            }

    return Context()


@pytest.fixture(name='trackstory_position', autouse=True)
def _trackstory_position(mockserver, load_json):
    class Context:
        @staticmethod
        @mockserver.json_handler('/driver-trackstory/position')
        def trackstory_position(request):
            return {
                'position': {
                    'direction': 214.5,
                    'lat': 55.4183979995,
                    'lon': 37.8954151234,
                    'speed': 35.4,
                    'timestamp': 1533817820,
                },
                'type': 'adjusted',
            }

    return Context()


@pytest.fixture(name='parks_profile_list', autouse=True)
def _parks_profile_list(mockserver, load_json):
    class Context:
        @staticmethod
        @mockserver.json_handler('/parks/driver-profiles/list')
        def parks_profile_list(request):
            body = json.loads(request.get_data())
            query = body.get('query')
            fields = [
                'taximeter_version',
                'hiring_details',
                'first_name',
                'middle_name',
                'last_name',
                'phone_pd_ids',
                'car_id',
                'id',
            ]
            driver_profile = body.get('fields').get('driver_profile')
            if len(fields) == len(driver_profile):
                assert driver_profile == fields
            else:
                assert driver_profile == fields[1:]
            fields = ['provider_config', 'id']
            park = body.get('fields').get('park')
            if len(fields) == len(park):
                assert park == fields
            else:
                assert park == fields[1:]
            fields = ['color', 'id']
            car = body.get('fields').get('car')
            if len(fields) == len(car):
                assert car == fields
            else:
                assert car == fields[1:]

            uu_id = query.get('park').get('driver_profile').get('id')[0]
            db_id = query.get('park').get('id')
            car_id = str(uuid.uuid4())
            return {
                'driver_profiles': [
                    {
                        'driver_profile': {
                            'id': uu_id,
                            'car_id': car_id,
                            'taximeter_version': '9.07 (1234)',
                            'first_name': 'Maxim',
                            'middle_name': 'Dmitrievich',
                            'last_name': 'Urev',
                            'phone_pd_ids': ['+799999999'],
                            'hiring_details': {
                                'hiring_type': 'type',
                                'hiring_date': '2020',
                            },
                        },
                        'car': {'id': car_id, 'color': 'red'},
                    },
                ],
                'limit': 1,
                'offset': 0,
                'parks': [
                    {
                        'id': db_id,
                        'provider_config': {
                            'yandex': {
                                'apikey': str(uuid.uuid4()),
                                'clid': '12345',
                                'version': 'сервис',
                            },
                        },
                    },
                ],
                'total': 1,
            }

    return Context()


@pytest.fixture(name='maps_router_jams', autouse=True)
def _maps_router_jams(mockserver, load_json):
    class Context:
        @staticmethod
        @mockserver.json_handler('/maps-router/v2/route')
        def route_jams(request):
            assert request.url.find('dir') != -1
            return mockserver.make_response('', 500)

    return Context()


@pytest.fixture(name='personal', autouse=True)
def _personal(mockserver, load_json):
    class Context:
        @staticmethod
        @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
        def personal_license_retrieve(request):
            body = json.loads(request.get_data())
            license_id = body['id']
            license_number = 'number-' + license_id
            return {'id': license_id, 'value': license_number}

        @staticmethod
        @mockserver.json_handler('/personal/v1/phones/retrieve')
        def personal_phone_retrieve(request):
            body = json.loads(request.get_data())
            phone_pd_id = body['id']
            phone = 'number-' + phone_pd_id
            return {'id': phone_pd_id, 'value': phone}

    return Context()


@pytest.fixture(name='freezer', autouse=True)
def _freezer(mockserver, load_json):
    class Context:
        @staticmethod
        @mockserver.json_handler('/driver-freeze/freeze')
        def freeze(request):
            return {'freezed': True}

        @staticmethod
        @mockserver.json_handler('/driver-freeze/defreeze')
        def _defreeze(request):
            assert False, 'should not be called'

    return Context()


@pytest.fixture(name='candidate-meta', autouse=True)
def _candidate_meta(mockserver, load_json):
    class Context:
        @staticmethod
        @mockserver.json_handler('/candidate-meta/v1/candidate/meta/update')
        def meta_update(request):
            return mockserver.make_response()

    return Context()


@pytest.fixture(name='contractor-orders-multioffer', autouse=True)
def _contracot_orders_multioffer(mockserver):
    @mockserver.json_handler(
        '/contractor-orders-multioffer/v1/contractor-for-order',
    )
    def _contracot_orders_multioffer_handler(request):
        return mockserver.make_response('{"message": "irrelevant"}', 200)


@pytest.fixture(name='manual-dispatch', autouse=True)
def _manual_dispatch(mockserver):
    class Context:
        @staticmethod
        @mockserver.json_handler('/manual-dispatch/v1/lookup')
        def v1_lookup(request):
            body = json.loads(request.get_data())
            assert body.get('manual_dispatch') is None
            return mockserver.make_response(200, json={})

    return Context()


@pytest.fixture(name='cars-catalog', autouse=True)
def _cars_catalog(mockserver, load_json):
    class Context:
        @staticmethod
        @mockserver.json_handler('cars-catalog/api/v1/cars/get_colors')
        def get_colors(request):
            data = {
                'items': [
                    {
                        'data': {
                            'raw_color': 'red',
                            'normalized_color': 'Red',
                            'color_code': 'red_code',
                        },
                        'revision': 1,
                    },
                    {
                        'data': {
                            'raw_color': 'yellow',
                            'normalized_color': 'Yellow',
                            'color_code': 'yellow_code',
                        },
                        'revision': 1,
                    },
                ],
            }
            return mockserver.make_response(200, json=data)

        @staticmethod
        @mockserver.json_handler('cars-catalog/api/v1/cars/get_color')
        def get_color(request):
            data = {'normalized_color': 'Green', 'color_code': 'green_code'}
            return mockserver.make_response(200, json=data)

    return Context()


@pytest.fixture(name='excluded-drivers', autouse=True)
def _excluded_drivers(mockserver, load_json):
    class Context:
        @staticmethod
        @mockserver.json_handler(
            '/excluded-drivers/excluded-drivers/v1/drivers/list',
        )
        def get_excluded_drivers(request):
            data = {
                'excluded_drivers_pd_ids': [
                    'excluded_license_0',
                    'excluded_license_1',
                    'excluded_license_2',
                    'excluded_license_3',
                ],
            }
            return mockserver.make_response(200, json=data)

    return Context()


@pytest.fixture(name='driver-tags', autouse=True)
def _driver_tags(mockserver, load_json):
    class Context:
        @staticmethod
        @mockserver.json_handler('/driver-tags/v1/drivers/retrieve/profile')
        def get_excluded_drivers(request):
            data = {'tags': ['tag0', 'tag1', 'tag2', 'tag3']}
            return mockserver.make_response(200, json=data)

    return Context()


@pytest.fixture(autouse=True, name='driver_app_profiles')
def driver_app_profile_fixture(mockserver):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_get_driver_app(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': request.json['id_in_set'][0],
                    'data': {'metrica_device_id': '112233'},
                },
            ],
        }

    return _mock_get_driver_app


@pytest.fixture(autouse=True, name='driver-metrics')
def _driver_metrics_fixture(mockserver):
    class Context:
        @staticmethod
        @mockserver.json_handler('/driver-metrics/v2/lookup_info/')
        def mock_v2_lookup_info(request):
            return mockserver.make_response('', 500)

    return Context()


@pytest.fixture(autouse=True, name='autoaccept')
def _autoaccept_fixture(mockserver):
    class Context:
        @staticmethod
        @mockserver.json_handler('/autoaccept/v1/decide-autoaccept')
        def mock_decide_autoaccept(request):
            return mockserver.make_response('', 500)

    return Context()


@pytest.fixture(autouse=True, name='order_core')
def _order_core_fixture(mockserver, load_json):
    order_core_context = order_core.OrderCoreContext()
    order_core_context.set_get_fields_response(load_json('order_proc.json'))

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_core_get(request):
        result = {
            'document': order_core_context.get_fields_response,
            'revision': {'version': 1},
        }
        return mockserver.make_response(bson.BSON.encode(result), 200)

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/new_driver_found',
    )
    def _order_core_event(request):
        order_core_context.set_driver_found(
            bson.BSON.decode(request.get_data())['extra_update']['$push'][
                'candidates'
            ],
        )
        return mockserver.make_response('', 200)

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _order_core_set(request):
        return mockserver.make_response('', 200)

    return order_core_context


@pytest.fixture(autouse=True, name='fleet_parks')
def _fleet_parks_fixture(mockserver, load_json):
    class Context:
        @staticmethod
        @mockserver.json_handler('/fleet-parks/v1/parks/list')
        def mock_parks_list(request):
            return mockserver.make_response('', 500)

    return Context()


@pytest.fixture(name='acquire_candidate')
def _acquire_candidate(stq_runner, order_core):
    async def perform(order, expect_fail=False):
        order_core.set_get_fields_response(order)
        order_core.set_driver_found(None)
        await stq_runner.lookup_contractor.call(
            task_id='order_id',
            args=[],
            kwargs={'order_id': 'id'},
            expect_fail=expect_fail,
        )
        return order_core.driver_found

    return perform


@pytest.fixture(
    autouse=True,
    scope='function',
    params=[
        pytest.param(
            'agglomeration_settings',
            marks=[
                pytest.mark.experiments3(
                    filename='agglomeration_settings.json',
                ),
            ],
        ),
    ],
)
def _exp_agglomeration_settings():
    pass
