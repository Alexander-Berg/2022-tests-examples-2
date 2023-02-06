# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest
import yandex.maps.proto.driving_matrix.matrix_pb2 as ProtoMatrix

from shuttle_control_plugins import *  # noqa: F403 F401


def proto_matrix_support_columns(data):
    response = ProtoMatrix.Matrix()
    for row_data in data:
        row = response.row.add()
        for elem in row_data:
            item = row.element.add()
            item.summary.duration.value = elem['time']
            item.summary.duration.text = ''
            item.summary.distance.value = elem['distance']
            item.summary.distance.text = ''

    return response.SerializeToString()


@pytest.fixture(name='driver_trackstory', autouse=True)
def mock_driver_trackstory(mockserver, load_json):
    @mockserver.json_handler('/driver-trackstory/positions')
    def _mock_trackstory_positions(_):
        return {'results': []}


@pytest.fixture(name='cached_stops_route_info', autouse=True)
def mock_cached_stops_route_info(mockserver):
    class Context:
        def __init__(self):
            self.distance = 42
            self.time = 69
            self.mock = None

        def set_distance(self, distance):
            self.distance = distance

        def set_time(self, time):
            self.time = time

    ctx = Context()

    @mockserver.handler('/maps-matrix-router/v2/matrix')
    def _mock_matrix_router(request):
        nonlocal ctx

        dsts = len(
            request.query.get('dstll').split('~'),
        )  # assume srcll is ALWAYS equals to one
        data = []
        for _ in range(dsts):
            data.append({'distance': ctx.distance, 'time': ctx.time})

        return mockserver.make_response(
            response=proto_matrix_support_columns([data]),
            status=200,
            content_type='application/x-protobuf',
        )

    ctx.mock = _mock_matrix_router

    return ctx


@pytest.fixture(autouse=True)
def mock_coordinates_settings_exp(experiments3):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_coordinate_source_settings',
        consumers=['shuttle-control/coordinate_settings'],
        default_value={
            'position_freshness_duration_s': 63000000,
            'use_raw_coordinates': False,
        },
        clauses=[],
    )


@pytest.fixture
def mocks_experiments(experiments3):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_in_workshift',
        consumers=['shuttle-control/match_in_workshift'],
        default_value={'enabled': False},
        clauses=[],
    )


@pytest.fixture(autouse=True)
def mock_v2_route(mockserver):
    @mockserver.handler('/maps-router/v2/route')
    def _mock_router_route(request):
        return mockserver.make_response(
            status=200, content_type='application/x-protobuf',
        )
