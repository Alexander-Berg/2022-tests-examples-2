import logging

from taxi.graph.external.graph2 import pygraph

import yatest.common

logger = logging.getLogger("test_logger")

roadGraph = pygraph.create_road_graph(
    road_graph_filename=yatest.common.binary_path(
        'taxi/graph/data/graph3/road_graph.fb'),
    rtree_filename=yatest.common.binary_path(
        'taxi/graph/data/graph3/rtree.fb'),
)


def test_point_segment_polyline():
    point = pygraph.Point(37.0, 55.0)
    point.lat = 37.5
    point.lon = 55.2
    assert point.lat == 37.5
    assert point.lon == 55.2

    another_point = pygraph.Point(37.2, 55.5)
    segment = pygraph.Segment(point, another_point)
    segment.start = another_point
    segment.end = point

    polyline = pygraph.Polyline()
    polyline.reservePoints(5)
    for step in range(5):
        newpoint = pygraph.Point(37.0 + 0.1 * step, 55.0 + 0.1 * step ** 2)
        polyline.addPoint(newpoint)

    assert polyline.segmentsSize() == 4
    assert polyline.pointsSize() == 5

    point = polyline.pointAt(2)
    assert point.lon == 37.2
    assert point.lat == 55.4

    segment = polyline.segmentAt(2)
    assert segment.start.lon == 37.2
    assert segment.start.lat == 55.4
    assert segment.end.lon == 37.3
    assert segment.end.lat == 55.9


def test_edge_functions():
    position = roadGraph.getNearestEdgePoint(37.577730, 55.814286, 200)
    assert position.edgeId == 123751
    assert round(position.position, 3) == 0.084
    assert not position.isUndefined()

    coords = roadGraph.getCoords(position)
    assert round(coords.lon, 6) == 37.577455
    assert round(coords.lat, 6) == 55.814239


def test_reverse_edge():

    targetEdgeId = 123751

    reverseEdgeId = roadGraph.getReverseEdgeId(targetEdgeId)
    assert not reverseEdgeId


def test_edge_data():

    targetEdgeId = 123751

    data = roadGraph.getEdgeData(targetEdgeId)
    assert data
    assert not data.speedLimit
    assert data.speed == 14.0
    assert round(data.length, 8) == 1063.19995117
    assert data.category == 3
    assert data.passable
    assert not data.isTollRoad
    assert data.access == 10

    geometry = roadGraph.getEdgeGeometry(targetEdgeId)
    assert geometry.segmentsSize() == 10


def test_positions_and_coords():
    position = roadGraph.getNearestEdgePoint(37.577730, 55.814286, 200)

    posOnGraph = roadGraph.getPositionOnGraph(position)
    assert posOnGraph.edgeId == 123751
    assert round(posOnGraph.position, 6) == 0.257727
    assert not posOnGraph.isUndefined()
    assert posOnGraph.segmentIdx == 1

    coords = roadGraph.getCoords(posOnGraph)
    assert round(coords.lon, 6) == 37.577455
    assert round(coords.lat, 6) == 55.814239

    posOnEdge = roadGraph.getPositionOnEdge(posOnGraph)
    assert posOnEdge.edgeId == posOnGraph.edgeId
    assert round(posOnEdge.position, 3) == 0.084
    assert not posOnEdge.isUndefined()


def test_detect_gates():

    position = roadGraph.getNearestEdgePoint(37.577730, 55.814286, 200)

    gates_stats = pygraph.detect_gates(roadGraph, position, 1800)
    assert gates_stats.gatesCount == 0
    assert gates_stats.looseEndsCount == 31
    assert gates_stats.edgesVisited == 43

    position = roadGraph.getNearestEdgePoint(37.650329, 55.705780, 200)

    gates_stats = pygraph.detect_gates(roadGraph, position, 1000)
    # Unfortunately, there are no gates on the test graph
    assert gates_stats.gatesCount == 0
    assert gates_stats.looseEndsCount == 2
    assert gates_stats.edgesVisited == 7
