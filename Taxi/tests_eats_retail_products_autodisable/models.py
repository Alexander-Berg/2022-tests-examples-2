import dataclasses
import datetime as dt
from typing import List


def recursive_dict(x):
    result_dict = {}
    for key, value in x.__dict__.items():
        if isinstance(value, List):
            result_dict[key] = [recursive_dict(i) for i in sorted(value)]
        elif '__dict__' in dir(value):
            result_dict[key] = recursive_dict(value)
        else:
            result_dict[key] = value
    return result_dict


@dataclasses.dataclass
class AutodisabledProduct:
    place_id: int
    origin_id: str
    force_unavailable_until: dt.datetime
    algorithm_name: str
    last_disabled_at: dt.datetime
    disabled_count: int = 0

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return (self.place_id < other.place_id) or (
            self.place_id == other.place_id
            and self.origin_id < other.origin_id
        )
