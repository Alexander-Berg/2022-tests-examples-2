# flake8: noqa IS001
from typing import List, Optional


class Point:
    EPS = 1e-6

    def __init__(self, lon: float, lat: float):
        self.lon = lon
        self.lat = lat

    def __eq__(self, other):
        return (
            abs(self.lon - other.lon) < Point.EPS
            and abs(self.lat - other.lat) < Point.EPS
        )


class DriverIds:
    def __init__(
            self,
            park_id: str,
            driver_profile_id: str,
            udid: Optional[str] = None,
            car_number: Optional[str] = None,
            driver_license_hash: Optional[bytes] = None,
    ):
        self.park_id = park_id
        self.driver_profile_id = driver_profile_id
        self.udid = udid
        self.car_number = car_number
        self.driver_license_hash = driver_license_hash

    def __eq__(self, other):
        return (
            self.park_id == other.park_id
            and self.driver_profile_id == other.driver_profile_id
            and self.udid == other.udid
            and self.car_number == other.car_number
            and self.driver_license_hash == other.driver_license_hash
        )


class CarClasses:
    def __init__(
            self,
            actual: List[str],
            dispatch: List[str],
            taximeter: List[str],
            chain: List[str],
    ):
        self.actual = actual
        self.dispatch = dispatch
        self.taximeter = taximeter
        self.chain = chain

    def __eq__(self, other):
        return (
            sorted(self.actual) == sorted(other.actual)
            and sorted(self.dispatch) == sorted(other.dispatch)
            and sorted(self.taximeter) == sorted(other.taximeter)
            and sorted(self.chain) == sorted(other.chain)
        )


class Tags:
    def __init__(self, tag_names: List[str]):
        self.tag_names = tag_names

    def __eq__(self, other):
        return sorted(self.tag_names) == sorted(other.tag_names)


class Reposition:
    def __init__(
            self,
            enabled: bool,
            mode: Optional[str] = None,
            geopoint: Optional[Point] = None,
    ):
        self.enabled = enabled
        self.mode = mode
        self.geopoint = geopoint

    def __eq__(self, other):
        return (
            self.enabled == other.enabled
            and self.mode == other.mode
            and self.geopoint == other.geopoint
        )


class IsFrozen:
    def __init__(self, freeze: bool):
        self.freeze = freeze

    def __eq__(self, other):
        return self.freeze == other.freeze


# pylint: disable=W0102
class PaymentMethods:
    def __init__(
            self,
            actual: List[str] = [],
            dispatch: List[str] = [],
            taximeter: List[str] = [],
    ):
        self.actual = actual
        self.dispatch = dispatch
        self.taximeter = taximeter

    def __eq__(self, other):
        return (
            sorted(self.actual) == sorted(other.actual)
            and sorted(self.dispatch) == sorted(other.dispatch)
            and sorted(self.taximeter) == sorted(other.taximeter)
        )


class Statuses:
    def __init__(
            self, driver: str, taximeter: str, order: Optional[str] = None,
    ):
        self.driver = driver
        self.taximeter = taximeter
        self.order = order

    def __eq__(self, other):
        return (
            self.driver == other.driver
            and self.taximeter == other.taximeter
            and self.order == other.order
        )


class OrderInfo:
    def __init__(
            self,
            order_id: str,
            chained_id: Optional[str] = None,
            point_b: Optional[Point] = None,
    ):
        self.order_id = order_id
        self.chained_id = chained_id
        self.point_b = point_b

    def __eq__(self, other):
        return (
            self.order_id == other.order_id
            and self.chained_id == other.chained_id
            and self.point_b == other.point_b
        )


class Airports:
    def __init__(self, queue_place: int):
        self.queue_place = queue_place

    def __eq__(self, other):
        return self.queue_place == other.queue_place


class LocationSettings:
    def __init__(self, realtime_source: str, verified_source: str):
        self.realtime_source = realtime_source
        self.verified_source = verified_source

    def __eq__(self, other):
        return (
            self.realtime_source == other.realtime_source
            and self.verified_source == other.verified_source
        )


class TaximeterVersion:
    def __init__(
            self,
            taximeter_brand: Optional[str] = None,
            taximeter_platform: Optional[str] = None,
            taximeter_version: Optional[str] = None,
            taximeter_version_type: Optional[str] = None,
    ):
        self.taximeter_brand = taximeter_brand
        self.taximeter_platform = taximeter_platform
        self.taximeter_version = taximeter_version
        self.taximeter_version_type = taximeter_version_type

    def __eq__(self, other):
        return (
            self.taximeter_brand == other.taximeter_brand
            and self.taximeter_platform == other.taximeter_platform
            and self.taximeter_version == other.taximeter_version
            and self.taximeter_version_type == other.taximeter_version_type
        )


class DriverInfo:
    def __init__(
            self,
            geopoint: Point,
            ids: DriverIds,
            car_classes: Optional[CarClasses] = None,
            tags: Optional[Tags] = None,
            reposition: Optional[Reposition] = None,
            is_frozen: Optional[IsFrozen] = None,
            tariff_zone: Optional[str] = None,
            payment_methods: Optional[PaymentMethods] = None,
            statuses: Optional[Statuses] = None,
            order_info: Optional[OrderInfo] = None,
            airports: Optional[Airports] = None,
            location_settings: Optional[LocationSettings] = None,
            city: Optional[str] = None,
            combo_order_ids: Optional[List[str]] = None,
            taximeter_version: Optional[TaximeterVersion] = None,
    ):
        self.geopoint = geopoint
        self.ids = ids
        self.car_classes = car_classes
        self.tags = tags
        self.reposition = reposition
        self.is_frozen = is_frozen
        self.tariff_zone = tariff_zone
        self.payment_methods = payment_methods
        self.statuses = statuses
        self.order_info = order_info
        self.airports = airports
        self.location_settings = location_settings
        self.city = city
        self.combo_order_ids = combo_order_ids
        self.taximeter_version = taximeter_version

    def __eq__(self, other):
        return (
            self.geopoint == other.geopoint
            and self.ids == other.ids
            and self.car_classes == other.car_classes
            and self.tags == other.tags
            and self.reposition == other.reposition
            and self.is_frozen == other.is_frozen
            and self.tariff_zone == other.tariff_zone
            and self.payment_methods == other.payment_methods
            and self.statuses == other.statuses
            and self.order_info == other.order_info
            and self.airports == other.airports
            and self.location_settings == other.location_settings
            and self.city == other.city
            and self.combo_order_ids == other.combo_order_ids
            and self.taximeter_version == other.taximeter_version
        )


def compare_drivers(lhs, rhs, categories):
    def should_check(name: str):
        return name in categories

    # required field
    assert lhs.geopoint == rhs.geopoint
    # required subfields
    if should_check('ids'):
        assert lhs.ids == rhs.ids
    else:
        assert lhs.ids.park_id == rhs.ids.park_id
        assert lhs.ids.driver_profile_id == rhs.ids.driver_profile_id
        assert lhs.ids.udid is None
        assert lhs.ids.car_number is None

    for field_category in [
            'car_classes',
            'is_frozen',
            'reposition',
            'tags',
            'tariff_zone',
            'payment_methods',
            'statuses',
            'airports',
            'location_settings',
            'taximeter_version',
    ]:
        lhs_field = getattr(lhs, field_category)
        if should_check(field_category):
            assert lhs_field == getattr(rhs, field_category)
        else:
            assert lhs_field is None

    compare_order_info(lhs, rhs, categories)


def compare_order_info(lhs, rhs, categories):
    def should_check(name: str):
        return name in categories

    field_category = 'order_info'
    if should_check(field_category):
        lhs_field = getattr(lhs, field_category)
        rhs_field = getattr(rhs, field_category)
        if rhs_field is None:
            assert lhs_field == OrderInfo(
                order_id='', point_b=Point(lon=0, lat=0),
            )
        else:
            assert lhs_field == rhs_field
