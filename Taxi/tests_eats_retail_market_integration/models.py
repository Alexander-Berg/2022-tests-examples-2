import dataclasses
from typing import Dict
from typing import List
from typing import Optional


def recursive_dict(x):
    result_dict = {}
    if isinstance(x, dict):
        key_values = x.items()
    else:
        key_values = x.__dict__.items()

    for key, value in key_values:
        if isinstance(value, List):
            if value and not isinstance(value[0], Dict):
                result_dict[key] = [recursive_dict(i) for i in sorted(value)]
            else:
                result_dict[key] = [recursive_dict(i) for i in value]
        elif '__dict__' in dir(value):
            result_dict[key] = recursive_dict(value)
        else:
            result_dict[key] = value
    return result_dict


@dataclasses.dataclass
class Place:
    place_id: str
    slug: str
    brand_id: Optional[str] = None

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.place_id < other.place_id


@dataclasses.dataclass
class Brand:
    brand_id: str
    slug: str
    _places: Dict[str, Place] = dataclasses.field(default_factory=dict)

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.brand_id < other.brand_id

    def add_place(self, place: Place):
        assert place.place_id not in self._places  # pylint: disable=E1135
        if place.brand_id:
            assert place.brand_id == self.brand_id
        place.brand_id = self.brand_id
        self._places[place.place_id] = place  # pylint: disable=E1137

    def add_places(self, places: List[Place]):
        for place in places:
            self.add_place(place)

    def get_places(self):
        return self._places


@dataclasses.dataclass
class MarketBrandPlace:
    brand_id: str
    place_id: str
    business_id: int
    partner_id: int
    feed_id: int

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return (self.brand_id < other.brand_id) or (
            (self.brand_id == other.brand_id)
            and (self.place_id < other.place_id)
        )


@dataclasses.dataclass
class PlaceInfo:
    partner_id: int
    place_id: str
    place_name: str
    brand_name: Optional[str] = None
    legal_name: Optional[str] = None
    legal_address: Optional[str] = None
    legal_address_postcode: Optional[str] = None
    reg_number: Optional[str] = None
    email: Optional[str] = None
    address_full: Optional[str] = None
    phone: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None
    geo_id: Optional[int] = None
    schedule: Optional[Dict] = None
    assembly_cost: Optional[int] = None
    brand_id: Optional[str] = None

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.partner_id < other.partner_id


@dataclasses.dataclass
class Order:
    order_nr: str
    eater_id: str

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        # order_nr is unique in orders table
        return self.order_nr < other.order_nr
