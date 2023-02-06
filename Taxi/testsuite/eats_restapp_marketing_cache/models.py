import dataclasses


@dataclasses.dataclass
class PlaceBanner:
    place_id: int
    banner_id: int

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)
