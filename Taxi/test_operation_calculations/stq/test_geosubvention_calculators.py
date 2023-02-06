import pytest
import shapely.geometry as shapely_geo

from operation_calculations.geosubventions.calculators import (
    polygonizer as shaper_lib,
)
import operation_calculations.geosubventions.calculators.utils as utils

POLYGONS = [
    [[1, 3], [1, 4], [4, 4], [4, 2], [3, 2], [3, 3]],
    [[3, 6], [3, 7], [4, 7], [4, 6]],
    [[5, 5], [5, 6], [6, 6], [6, 5]],
    [[7, 4], [7, 5], [8, 5], [8, 4]],
    [[3, 3], [3, 7], [7, 7], [7, 5], [9, 5], [9, 4], [7, 4], [7, 3]],
]


@pytest.mark.parametrize(
    'intersection_cut_smaller, expected',
    [
        [
            True,
            {
                0: [
                    [
                        [1.0, 3.0],
                        [1.0, 4.0],
                        [3.0, 4.0],
                        [3.0, 3.0],
                        [1.0, 3.0],
                    ],
                ],
                1: [[]],
                2: [[]],
                3: [[]],
                4: [
                    [
                        [3.0, 3.0],
                        [3.0, 7.0],
                        [7.0, 7.0],
                        [7.0, 5.0],
                        [9.0, 5.0],
                        [9.0, 4.0],
                        [7.0, 4.0],
                        [7.0, 3.0],
                        [3.0, 3.0],
                    ],
                ],
            },
        ],
        [
            False,
            {
                0: [
                    [
                        [1.0, 3.0],
                        [1.0, 4.0],
                        [4.0, 4.0],
                        [4.0, 2.0],
                        [3.0, 2.0],
                        [3.0, 3.0],
                        [1.0, 3.0],
                    ],
                ],
                1: [
                    [
                        [3.0, 6.0],
                        [3.0, 7.0],
                        [4.0, 7.0],
                        [4.0, 6.0],
                        [3.0, 6.0],
                    ],
                ],
                2: [[]],
                3: [
                    [
                        [7.0, 4.0],
                        [7.0, 5.0],
                        [8.0, 5.0],
                        [8.0, 4.0],
                        [7.0, 4.0],
                    ],
                ],
                4: [
                    [
                        [3.0, 4.0],
                        [3.0, 6.0],
                        [4.0, 6.0],
                        [4.0, 7.0],
                        [7.0, 7.0],
                        [7.0, 5.0],
                        [7.0, 4.0],
                        [7.0, 3.0],
                        [4.0, 3.0],
                        [4.0, 4.0],
                        [3.0, 4.0],
                    ],
                ],
            },
        ],
    ],
)
def test_poly_intersections(intersection_cut_smaller, expected):
    polygons = {i: shapely_geo.Polygon(p) for i, p in enumerate(POLYGONS)}
    shaper = shaper_lib.Shaper(intersect_cut_smaller=intersection_cut_smaller)
    non_intersecting = shaper.poly_crossing(polygons)
    non_intersecting = {
        k: utils.get_coords(v) for k, v in non_intersecting.items()
    }
    assert non_intersecting == expected


def test_polygon_split():
    allowed_geo = shapely_geo.MultiPolygon(
        [
            shapely_geo.Polygon([[0, 0], [0, 4], [2, 4], [2, 0]]),
            shapely_geo.Polygon([[3, 3], [3, 4], [4, 4], [4, 3]]),
        ],
    )
    shaper = shaper_lib.Shaper(allowed_geo=allowed_geo)
    polygons = {
        '2': shapely_geo.Polygon([[0, 0], [0, 1], [1, 1], [1, 0]]),
        '8': shapely_geo.Polygon([[0, 3], [0, 4], [4, 4], [4, 3]]),
    }
    splitted_polygons = {
        k: utils.get_coords(v)
        for k, v in shaper.split_polygons(polygons).items()
    }
    assert splitted_polygons == {
        '10': [[[3.0, 4.0], [4.0, 4.0], [4.0, 3.0], [3.0, 3.0], [3.0, 4.0]]],
        '2': [[[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]],
        '9': [[[0.0, 3.0], [0.0, 4.0], [2.0, 4.0], [2.0, 3.0], [0.0, 3.0]]],
    }
