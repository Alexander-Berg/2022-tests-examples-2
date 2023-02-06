# pylint: disable=wildcard-import, import-error
import datetime
import json

import pytest

from candidates_plugins import *  # noqa: F403 F401, I100, I202

import tests_candidates.busy_drivers
import tests_candidates.categories
import tests_candidates.combo_contractors
import tests_candidates.driver_positions
import tests_candidates.driver_status
import tests_candidates.route_info


@pytest.fixture(name='driver_positions')
def _driver_positions(taxi_candidates, redis_store, testpoint, now):
    async def _publish(positions):
        await tests_candidates.driver_positions.publish(
            taxi_candidates, positions, redis_store, testpoint, now,
        )

    return _publish


@pytest.fixture(name='driver_positions_route_predicted')
def _driver_positions_route_predicted(
        taxi_candidates, redis_store, testpoint, now,
):
    async def _publish(positions):
        await tests_candidates.driver_positions.publish_route_predicted(
            taxi_candidates, positions, redis_store, testpoint, now,
        )

    return _publish


@pytest.fixture(name='chain_busy_drivers', autouse=True)
def _chain_busy_drivers_bulk(mockserver):
    store_drivers = []

    @mockserver.handler('/busy-drivers/chain_busy_drivers_bulk')
    def _mock_chain_busy_drivers_bulk(request):
        params = request.args
        assert 'chunk_id' in params
        data = store_drivers if int(params['chunk_id']) == 0 else []
        timestamp = (
            datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000
        )
        return mockserver.make_response(
            response=tests_candidates.busy_drivers.fbs_chain_busy_drivers(
                data, timestamp,
            ),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    @mockserver.handler('/busy-drivers/v2/chain_busy_drivers_bulk')
    def _mock_v2_chain_busy_drivers_bulk(request):
        params = request.args
        assert 'chunk_idx' in params
        assert 'chunk_count' in params
        data = store_drivers if int(params['chunk_idx']) == 0 else []
        timestamp = datetime.datetime.now(datetime.timezone.utc).timestamp()
        return mockserver.make_response(
            response=tests_candidates.busy_drivers.fbs_chain_busy_drivers(
                data, timestamp,
            ),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    def _store(drivers):
        for driver in drivers:
            store_drivers.append(
                {
                    'driver_id': driver['driver_id'],
                    'order_id': driver.get('order_id', 'unknown'),
                    'destination': driver['destination'],
                    'left_time': int(driver['left_time']),
                    'left_distance': int(driver['left_distance']),
                    'approximate': driver.get('approximate', False),
                    'flags': driver.get('flags', '0'),
                },
            )

    return _store


@pytest.fixture(autouse=True)
def classifier_request(mockserver):
    @mockserver.json_handler('/classifier/v1/classifiers/updates')
    def _mock_tariffs_updates(request):
        return {
            'limit': 100,
            'classifiers': [
                {'classifier_id': 'Москва', 'is_allowing': True},
                {'classifier_id': 'Екатеринбург', 'is_allowing': False},
            ],
        }

    @mockserver.json_handler('/classifier/v1/classifier-tariffs/updates')
    def _mock_classifiers_updates(request):
        return {
            'cursor': {'id': 2},
            'limit': 100,
            'tariffs': [
                {
                    'classifier_id': 'Москва',
                    'is_allowing': True,
                    'tariff_id': 'econom',
                },
                {
                    'classifier_id': 'Москва',
                    'is_allowing': True,
                    'tariff_id': 'vip',
                },
            ],
        }

    @mockserver.json_handler('/classifier/v1/classification-rules/updates')
    def _mock_classification_rules_updates(request):
        return {'classification_rules': [], 'limit': 100}

    @mockserver.json_handler('/classifier/v1/cars-first-order-date/updates')
    def _mock_cars_first_order_date_updates(request):
        return {'cars_first_order_date': [], 'limit': 100}

    @mockserver.json_handler('/classifier/v2/classifier-exceptions/updates')
    def _mock_classifier_exceptions_updates_v2(request):
        return {'classifier_exceptions_V2': [], 'limit': 100}


@pytest.fixture(autouse=True)
def cars_catalog_request(mockserver):
    @mockserver.json_handler('/cars-catalog/api/v1/cars/get_brand_models')
    def _mock_brand_models(request):
        assert request.method == 'GET'
        data = {
            'items': [
                {
                    'revision': 0,
                    'data': {
                        'raw_brand': 'BMW',
                        'raw_model': 'X2',
                        'normalized_mark_code': 'BMW',
                        'normalized_model_code': 'X2',
                        'corrected_model': 'BMW X2',
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'raw_brand': 'BMW',
                        'raw_model': 'X5',
                        'normalized_mark_code': 'BMW',
                        'normalized_model_code': 'X5',
                        'corrected_model': 'BMW X5',
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'raw_brand': 'Audi',
                        'raw_model': 'A5',
                        'normalized_mark_code': 'AUDI',
                        'normalized_model_code': 'A5',
                        'corrected_model': 'Audi A5',
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'raw_brand': 'Газель',
                        'raw_model': 'Next',
                        'normalized_mark_code': 'Газель',
                        'normalized_model_code': 'Next',
                        'corrected_model': 'Газель Next',
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'raw_brand': 'Kia',
                        'raw_model': 'Rio',
                        'normalized_mark_code': 'Kia',
                        'normalized_model_code': 'Rio',
                        'corrected_model': 'Kia Rio',
                    },
                },
            ],
        }
        return mockserver.make_response(response=json.dumps(data))

    @mockserver.json_handler('/cars-catalog/api/v1/cars/get_prices')
    def _mock_prices(request):
        assert request.method == 'GET'
        data = {
            'items': [
                {
                    'revision': 0,
                    'data': {
                        'normalized_mark_code': 'BMW',
                        'normalized_model_code': 'X2',
                        'car_year': 2018,
                        'car_age': 1,
                        'car_price': 4624647,
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'normalized_mark_code': 'BMW',
                        'normalized_model_code': 'X5',
                        'car_year': 2018,
                        'car_age': 1,
                        'car_price': 4624647,
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'normalized_mark_code': 'AUDI',
                        'normalized_model_code': 'A5',
                        'car_year': 2018,
                        'car_age': 1,
                        'car_price': 4624647,
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'normalized_mark_code': 'Газель',
                        'normalized_model_code': 'Next',
                        'car_year': 2015,
                        'car_age': 5,
                        'car_price': 463647,
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'normalized_mark_code': 'Kia',
                        'normalized_model_code': 'Rio',
                        'car_year': 2017,
                        'car_age': 3,
                        'car_price': 663647,
                    },
                },
            ],
        }
        return mockserver.make_response(response=json.dumps(data))


@pytest.fixture(autouse=True)
def driver_freeze_request(mockserver, load_binary):
    @mockserver.json_handler('/driver-freeze/frozen')
    def _mock_frozen(request):
        return mockserver.make_response(
            response=load_binary('empty_response.fb.gz'),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )


@pytest.fixture(autouse=True)
def driver_categories_api_services(request, mockserver, load_json):
    @mockserver.handler('/driver-categories-api/v1/drivers/categories/bulk')
    def _mock_categories(request):
        request_json = json.loads(request.get_data())
        result = tests_candidates.categories.fbs_categories(
            load_json('driver_categories_api_response.json'),
        )
        headers = {
            'Content-Type': 'application/octet-stream',
            'X-YaTaxi-Cars-Revision': '1',
            'X-YaTaxi-Parks-Revision': '1',
            'X-YaTaxi-Drivers-Revision': '1',
        }
        if request_json['revisions']['parks'] == '1':
            result = tests_candidates.categories.fbs_categories(
                {
                    'blocked_by_driver': [],
                    'cars': [],
                    'parks': [],
                    'revisions': {'parks': '1', 'cars': '1', 'drivers': '1'},
                },
            )
        return mockserver.make_response(response=result, headers=headers)

    @mockserver.handler('/driver-categories-api/v2/driver/restrictions')
    def _mock_drivers_load_single(request):
        data = load_json('active_drivers_restrictions.json')

        params = request.args
        assert 'park_id' in params
        assert 'driver_id' in params

        park_id = params['park_id']
        driver_id = params['driver_id']
        dbid_uuid = park_id + '_' + driver_id
        categories = []
        if dbid_uuid in data:
            categories = data[dbid_uuid]
        response = {'categories': []}
        for category in categories:
            response['categories'].append({'name': category})

        return mockserver.make_response(response=json.dumps(response))

    @mockserver.handler('/driver-categories-api/v2/aggregation/drivers/load')
    def _mock_drivers_load_bulk(request):

        data = load_json('active_drivers_restrictions_load.json')

        categories = []
        missing = []
        for park in request.json['parks']:
            park_id = park['park_id']
            drivers = park['drivers']
            for driver_id in drivers:
                dbid_uuid = park_id + '_' + driver_id
                if dbid_uuid in data:
                    categories.append(data[dbid_uuid])
                else:
                    missing.append(
                        {'park_id': park_id, 'driver_id': driver_id},
                    )
        drivers_revision = '1'
        response = {
            'categories': categories,
            'missing': missing,
            'drivers_revision': drivers_revision,
        }
        headers = {'X-YaTaxi-Drivers-Revision': drivers_revision}
        return mockserver.make_response(
            response=json.dumps(response), headers=headers,
        )

    @mockserver.handler('/driver-categories-api/v2/aggregation/drivers/update')
    def _mock_drivers_update_bulk(request):
        result = tests_candidates.categories.fbs_categories_drivers(
            load_json('active_drivers_restrictions_update.json'),
        )
        headers = {
            'Content-Type': 'application/octet-stream',
            'X-YaTaxi-Drivers-Revision': '1',
        }
        return mockserver.make_response(response=result, headers=headers)

    @mockserver.handler('/driver-categories-api/v2/car/categories')
    def _mock_cars_load_single(request):
        data = load_json('active_cars_categories.json')

        params = request.args
        assert 'park_id' in params
        assert 'car_id' in params

        park_id = params['park_id']
        car_id = params['car_id']
        dbid_uuid = park_id + '_' + car_id
        categories = []
        if dbid_uuid in data:
            categories = data[dbid_uuid]
        response = {'categories': []}
        for category in categories:
            response['categories'].append({'name': category})

        return mockserver.make_response(response=json.dumps(response))

    @mockserver.handler('/driver-categories-api/v2/aggregation/cars/load')
    def _mock_cars_load_bulk(request):

        data = load_json('active_cars_categories_load.json')

        categories = []
        missing = []
        for park in request.json['parks']:
            park_id = park['park_id']
            cars = park['cars']
            for car_id in cars:
                dbid_uuid = park_id + '_' + car_id
                if dbid_uuid in data:
                    categories.append(data[dbid_uuid])
                else:
                    missing.append({'park_id': park_id, 'car_id': car_id})
        cars_revision = '1'
        response = {
            'categories': categories,
            'missing': missing,
            'cars_revision': cars_revision,
        }
        headers = {'X-YaTaxi-Cars-Revision': cars_revision}
        return mockserver.make_response(
            response=json.dumps(response), headers=headers,
        )

    @mockserver.handler('/driver-categories-api/v2/aggregation/cars/update')
    def _mock_cars_update_bulk(request):
        result = tests_candidates.categories.fbs_categories_cars(
            load_json('active_cars_categories_update.json'),
        )
        headers = {
            'Content-Type': 'application/octet-stream',
            'X-YaTaxi-Cars-Revision': '1',
        }
        return mockserver.make_response(response=result, headers=headers)

    @mockserver.handler('/driver-categories-api/v2/aggregation/parks/update')
    def _mock_parks_update_bulk(request):
        result = tests_candidates.categories.fbs_categories_parks(
            load_json('active_parks_categories_update.json'),
        )
        headers = {
            'Content-Type': 'application/octet-stream',
            'X-YaTaxi-Parks-Revision': '1',
        }
        return mockserver.make_response(response=result, headers=headers)


@pytest.fixture(autouse=True)
def dispatch_airport_request(mockserver):
    @mockserver.json_handler('/dispatch-airport/v1/active-drivers-queues')
    def _active_drivers_queues(request):
        return {
            'queues': [
                {
                    'tariff': 'econom',
                    'active_drivers': [
                        {
                            'dbid_uuid': 'dbid0_uuid0',
                            'queued': '2019-06-10T13:02:20Z',
                        },
                    ],
                },
            ],
        }


@pytest.fixture(autouse=True)
def driver_status_request(request, mockserver, load_json):
    @mockserver.handler('/driver-status/v2/blocks/updates')
    def _mock_blocks(request):
        blocks = tests_candidates.driver_status.load_blocks_mock(
            load_json, 'driver_status_blocks_response.json',
        )
        result = tests_candidates.driver_status.build_blocks_fbs(
            blocks['revision'],
            blocks['blocks'],
            request.query.get('compression', 'gzip'),
        )
        return mockserver.make_response(
            response=result,
            headers={'Content-Type': 'application/x-flatbuffers'},
            status=200,
        )

    @mockserver.handler('/driver-status/v2/orders/updates')
    def _mock_orders(request):
        orders_input = tests_candidates.driver_status.load_drv_orders_mock(
            load_json, 'driver_status_orders_response.json',
        )
        response_data = tests_candidates.driver_status.build_orders_fbs(
            orders_input['revision'],
            orders_input['orders'],
            request.query.get('compression', 'gzip'),
        )
        return mockserver.make_response(
            response=response_data,
            headers={'Content-Type': 'application/x-flatbuffers'},
            status=200,
        )

    @mockserver.handler('/driver-status/v2/statuses/updates')
    def _mock_driver_statuses(request):
        statuses = tests_candidates.driver_status.load_drv_statuses_mock(
            load_json, 'driver_status_statuses_response.json',
        )
        result = tests_candidates.driver_status.build_statuses_fbs(
            statuses['revision'],
            statuses['statuses'],
            request.query.get('compression', 'gzip'),
        )
        return mockserver.make_response(
            response=result,
            headers={'Content-Type': 'application/x-flatbuffers'},
            status=200,
        )


@pytest.fixture(autouse=True)
def driver_weariness_request(mockserver):
    @mockserver.json_handler('/driver-weariness/v1/tired-drivers')
    def _tired_drivers(request):
        return {'items': []}


class ApiOverData:
    def __init__(self, data):
        self.data = data if data else []

    def updates(self, last_revision=None):
        if not last_revision:
            return self.data
        return [x for x in self.data if x['revision'] > last_revision]

    def get(self, **kwargs):
        return next(
            iter(
                [
                    x
                    for x in self.data
                    if all([x.get(k) == kwargs[k] for k in kwargs])
                ],
            ),
            None,
        )


@pytest.fixture(autouse=True)
def mock_virtual_tariffs(mockserver):
    @mockserver.json_handler(
        '/virtual-tariffs/v1/special-requirements/updates',
    )
    def _special_requirements_updates(request):
        cursor = 'string'
        if not request.query:
            return {
                'special_requirements': [
                    {
                        'id': 'wrong_requirement',
                        'requirements': [
                            {
                                'field': 'foo',
                                'operation': 'bar',
                                'arguments': [{'value': 'ыыыы'}],
                            },
                        ],
                    },
                    {
                        'id': 'tag_group1',
                        'requirements': [
                            {
                                'field': 'Tags',
                                'operation': 'ContainsAll',
                                'arguments': [
                                    {'value': 'tag1'},
                                    {'value': 'tag2'},
                                    {'value': 'tag3'},
                                ],
                            },
                        ],
                    },
                    {
                        'id': 'tag_group2',
                        'requirements': [
                            {
                                'field': 'Tags',
                                'operation': 'ContainsAll',
                                'arguments': [
                                    {'value': 'tag1'},
                                    {'value': 'tag2'},
                                    {'value': 'tag3'},
                                    {'value': 'tag4'},
                                ],
                            },
                        ],
                    },
                ],
                'cursor': cursor,
                'has_more_records': True,
            }
        assert request.query['cursor'] == cursor
        return {
            'special_requirements': [],
            'cursor': cursor,
            'has_more_records': False,
        }

    return _special_requirements_updates


@pytest.fixture(autouse=True)
def parks_activation_request(request, mockserver, load_json):
    marker = request.node.get_closest_marker('parks_activation')
    data = marker.args[0] if marker else load_json('parks_activation.json')
    parks_activation = ApiOverData(data)

    @mockserver.json_handler('/parks-activation/v1/parks/activation/updates')
    def _mock_updates(request):
        revision = request.json['last_known_revision']
        parks = parks_activation.updates(revision)
        if parks:
            return {
                'last_revision': parks[-1]['revision'],
                'last_modified': '1970-01-15T03:56:07.000',
                'parks_activation': parks,
            }

        return {'parks_activation': []}


@pytest.fixture(autouse=True)
def mock_active_claims(mockserver):
    @mockserver.json_handler('/cargo-claims/v1/claims/list/performer-lookup')
    def _claims_bulk_performer_lookup_in_progress(request):
        return {'claims': []}

    return _claims_bulk_performer_lookup_in_progress


@pytest.fixture(autouse=True)
def contractor_transport_request(request, mockserver, load_json):
    marker = request.node.get_closest_marker('contractors_transport')
    data = marker.args[0] if marker else load_json('contractors_default.json')

    @mockserver.json_handler(
        '/contractor-transport/v1/transport-active/updates',
    )
    def _mock_transport_active(request):
        assert request.method == 'GET'
        if request.query.get('cursor') == data['cursor']:
            return {'contractors_transport': [], 'cursor': '1234567_4'}
        return mockserver.make_response(response=json.dumps(data))

    @mockserver.json_handler(
        '/contractor-transport/v1/transport-active/retrieve-by-contractor-id',
    )
    def _mock_retrieve_by_contractor_id(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            response=json.dumps({'contractors_transport': []}),
        )


@pytest.fixture(autouse=True)
def quality_control_cpp(request, mockserver, load_json):
    marker = request.node.get_closest_marker('quality_control_cpp')
    data = marker.args[0] if marker else load_json('quality_control_cpp.json')
    entity_to_object = dict(
        {
            x['data']['id']: x['object_id']
            for x in data
            if x.get('data', {}).get('id')
        },
    )

    qc_cpp = ApiOverData(data)

    @mockserver.json_handler('/quality-control-cpp/v1/blocks/updates')
    def _mock_updates(request):
        revision = request.query.get('last_known_revision')
        entities = qc_cpp.updates(revision)
        headers = {'X-Polling-Delay-Ms': '0'}
        data = {'entities': []}
        if entities:
            data['entities'] = entities
            data['last_revision'] = entities[-1]['revision']
            data['last_modified'] = datetime.datetime.utcnow()

        return mockserver.make_response(
            response=json.dumps(data), headers=headers,
        )

    @mockserver.json_handler('/quality-control-cpp/v1/blocks')
    def _mock_blocks(request):
        entities_by_id = []
        for entity_id in request.json['entity_id_in_set']:
            item = dict(entity_id=entity_id)
            object_id = entity_to_object.get(entity_id)
            item['entities'] = (
                [qc_cpp.get(object_id=object_id)] if object_id else []
            )
            entities_by_id.append(item)
        return mockserver.make_response(
            response=json.dumps(dict(entities_by_id=entities_by_id)),
        )


def pytest_collection_modifyitems(config, items):
    for item in items:
        item.add_marker(pytest.mark.geoareas(filename='geoareas.json'))
        item.add_marker(
            pytest.mark.geoareas(sg_filename='subvention_geoareas.json'),
        )
        item.add_marker(pytest.mark.tariffs(filename='tariffs.json'))


@pytest.fixture(autouse=True)
def driver_lessons_progress_bulk(mockserver):
    @mockserver.json_handler(
        '/driver-lessons'
        '/internal/driver-lessons/v1/lessons-progress/bulk-retrieve',
    )
    def _lessons_progress_mock(_request):
        return {'lessons_progress': []}


@pytest.fixture(autouse=True)
def driver_lessons_progress_upd(mockserver):
    @mockserver.json_handler(
        '/driver-lessons/internal/driver-lessons/v1/lessons-progress/updates',
    )
    def _lessons_progress_mock(_request):
        return {'lessons_progress': [], 'revision': None}


@pytest.fixture(autouse=True)
def driver_lessons_progress_lr(mockserver):
    @mockserver.json_handler(
        '/driver-lessons'
        '/internal/driver-lessons/v1/lessons-progress/latest-revision',
    )
    def _lessons_latest_revision(_request):
        return {'revision': None}


@pytest.fixture(autouse=True)
def eats_shifts_journal(mockserver):
    @mockserver.json_handler(
        '/eats-performer-shifts/internal/eats-performer-shifts/v1/courier-shift-states/updates',  # noqa: E501
    )
    def _eats_shifts_journal(request):
        return {'data': {'shifts': [], 'cursor': '1'}}


@pytest.fixture(autouse=True)
def grocery_shifts_journal(mockserver):
    @mockserver.json_handler(
        '/grocery-wms/api/external/courier_shifts/v1/updates',
    )
    def _eats_shifts_journal(request):
        return {'data': {'shifts': [], 'cursor': '1'}}


@pytest.fixture(autouse=True)
def eats_couriers_bindings_journal(mockserver):
    @mockserver.json_handler(
        '/driver-profiles/v1/eats-couriers-binding/updates',
    )
    def _eats_couriers_bindings_journal(request):
        return {'binding': [], 'last_known_revision': '1', 'has_next': False}


@pytest.fixture(autouse=True)
def selfemployed_profiles(request, mockserver):
    marker = request.node.get_closest_marker('selfemployed_profiles')
    profiles_map = marker.args[0] if marker else {}
    empty_data = {}

    @mockserver.json_handler('/selfemployed-fns-replica/v1/profiles/retrieve')
    def _selfemployed_profiles(request):
        id_in_set = request.json['id_in_set']
        data = {
            'profiles': [
                {
                    'data': profiles_map.get(dbid_uuid, empty_data),
                    'revision': f'rev_{dbid_uuid}',
                    'park_contractor_profile_id': dbid_uuid,
                }
                for dbid_uuid in id_in_set
            ],
        }
        return mockserver.make_response(
            json=data, headers={'X-Polling-Delay-Ms': '0'},
        )

    @mockserver.json_handler('/selfemployed-fns-replica/v1/profiles/updates')
    def _selfemployed_profiles_updates(request):
        return mockserver.make_response(
            json={'profiles': []}, headers={'X-Polling-Delay-Ms': '0'},
        )


@pytest.fixture(autouse=True)
def nalogru_bonds(request, mockserver):
    marker = request.node.get_closest_marker('nalogru_bonds')
    bonds_map = marker.args[0] if marker else {}

    @mockserver.json_handler(
        '/selfemployed-fns-replica/v1/bindings/retrieve-by-inn',
    )
    def _nalogru_bonds(request):
        id_in_set = request.json['inn_pd_id_in_set']
        data = {
            'bindings_by_inns': [
                {
                    'inn_pd_id': inn_pd_id,
                    'bindings': (
                        [
                            {
                                'data': bonds_map[inn_pd_id],
                                'phone_pd_id': f'phone_{inn_pd_id}',
                                'revision': f'rev_{inn_pd_id}',
                            },
                        ]
                        if inn_pd_id in bonds_map
                        else [{}]
                    ),
                }
                for inn_pd_id in id_in_set
            ],
        }
        return mockserver.make_response(
            json=data, headers={'X-Polling-Delay-Ms': '0'},
        )

    @mockserver.json_handler('/selfemployed-fns-replica/v1/bindings/updates')
    def _nalogru_bonds_updates(request):
        return mockserver.make_response(
            json={'bindings': []}, headers={'X-Polling-Delay-Ms': '0'},
        )


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'contractors_transport: contractors transport',
    )
    config.addinivalue_line('markers', 'quality_control_cpp: quality control')
    config.addinivalue_line(
        'markers', 'selfemployed_profiles: selfemployed profiles',
    )
    config.addinivalue_line('markers', 'nalogru_bonds: nalogru bonds')


@pytest.fixture(autouse=True)
def mock_blocklist_updates(mockserver):
    @mockserver.json_handler('/blocklist/v1/blocks/updates')
    def _mock(request):
        headers = {'X-Polling-Delay-Ms': '0'}
        data = {'blocks': [], 'last_revision': '0', 'last_modified': '0'}
        return mockserver.make_response(
            response=json.dumps(data), headers=headers,
        )


@pytest.fixture(autouse=True)
def mock_blocklist_predicates(mockserver):
    @mockserver.json_handler('/blocklist/internal/blocklist/v1/predicates')
    def _mock(request):
        return {'predicates': []}


@pytest.fixture(name='combo_contractors', autouse=True)
def _combo_contractors(mockserver):
    stored_contractors = []

    @mockserver.handler('/combo-contractors/contractors')
    def _mock_contractors(request):
        params = request.args
        assert 'chunk_idx' in params
        assert 'chunk_count' in params
        assert int(params['chunk_count']) > 0
        assert int(params['chunk_idx']) < int(params['chunk_count'])
        data = stored_contractors if int(params['chunk_idx']) == 0 else []
        return mockserver.make_response(
            response=tests_candidates.combo_contractors.fbs_combo_contractors(
                data, datetime.datetime.utcnow(),
            ),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    @mockserver.handler('/combo-contractors/v1/match')
    def _mock_v1_match(request):
        assert 'contractors' in request.json
        contractors = request.json['contractors']
        ids = set()
        for contractor in contractors:
            ids.add(contractor['dbid_uuid'])
        result = []
        for contractor in stored_contractors:
            if contractor['dbid_uuid'] in ids:
                result.append(
                    {
                        'dbid_uuid': contractor['dbid_uuid'],
                        'combo_info': {'active': True},
                    },
                )
        return mockserver.make_response(
            response=json.dumps({'contractors': result}),
        )

    def _store(contractors):
        for contractor in contractors:
            stored_contractors.append({'dbid_uuid': contractor['dbid_uuid']})

    return _store


@pytest.fixture(name='contractor_orders_multioffer', autouse=True)
def _contractor_orders_multioffer_mock(mockserver):
    multioffers = []

    @mockserver.json_handler(
        '/contractor-orders-multioffer/internal/v1/multioffer/updates',
    )
    def _mock(request):
        return {
            'last_updated_at': '2020-07-28T09:07:12+0000',
            'multioffers': multioffers,
        }

    def _store(new_multioffers):
        multioffers.clear()
        multioffers.extend(new_multioffers)

    return _store


@pytest.fixture(name='dispatch_settings', autouse=True)
def _dispatch_settings_mock(dispatch_settings_mocks):
    saved_settings = [
        {
            'zone_name': '__default__',
            'tariff_name': '__default__base__',
            'parameters': [
                {
                    'values': {
                        'ORDER_CHAIN_MAX_LINE_DISTANCE': 2000,
                        'ORDER_CHAIN_MAX_ROUTE_DISTANCE': 3000,
                        'ORDER_CHAIN_MAX_ROUTE_TIME': 300,
                        'ORDER_CHAIN_PAX_EXCHANGE_TIME': 120,
                        'PEDESTRIAN_DISABLED': True,
                    },
                },
            ],
        },
    ]

    dispatch_settings_mocks.set_settings(saved_settings)

    def _set_settings(settings):
        dispatch_settings_mocks.set_settings(settings)

    return _set_settings


@pytest.fixture(name='deptrans_driver_status', autouse=True)
def _deptrans_driver_status_mock(mockserver):
    class Context:
        def __init__(self):
            self.status = None

        def update_status(self, status):
            self.status = status

    context = Context()

    @mockserver.json_handler(
        '/deptrans-driver-status/internal/v3/profiles/updates',
    )
    def _mock_deptrans_profiles_updates(request):
        if context.status:
            return mockserver.make_response(
                json={
                    'cursor': 'some_value',
                    'binding': [
                        {
                            'license_pd_id': 'AB0253_id',
                            'status': context.status,
                        },
                    ],
                },
            )
        return mockserver.make_response(
            json={'cursor': 'some_value', 'binding': []},
        )

    return context


@pytest.fixture(autouse=True)
def mock_orders_guarantee(mockserver):
    @mockserver.json_handler('/fleet-orders-guarantee/v1/guaranteed/list')
    def _mock(request):
        return {'orders': []}


@pytest.fixture(name='route_infos')
def _route_info(taxi_candidates, redis_store, testpoint, now):
    async def _publish(geohash):
        await tests_candidates.route_info.publish(
            taxi_candidates, geohash, redis_store, testpoint, now,
        )

    return _publish
