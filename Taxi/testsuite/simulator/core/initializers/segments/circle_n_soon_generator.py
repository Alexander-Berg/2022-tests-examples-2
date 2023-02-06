"""
    Creates N segments in circle.
"""
import datetime
from typing import List
from typing import Optional
from typing import Tuple

from simulator.core import structures
from simulator.core.utils import randomize_coordinates
from tests_united_dispatch.plugins import cargo_dispatch_manager


def make_segments(
        *,
        segments_count: int,
        center: structures.Point,
        radius: int,
        distance: float = None,
        delayed_special_requirements: Optional[
            List[Tuple[str, datetime.timedelta]]
        ] = None,
        **segment_kwargs,
) -> List[structures.DispatchSegment]:
    segments = []
    if delayed_special_requirements is None:
        delayed_special_requirements = []
    for _ in range(segments_count):
        # first point in radius [m] to center
        pickup_coordinates = randomize_coordinates.by_center(
            center=center, radius=radius,
        )
        if distance is not None:
            # second point is distance [m] away from pickup
            dropoff_coordinates = randomize_coordinates.by_center(
                center=pickup_coordinates, radius=radius, distance=distance,
            )
        else:
            # second point just in radius [m] near center
            dropoff_coordinates = randomize_coordinates.by_center(
                center=center, radius=radius,
            )
        segment = cargo_dispatch_manager.make_segment(
            pickup_coordinates=pickup_coordinates.to_list(),
            dropoff_coordinates=dropoff_coordinates.to_list(),
            **segment_kwargs,
        )

        dispatch_segment = structures.DispatchSegment(info=segment)
        for req, since in delayed_special_requirements:
            dispatch_segment.add_delayed_special_requirement(req, since)

        segments.append(dispatch_segment)

    return segments
