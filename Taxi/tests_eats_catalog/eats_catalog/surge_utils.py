import dataclasses
import typing


@dataclasses.dataclass
class SurgeRadius:
    pedestrian: typing.Optional[int] = None
    taxi: typing.Optional[int] = None
    native_surge_level: int = 0
    lavka_surge_level: int = 0
    additional_fee: int = 0
    minimum_order: int = 0
