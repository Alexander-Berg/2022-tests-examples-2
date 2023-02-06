import dataclasses
import enum
import typing


@dataclasses.dataclass
class CategoryIds:
    # pylint: disable=C0103
    id: str
    legacy_id: typing.Optional[int] = None

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class CategoryInfo:
    # pylint: disable=C0103
    id: str
    name: str
    legacy_id: typing.Optional[int] = None

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


class ShippingType(str, enum.Enum):
    Delivery = 'delivery'
    Pickup = 'pickup'


@dataclasses.dataclass
class Picture:
    url: str
    avatarnica_identity: typing.Optional[str] = None
    ratio: typing.Optional[float] = None
    sort: typing.Optional[int] = None


@dataclasses.dataclass
class Weight:
    unit: str
    value: str
