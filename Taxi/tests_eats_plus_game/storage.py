# pylint: disable=C5521
import datetime
from typing import List


UTC_3: datetime.tzinfo = datetime.timezone(datetime.timedelta(hours=3))


class Business:
    Restaurant = 'restaurant'
    Shop = 'shop'
    Store = 'store'
    Pharmacy = 'pharmacy'
    FuelStation = 'zapravki'


class Currency(dict):
    def __init__(self, sign: str = '$', code: str = 'USD'):
        dict.__init__(self, sign=sign, code=code)


class Country(dict):
    def __init__(
            self,
            country_id: int = 35,
            name: str = 'Россия',
            code: str = 'RU',
            currency: Currency = Currency(),
    ):
        dict.__init__(self)
        self['id'] = country_id
        self['name'] = name
        self['code'] = code
        self['currency'] = currency


class Category(dict):
    def __init__(self, category_id: int = 1, name: str = 'Завтраки'):
        dict.__init__(self)
        self['id'] = category_id
        self['name'] = name


class Place(dict):
    def __init__(
            self,
            place_id: int = 1,
            business: str = Business.Restaurant,
            currency: Currency = Currency(),
            categories: List[Category] = None,
    ):
        dict.__init__(self)

        if categories is None:
            categories = list()

        self['id'] = place_id
        self['business'] = business
        self['categories'] = categories
        self['currency'] = currency
