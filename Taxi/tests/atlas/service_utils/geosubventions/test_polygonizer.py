from atlas.service_utils.geosubventions.core.polygonizer import Shaper
import pytest
from shapely.geometry import Polygon
from atlas.service_utils.geosubventions.core.utils import get_coords
POLYGONS = [
        [[1, 3], [1, 4], [4, 4], [4, 2], [3, 2], [3, 3]],
        [[3, 6], [3, 7], [4, 7], [4, 6]],
        [[5, 5], [5, 6], [6, 6], [6, 5]],
        [[7, 4], [7, 5], [8, 5], [8, 4]],
        [[3, 3], [3, 7], [7, 7], [7, 5], [9, 5], [9, 4], [7, 4], [7, 3]]
    ]
@pytest.mark.parametrize(
    "intersection_cut_smaller, expected",
    [
        [
            True,
            {
                0: [[[1., 3.], [1., 4.], [3., 4.], [3., 3.], [1., 3.]]],
                1: [[]],
                2: [[]],
                3: [[]],
                4: [[[3., 3.], [3., 7.], [7., 7.], [7., 5.], [9., 5.], [9., 4.], [7., 4.], [7., 3.], [3., 3.]]]
            }
        ],
        [
            False,
            {
                0: [[[1., 3.], [1., 4.], [4., 4.], [4., 2.], [3., 2.], [3., 3.], [1., 3.]]],
                1: [[[3., 6.], [3., 7.], [4., 7.], [4., 6.], [3., 6.]]],
                2: [[]],
                3: [[[7., 4.], [7., 5.], [8., 5.], [8., 4.], [7., 4.]]],
                4: [[[3., 4.], [3., 6.], [4., 6.], [4., 7.], [7., 7.], [7., 5.], [7., 4.], [7., 3.], [4., 3.], [4., 4.], [3., 4.]]]
            }
        ]
    ]
)
def test_poly_intersections(intersection_cut_smaller, expected):
    polygons = {i: Polygon(p) for i, p in enumerate(POLYGONS)}
    shaper = Shaper(intersect_cut_smaller=intersection_cut_smaller)
    non_intersecting = shaper.poly_crossing(polygons)
    non_intersecting = {k: get_coords(v) for k,v in non_intersecting.items()}
    assert non_intersecting == expected
