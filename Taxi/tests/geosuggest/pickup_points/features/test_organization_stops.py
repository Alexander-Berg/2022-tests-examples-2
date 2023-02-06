from nile.api.v1 import Record

from projects.geosuggest.pickup_points.features.points_storage import (
    PointsStorage,
)
from projects.geosuggest.pickup_points.features.organization_stops.objects import (  # noqa pylint: disable=line-too-long
    OrganizationStopsAggregator,
    OrganizationStopsStorage,
)


def create_stop_record(
        oid, stop_type, edge_persistent_id, edge_distance, weight=1,
):
    return Record(
        oid=oid,
        stop_type=stop_type,
        edge_persistent_id=edge_persistent_id,
        edge_distance=edge_distance,
        weight=weight,
    )


def test_aggregator():
    points_storage = PointsStorage()
    points_storage.add(Record(id=b'a', edge_persistent_id=1, edge_distance=10))
    points_storage.add(Record(id=b'b', edge_persistent_id=2, edge_distance=0))
    points_storage.finalize()

    aggregator = OrganizationStopsAggregator(
        points_storage=points_storage, max_edge_distance=10,
    )

    stops_storage = OrganizationStopsStorage()
    stops_storage.add(create_stop_record(1, b'pickup', 1, 5))
    stops_storage.add(create_stop_record(1, b'dropoff', 1, 15))
    stops_storage.add(create_stop_record(1, b'pickup', 2, 5))
    stops_storage.add(create_stop_record(2, b'pickup', 2, 5))
    stops_storage.add(create_stop_record(3, b'dropoff', 2, 100))
    stops_storage.finalize()

    aggregator.update_states(stops_storage)

    packed_states = [state.pack() for state in aggregator.states]
    assert packed_states == [
        [
            {b'oid': 1, b'stop_type': b'pickup', b'weight': 1},
            {b'oid': 1, b'stop_type': b'dropoff', b'weight': 1},
        ],
        [
            {b'oid': 1, b'stop_type': b'pickup', b'weight': 1},
            {b'oid': 2, b'stop_type': b'pickup', b'weight': 1},
        ],
    ]

    states = [
        OrganizationStopsAggregator.State.unpack(packed_state)
        for packed_state in packed_states
    ]
    result = states[0]
    result.update_by_state(states[1])
    assert result.pack() == [
        {b'oid': 1, b'stop_type': b'pickup', b'weight': 2},
        {b'oid': 1, b'stop_type': b'dropoff', b'weight': 1},
        {b'oid': 2, b'stop_type': b'pickup', b'weight': 1},
    ]
