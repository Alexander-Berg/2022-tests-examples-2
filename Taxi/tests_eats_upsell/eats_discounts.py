import dataclasses


# pylint: disable=invalid-name


@dataclasses.dataclass
class MenuDiscount:
    id: int
    discount_id: int
    value: str
    value_type: str
    name: str
    description: str
    picture_uri: str
    promo_type: str = ' '

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class RestaurantMenuDiscount:
    id: int
    discount_id: int
    value: str
    name: str
    description: str
    picture_uri: str
    value_type: str

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class ProductDiscount:
    id: int
    discount_id: int
    value: str
    bundle: str
    name: str
    description: str
    picture_uri: str

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class V2MatchDiscountsResponse:
    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )
