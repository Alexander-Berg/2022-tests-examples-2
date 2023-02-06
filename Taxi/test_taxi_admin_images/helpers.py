import dataclasses
import typing


@dataclasses.dataclass
class RealImage:
    format: str
    size: typing.Optional[typing.Tuple[int, int]] = None
