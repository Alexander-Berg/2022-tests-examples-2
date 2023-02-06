"""
    Structure for statistics
"""

import datetime
from typing import List
from typing import Optional

import pydantic


class CandidateStats(pydantic.BaseSettings):
    on_order_durations: List[datetime.timedelta] = pydantic.Field(
        default_factory=list,
    )
    free_durations: List[datetime.timedelta] = pydantic.Field(
        default_factory=list,
    )
    distances_to_pickup: List[float] = pydantic.Field(default_factory=list)

    def duration_free(self):
        return sum([d.total_seconds() for d in self.free_durations])

    def duration_busy(self):
        return sum([d.total_seconds() for d in self.on_order_durations])


class DispatchRunStats(pydantic.BaseSettings):
    propositions: int = 0
    assigned_candidates: int = 0
    passed_segments: int = 0
    skipped_segments: int = 0
    elapsed_time: float = 0


class DispatchStats(pydantic.BaseSettings):
    run_stats: List[DispatchRunStats] = pydantic.Field(default_factory=list)

    def add_result(self, result: DispatchRunStats):
        self.run_stats.append(result)

    def clear(self):
        self.run_stats.clear()


class RunnerStats(pydantic.BaseSettings):
    start_simulation_timestamp: Optional[datetime.datetime] = None
    finish_simulation_timestamp: Optional[datetime.datetime] = None
    start_real_timestamp: Optional[datetime.datetime] = None
    finish_real_timestamp: Optional[datetime.datetime] = None

    def set_start(self, simulation_timestamp: datetime.datetime):
        assert self.start_simulation_timestamp is None
        self.start_simulation_timestamp = simulation_timestamp
        self.start_real_timestamp = datetime.datetime.now()

    def set_finish(self, simulation_timestamp: datetime.datetime):
        assert self.finish_simulation_timestamp is None
        self.finish_simulation_timestamp = simulation_timestamp
        self.finish_real_timestamp = datetime.datetime.now()

    def gather(self):
        return {
            'start_simulation_timestamp': self.start_simulation_timestamp,
            'finish_simulation_timestamp': self.finish_simulation_timestamp,
            'start_real_timestamp': self.start_real_timestamp,
            'finish_real_timestamp': self.finish_real_timestamp,
        }

    def clear(self):
        self.start_simulation_timestamp = None
        self.finish_simulation_timestamp = None
        self.start_real_timestamp = None
        self.finish_real_timestamp = None


class SegmentStats(pydantic.BaseSettings):
    candidates_count: int = 0
    time_to_first_performer_found: Optional[datetime.timedelta] = None
    time_to_last_performer_found: Optional[datetime.timedelta] = None
    time_to_pickup: Optional[datetime.timedelta] = None
    time_to_delivery: Optional[datetime.timedelta] = None

    def on_candidate_found(self, lookup_duration):
        self.candidates_count += 1
        if self.time_to_first_performer_found is None:
            self.time_to_first_performer_found = lookup_duration
        self.time_to_last_performer_found = lookup_duration
