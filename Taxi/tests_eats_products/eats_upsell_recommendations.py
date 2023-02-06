import dataclasses
import enum

PUBLIC_IDS = [
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
]


class Source(str, enum.Enum):
    Complement = 'complement'
    Advert = 'advert'


@dataclasses.dataclass
class Recommendation:
    public_id: str
    source: Source = Source.Complement

    def asdict(self) -> dict:
        return dataclasses.asdict(self)


DEFAULT_RECOMMENDATIONS = [
    Recommendation(PUBLIC_IDS[0], Source.Advert),
    Recommendation(PUBLIC_IDS[1], Source.Advert),
    Recommendation(PUBLIC_IDS[2], Source.Advert),
]
