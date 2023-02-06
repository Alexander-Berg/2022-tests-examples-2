import pytest
from nile.api.v1 import Record

from projects.geosuggest.pickup_points.features.points_storage import (
    PointsStorage,
)
from projects.geosuggest.pickup_points.features.nearest_maps_items.objects import (  # noqa pylint: disable=line-too-long
    NearestMapsItemsAggregator,
    MapsItemsStorage,
)


def create_output(ft_type_id, lon, lat, distance, eps=1e-3):
    return {
        b'key': ft_type_id,
        b'distance': pytest.approx(distance, abs=eps),
        b'item': {
            b'ft_type_id': ft_type_id,
            b'lon': pytest.approx(lon, abs=eps),
            b'lat': pytest.approx(lat, abs=eps),
        },
    }


def test_nearest_items_aggregator():
    points_storage = PointsStorage()
    points_storage.add(Record(id=b'a', lon=37.6421, lat=55.7351))
    points_storage.add(Record(id=b'b', lon=37.6438, lat=55.7334))
    points_storage.finalize()

    aggregator = NearestMapsItemsAggregator(
        points_storage=points_storage, max_distance=1000,
    )

    maps_storage = MapsItemsStorage()
    maps_storage.add(Record(ft_type_id=0, lon=37.6427, lat=55.7336))
    maps_storage.add(Record(ft_type_id=1, lon=37.6424, lat=55.7341))
    maps_storage.finalize()

    aggregator.update_states(maps_storage)

    packed_states = [state.pack() for state in aggregator.states]
    assert packed_states == [
        [
            create_output(0, 37.6427, 55.7336, 171.0181),
            create_output(1, 37.6424, 55.7341, 112.8017),
        ],
        [
            create_output(0, 37.6427, 55.7336, 72.3903),
            create_output(1, 37.6424, 55.7341, 117.2551),
        ],
    ]

    states = [
        NearestMapsItemsAggregator.State.unpack(packed_state)
        for packed_state in packed_states
    ]
    result = states[0]
    result.update_by_state(states[1])
    assert result.pack() == [
        create_output(0, 37.6427, 55.7336, 72.3903),
        create_output(1, 37.6424, 55.7341, 112.8017),
    ]
