# pylint: disable=import-error

import pytest
from yamaps_tools import driving as yamaps_driving  # noqa: F401 C5521
from yamaps_tools import (
    driving_matrix as yamaps_driving_matrix,
)  # noqa: F401 C5521
import yandex.maps.proto.driving_matrix.matrix_pb2 as ProtoMatrix


async def test_eta(taxi_eats_eta, mockserver):
    @mockserver.handler('/maps-router/v2/summary')
    def _mock_route_jams(request):
        data = {'time': 2500, 'distance': 2500}
        return mockserver.make_response(
            response=yamaps_driving.proto_driving_summary(data),
            status=200,
            content_type='application/x-protobuf',
        )

    for _ in range(1, 3):
        response = await taxi_eats_eta.post(
            'v1/eta',
            json={
                'sources': [[37.683000, 55.774000]],
                'destination': [37.656000, 55.764000],
                'type': 'taxi',
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            'etas': [{'distance': 2500.0, 'time': 2500.0}],
        }

        assert _mock_route_jams.times_called == 1


@pytest.mark.config(EATS_ETA_ROUTING={'bulk': True, 'cache_ttl_seconds': 300})
async def test_eta_bulk(taxi_eats_eta, mockserver):
    shared = {
        'response': [
            {'distance': 10.0, 'time': 2500.0},
            {'distance': 20.0, 'time': 2500.0},
            {'distance': 30.0, 'time': 2500.0},
        ],
    }

    @mockserver.handler('/maps-matrix-router/v2/matrix')
    def _mock_route_jams(request):
        data = shared['response']
        return mockserver.make_response(
            response=yamaps_driving_matrix.proto_matrix(data),
            status=200,
            content_type='application/x-protobuf',
        )

    response = await taxi_eats_eta.post(
        'v1/eta',
        json={
            'sources': [[1, 55.774000], [2, 55.774000], [3, 55.774000]],
            'destination': [37.656000, 55.764000],
            'type': 'taxi',
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'etas': [
            {'distance': 10.0, 'time': 2500.0},
            {'distance': 20.0, 'time': 2500.0},
            {'distance': 30.0, 'time': 2500.0},
        ],
    }

    shared = {'response': [{'distance': 200.0, 'time': 2500.0}]}

    response = await taxi_eats_eta.post(
        'v1/eta',
        json={
            'sources': [[1, 55.774000], [20, 55.774000], [3, 55.774000]],
            'destination': [37.656000, 55.764000],
            'type': 'taxi',
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'etas': [
            {'distance': 10.0, 'time': 2500.0},
            {'distance': 200.0, 'time': 2500.0},
            {'distance': 30.0, 'time': 2500.0},
        ],
    }

    assert _mock_route_jams.times_called == 2


@pytest.mark.config(EATS_ETA_ROUTING={'bulk': True, 'cache_ttl_seconds': 300})
async def test_eta_bulk_500(taxi_eats_eta, mockserver):
    router_response = [
        {'distance': 10.0, 'time': 2500.0},
        {},
        {'distance': 30.0, 'time': 2500.0},
    ]

    sources = [[1, 55.774000], [2, 55.774000], [3, 55.774000]]
    destination = [37.656000, 55.764000]

    @mockserver.handler('/maps-matrix-router/v2/matrix')
    def _mock_route_jams(_):
        response = ProtoMatrix.Matrix()
        for elem in router_response:
            row = response.row.add()
            item = row.element.add()
            if 'time' in elem:
                item.summary.duration.value = elem['time']
                item.summary.duration.text = ''
            if 'distance' in elem:
                item.summary.distance.value = elem['distance']
                item.summary.distance.text = ''
        return mockserver.make_response(
            response=response.SerializeToString(),
            status=200,
            content_type='application/x-protobuf',
        )

    response = await taxi_eats_eta.post(
        'v1/eta',
        json={'sources': sources, 'destination': destination, 'type': 'taxi'},
    )

    assert response.status_code == 500

    assert _mock_route_jams.times_called == 1

    response = await taxi_eats_eta.post(
        'v1/eta',
        json={
            'sources': sources[::2],
            'destination': destination,
            'type': 'taxi',
        },
    )

    assert response.status_code == 200

    assert _mock_route_jams.times_called == 1

    assert response.json() == {
        'etas': [
            {'distance': 10.0, 'time': 2500.0},
            {'distance': 30.0, 'time': 2500.0},
        ],
    }
