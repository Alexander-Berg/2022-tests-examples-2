# pylint: disable=redefined-outer-name

import itertools

import pytest

from . import fixtures


@pytest.fixture
def mock_segment_dispatch_journal(
        mockserver, cargo_dispatch: fixtures.CargoDispatch,
):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/dispatch-journal')
    def mock_dispatch_journal(request):
        events, cursor = cargo_dispatch.read_segments_journal(
            request.json.get('cursor'),
        )
        return mockserver.make_response(
            headers={'X-Polling-Delay-Ms': '0'},
            json={'cursor': cursor, 'events': events},
        )

    return mock_dispatch_journal


@pytest.fixture
def mock_waybill_dispatch_journal(
        mockserver, cargo_dispatch: fixtures.CargoDispatch,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/dispatch-journal')
    def mock_dispatch_journal(request):
        events, cursor = cargo_dispatch.read_waybills_journal(
            request.json.get('cursor'),
        )
        return mockserver.make_response(
            headers={'X-Polling-Delay-Ms': '0'},
            json={'cursor': cursor, 'events': events},
        )

    return mock_dispatch_journal


@pytest.fixture
def mock_dispatch_waybill_info(
        mockserver, cargo_dispatch: fixtures.CargoDispatch,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def mock(request):
        waybill_ref = request.args['waybill_external_ref']
        if not cargo_dispatch.has_waybill(waybill_ref):
            return mockserver.make_response(
                status=404,
                json={'code': 'not found', 'message': 'waybill not found'},
            )
        return cargo_dispatch.get_waybill(waybill_ref)

    return mock


@pytest.fixture
def mock_dispatch_segment(mockserver, cargo_dispatch: fixtures.CargoDispatch):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    def mock_segment_info(request):
        segment_id = request.args['segment_id']
        if not cargo_dispatch.has_segment(segment_id):
            return mockserver.make_response(
                status=404,
                json={'code': 'not found', 'message': 'segment not found'},
            )
        return cargo_dispatch.get_segment(segment_id)

    return mock_segment_info


@pytest.fixture
def check_proposition(cargo_dispatch: fixtures.CargoDispatch):
    def proposition_checker(proposition):
        segment_points = set()
        for seg in proposition['segments']:
            segment_id = seg['segment_id']
            if not cargo_dispatch.has_segment(segment_id):
                raise RuntimeError(
                    f'Proposition reference to unknown segment {segment_id}',
                )
            segment = cargo_dispatch.get_segment(segment_id)
            for point in segment['segment']['points']:
                segment_points.add((segment_id, point['point_id']))

        points = set()
        for point in proposition['points']:
            segment_id = point['segment_id']
            point_id = point['point_id']
            key = segment_id, point_id
            if key not in segment_points:
                raise RuntimeError(f'Reference to unknown point {key}')
            if key in points:
                raise RuntimeError(f'Multiple refrences to point {key}')
            points.add(key)

        assert (
            segment_points == points
        ), 'Proposition points does not match segments'

    return proposition_checker


@pytest.fixture
def mock_waybill_propose(
        mockserver,
        propositions_manager: fixtures.PropositionsManager,
        check_proposition,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/propose')
    def mock_propose(request):
        check_proposition(request.json)
        propositions_manager.add_propositon(request.json)
        return {}

    return mock_propose


@pytest.fixture
def basic_mocks(mockserver):
    async def wrapper(*, employer_names=None, order_sources=None, polygon=None):
        @mockserver.json_handler('/typed-geoareas/v1/fetch_geoareas')
        def geoareas(request):
            return {
                'geoareas': [
                    {
                        'id': '1493739bdda6488f8de7bda1eddbbaf0',
                        'geoarea_type': 'p2p_shard',
                        'name': 'sadovoe',
                        'geometry': {
                            'type': 'Polygon',
                            'coordinates': [[
                                [37.57942199707031, 55.72846342126635],
                                [37.65804290771484, 55.72846342126635],
                                [37.65804290771484, 55.77367652953477],
                                [37.57942199707031, 55.77367652953477],
                                [37.57942199707031, 55.72846342126635],
                            ]],
                        },
                        'area': 0.002633872514211988,
                        'created': '2022-02-09T14:48:17.291+0000',
                    },
                ],
                'removed': [],
            }

        @mockserver.json_handler('/tags/v2/match')
        def tags(request):
            return {'entities': [{'id': 'driver1', 'tags': []}]}

        @mockserver.json_handler('/v1/order/search-limits')
        def search_limits(requests):
            return {
                'settings': [
                    {
                        'zone_id': 'moscow',
                        'tariff': tariff_class,
                        'limits': {
                            'free_preferred': 10,
                            'limit': 20,
                            'max_line_distance': 20000,
                            'max_route_distance': 4000,
                            'max_route_time': 600,
                            'pedestrian_max_search_radius': 2000,
                            'pedestrian_max_search_route_time': 1200,
                            'pedestrian_max_route_distance': 15000,
                            'pedestrian_max_route_time': 10800,
                            'transport_types': [
                                {
                                    'type': '__default__',
                                    'settings': {
                                        'max_search_radius': 2000,
                                        'max_search_route_time': 1200,
                                        'max_route_distance': 15000,
                                        'max_route_time': 10800,
                                    },
                                },
                            ],
                        },
                    }
                    for tariff_class in ('courier', 'express')
                ],
            }

        @mockserver.json_handler(
            '/v1/experiments',
        )
        def experiments(request):
            return {}

        @mockserver.json_handler('/monitoring/push')
        def monitoring_push(request):
            print(request)
            return {}
    return wrapper


@pytest.fixture
def mock_candidates(
        mockserver, candidates_context: fixtures.CandidatesContext,
):
    """
    A simple mock of candidates service.

    https://pages.github.yandex-team.ru/taxi/schemas/Taxi_Documentation/Uservices/Index/#candidates
    """

    class CandidatesMocks:
        @mockserver.json_handler('/candidates/order-search')
        def order_search(request):
            r = request.json
            assert 'point' in r
            candidates = []
            for dbid_uuid, candidate in candidates_context.candidates.items():
                if 'allowed_classes' in r:
                    matching_classes = set(r['allowed_classes']) & set(
                        candidate['tariff_classes'],
                    )
                    if not matching_classes:
                        continue

                candidates.append(
                    {
                        'position': candidate['position'],
                        'classes': candidate['tariff_classes'],
                        'id': candidate['id'],
                        'dbid': candidate['dbid'],
                        'uuid': candidate['uuid'],
                        'transport': candidate['transport'],
                    },
                )
            return {'candidates': candidates}

        @mockserver.json_handler('/candidates/profiles')
        def profiles(request):
            r = request.json
            assert 'data_keys' in r
            drivers = []
            for d in r['driver_ids']:
                dbid_uuid = d['dbid'] + '_' + d['uuid']
                if dbid_uuid not in candidates_context.candidates:
                    continue
                driver = {}
                for data_key in itertools.chain(
                        ['id', 'dbid', 'uuid', 'position'], r['data_keys'],
                ):
                    driver[data_key] = candidates_context.candidates[
                        dbid_uuid
                    ][data_key]
                drivers.append(driver)

            return {'drivers': drivers}

    return CandidatesMocks()


@pytest.fixture
def dummy_router(mockserver):
    @mockserver.json_handler('/yamaps/v2/route')
    def route(request):
        return ''

    @mockserver.json_handler('/yamaps/v2/matrix')
    def matrix(request):
        return ''


@pytest.fixture
def dummy_pedestrian_router(mockserver):
    @mockserver.json_handler('/yamaps/pedestrian/v2/route')
    def pedestrian_route(request):
        return ''

    @mockserver.json_handler('/yamaps/pedestrian/v2/matrix')
    def pedestrian_matrix(request):
        return ''


@pytest.fixture
def dummy_masstransit_router(mockserver):
    @mockserver.json_handler('/yamaps/masstransit/v2/route')
    def masstransit_route(request):
        return ''

    @mockserver.json_handler('/yamaps/masstransit/v2/matrix')
    def masstransit_matrix(request):
        return ''
