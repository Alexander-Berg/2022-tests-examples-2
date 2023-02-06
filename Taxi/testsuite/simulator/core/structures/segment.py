"""
    Structure for dispatch waybill and candidate
"""
# pylint: disable=no-member,import-only-modules

import collections
import copy
import dataclasses
import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple


from simulator.core.utils import current_time
from tests_united_dispatch.plugins import cargo_dispatch_manager
from .statistic import SegmentStats


@dataclasses.dataclass
class DispatchSegment:
    info: cargo_dispatch_manager.Segment

    # taxi_class -> (ignorable_special_requirement, delay)
    delayed_special_requirements: Dict[
        str, List[Tuple[str, datetime.timedelta]],
    ] = dataclasses.field(
        default_factory=lambda: collections.defaultdict(list),
    )
    stats: SegmentStats = dataclasses.field(default_factory=SegmentStats)

    # pylint: disable=invalid-name
    @property
    def id(self) -> str:
        return self.info.id

    def add_delayed_special_requirement(
            self,
            special_requirement_id: str,
            since_lookup: datetime.timedelta,
    ) -> None:
        # since due not supported yet
        for taxi_class in self.info.taxi_classes:
            # pylint: disable=unsubscriptable-object,
            self.delayed_special_requirements[taxi_class].append(
                (special_requirement_id, since_lookup),
            )

    def get_current_special_requirements(self) -> Dict[str, Any]:
        special_requirements = copy.deepcopy(self.info.special_requirements)
        for taxi_class, by_class in special_requirements.items():
            ignored_special_requirements = set()
            for (
                    ignorable_special_requirement,
                    delay,
            ) in self.delayed_special_requirements.get(taxi_class, []):
                if (
                        self.info.created_ts + delay
                        <= current_time.CurrentTime.get()
                ):
                    ignored_special_requirements.add(
                        ignorable_special_requirement,
                    )

            special_requirements[taxi_class] = {
                s for s in by_class if s not in ignored_special_requirements
            }

        return special_requirements

    def on_candidate_found(self):
        self.stats.on_candidate_found(
            lookup_duration=current_time.CurrentTime.get()
            - self.info.created_ts,
        )
