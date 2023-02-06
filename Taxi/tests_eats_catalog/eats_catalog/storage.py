# pylint: disable=C5521
import datetime
from datetime import datetime as dt
from enum import Enum
from typing import List
from typing import Optional


UTC_3: datetime.tzinfo = datetime.timezone(datetime.timedelta(hours=3))


class PlaceType:
    Native = 'native'
    Marketplace = 'marketplace'


class Business:
    Restaurant = 'restaurant'
    Shop = 'shop'
    Store = 'store'
    Pharmacy = 'pharmacy'
    FuelStation = 'zapravki'


class PaymentMethod:
    Cash = 'cash'
    Payture = 'payture'
    ApplePay = 'applePay'
    Taxi = 'taxi'
    GooglePay = 'googlePay'
    CardPostPayment = 'cardPostPayment'


class CouriersType:
    Pedestrian = 'pedestrian'
    Bicycle = 'bicycle'
    Vehicle = 'vehicle'
    Monorcycle = 'motorcycle'
    YandexTaxi = 'yandex_taxi'
    ElectircBicycle = 'electric_bicycle'
    YandexRover = 'yandex_rover'


class ShippingType:
    Delivery = 'delivery'
    Pickup = 'pickup'


class ConstraintCode:
    MaxOrderPrice = 'max_order_cost'
    MaxOrderWeight = 'max_order_weight'


class ShopPickingType:
    OurPicking = 'our_picking'
    ShopPicking = 'shop_picking'


class Picture(dict):
    def __init__(
            self,
            media_type: str = 'picture',
            url: str = 'https://avatars.mds.yandex.net/get-eda/h/214x140',
            template: str = '/images/1387779/71876d2d734cf1c006ba-{w}x{h}.jpg',
            weight: int = 10,
    ):
        dict.__init__(self)
        self['type'] = media_type
        self['url'] = url
        self['template'] = template
        self['weight'] = weight


class PictureScaleType(str, Enum):
    AspectFit = 'aspect_fit'
    AspectFill = 'aspect_fill'


class Brand(dict):
    def __init__(
            self,
            brand_id: int = 1,
            slug: str = 'coffee_boy_euocq',
            name='COFFEE BOY',
            picture_scale_type: PictureScaleType = PictureScaleType.AspectFit,
    ):
        dict.__init__(self)
        self['id'] = brand_id
        self['slug'] = slug
        self['name'] = name
        self['picture_scale_type'] = picture_scale_type


class Address(dict):
    def __init__(
            self,
            city: str = 'Москва',
            short: str = 'Новодмитровская улица, 2к6',
    ):
        dict.__init__(self, city=city, short=short)


class Currency(dict):
    def __init__(self, sign: str = '₽', code: str = 'RUB'):
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


class QuickFilter(dict):
    def __init__(
            self,
            quick_filter_id: int = 1,
            slug: str = 'breakfast',
            name: str = 'Завтраки',
    ):
        dict.__init__(self)
        self['id'] = quick_filter_id
        self['slug'] = slug
        self['name'] = name

    @property
    def quick_filter_id(self) -> int:
        return self['id']

    @property
    def slug(self) -> str:
        return self['slug']

    @property
    def name(self) -> str:
        return self['name']


class QuickFilters(dict):
    def __init__(
            self,
            general: List[QuickFilter] = None,
            wizard: List[QuickFilter] = None,
    ):
        default = [
            QuickFilter(quick_filter_id=17, slug='desert', name='Десерты'),
            QuickFilter(quick_filter_id=21, slug='breakfast', name='Завтраки'),
            QuickFilter(
                quick_filter_id=9, slug='healthy', name='Здоровая еда',
            ),
            QuickFilter(quick_filter_id=56, slug='coffe', name='Кофе'),
            QuickFilter(quick_filter_id=61, slug='lunch', name='Ланчи'),
        ]

        if general is None:
            general = default
        if wizard is None:
            wizard = default

        dict.__init__(self, general=general, wizard=wizard)

    def append_common(self, quick_filter: QuickFilter):
        if 'common' not in self:
            self['common'] = []
        self['common'].append(quick_filter)
        return self

    def append_wizard(self, quick_filter: QuickFilter):
        if 'wizard' not in self:
            self['wizard'] = []
        self['wizard'].append(quick_filter)
        return self


class Region(dict):
    def __init__(
            self,
            region_id: int = 1,
            geobase_ids: List[int] = None,
            time_zone: str = 'Europe/Moscow',
            name: str = 'Москва',
    ):
        dict.__init__(self)

        if geobase_ids is None:
            geobase_ids = [255]

        self['id'] = region_id
        self['geobase_ids'] = geobase_ids
        self['time_zone'] = time_zone
        self['name'] = name


class Location(dict):
    def __init__(self, lon: float = 37.5916, lat: float = 55.8129):
        dict.__init__(self, geo_point=[lon, lat])


class NewRating(dict):
    def __init__(
            self, rating: float = 4.8002, show: bool = True, count: int = 123,
    ):
        dict.__init__(self, rating=rating, show=show, count=count)


class PriceCategory(dict):
    def __init__(
            self, price_category_id: int = 1, name='name', value: float = 1,
    ):
        dict.__init__(self)
        self['id'] = price_category_id
        self['name'] = name
        self['value'] = value


class ExtraInfo(dict):
    def __init__(
            self,
            footer_description: Optional[str] = None,
            legal_info_description: Optional[str] = (
                'Исполнитель (продавец): ОБЩЕСТВО С ОГРАНИЧЕННОЙ '
                'ОТВЕТСТВЕННОСТЬЮ "КОФЕ БОЙ", 127015, Москва, ул Вятская, '
                'д 27, стр 11, ИНН 7714457772, рег.номер 1207700043759.'
            ),
    ):
        dict.__init__(
            self,
            footer_description=footer_description,
            legal_info_description=legal_info_description,
        )


class BrandUIBackground(dict):
    def __init__(self, theme: str = 'dark', color: str = '#bada55'):
        dict.__init__(self, theme=theme, color=color)


class BrandUILogo(dict):
    def __init__(
            self,
            theme: str = 'dark',
            url: str = 'https://avatars.mds.yandex.net/get-eda/aaaaaa/214x140',
            size: str = 'small',
    ):
        dict.__init__(self, theme=theme, url=url, size=size)


class Constraint(dict):
    def __init__(self, code: str, value: int):
        dict.__init__(self, code=code, value=value)


class Features(dict):
    def __init__(
            self,
            ignore_surge: bool = False,
            supports_preordering: bool = True,
            fast_food: bool = False,
            eco_package: bool = False,
            visibility_mode: str = 'on',
            availability_strategy: Optional[str] = 'default',
            editorial_verdict: Optional[str] = None,
            editorial_description: Optional[str] = None,
            brand_ui_backgrounds: List[BrandUIBackground] = None,
            brand_ui_logos: List[BrandUILogo] = None,
            constraints: List[Constraint] = None,
            shop_picking_type: ShopPickingType = None,
    ):

        if brand_ui_backgrounds is None:
            brand_ui_backgrounds = [BrandUIBackground()]

        if brand_ui_logos is None:
            brand_ui_logos = [BrandUILogo()]

        dict.__init__(
            self,
            ignore_surge=ignore_surge,
            supports_preordering=supports_preordering,
            fast_food=fast_food,
            eco_package=eco_package,
            visibility_mode=visibility_mode,
            availability_strategy=availability_strategy,
            editorial_verdict=editorial_verdict,
            editorial_description=editorial_description,
            brand_ui_backgrounds=brand_ui_backgrounds,
            brand_ui_logos=brand_ui_logos,
            constraints=constraints,
            shop_picking_type=shop_picking_type,
        )


class PlaceTiming(dict):
    def __init__(
            self,
            preparation: float = 10 * 60,
            extra_preparation: float = 0,
            average_preparation: float = 12 * 60,
    ):
        dict.__init__(
            self,
            preparation=preparation,
            extra_preparation=extra_preparation,
            average_preparation=average_preparation,
        )


class Sorting(dict):
    def __init__(self, weight: int = 1, popular: int = 1, wizard: int = 1):
        dict.__init__(self, weight=weight, popular=popular, wizard=wizard)


class WorkingInterval(dict):
    def __init__(self, start: dt, end: dt):
        dict.__init__(self)
        self['from'] = start.isoformat('T')
        self['to'] = end.isoformat('T')


class Place(dict):
    def __init__(
            self,
            place_id: int = 1,
            slug: str = 'coffee_boy_novodmitrovskaya_2k6',
            enabled: bool = True,
            name: str = 'Тестовое заведение 1293',
            place_type: str = PlaceType.Native,
            business: str = Business.Restaurant,
            launched_at: Optional[dt] = None,
            payment_methods: List[str] = None,
            gallery: List[Picture] = None,
            brand: Brand = Brand(),
            address: Address = Address(),
            country: Country = Country(),
            categories: List[Category] = None,
            quick_filters: QuickFilters = QuickFilters(),
            region: Region = Region(),
            location: Location = Location(),
            price_category: PriceCategory = PriceCategory(),
            extra_info: ExtraInfo = ExtraInfo(),
            features: Features = Features(),
            timing: PlaceTiming = PlaceTiming(),
            sorting: Sorting = Sorting(),
            assembly_cost: float = 123,
            new_rating: NewRating = NewRating(),
            working_intervals: List[WorkingInterval] = None,
            allowed_couriers_types: List[CouriersType] = None,
            tags: Optional[List[str]] = None,
            real_updated_at: Optional[dt] = None,
    ):
        dict.__init__(self)

        if payment_methods is None:
            payment_methods = [
                PaymentMethod.Payture,
                PaymentMethod.ApplePay,
                PaymentMethod.Taxi,
                PaymentMethod.GooglePay,
            ]

        if gallery is None:
            gallery = [Picture()]

        if categories is None:
            categories = [Category()]

        if launched_at is None:
            launched_at = dt.combine(
                datetime.datetime(2018, 1, 12),
                datetime.time(12, 12),
                tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
            )

        if real_updated_at is None:
            real_updated_at = dt.combine(
                datetime.datetime(2018, 1, 12),
                datetime.time(12, 12),
                tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
            )

        if working_intervals is None:
            working_intervals = []

        if allowed_couriers_types is None:
            allowed_couriers_types = []

        if tags is None:
            tags = []

        self['id'] = place_id
        self['slug'] = slug
        self['enabled'] = enabled
        self['name'] = name
        self['type'] = place_type
        self['business'] = business
        self['launched_at'] = launched_at.isoformat('T')
        self['payment_methods'] = payment_methods
        self['gallery'] = gallery
        self['brand'] = brand
        self['address'] = address
        self['country'] = country
        self['categories'] = categories
        self['quick_filters'] = quick_filters
        self['region'] = region
        self['location'] = location
        self['price_category'] = price_category
        self['extra_info'] = extra_info
        self['features'] = features
        self['timing'] = timing
        self['sorting'] = sorting
        self['assembly_cost'] = assembly_cost
        self['new_rating'] = new_rating
        self['working_intervals'] = working_intervals
        self['allowed_couriers_types'] = allowed_couriers_types
        self['tags'] = tags
        self['real_updated_at'] = real_updated_at.isoformat('T')


class DeliveryCondition(dict):
    def __init__(self, order_cost: int, delivery_cost: int):
        dict.__init__(self, order_cost=order_cost, delivery_cost=delivery_cost)


class ZoneTiming(dict):
    def __init__(self, code: str, value: float):
        dict.__init__(self, code=code, value=value)


class ZoneTimings(list):
    def __init__(
            self,
            market_avg_time: float = 20 * 60,
            arrival_time: float = 20 * 60,
    ):
        timings: List[ZoneTiming] = []
        if market_avg_time is not None:
            timings.append(
                ZoneTiming(code='market_avg_time', value=market_avg_time),
            )
        if arrival_time:
            timings.append(ZoneTiming(code='arrival_time', value=arrival_time))
        list.__init__(self, timings)


class Polygon(dict):
    def __init__(self, edges: List[List[float]] = None):
        dict.__init__(self)

        if edges is None:
            edges = [
                [36.98822021484375, 55.4204408577456],
                [38.395843505859375, 55.4204408577456],
                [38.395843505859375, 56.03676022216059],
                [36.98822021484375, 56.03676022216059],
                [36.98822021484375, 55.4204408577456],
            ]

        self['coordinates'] = [edges]


class SourceInfo(dict):
    def __init__(self, source: str, external_id: str):
        dict.__init__(self)
        self['source'] = source
        self['external_id'] = external_id


class ZoneFeatures(dict):
    def __init__(self, is_ultima: bool):
        dict.__init__(self)
        self['is_ultima'] = is_ultima


class Zone(dict):
    def __init__(
            self,
            place_id: int = 1,
            zone_id: int = 1,
            couriers_zone_id: int = 1,
            enabled: bool = True,
            name: str = 'Zone Name',
            couriers_type: str = CouriersType.Pedestrian,
            shipping_type: str = ShippingType.Delivery,
            delivery_conditions: List[DeliveryCondition] = None,
            timing: ZoneTimings = ZoneTimings(),
            working_intervals: List[WorkingInterval] = None,
            polygon: Polygon = Polygon(),
            source_info: SourceInfo = None,
            features: Optional[ZoneFeatures] = None,
            real_updated_at: Optional[dt] = None,
    ):
        dict.__init__(self)

        if working_intervals is None:
            working_intervals = create_working_intervals(
                start_hour=10, start_minute=20, end_hour=19, end_minute=38,
            )

        if delivery_conditions is None:
            delivery_conditions = [
                DeliveryCondition(order_cost=0, delivery_cost=139),
                DeliveryCondition(order_cost=2000, delivery_cost=0),
                DeliveryCondition(order_cost=500, delivery_cost=89),
            ]

        if source_info is None:
            source_info = SourceInfo(
                source='eats_core', external_id=str(zone_id),
            )

        if real_updated_at is None:
            real_updated_at = dt.combine(
                datetime.datetime(2018, 1, 12),
                datetime.time(12, 12),
                tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
            )

        self['id'] = zone_id
        self['place_id'] = place_id
        self['couriers_zone_id'] = couriers_zone_id
        self['enabled'] = enabled
        self['name'] = name
        self['couriers_type'] = couriers_type
        self['shipping_type'] = shipping_type
        self['delivery_conditions'] = delivery_conditions
        self['timing'] = timing
        self['working_intervals'] = working_intervals
        self['polygon'] = polygon
        self['source_info'] = source_info
        self['features'] = features
        self['real_updated_at'] = real_updated_at.isoformat('T')


def create_working_intervals(
        start_hour: int = 8,
        start_minute: int = 0,
        end_hour: int = 20,
        end_minute: int = 0,
) -> List[WorkingInterval]:

    today: datetime.date = datetime.date.today()
    yesterday: datetime.date = today - datetime.timedelta(days=1)
    tomorrow: datetime.date = today + datetime.timedelta(days=1)

    start_time = datetime.time(hour=start_hour, minute=start_minute)
    end_time = datetime.time(hour=end_hour, minute=end_minute)

    return [
        WorkingInterval(
            start=dt.combine(yesterday, start_time, tzinfo=UTC_3),
            end=dt.combine(yesterday, end_time, tzinfo=UTC_3),
        ),
        WorkingInterval(
            start=dt.combine(today, start_time, tzinfo=UTC_3),
            end=dt.combine(today, end_time, tzinfo=UTC_3),
        ),
        WorkingInterval(
            start=dt.combine(tomorrow, start_time, tzinfo=UTC_3),
            end=dt.combine(tomorrow, end_time, tzinfo=UTC_3),
        ),
    ]


def opened_at(time) -> List[WorkingInterval]:
    return [
        WorkingInterval(
            start=time - datetime.timedelta(hours=2),
            end=time + datetime.timedelta(hours=2),
        ),
    ]


def closed_at(time) -> List[WorkingInterval]:
    return [
        WorkingInterval(
            start=time + datetime.timedelta(hours=2),
            end=time + datetime.timedelta(hours=4),
        ),
    ]
