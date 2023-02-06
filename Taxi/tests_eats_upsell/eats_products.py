import enum
import typing

DEFAULT_PRICE: int = 10


class Mapping(dict):
    def __init__(self, core_id: int, public_id: typing.Optional[str] = None):
        dict.__init__(self)
        self['core_id'] = core_id
        self['public_id'] = public_id or str(core_id)


class OptionGroup(dict):
    def __init__(self):
        dict.__init__(self)


class Picture(dict):
    def __init__(self):
        dict.__init__(self)


class PromoType(dict):
    def __init__(self):
        dict.__init__(self)


class ItemShippingType(str, enum.Enum):
    All = 'all'
    Delivery = 'delivery'
    Pickup = 'pickup'


class RetailItem(dict):
    def __init__(
            self,
            core_item_id: int,
            public_id: typing.Optional[str] = None,
            origin_id: typing.Optional[str] = None,
            name: typing.Optional[str] = None,
            description: typing.Optional[str] = None,
            available: bool = True,
            in_stock: typing.Optional[int] = None,
            price: int = DEFAULT_PRICE,
            decimal_price: typing.Optional[str] = str(DEFAULT_PRICE),
            promo_price: typing.Optional[int] = None,
            decimal_promo_price: typing.Optional[str] = None,
            options_groups: typing.List[OptionGroup] = None,
            picture: typing.Optional[Picture] = None,
            promo_types: typing.List[PromoType] = None,
            adult: bool = False,
            item_shipping_type: ItemShippingType = ItemShippingType.All,
            is_catch_weight: bool = False,
            categories: typing.List[str] = None,
    ):
        dict.__init__(self)

        public_id = public_id or str(core_item_id)
        origin_id = origin_id or str(core_item_id)

        self['id'] = core_item_id
        self['public_id'] = public_id
        self['origin_id'] = origin_id
        self['name'] = name or f'name {public_id}'
        self['description'] = description or f'description {public_id}'
        self['available'] = available
        self['in_stock'] = in_stock
        self['price'] = price
        self['decimal_price'] = decimal_price
        self['promo_price'] = price
        self['promo_decimal_price'] = decimal_price
        self['options_groups'] = options_groups or []
        self['picture'] = picture
        self['weight'] = '100 кг'
        self['weight_number'] = 0
        self['weight_kilograms'] = '100'
        self['promo_types'] = promo_types or []
        self['adult'] = adult
        self['shipping_type'] = item_shipping_type
        self['is_catch_weight'] = is_catch_weight
        self['categories'] = categories or []
