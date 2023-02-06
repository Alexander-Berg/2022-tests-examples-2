import dataclasses


@dataclasses.dataclass
class UmlaasEta:
    place_id: int
    eta_min: int
    eta_max: int
