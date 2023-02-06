from taxi_pyml.common import geo

import numpy as np
import pytest


def test_distance():
    res = geo.earth_distance(0, 0, 1.0, 0, is_radians=True)
    assert res == geo.EARTH_RADIUS_METERS


def test_pairwise_distance():
    lon1, lat1 = 0.0, 0.0
    lon2, lat2 = 1.0, 0.0

    res = geo.earth_pairwise_distance(
        np.array([lon1, lon2]),
        np.array([lat1, lat2]),
        np.array([lon1, lon2]),
        np.array([lat1, lat2]),
        is_radians=True,
    )

    assert res[0, 0] == 0.0
    assert res[0, 1] == geo.EARTH_RADIUS_METERS
    assert res[1, 1] == 0.0
    assert res[1, 0] == geo.EARTH_RADIUS_METERS


def test_angle_clockwise():
    lon1, lat1 = 37, 55
    eps = 1e-6
    lon2 = np.array([lon1, lon1 + eps, lon1, lon1 - eps])
    lat2 = np.array([lat1 + eps, lat1, lat1 - eps, lat1])

    angles = geo.angle_clockwise(lon1, lat1, lon2, lat2)
    assert angles == pytest.approx([0, 90, 180, 270], abs=1e-6)
