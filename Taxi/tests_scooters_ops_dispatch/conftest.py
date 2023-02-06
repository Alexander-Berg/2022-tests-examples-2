# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from scooters_ops_dispatch_plugins import *  # noqa: F403 F401

from tests_scooters_ops_dispatch import bicycle_proto as proto


class Context:
    def __init__(self):
        self.handler = None

    def times_called(self):
        return self.handler.times_called


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'router_request_info: Routing request and response info',
    )


@pytest.fixture(name='mock_router_bicycle', autouse=True)
def mock_router_bicycle(request, load_json, mockserver):
    router_request_info = request.node.get_closest_marker(
        'router_request_info',
    )

    router_info_data = {}
    default_info = True
    if router_request_info:
        default_info = False
        if router_request_info.kwargs['file']:
            router_info_data = load_json(router_request_info.kwargs['file'])
        else:
            for req_info in router_request_info.args[0]:
                router_info_data.update(req_info)
    else:
        router_info = {}
        router_info['time'] = 500
        router_info['distance'] = 1000
        router_info_data['default'] = router_info

    @mockserver.handler('/maps-bicycle-router/v2/summary')
    def _mock_router_bicycle(request):
        assert request.method == 'GET'

        segments = request.query.get('rll').split('~')

        fst = [float(e) for e in segments[0].split(',')]
        snd = [float(e) for e in segments[1].split(',')]

        assert len(fst) == 2 and len(snd) == 2

        router_info = {}
        if default_info:
            router_info = router_info_data['default']
        else:
            router_info = router_info_data[
                '{}:{}'.format(segments[0], segments[1])
            ]

        return mockserver.make_response(
            status=200,
            content_type='application/x-protobuf',
            response=proto.proto_bicycle_summary_time_distance(
                time=router_info['time'], distance=router_info['distance'],
            ),
        )


@pytest.fixture(name='mock_router_matrix', autouse=True)
def mock_router_matrix(request, load_json, mockserver):
    context = Context()

    router_request_info = request.node.get_closest_marker(
        'router_request_info',
    )
    router_info_data = {}
    default_info = True
    if router_request_info:
        default_info = False
        if router_request_info.kwargs['file']:
            router_info_data = load_json(router_request_info.kwargs['file'])
        else:
            for req_info in router_request_info.args[0]:
                router_info_data.update(req_info)
    else:
        router_info = {}
        router_info['time'] = 500
        router_info['distance'] = 1000
        router_info_data['default'] = router_info

    @mockserver.handler('/maps-bicycle-matrix-router/v2/matrix')
    @mockserver.handler('/maps-matrix-router/v2/matrix')
    def _mock_router_matrix(request):
        assert request.method == 'GET'
        srcs = request.query.get('srcll').split('~')
        dsts = request.query.get('dstll').split('~')

        src_size = len(srcs)
        dst_size = len(dsts)

        response_data = []
        if default_info:
            for _ in range(0, src_size * dst_size):
                response_data.append(router_info_data['default'])
        else:
            for srs in srcs:
                for dst in dsts:
                    response_data.append(
                        router_info_data['{}:{}'.format(srs, dst)],
                    )

        response = None
        if request.query.get('vehicle_type') == 'scooter':
            response = proto.proto_bicycle_matrix(
                response_data, src_size, dst_size,
            )
        else:
            response = proto.proto_car_matrix(
                response_data, src_size, dst_size,
            )

        return mockserver.make_response(
            status=200,
            content_type='application/x-protobuf',
            response=response,
        )

    context.handler = _mock_router_matrix

    return context
