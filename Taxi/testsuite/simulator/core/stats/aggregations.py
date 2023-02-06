import statistics
from typing import List
from typing import Optional

import pydantic

from simulator.core import structures
from simulator.core.utils import distance


def _display_intervals(intervals: list):
    non_none = [i for i in intervals if i is not None]
    result = {
        'sum': sum(non_none) if non_none else None,
        'mean': statistics.mean(non_none) if non_none else None,
        'median': statistics.median(non_none) if non_none else None,
        'none': len(intervals) - len(non_none),
    }
    return result


class CandidateStatsAggregation(pydantic.BaseSettings):
    free_part: List[float] = pydantic.Field(default_factory=list)
    busy_part: List[float] = pydantic.Field(default_factory=list)
    on_order_durations: List[float] = pydantic.Field(default_factory=list)
    free_durations: List[float] = pydantic.Field(default_factory=list)
    distances_to_pickup: List[float] = pydantic.Field(default_factory=list)
    total_candidates: int = 0
    total_orders: int = 0

    def aggregate(self, candidate: structures.DispatchCandidate):
        stats = candidate.stats
        self.on_order_durations += [
            d.total_seconds() for d in stats.on_order_durations
        ]
        self.free_durations += [
            d.total_seconds() for d in stats.free_durations
        ]
        self.distances_to_pickup += stats.distances_to_pickup

        duration_total = stats.duration_free() + stats.duration_busy()
        if duration_total > 1:
            self.free_part.append(stats.duration_free() / duration_total)
            self.busy_part.append(stats.duration_busy() / duration_total)

        self.total_candidates += 1
        self.total_orders += len(stats.on_order_durations)

    def gather(self):
        return {
            'is_free_mean': (
                statistics.mean(self.free_part) if self.free_part else None
            ),
            'is_busy_mean': (
                statistics.mean(self.busy_part) if self.busy_part else None
            ),
            'wait_for_order_seconds': _display_intervals(self.free_durations),
            'on_order_seconds': _display_intervals(self.on_order_durations),
            'total_candidates': self.total_candidates,
            'orders_per_candidate_mean': (
                self.total_orders / self.total_candidates
            ),
            'distances_to_pickup': _display_intervals(
                self.distances_to_pickup,
            ),
        }


class SegmentStatsAggregation(pydantic.BaseSettings):
    candidates_count: List[int] = pydantic.Field(default_factory=list)
    candidates_count_non_zeros: List[int] = pydantic.Field(
        default_factory=list,
    )
    time_to_first_performer_found: List[Optional[float]] = pydantic.Field(
        default_factory=list,
    )
    time_to_last_performer_found: List[Optional[float]] = pydantic.Field(
        default_factory=list,
    )
    time_to_pickup: List[Optional[float]] = pydantic.Field(
        default_factory=list,
    )
    time_to_delivery: List[Optional[float]] = pydantic.Field(
        default_factory=list,
    )
    route_distance: List[float] = pydantic.Field(default_factory=list)

    delivered_count: int = 0
    performer_not_found_count: int = 0
    canceled_count: int = 0
    total_count: int = 0
    total_points: int = 0

    def aggregate(self, segment: structures.DispatchSegment):
        stats = segment.stats

        self.candidates_count.append(stats.candidates_count)
        if stats.candidates_count:
            self.candidates_count_non_zeros.append(stats.candidates_count)
        self.time_to_first_performer_found.append(
            stats.time_to_first_performer_found.total_seconds()
            if stats.time_to_first_performer_found is not None
            else None,
        )
        self.time_to_last_performer_found.append(
            stats.time_to_last_performer_found.total_seconds()
            if stats.time_to_last_performer_found is not None
            else None,
        )
        self.time_to_pickup.append(
            stats.time_to_pickup.total_seconds()
            if stats.time_to_pickup
            else None,
        )
        self.time_to_delivery.append(
            stats.time_to_delivery.total_seconds()
            if stats.time_to_delivery
            else None,
        )
        self.route_distance.append(self._calc_segment_distance(segment))

        self.total_points += len(segment.info.points)
        self.total_count += 1
        if segment.info.resolution == 'cancelled_by_user':
            self.canceled_count += 1
        elif segment.info.resolution == 'performer_not_found':
            self.performer_not_found_count += 1
        elif segment.info.resolution == 'resolved':
            self.delivered_count += 1

    def gather(self):
        return {
            'candidates_count': _display_intervals(self.candidates_count),
            'candidates_count_non_zeros': _display_intervals(
                self.candidates_count_non_zeros,
            ),
            'time_to_first_performer_found': _display_intervals(
                self.time_to_first_performer_found,
            ),
            'time_to_last_performer_found': _display_intervals(
                self.time_to_last_performer_found,
            ),
            'time_to_pickup': _display_intervals(self.time_to_pickup),
            'time_to_delivery': _display_intervals(self.time_to_delivery),
            'route_distance': _display_intervals(self.route_distance),
            'total_distance': sum(self.route_distance),
            'performer_not_found_rate': (
                self.performer_not_found_count / self.total_count
            ),
            'canceled_rate': self.canceled_count / self.total_count,
            'complete_rate': self.delivered_count / self.total_count,
            'total_count': self.total_count,
            'points_per_segment_mean': self.total_points / self.total_count,
        }

    def _calc_segment_distance(
            self, segment: structures.DispatchSegment,
    ) -> float:
        return distance.path_distance(
            [
                structures.Point.from_list(p.coordinates)
                for p in segment.info.points[:-1]
            ],
        )


class DispatchStatsAggregation(pydantic.BaseSettings):
    total_propositions: int = 0
    total_assigned_candidates: int = 0
    total_passed_segments: int = 0
    total_skipped_segments: int = 0
    elapsed_time: float = 0

    total_runs: int = 0
    idle_runs: int = 0  # runs without any output result

    def aggregate(self, stats: structures.DispatchStats):
        for run in stats.run_stats:
            self.total_propositions += run.propositions
            self.total_assigned_candidates += run.assigned_candidates
            self.total_passed_segments += run.passed_segments
            self.total_skipped_segments += run.skipped_segments

            self.total_runs += 1
            if not run.propositions and not run.assigned_candidates:
                self.idle_runs += 1
            self.elapsed_time += run.elapsed_time

    def gather(self):
        return {
            'total_propositions': self.total_propositions,
            'total_assigned_candidates': self.total_assigned_candidates,
            'total_passed_segments': self.total_passed_segments,
            'total_skipped_segments': self.total_skipped_segments,
            'total_runs': self.total_runs,
            'idle_runs': self.idle_runs,
            'elapsed_time': self.elapsed_time,
        }
