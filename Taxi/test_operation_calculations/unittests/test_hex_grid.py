import random

import numpy
import numpy as np
import pytest

from operation_calculations.geosubventions.calculators import (
    grid_polygon_maker as gpm_lib,
)


@pytest.mark.parametrize(
    'loc,expected_vector',
    [
        ((0.0, 0.0), (0.0, 0.0)),
        ((53.21, 34.67), (26605.0, 18501.36653)),
        ((23.5, 14.67), (11750.0, 7416.48168)),
        ((-152.42776, 89.90543), (-76213.88, 203393.9696)),
    ],
)
def test_loc2vector(loc, expected_vector):
    grid = gpm_lib.FlatTopHexGeoGrid()
    assert tuple(grid.loc2vector(*loc)) == expected_vector


@pytest.mark.parametrize(
    'vector,expected_loc',
    [
        ((0.0, 0.0), (0.0, 0.0)),
        ((26605.0, 18501.36653), (53.21, 34.67)),
        ((11750.0, 7416.48168), (23.5, 14.67)),
    ],
)
def test_vector2loc(vector, expected_loc):
    grid = gpm_lib.FlatTopHexGeoGrid()
    assert tuple(grid.vector2loc(numpy.array(vector))) == expected_loc


def test_loc2vector2loc():
    grid = gpm_lib.FlatTopHexGeoGrid()
    for _ in range(1000):
        loc = (
            round(random.random() * 360 - 180, 5),
            round(random.random() * 180 - 90, 5),
        )
        vector = grid.loc2vector(*loc)
        assert tuple(grid.vector2loc(vector)) == loc, (loc, vector)


def test_get_neighbours():
    grid = gpm_lib.FlatTopHexGeoGrid()
    assert set(grid.get_neighbours(7, 7)) == {
        (7, 6),
        (6, 7),
        (8, 7),
        (7, 8),
        (6, 8),
        (8, 6),
    }


def test_get_cell_polygon():
    grid = gpm_lib.FlatTopHexGeoGrid()
    assert grid.get_cell_polygon(7, 7) == [
        [0.069, 0.10912],
        [0.066, 0.11432],
        [0.06, 0.11432],
        [0.057, 0.10912],
        [0.06, 0.10392],
        [0.066, 0.10392],
        [0.069, 0.10912],
    ]


@pytest.mark.parametrize(
    'loc,expected_cell',
    [
        ((0.0, 0.0), (0, 0)),
        ((53.21, 34.67), (5912, 605)),
        ((23.5, 14.67), (2611, 122)),
        ((-152.42776, 89.90543), (-16936, 47611)),
    ],
)
def test_loc2cell(loc, expected_cell):
    grid = gpm_lib.FlatTopHexGeoGrid()
    assert tuple(grid.loc2cell(*np.array([loc]).T)[0]) == expected_cell
