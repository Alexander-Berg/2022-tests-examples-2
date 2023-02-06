import dataclasses
from typing import Any
from typing import List
from typing import Optional


@dataclasses.dataclass
class PriorityValue:
    backend: int
    display: int


def _check_rating_bounds(value: float):
    assert 1.0 <= value <= 5.0


@dataclasses.dataclass
class RatingValue:
    # single bound rules
    lower_than: Optional[float] = None
    higher_than: Optional[float] = None
    # multiple bounds
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None

    def __init__(
            self, lower_bound: Optional[float], upper_bound: Optional[float],
    ):
        assert (lower_bound is not None) or (upper_bound is not None)
        if lower_bound is not None:
            _check_rating_bounds(lower_bound)
            if upper_bound is not None:
                _check_rating_bounds(upper_bound)
                self.lower_bound = lower_bound
                self.upper_bound = upper_bound
            else:
                self.higher_than = lower_bound
        else:
            assert upper_bound is not None
            _check_rating_bounds(upper_bound)
            self.lower_than = upper_bound


@dataclasses.dataclass
class CarYear:
    higher_than: Optional[int] = None
    lower_than: Optional[int] = None

    def __init__(self, is_higher: bool, car_year_value: int):
        assert car_year_value >= 0
        if is_higher:
            self.higher_than = car_year_value
        else:
            self.lower_than = car_year_value


@dataclasses.dataclass
class LogicRule:
    name: str
    items: List[Any]

    def __init__(self, name: str, items: List[Any]):
        assert name in ['and', 'or', 'none_of']
        self.name = name
        self.items = items


@dataclasses.dataclass
class AndRule:
    and_: Any


@dataclasses.dataclass
class TagRule:
    tag_name: str
    priority_value: PriorityValue
    override: Optional[LogicRule]


@dataclasses.dataclass
class RatingRule:
    rating: RatingValue
    priority_value: PriorityValue
    tanker_key_part: str
    override: Optional[LogicRule]

    def __init__(
            self,
            rating: RatingValue,
            priority_value: PriorityValue,
            tanker_key_part: str,
            override: Optional[LogicRule],
    ):
        self.rating = rating
        self.priority_value = priority_value
        self.tanker_key_part = tanker_key_part
        self.override = override


@dataclasses.dataclass
class CarYearRule:
    car_year: CarYear
    priority_value: PriorityValue
    tanker_key_part: str
    override: Optional[LogicRule]

    def __init__(
            self,
            car_year: CarYear,
            priority_value: PriorityValue,
            tanker_key_part: str,
            override: Optional[LogicRule],
    ):
        self.car_year = car_year
        self.priority_value = priority_value
        self.tanker_key_part = tanker_key_part
        self.override = override
