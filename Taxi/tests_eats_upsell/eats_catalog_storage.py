import enum
from typing import Optional


class Business(str, enum.Enum):
    RESTAURANT = 'restaurant'
    SHOP = 'shop'


class PictureScaleType(str, enum.Enum):
    ASPECT_FIT = 'aspect_fit'
    ASPECT_FILL = 'aspect_fill'


class Brand(dict):
    def __init__(
            self,
            brand_id: int = 1,
            name: Optional[str] = None,
            slug: Optional[str] = None,
            picture_scale_type: PictureScaleType = PictureScaleType.ASPECT_FIT,
    ):
        dict.__init__(self)
        self['id'] = brand_id
        self['slug'] = slug or f'brand_{brand_id}'
        self['name'] = name or f'brand {brand_id}'
        self['picture_scale_type'] = picture_scale_type

    @property
    def brand_id(self) -> int:
        return self['id']


class Place(dict):
    def __init__(
            self,
            slug: str,
            brand: Brand = Brand(),
            business: Business = Business.RESTAURANT,
    ):
        dict.__init__(self)
        self['slug'] = slug
        self['enabled'] = True
        self['name'] = slug
        self['revision'] = 1
        self['type'] = 'native'
        self['business'] = business
        self['launched_at'] = '2021-05-27T12:00:00+03:00'
        self['payment_methods'] = ['cash']
        self['gallery'] = []
        self['brand'] = brand
        self['address'] = {'city': 'Moscow', 'short': 'Moscow, 21-city'}
        self['country'] = {
            'id': 1,
            'name': 'Russian Federation',
            'code': 'RU',
            'currency': {'sign': 'Р', 'code': 'Rub'},
        }
        self['categories'] = []
        self['quick_filters'] = {'general': [], 'wizard': []}
        self['region'] = {
            'id': 77,
            'geobase_ids': [],
            'time_zone': 'MSK+3',
            'name': 'Moscow',
        }
        self['location'] = {'geo_point': [37, 55]}
        self['rating'] = {'users': 5, 'admin': 5, 'count': 100}
        self['price_category'] = {'id': 1, 'name': 'cheap', 'value': 1}
        self['extra_info'] = {}
        self['features'] = {
            'ignore_surge': False,
            'supports_preordering': True,
            'fast_food': False,
        }
        self['timing'] = {
            'preparation': 600,
            'extra_preparation': 180,
            'average_preparation': 840,
        }
        self['sorting'] = {'weight': 1, 'popular': 1}
        self['assembly_cost'] = 0

    @property
    def slug(self) -> str:
        return self['slug']

    @property
    def brand(self) -> Brand:
        return self['brand']


class StoragePlace(dict):
    def __init__(self, place_id: int, place: Place):
        dict.__init__(self)
        self['place_id'] = place_id
        self['created_at'] = '2021-05-27T12:00:00+03:00'
        self['updated_at'] = '2021-05-27T12:00:00+03:00'
        self['place'] = place

    @property
    def place_id(self) -> int:
        return self['place_id']

    @property
    def place(self) -> Place:
        return self['place']

    @property
    def place_slug(self) -> str:
        return self.place.slug

    @property
    def brand(self) -> Brand:
        return self.place.brand


def build_storage_place(
        place_id: int, business: Business = Business.RESTAURANT,
) -> StoragePlace:
    return StoragePlace(
        place_id=place_id,
        place=Place(slug=f'place_{place_id}', business=business),
    )
