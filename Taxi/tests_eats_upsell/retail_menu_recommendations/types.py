import enum
import typing


class RequestShippingType(str, enum.Enum):
    DELIVERY = 'delivery'
    PICKUP = 'pickup'


class RequestItem(dict):
    def __init__(self, public_id: str, categories: typing.List[str] = None):
        dict.__init__(self)
        self['public_id'] = public_id
        if categories:
            self['public_category_ids'] = categories


class Location(dict):
    def __init__(
            self, latitude: float = 55.567235, longitude: float = 37.345891,
    ):
        dict.__init__(self)
        self['latitude'] = latitude
        self['longitude'] = longitude


class RecommendationSource(str, enum.Enum):
    COMPLEMENT = 'complement'
    ADVERT = 'advert'


class Recommendation(dict):
    def __init__(
            self,
            public_id: str,
            source: RecommendationSource = RecommendationSource.COMPLEMENT,
    ):
        dict.__init__(self)
        self['public_id'] = public_id
        self['source'] = source
