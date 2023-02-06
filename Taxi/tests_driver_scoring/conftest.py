# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name
from typing import List
from typing import Tuple

from driver_scoring_plugins import *  # noqa: F403 F401
from fbs.driver_priority.handlers.v1_priority_values import (
    Chunk as DriverPriorityChunk,
)
from fbs.driver_priority.handlers.v1_priority_values import (
    Priority as DriverPriority,
)
from fbs.driver_priority.handlers.v1_priority_values import (
    Response as DriverPriorityResponse,
)
from fbs.driver_priority.handlers.v1_priority_values import (
    Value as DriverPriorityValue,
)
import flatbuffers
import pytest
from reposition_matcher.fbs.v1.service.match_orders_drivers import (
    CheckResult as RepositionMatcherCheckResult,
)
from reposition_matcher.fbs.v1.service.match_orders_drivers import (
    OkResponse as RepositionMatcherResponse,
)
from reposition_matcher.fbs.v1.service.match_orders_drivers import (
    Request as RepositionMatcherRequest,
)

from tests_driver_scoring import dispatch_settings


class MatchOrdersDriversContext:
    def __init__(self):
        self.tags_list = {}
        self.expected_request = None

    def set_tags_list(self, tags_list):
        self.tags_list = tags_list

    def set_expected_request(self, expected_request):
        self.expected_request = expected_request

    def reset(self):
        self.tags_list = {}
        self.expected_request = None


@pytest.fixture(name='match_orders_drivers_mocks')
def _match_orders_drivers_mocks(mockserver):
    context = MatchOrdersDriversContext()

    def _parse_request(data, expected_request):
        request = RepositionMatcherRequest.Request.GetRootAsRequest(data, 0)
        result = {}

        def fetch_vector(vec, length):
            return [vec(i) for i in range(length)]

        orders = []
        for i in range(request.OrdersLength()):
            order_fbs = request.Orders(i)
            orders.append(
                {
                    'id': order_fbs.Id(),
                    'zone': order_fbs.Zone(),
                    'allowed_classes': fetch_vector(
                        order_fbs.AllowedClasses,
                        order_fbs.AllowedClassesLength(),
                    ),
                },
            )

        drivers = []
        for i in range(request.DriversLength()):
            driver_fbs = request.Drivers(i)
            drivers.append(
                {'dbid': driver_fbs.Dbid(), 'uuid': driver_fbs.Uuid()},
            )

        check_requests = []
        for i in range(0, request.CheckRequestsLength()):
            check_request_fbs = request.CheckRequests(i)

            check_request = {
                'driver_id': check_request_fbs.DriverId(),
                'order_id': check_request_fbs.OrderId(),
            }

            pickup_route_info = check_request_fbs.PickupRouteInfo()

            if pickup_route_info:
                check_request['pickup_route_info'] = {
                    'time': pickup_route_info.Time(),
                    'distance': pickup_route_info.Distance(),
                }

            check_requests.append(check_request)

        result = {
            'orders': orders,
            'drivers': drivers,
            'check_requests': check_requests,
        }

        if expected_request is not None:

            def sort_by_str_repr(values):
                return sorted(values, key=str)

            def sort_check_requests(check_requests, orders, drivers):
                values = [
                    {
                        'order_id': orders[check_request['order_id']]['id'],
                        'uuid': drivers[check_request['driver_id']]['uuid'],
                        'dbid': drivers[check_request['driver_id']]['dbid'],
                        'pickup_route_info': check_request.get(
                            'pickup_route_info',
                        ),
                    }
                    for check_request in check_requests
                ]
                return sorted(
                    values,
                    key=lambda d: '_'.join(
                        [
                            d['order_id'].decode(),
                            d['uuid'].decode(),
                            d['dbid'].decode(),
                            str(
                                d.get('pickup_route_info', {}).get(
                                    'time', 'null',
                                ),
                            ),
                            str(
                                d.get('pickup_route_info', {}).get(
                                    'distance', 'null',
                                ),
                            ),
                        ],
                    ),
                )

            assert result.keys() == expected_request.keys()
            assert sort_by_str_repr(result['orders']) == sort_by_str_repr(
                expected_request['orders'],
            )
            assert sort_by_str_repr(result['drivers']) == sort_by_str_repr(
                expected_request['drivers'],
            )
            assert (
                sort_check_requests(
                    result['check_requests'],
                    result['orders'],
                    result['drivers'],
                )
                == sort_check_requests(
                    expected_request['check_requests'],
                    expected_request['orders'],
                    expected_request['drivers'],
                )
            )

        return result

    def _build_match_orders_drivers_response(request, tags):
        builder = flatbuffers.Builder(0)
        check_results = []

        for req in request['check_requests']:
            driver_id = req['driver_id']
            order_id = req['order_id']

            driver = request['drivers'][driver_id]
            order = request['orders'][order_id]
            tag = tags.get((driver['dbid'], driver['uuid'], order['id']))
            if tag:
                mode = tag.get('mode', '')
                suitable = tag.get('suitable', True)
                score = tag.get('score', None)
            else:
                continue

            mode_fbs = builder.CreateString(mode)

            RepositionMatcherCheckResult.CheckResultStart(builder)
            RepositionMatcherCheckResult.CheckResultAddDriverId(
                builder, driver_id,
            )
            RepositionMatcherCheckResult.CheckResultAddOrderId(
                builder, order_id,
            )
            RepositionMatcherCheckResult.CheckResultAddMode(builder, mode_fbs)
            RepositionMatcherCheckResult.CheckResultAddSuitable(
                builder, suitable,
            )
            if score:
                RepositionMatcherCheckResult.CheckResultAddScore(
                    builder, score,
                )

            check_results.append(
                RepositionMatcherCheckResult.CheckResultEnd(builder),
            )

        RepositionMatcherResponse.OkResponseStartCheckResultsVector(
            builder, len(check_results),
        )
        for result in check_results:
            builder.PrependUOffsetTRelative(result)
        check_results = builder.EndVector(len(check_results))

        RepositionMatcherResponse.OkResponseStart(builder)
        RepositionMatcherResponse.OkResponseAddCheckResults(
            builder, check_results,
        )
        response = RepositionMatcherResponse.OkResponseEnd(builder)
        builder.Finish(response)

        return builder.Output()

    @mockserver.handler('/reposition-matcher/v1/service/match_orders_drivers')
    def _mock_match_orders_drivers(request):
        req = _parse_request(request.get_data(), context.expected_request)
        response = _build_match_orders_drivers_response(req, context.tags_list)
        return mockserver.make_response(
            response,
            content_type='application/x-flatbuffers',
            charset='utf-8',
        )

    return context


@pytest.fixture(name='match_orders_drivers_fixture', autouse=True)
def _match_orders_drivers_fixture(match_orders_drivers_mocks, request):
    match_orders_drivers_mocks.reset()

    marker_results = request.node.get_closest_marker(
        'reposition_matcher_check_results',
    )
    if marker_results:
        match_orders_drivers_mocks.set_tags_list(marker_results.args[0])

    marker_request = request.node.get_closest_marker(
        'expect_reposition_matcher_check_request',
    )
    if marker_request:
        match_orders_drivers_mocks.set_expected_request(marker_request.args[0])

    yield match_orders_drivers_mocks

    match_orders_drivers_mocks.reset()


class BulkMatchOrdersDriversContext:
    def __init__(self):
        self.tags_list = {}
        self.expected_request = None

    def set_tags_list(self, tags_list):
        self.tags_list = tags_list

    def set_expected_request(self, expected_request):
        self.expected_request = expected_request

    def reset(self):
        self.tags_list = {}
        self.expected_request = None


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'reposition_matcher_check_results: reposition matcher check results',
    )
    config.addinivalue_line(
        'markers',
        'expect_reposition_matcher_check_request: '
        'expected reposition matcher check request',
    )
    config.addinivalue_line(
        'markers', 'managed_client_qos: managed client qos config',
    )
    config.addinivalue_line(
        'markers',
        'passenger_tags_entities: dict containing the only entities that'
        ' should be recognized by `/passenger-tags/v2/match` mock',
    )
    config.addinivalue_line(
        'markers',
        'eats_tags_entities: dict containing the only entities that'
        ' should be recognized by `/eats-tags/v2/match` mock',
    )


@pytest.fixture(name='candidates', autouse=True)
def mock_candidates(mockserver):
    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        data = request.json
        assert 'driver_ids' in data
        assert 'data_keys' in data
        assert data['data_keys'] == ['classes', 'car_id']
        drivers = []
        for i, driver_id in enumerate(data['driver_ids']):
            driver = {
                'dbid': driver_id['dbid'],
                'uuid': driver_id['uuid'],
                'position': [39.59568, 52.568001],
                'classes': ['econom', 'comfortplus', 'business'],
            }
            if i % 2 == 0:
                driver['car_id'] = 'car' + str(i)
            drivers.append(driver)
        return {'drivers': drivers}


@pytest.fixture(name='umlaas-dispatch', autouse=True)
def mock_umlaas_dispatch(mockserver):
    @mockserver.json_handler(
        '/umlaas-dispatch/umlaas-dispatch/v1/candidates-bonuses',
    )
    def _bonuses(request):
        data = request.json
        assert 'requests' in data
        candidates = []
        for req in data['requests']:
            assert 'order' in req
            for field in ('source', 'allowed_classes'):
                assert field in req['order']
            assert 'candidates' in req

            for candidate in req['candidates']:
                for field in ('id', 'position', 'route_info', 'classes'):
                    assert field in candidate
                candidates.append(
                    {
                        'id': candidate['id'],
                        'bonuses': [
                            {'name': 'test_ml_bonus', 'value': 10.0},
                            {'name': 'backoffer', 'value': -23.0},
                        ],
                    },
                )

        return {'responses': [{'candidates': candidates}]}


@pytest.fixture(name='tags_v2_index_fixture', autouse=True)
def _tags_v2_index_fixture(request, tags_index_mocks):
    marker = request.node.get_closest_marker('tags_v2_index')
    if marker and ('topic_relations' not in marker.kwargs):
        topic_relations = []
        tags_list = marker.kwargs.get('tags_list')
        for _, _, tag in tags_list:
            topic_relations.append(('driver_scoring', tag))

        tags_index_mocks.set_tags_list(tags_list, topic_relations)


@pytest.fixture(name='tags_v1_topics_items', autouse=True)
def mock_tags_v1_topic_items(mockserver):
    @mockserver.json_handler('/tags/v1/topics/items')
    def _mock_items(_):
        return {'responses': []}


@pytest.fixture(name='passenger-tags', autouse=True)
def mock_passenger_tags(mockserver, request):
    marker = request.node.get_closest_marker('passenger_tags_entities')

    if marker:
        # `passenger-tags` is mocked explicitly, we should check
        # if entities exist in mocked "database"
        user_id_entities = marker.kwargs['user_id_entities']
        user_phone_id_entities = marker.kwargs['user_phone_id_entities']

        @mockserver.json_handler('/passenger-tags/v2/match')
        def _profiles(request):
            data = request.json
            assert 'entities' in data

            result_entities = []
            for entity in data['entities']:
                tags = []
                for match in entity['match']:
                    if (
                            match['type'] == 'user_id'
                            and match['value'] in user_id_entities
                    ):
                        tags.extend(user_id_entities[match['value']])
                    elif (
                        match['type'] == 'user_phone_id'
                        and match['value'] in user_phone_id_entities
                    ):
                        tags.extend(user_phone_id_entities[match['value']])

                if tags:
                    result_entities.append({'id': entity['id'], 'tags': tags})
            return {'entities': result_entities}

    else:
        # `passenger-tags` is not mocked explicitly, we should return
        # some tags for whatever `user_id` and `user_phone_id` we get
        @mockserver.json_handler('/passenger-tags/v2/match')
        def _profiles(request):
            data = request.json
            assert 'entities' in data

            result_entities = []
            for entity in data['entities']:
                tags = []
                for match in entity['match']:
                    if match['type'] == 'user_id':
                        tags += ['some_user_tag_1', 'some_user_tag_2']
                    elif match['type'] == 'user_phone_id':
                        tags += ['some_user_tag_3', 'some_user_tag_4']

                if tags:
                    result_entities.append({'id': entity['id'], 'tags': tags})
            return {'entities': result_entities}


@pytest.fixture(name='eats_tags')
def mock_eats_tags(mockserver, request):
    marker = request.node.get_closest_marker('eats_tags_entities')

    if marker:
        # `eats-tags` is mocked explicitly
        user_id_entities = marker.kwargs.get('user_id_entities', {})
        personal_phone_id_entities = marker.kwargs.get(
            'personal_phone_id_entities', {},
        )
        place_id_entities = marker.kwargs.get('place_id_entities', {})

        @mockserver.json_handler('/eats-tags/v2/match')
        def _profiles(request):
            data = request.json
            assert 'entities' in data

            result_entities = []
            for entity in data['entities']:
                tags = []
                for match in entity['match']:
                    if (
                            match['type'] == 'user_id'
                            and match['value'] in user_id_entities
                    ):
                        tags.extend(user_id_entities[match['value']])
                    elif (
                        match['type'] == 'personal_phone_id'
                        and match['value'] in personal_phone_id_entities
                    ):
                        tags.extend(personal_phone_id_entities[match['value']])
                    elif (
                        match['type'] == 'place_id'
                        and match['value'] in place_id_entities
                    ):
                        tags.extend(place_id_entities[match['value']])

                if tags:
                    result_entities.append({'id': entity['id'], 'tags': tags})
            return {'entities': result_entities}

    else:
        # `eats-tags` is not mocked explicitly
        @mockserver.json_handler('/eats-tags/v2/match')
        def _profiles(request):
            data = request.json
            assert 'entities' in data

            result_entities = []
            for entity in data['entities']:
                tags = []
                for match in entity['match']:
                    if match['type'] == 'user_id':
                        tags += ['some_user_tag_1', 'some_user_tag_2']
                    elif match['type'] == 'personal_phone_id':
                        tags += ['some_user_tag_3', 'some_user_tag_4']
                    elif match['type'] == 'place_id':
                        tags += ['some_place_tag_1', 'some_place_tag_2']

                if tags:
                    result_entities.append({'id': entity['id'], 'tags': tags})
            return {'entities': result_entities}


class DriverPriorityContext:
    def __init__(self):
        self.priorities = {}

    def set_priority(
            self, dbid: str, uuid: str, priorities: List[Tuple[str, int]],
    ):
        self.priorities[f'{dbid}_{uuid}'] = priorities


@pytest.fixture(name='driver_priority_values_mock', autouse=True)
def _driver_priority_values_mock(mockserver):
    context = DriverPriorityContext()

    @mockserver.handler('/driver-priority/v1/priority/values')
    def _mock_priority_values(request):
        req = request.json

        builder = flatbuffers.Builder(0)

        chunks = []
        for chunk in req['chunks']:
            priorities = []
            for driver in chunk['drivers']:
                dbid_uuid = f'{driver["dbid"]}_{driver["uuid"]}'

                values = []
                if dbid_uuid in context.priorities:
                    for priority in context.priorities[dbid_uuid]:
                        name = builder.CreateString(priority[0])
                        DriverPriorityValue.ValueStart(builder)
                        DriverPriorityValue.ValueAddPriorityName(builder, name)
                        DriverPriorityValue.ValueAddValue(builder, priority[1])
                        values.append(DriverPriorityValue.ValueEnd(builder))

                DriverPriority.PriorityStartValuesVector(builder, len(values))
                for value in values:
                    builder.PrependUOffsetTRelative(value)
                values = builder.EndVector(len(values))

                dbid_uuid_offset = builder.CreateString(dbid_uuid)
                DriverPriority.PriorityStart(builder)
                DriverPriority.PriorityAddProfile(builder, dbid_uuid_offset)
                DriverPriority.PriorityAddValues(builder, values)
                priorities.append(DriverPriority.PriorityEnd(builder))

            DriverPriorityChunk.ChunkStartPrioritiesVector(
                builder, len(priorities),
            )
            for priority in reversed(priorities):
                builder.PrependUOffsetTRelative(priority)
            priorities = builder.EndVector(len(priorities))

            DriverPriorityChunk.ChunkStart(builder)
            DriverPriorityChunk.ChunkAddPriorities(builder, priorities)
            chunks.append(DriverPriorityChunk.ChunkEnd(builder))

        DriverPriorityResponse.ResponseStartChunksVector(builder, len(chunks))
        for chunk in reversed(chunks):
            builder.PrependUOffsetTRelative(chunk)
        chunks = builder.EndVector(len(chunks))

        DriverPriorityResponse.ResponseStart(builder)
        DriverPriorityResponse.ResponseAddChunks(builder, chunks)
        response = DriverPriorityResponse.ResponseEnd(builder)

        builder.Finish(response)

        return mockserver.make_response(
            builder.Output(),
            content_type='application/x-flatbuffers',
            charset='utf-8',
        )

    return context


@pytest.fixture(name='managed_clients_qos_fixture', autouse=True)
def _managed_clients_qos(request, experiments3):
    marker = request.node.get_closest_marker('managed_client_qos')
    clauses = []
    default_client_qos = [
        {
            'service': 'umlaas-dispatch',
            'handle': '/umlaas-dispatch/v1/candidates-bonuses',
            'enabled': True,
            'disable_on_fallbacks': [
                'handler.umlaas-dispatch.v1.candidates-bonuses-post.fallback',
            ],
        },
    ]

    def add_clause(client_qos):
        clauses.append(
            {
                'title': client_qos['service'],
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'service',
                                    'arg_type': 'string',
                                    'value': client_qos['service'],
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'arg_name': 'handle',
                                    'arg_type': 'string',
                                    'value': client_qos['handle'],
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {
                    'enabled': client_qos.get('enabled', True),
                    'disable_on_fallbacks': client_qos.get(
                        'disable_on_fallbacks', [],
                    ),
                },
            },
        )

    if marker and marker.args:
        for qos in marker.args[0]:
            add_clause(qos)

    for qos in default_client_qos:
        add_clause(qos)

    experiments3.add_config(
        consumers=['driver-scoring/managed-clients'],
        name='driver_scoring_managed_clients_qos',
        match={
            'enabled': True,
            'consumers': [{'name': 'driver-scoring/managed-clients'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=clauses,
        default_value={
            'enabled': True,
            'disable_on_fallbacks': ['global-fallback'],
        },
    )


_DISPATCH_SETTINGS_MARKER = 'dispatch_settings'


@pytest.fixture(name='dispatch_settings_fixture')
def _dispatch_settings_fixture(dispatch_settings_mocks, request, autouse=True):
    marker = request.node.get_closest_marker(_DISPATCH_SETTINGS_MARKER)
    if marker:
        dispatch_settings_mocks.set_settings(**marker.kwargs)
    else:
        dispatch_settings_mocks.set_settings(
            settings=dispatch_settings.DISPATCH_SETTINGS,
        )

    yield dispatch_settings_mocks

    dispatch_settings_mocks.reset()


@pytest.fixture(name='autoaccept', autouse=True)
def mock_autoaccept(mockserver):
    @mockserver.json_handler('/autoaccept/v1/decide-autoaccept-bulk')
    def _decide_autoaccept(request):
        response = {'orders': []}
        for order in request.json['orders']:
            response_order = {'order_id': order['order_id'], 'candidates': []}
            for candidate in order['candidates']:
                response_order['candidates'].append(
                    {
                        'park_id': candidate['dbid'],
                        'driver_profile_id': candidate['uuid'],
                        'autoaccept': False,
                    },
                )
            response['orders'].append(response_order)
        return response


@pytest.fixture(
    autouse=True,
    scope='function',
    params=[
        pytest.param(
            'driver_scoring_time_dist_weights',
            marks=[
                pytest.mark.experiments3(
                    filename='experiments3_time_dist_weights.json',
                ),
            ],
        ),
    ],
)
def _exp_driver_scoring_time_dist_weights():
    pass
