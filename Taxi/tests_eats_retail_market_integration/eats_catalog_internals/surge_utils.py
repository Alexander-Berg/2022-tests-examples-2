import dataclasses
import typing


@dataclasses.dataclass
class SurgeRadius:
    pedestrian: typing.Optional[int] = None
    taxi: typing.Optional[int] = None
