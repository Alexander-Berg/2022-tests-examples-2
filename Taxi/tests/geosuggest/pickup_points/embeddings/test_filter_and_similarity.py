import pytest

from projects.geosuggest.pickup_points.embeddings import similarity_extractors
from projects.geosuggest.pickup_points.common import objects
from projects.geosuggest.pickup_points.graph.nile_blocks.create_points import (
    _get_shifted_coordinates,
)
from taxi_pyml.common import geo

CATEGORY_SHIFT_MAPPING = {1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 3}


lhs_graph_info = objects.GraphInfo(
    lon=36.201594,
    lat=50.032955,
    edge_id=128585716,
    edge_persistent_id='14150703003860564258',
    reversed_edge_id=128585724,
    reversed_edge_persistent_id='14062830871367309829',
    segment_direction=158.22518371856063,
    segment_start=(36.12606259999999, 51.7755148),
    segment_end=(36.12663079999999, 51.7746324),
    edge_data=objects.EdgeData(
        length=123.4,
        category=7,
        speed=20,
        speed_limit=None,
        is_toll_road=False,
        is_passable=True,
        access=1,
    ),
    detect_gates_stats=objects.DetectGatesStats(
        edges_visited=123, gates_count=1, loose_ends_count=21,
    ),
    reversed_detect_gates_stats=objects.DetectGatesStats(
        edges_visited=321, gates_count=2, loose_ends_count=2,
    ),
)
rhs_graph_info = objects.GraphInfo(
    lon=36.20079199999998,
    lat=50.03295499999999,
    edge_id=13595688,
    edge_persistent_id='7244724932611144189',
    reversed_edge_id=13595699,
    reversed_edge_persistent_id='2231158053347074252',
    segment_direction=239.13736128223465,
    segment_start=(36.20079199999998, 50.03295499999999),
    segment_end=(36.200552999999985, 50.03286299999999),
    edge_data=objects.EdgeData(
        length=123.4,
        category=5,
        speed=20,
        speed_limit=30,
        is_toll_road=False,
        is_passable=True,
        access=1,
    ),
    detect_gates_stats=objects.DetectGatesStats(
        edges_visited=123, gates_count=1, loose_ends_count=21,
    ),
    reversed_detect_gates_stats=None,
)


def test_similarity_function():
    similarity_function = similarity_extractors.GraphSimilarityExtractor(
        intersection_distance=250, small_category_ids=[8], min_angle=120,
    )
    assert similarity_function(lhs_graph_info, rhs_graph_info) is True


def test_points_shift():
    shifted_coords = _get_shifted_coordinates(
        graph_info=rhs_graph_info,
        category_shift_mapping=CATEGORY_SHIFT_MAPPING,
    )
    shift_distance = geo.earth_distance(
        rhs_graph_info.lon, rhs_graph_info.lat, *shifted_coords,
    )
    mapping_shift = CATEGORY_SHIFT_MAPPING[rhs_graph_info.edge_data.category]
    assert shift_distance == pytest.approx(mapping_shift)
    assert shifted_coords == pytest.approx([36.200792, 50.032955])
