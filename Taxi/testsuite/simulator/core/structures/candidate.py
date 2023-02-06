"""
    Structure for dispatch waybill and candidate
"""
# pylint: disable=no-member,import-only-modules

import dataclasses
import datetime
from typing import List
from typing import Optional

from simulator.core import config
from simulator.core.utils import current_time
from tests_united_dispatch.plugins import candidates_manager
from tests_united_dispatch.plugins import cargo_dispatch_manager
from .statistic import CandidateStats


@dataclasses.dataclass
class CandidateDestination:
    visit_order: int
    start_coordinates: List[float]  # lon lat
    end_coordinates: List[float]  # lon lat
    start_ts: datetime.datetime
    duration: datetime.timedelta

    def move_percent(self) -> float:
        now = current_time.CurrentTime.get()
        return (now - self.start_ts) / self.duration

    def current_pos(self) -> List[float]:
        move_percent = self.move_percent()
        if move_percent <= 0.0001:
            return self.start_coordinates
        if move_percent >= 0.9999:
            return self.end_coordinates

        delta_lon = self.end_coordinates[0] - self.start_coordinates[0]
        delta_lat = self.end_coordinates[1] - self.start_coordinates[1]
        return [
            self.start_coordinates[0] + delta_lon * move_percent,
            self.start_coordinates[1] + delta_lat * move_percent,
        ]


@dataclasses.dataclass
class DispatchCandidate:
    info: candidates_manager.Candidate

    waybill: Optional[cargo_dispatch_manager.Waybill] = None
    destination: Optional[CandidateDestination] = None
    position_ts: datetime.datetime = dataclasses.field(
        default_factory=current_time.CurrentTime.get,
    )
    tags: List[str] = dataclasses.field(default_factory=list)
    last_status_change_ts: datetime.datetime = dataclasses.field(
        default_factory=current_time.CurrentTime.get,
    )

    stats: CandidateStats = dataclasses.field(default_factory=CandidateStats)

    # pylint: disable=invalid-name
    @property
    def id(self) -> str:
        return self.info.id

    @property
    def speed(self) -> float:
        return getattr(
            config.settings.candidates.speed, self.info.transport_type,
        )

    def set_position(
            self, position: List[float], timestamp: datetime.datetime,
    ):
        self.info.position = position
        self.position_ts = timestamp

    def sync_position(self, timestamp: datetime.datetime):
        if self.destination is None:
            # candidate doesn't move without order
            return

        assert self.position_ts <= timestamp

        self.set_position(
            position=self.destination.current_pos(), timestamp=timestamp,
        )

    def set_free(self) -> bool:
        if self.info.is_busy():
            self.on_status_change()
            self.info.set_free()
            self.waybill = None
        return True

    def set_busy(self, waybill: cargo_dispatch_manager.Waybill) -> bool:
        if self.info.is_free():
            self.on_status_change()
            self.info.set_busy()
            self.waybill = waybill
            return True
        return False

    def on_status_change(self) -> None:
        if self.info.is_free():
            self.stats.free_durations.append(
                current_time.CurrentTime.get() - self.last_status_change_ts,
            )
        else:
            self.stats.on_order_durations.append(
                current_time.CurrentTime.get() - self.last_status_change_ts,
            )
        self.last_status_change_ts = current_time.CurrentTime.get()
