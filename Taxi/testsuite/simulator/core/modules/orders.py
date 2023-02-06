"""
    Describes segments/waybills model.

    Storage/API over active orders.
    * segment - active order (claim) without proposition;
    * waybill - active proposition over "inactive" order;
"""
import copy
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from simulator.core import stats
from simulator.core import structures
from simulator.core.utils import current_time


class OrdersModel:
    # all segments. id -> segment
    _SEGMENTS: Dict[str, structures.DispatchSegment] = {}

    # active segments. ids
    _ACTIVE_SEGMENT_IDS: Set[str] = set()

    # all waybills. id -> waybill
    _WAYBILLS: Dict[str, structures.DispatchWaybill] = {}

    # active waybills. ids
    _ACTIVE_WAYBILL_IDS: Set[str] = set()

    @classmethod
    def add_segment(cls, segment: structures.DispatchSegment) -> None:
        assert segment.id not in cls._SEGMENTS

        cls._SEGMENTS[segment.id] = segment
        cls._ACTIVE_SEGMENT_IDS.add(segment.id)

    @classmethod
    def list_active_segments(
            cls, max_size: Optional[int] = None,
    ) -> List[structures.DispatchSegment]:
        segments = []

        for segment_id in cls._ACTIVE_SEGMENT_IDS:
            segments.append(cls._SEGMENTS[segment_id])
            if max_size and len(segments) >= max_size:
                break

        return segments

    @classmethod
    def add_waybill(cls, waybill: structures.DispatchWaybill) -> None:
        assert waybill.id not in cls._WAYBILLS

        cls._WAYBILLS[waybill.id] = waybill
        cls._ACTIVE_WAYBILL_IDS.add(waybill.id)
        for segment in waybill.info.segments:
            cls._ACTIVE_SEGMENT_IDS.discard(segment.id)

    @classmethod
    def list_active_waybills(
            cls, max_size: Optional[int] = None,
    ) -> List[structures.DispatchWaybill]:
        waybills = []

        for waybill_id in cls._ACTIVE_WAYBILL_IDS:
            # TODO: maybe remove deepcopy because it is so slow
            waybills.append(copy.deepcopy(cls._WAYBILLS[waybill_id]))
            if max_size and len(waybills) >= max_size:
                break

        return waybills

    @classmethod
    def set_point_resolution(
            cls,
            waybill_ref: str,
            visit_order: int,
            is_visited=True,
            is_skipped=False,
    ):
        assert waybill_ref in cls._ACTIVE_WAYBILL_IDS

        waybill = cls._WAYBILLS[waybill_ref]

        point = waybill.info.set_point_resolution(
            visit_order=visit_order,
            is_visited=is_visited,
            is_skipped=is_skipped,
        )

        is_last_segment_point = True
        for idx in range(visit_order + 1, len(waybill.info.points)):
            non_visited_point = waybill.info.points[idx]
            if (
                    non_visited_point.segment_id == point.segment_id
                    and non_visited_point.point_type != 'return'
            ):
                is_last_segment_point = False
                break

        segment = cls.get_segment(point.segment_id)
        if point.point_type == 'pickup':
            assert segment.stats.time_to_pickup is None
            segment.stats.time_to_pickup = (
                current_time.CurrentTime.get() - segment.info.created_ts
            )
        if is_last_segment_point:
            cls.resolve_segment(
                segment=segment,
                resolution='resolved',
                status='delivered_finish',
            )

    @classmethod
    def resolve_segment(
            cls,
            segment: structures.DispatchSegment,
            resolution: str,
            status: str,
    ):
        segment.info.set_resolution(status=status, resolution=resolution)

        assert segment.stats.time_to_delivery is None
        segment.stats.time_to_delivery = (
            current_time.CurrentTime.get() - segment.info.created_ts
        )

        cls._ACTIVE_SEGMENT_IDS.discard(segment.id)

    @classmethod
    def resolve_waybill(cls, waybill_ref: str):
        waybill = cls.get_waybill(waybill_ref)

        waybill.info.revision += 1
        waybill.info.resolution = 'completed'

        cls._ACTIVE_WAYBILL_IDS.discard(waybill.id)

    @classmethod
    def get_waybill(cls, waybill_ref: str) -> structures.DispatchWaybill:
        return cls._WAYBILLS[waybill_ref]

    @classmethod
    def get_segment(cls, segment_id: str) -> structures.DispatchSegment:
        return cls._SEGMENTS[segment_id]

    @classmethod
    def clear(cls):
        cls._SEGMENTS.clear()
        cls._ACTIVE_SEGMENT_IDS.clear()
        cls._WAYBILLS.clear()
        cls._ACTIVE_WAYBILL_IDS.clear()

    @classmethod
    def gather_statistics(cls):
        segments_agg = stats.SegmentStatsAggregation()
        for segment in cls._SEGMENTS.values():
            segments_agg.aggregate(segment)

        return {'segment': segments_agg.gather(), 'waybill': {}}
