import enum
import typing

from psycopg2 import extensions


class Business(enum.Enum):
    restaurant = enum.auto()
    shop = enum.auto()
    store = enum.auto()
    pharmacy = enum.auto()
    zapravki = enum.auto()


def adapt_business(business: Business):
    return extensions.adapt(business.name)


extensions.register_adapter(Business, adapt_business)


class Position(typing.NamedTuple):
    lon: float
    lat: float


def adapt_position(position: Position):
    lon = extensions.adapt(position.lon)
    lat = extensions.adapt(position.lat)
    return extensions.AsIs('point(%s, %s)' % (lon, lat))


extensions.register_adapter(Position, adapt_position)


class Ring:
    def __init__(self, positions: typing.List[Position]):
        self.positions = positions


def adapt_ring(ring: Ring):
    points = []
    for point in ring.positions:
        points.append(
            '(%s, %s)'
            % (extensions.adapt(point.lon), extensions.adapt(point.lat)),
        )

    return extensions.AsIs('\'{"(%s)"}\'' % ','.join(points))


extensions.register_adapter(Ring, adapt_ring)


def default_polygon() -> Ring:
    return Ring(
        [
            Position(0, 0),
            Position(0, 1),
            Position(1, 1),
            Position(1, 0),
            Position(0, 0),
        ],
    )


class Brand(typing.NamedTuple):
    # Идентификатор бренда
    brand_id: int
    # Слаг бренда
    slug: str = 'test_brand'
    # Название бренда
    name: str = 'Test Brand'


def adapt_brand(brand: Brand):
    brand_slug = extensions.adapt(brand.slug)
    brand_name = extensions.adapt(brand.name)
    return extensions.AsIs(
        """
        (
            %s,
            %s,
            %s,
            'aspect_fit'
        )::storage.place_brand_v2
        """
        % (brand.brand_id, brand_slug, brand_name),
    )


extensions.register_adapter(Brand, adapt_brand)


class Place(typing.NamedTuple):
    # Идентификатор заведения
    place_id: int
    # Слаг заведения
    slug: str = 'test_place'
    # Название заведения
    name: str = 'Test Place'
    # Бизнес заведения
    business: Business = Business.restaurant
    # Бренд
    brand: Brand = Brand(brand_id=1)
    # Локация заведения
    location: Position = Position(lon=0, lat=0)
    # Флаг активации заведения
    enabed: bool = True


class DeliverZone(typing.NamedTuple):
    # Идентифкатор зоны доставки
    zone_id: int
    # Внешний идентфифкатор
    external_id: str
    # Идентификатор заведения к которому привязана зона
    place_id: int
    # Полигон зоны доставки
    polygon: Ring
    # Название зоны
    name: str = 'Test Zone'
    # Флаг активации заведения
    enabled: bool = True


def insert_place(db, place: Place):
    time = '2022-04-05T13:20:00+03:00'

    db.cursor().execute(
        """
        INSERT INTO storage.places (
            id,
            created_at,
            updated_at,
            slug,
            enabled,
            name,
            business,
            launched_at,
            brand,
            location,
            revision,
            type,
            payment_methods,
            gallery,
            address,
            country,
            categories,
            quick_filters,
            wizard_quick_filters,
            region,
            price_category,
            assembly_cost,
            rating,
            extra_info,
            features,
            timing,
            sorting,
            working_intervals,
            allowed_couriers_types
        ) VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            nextval('storage.places_revision'),
            'native',
            ARRAY['cash','taxi']::storage.place_payment_method[],
            ARRAY[]::storage.place_gallery[],
            ('city','short')::storage.place_address,
            (
                1,
                'name',
                'code',
                ('code','sign')::storage.place_country_currency
            )::storage.place_country,
            ARRAY[]::storage.place_category[],
            ARRAY[]::storage.place_quick_filter[],
            ARRAY[]::storage.place_quick_filter[],
            (1,'{1,2}'::bigint[],'zone','name')::storage.place_region,
            (1,'name',0.5)::storage.place_price_category,
            123,
            '{"shown":4.83, "users":4.5, "admin":1.0, "count":200}',
            '{}',
            '{
                "fast_food": true,
                "ignore_surge": false,
                "supports_preordering": false
            }',
            '{
                "preparation": 300,
                "extra_preparation": 300,
                "average_preparation": 300
            }',
            '{"popular": 1, "weight": 1, "wizard": 1}',
            ARRAY[]::storage.working_interval[],
            ARRAY[]::storage.delivery_zone_couriers_type[]
        )
        """,
        (
            place.place_id,  # id
            time,  # created_at
            time,  # updated_at
            place.slug,  # slug
            place.enabed,  # enabled
            place.name,  # name
            place.business,  # business
            time,  # launched_at
            place.brand,  # brand
            place.location,  # location
        ),
    )


def insert_delivery_zone(db, zone: DeliverZone):
    db.cursor().execute(
        """
        INSERT INTO storage.delivery_zones(
            id,
            external_id,
            place_id,
            name,
            enabled,
            polygons,
            source,
            places_ids,
            couriers_zone_id,
            created_at,
            updated_at,
            revision,
            couriers_type,
            shipping_type,
            delivery_conditions,
            market_avg_time,
            arrival_time,
            working_intervals
        ) VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            'eats_core',
            NULL,
            1000,
            '2020-10-10T07:07:07+03:00',
            '2020-10-10T07:07:07+03:00',
            nextval('storage.delivery_zones_revision'),
            'vehicle',
            'delivery',
            ARRAY[
                (100,200)::storage.delivery_zone_delivery_condition
            ]::storage.delivery_zone_delivery_condition[],
            100.2,
            600.5,
            ARRAY[(
                '2020-10-10T10:00:00+03:00',
                '2020-10-10T19:00:00+03:00'
            )::storage.working_interval]::storage.working_interval[]
        )
        """,
        (
            zone.zone_id,
            zone.external_id,
            zone.place_id,
            zone.name,
            zone.enabled,
            zone.polygon,
        ),
    )
