import datetime
import json
import random

import pandas
import pytest

from operation_calculations.geosubventions.calculators import (
    grid_polygon_maker as gpm_lib,
)


TEST_POLYGONS_CELLS = {
    (-1, 1),
    (1, 0),
    (0, 1),
    (1, -1),
    (7, 1),
    (7, 0),
    (6, 1),
    (9, 3),
}


@pytest.fixture(name='test_data')
def data_fixture(open_file):
    with open_file('test_data.csv') as handler:
        return pandas.read_csv(handler)


@pytest.fixture(name='test_params')
def params_fixture(open_file):
    with open_file('test_data.json') as handler:
        params = json.load(handler)

    for intervals in params['rush_hours_groups'].values():
        for interval in intervals:
            interval[0] = datetime.datetime(*interval[0])
            interval[1] = datetime.datetime(*interval[1])

    for interval_geo in params['intervals_geo']:
        interval_geo['interval'] = [
            datetime.datetime(*interval_geo['interval'][0]),
            datetime.datetime(*interval_geo['interval'][1]),
        ]
    return params


def test_get_polygons_cells(test_data):
    gpm = gpm_lib.GridPolygonMaker(grid_min_group_size=2)

    test_data['trips'] = 1
    test_data['cell_x'] = 0
    test_data['cell_y'] = 0
    test_data[['cell_x', 'cell_y']] = gpm.grid.loc2cell(
        test_data['order_source_lon'], test_data['order_source_lat'],
    )

    polygons_cells = gpm.get_polygons_cells(test_data, 0.35)
    assert polygons_cells == {
        (4156.0, 4410.0),
        (4161.0, 4397.0),
        (4162.0, 4423.0),
        (4163.0, 4380.0),
        (4163.0, 4387.0),
        (4163.0, 4400.0),
        (4163.0, 4419.0),
        (4164.0, 4377.0),
        (4164.0, 4413.0),
        (4165.0, 4379.0),
        (4165.0, 4393.0),
        (4165.0, 4425.0),
        (4167.0, 4395.0),
        (4168.0, 4387.0),
        (4177.0, 4413.0),
        (4178.0, 4388.0),
        (4178.0, 4389.0),
        (4178.0, 4409.0),
        (4178.0, 4414.0),
        (4178.0, 4421.0),
        (4179.0, 4375.0),
        (4179.0, 4408.0),
        (4184.0, 4379.0),
        (4186.0, 4368.0),
        (4186.0, 4386.0),
        (4188.0, 4396.0),
        (4188.0, 4405.0),
        (4190.0, 4407.0),
        (4193.0, 4389.0),
        (4195.0, 4371.0),
        (4196.0, 4389.0),
        (4201.0, 4382.0),
        (4179.0, 4407.0),
        (4204.0, 4386.0),
        (4163.0, 4378.0),
    }


def test_smooth_cells_group():
    gpm = gpm_lib.GridPolygonMaker(grid_min_group_size=2)
    smoothed_group = gpm.smooth_cells_group(
        frozenset({(-1, 1), (1, 0), (0, 1), (1, -1)}),
    )
    assert smoothed_group == frozenset(
        {(-1, 1), (1, 0), (0, 1), (1, -1), (0, 0)},
    )


def test_group_polygons():
    gpm = gpm_lib.GridPolygonMaker(grid_min_group_size=2)
    poly_groups = gpm.group_polygons_cells(TEST_POLYGONS_CELLS)
    assert set(poly_groups) == {
        frozenset({(-1, 1), (1, 0), (0, 1), (1, -1)}),
        frozenset({(7, 1), (7, 0), (6, 1)}),
    }


def test_cells_to_polygon():
    gpm = gpm_lib.GridPolygonMaker()
    polygon_cells_group = frozenset({(-1, 1), (1, 0), (0, 1), (1, -1)})
    polygon = gpm.cells_to_polygon(polygon_cells_group)
    polygon_coords = list(zip(*polygon.exterior.xy))
    assert polygon_coords == [
        (0.012, 0.0),
        (0.015, -0.0052),
        (0.012, -0.01039),
        (0.006, -0.01039),
        (0.003, -0.0052),
        (0.006, 0.0),
        (0.003, 0.0052),
        (-0.003, 0.0052),
        (-0.006, 0.0),
        (-0.012, 0.0),
        (-0.015, 0.0052),
        (-0.012, 0.01039),
        (-0.006, 0.01039),
        (-0.003, 0.01559),
        (0.003, 0.01559),
        (0.006, 0.01039),
        (0.012, 0.01039),
        (0.015, 0.0052),
        (0.012, 0.0),
    ]


@pytest.mark.parametrize(
    'intervals, expected_order_share',
    [
        (
            [
                (
                    datetime.datetime(1900, 1, 1, 1),
                    datetime.datetime(1900, 1, 1, 6),
                ),
            ],
            0.2,
        ),
        (
            [
                (
                    datetime.datetime(1900, 1, 1, 6),
                    datetime.datetime(1900, 1, 1, 9),
                ),
            ],
            0.35,
        ),
        (
            [
                (
                    datetime.datetime(1900, 1, 1, 6),
                    datetime.datetime(1900, 1, 1, 9),
                ),
                (
                    datetime.datetime(1900, 1, 6, 6),
                    datetime.datetime(1900, 1, 6, 9),
                ),
            ],
            0.2,
        ),
        (
            [
                (
                    datetime.datetime(1900, 1, 1, 9),
                    datetime.datetime(1900, 1, 1, 12),
                ),
            ],
            0.35,
        ),
        (
            [
                (
                    datetime.datetime(1900, 1, 1, 1),
                    datetime.datetime(1900, 1, 1, 14),
                ),
            ],
            0.2,
        ),
        (
            [
                (
                    datetime.datetime(1900, 1, 1, 17),
                    datetime.datetime(1900, 1, 1, 21),
                ),
            ],
            0.2,
        ),
        (
            [
                (
                    datetime.datetime(1900, 1, 7, 6),
                    datetime.datetime(1900, 1, 7, 9),
                ),
            ],
            0.2,
        ),
    ],
)
def test_get_order_share_for_rh_group(intervals, expected_order_share):
    gpm = gpm_lib.GridPolygonMaker()
    order_share = gpm.get_order_share_for_rh_group(intervals)
    assert order_share == expected_order_share, intervals


async def test_run(test_data, test_params):
    gpm = gpm_lib.GridPolygonMaker(
        grid_min_group_size=3,
        surge_threshold=1.2,
        trips_quantile=0.75,
        orders_share_morning=1,
        orders_share_other=1,
    )
    result = await gpm.run(
        test_data,
        rush_hours_groups=test_params['rush_hours_groups'],
        polygons_params={},
        shaper_params={},
    )

    assert result == (test_params['intervals_geo'], test_params['polygons'])


def generate_cells(number, min_x, max_x):
    return {
        (random.randint(min_x, max_x), random.randint(min_x, max_x))
        for _ in range(number)
    }


def test_polygon_smooth():
    gpm = gpm_lib.GridPolygonMaker()
    for _ in range(1000):
        cells = generate_cells(100, -20, 20)
        poly_groups = gpm.group_polygons_cells(cells)
        for group_cells in poly_groups:
            smoothed = gpm.smooth_cells_group(group_cells)
            new_cells = smoothed - group_cells
            for cell in new_cells:
                neighbours = 0
                original_neighbours = 0
                for neighbour in gpm.grid.get_neighbours(*cell):
                    neighbours += int(neighbour in smoothed)
                    original_neighbours += int(neighbour in group_cells)
                assert neighbours > 3, str(group_cells)
                assert neighbours <= 6, str(group_cells)
                assert original_neighbours > 0, str(group_cells)
