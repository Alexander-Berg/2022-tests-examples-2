import hashlib
import hmac
import random
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
import uuid

from . import driver_info


_DEFAULT_POINT = driver_info.Point(37.39, 55.77)
_DEFAULT_DESTINATION_POINT = driver_info.Point(37.49, 55.75)
_TAGS: List[List[str]] = [
    [],
    ['gold'],
    ['gold', 'lightbox'],
    ['privae_car'],
    ['has_chair', 'lightbox'],
]
_TARIFF_POINTS: List[Dict[str, Union[str, float]]] = [
    {'name': 'moscow', 'lon': 37.39, 'lat': 55.77, 'city_id': 'Москва'},
    {'name': 'tula', 'lon': 37.60, 'lat': 54.20, 'city_id': 'Тула'},
    {'name': 'mytishchi', 'lon': 37.71, 'lat': 56.05, 'city_id': 'Москва'},
]


DEFAULT_SEARCH_AREA = {
    'top_left': {'lon': 37, 'lat': 55},
    'bottom_right': {'lon': 38, 'lat': 56},
}


def generate_id(prefix: str, index: int) -> str:
    return prefix + '{:02}'.format(index)


_HASH_KEY = b'secret_key'
_LICENSE_ID_HASHES: Dict[str, bytes] = {
    generate_id('license', i): hmac.new(
        _HASH_KEY, generate_id('license', i).encode('utf-8'), hashlib.sha256,
    ).digest()
    for i in range(64)
}


def encode_license(license_id: str) -> bytes:
    return _LICENSE_ID_HASHES[license_id]


def decode_license(license_id_hash: bytes) -> str:
    return next(
        key
        for key, value in _LICENSE_ID_HASHES.items()
        if value == license_id_hash
    )


def generate_statuses(index_driver: int) -> driver_info.Statuses:
    order_status = None
    if index_driver % 7 == 0:
        order_status = 'waiting'
    elif index_driver % 7 == 4:
        order_status = 'transporting'
    elif index_driver % 7 == 6:
        order_status = 'driving'
    return driver_info.Statuses('busy', 'order', order_status)


def generate_is_frozen(index_driver: int) -> driver_info.IsFrozen:
    return driver_info.IsFrozen(index_driver % 3 == 0)


def generate_order_info(index_driver: int) -> Optional[driver_info.OrderInfo]:
    if index_driver % 7 in [0, 4, 6]:
        point_b = (
            _DEFAULT_DESTINATION_POINT if index_driver % 7 in [4, 6] else None
        )
        return driver_info.OrderInfo(
            order_id=generate_id('order_id', index_driver), point_b=point_b,
        )
    return None


def generate_payment_methods(index_driver: int) -> driver_info.PaymentMethods:
    if index_driver % 7 == 0:
        dispatch = ['cash', 'card', 'coupon', 'corp']
    elif index_driver % 7 == 1:
        dispatch = ['cash', 'coupon', 'corp']
    elif index_driver % 7 == 2:
        dispatch = ['card']
    elif index_driver % 7 == 3:
        dispatch = []
    elif index_driver % 7 == 4:
        dispatch = ['coupon', 'corp']
    else:
        dispatch = []
    return driver_info.PaymentMethods(
        actual=['card'], dispatch=dispatch, taximeter=['card'],
    )


def generate_parks_activation(drivers: List[driver_info.DriverInfo]):
    parks = []
    for index, driver in enumerate(drivers):
        if driver.payment_methods:
            clid = generate_id('clid', index)
            dispatch = driver.payment_methods.dispatch
            deactivated = not bool(dispatch)
            park: Dict[str, Any] = {
                'revision': index + 1,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': clid,
                'city_id': 'spb',
                'data': {
                    'deactivated': deactivated,
                    'can_cash': bool('cash' in dispatch),
                    'can_card': bool('card' in dispatch),
                    'can_coupon': bool('coupon' in dispatch),
                    'can_corp': bool('corp' in dispatch),
                },
            }
            if deactivated:
                data = park['data']
                data['deactivated_reason'] = 'blocked'
            parks.append(park)
    return parks


def generate_reposition(index_driver: int) -> driver_info.Reposition:
    if index_driver % 2 == 0:
        return driver_info.Reposition(
            True,
            'home' if index_driver % 4 else 'poi',
            driver_info.Point(55.403, 37.96),
        )
    return driver_info.Reposition(False)


def generate_tags(index_driver: int) -> driver_info.Tags:
    index = index_driver % len(_TAGS)
    return driver_info.Tags(_TAGS[index])


def generate_point(index_driver: int) -> driver_info.Point:
    index = index_driver % len(_TARIFF_POINTS)
    lon = _TARIFF_POINTS[index]['lon']
    lat = _TARIFF_POINTS[index]['lat']
    return driver_info.Point(float(lon), float(lat))


def generate_tariff_zone(index_driver: int) -> str:
    index = index_driver % len(_TARIFF_POINTS)
    return str(_TARIFF_POINTS[index]['name'])


def generate_city(index_driver: int) -> str:
    index = index_driver % len(_TARIFF_POINTS)
    return str(_TARIFF_POINTS[index]['city_id'])


def generate_combo_order_ids(index_driver: int) -> Optional[List[str]]:
    if index_driver % 7 in [0, 4, 6]:
        length = random.randint(2, 4)
        return [str(uuid.uuid4()) for _ in range(length)]

    return []


def generate_drivers(
        num_drivers: int,
        point=None,
        car_classes=None,
        tags=None,
        reposition=None,
        is_frozen=None,
        tariff_zone=None,
        payment_methods=None,
        statuses=None,
        order_info=None,
        airports=None,
        location_settings=None,
        city=None,
        combo_order_ids=None,
        taximeter_versions=None,
) -> List[driver_info.DriverInfo]:
    ans = []
    for i in range(num_drivers):
        ans.append(
            driver_info.DriverInfo(
                point(i) if point else _DEFAULT_POINT,
                driver_info.DriverIds(
                    generate_id('dbid', i),
                    generate_id('uuid', i),
                    generate_id('udid', i),
                    generate_id('car_number', i),
                    encode_license(generate_id('license', i)),
                ),
                car_classes=car_classes(i) if car_classes else None,
                tags=tags(i) if tags else None,
                reposition=reposition(i) if reposition else None,
                is_frozen=is_frozen(i) if is_frozen else None,
                tariff_zone=tariff_zone(i) if tariff_zone else None,
                payment_methods=payment_methods(i)
                if payment_methods
                else None,
                statuses=statuses(i) if statuses else None,
                order_info=order_info(i) if order_info else None,
                airports=airports(i) if airports else None,
                location_settings=location_settings(i)
                if location_settings
                else None,
                city=city(i) if city else None,
                combo_order_ids=combo_order_ids(i)
                if combo_order_ids
                else None,
                taximeter_version=taximeter_versions(i)
                if taximeter_versions
                else None,
            ),
        )

    return ans


def generate_repositions(num_drivers: int, reposition) -> Dict[str, Any]:
    ans = {}
    for i in range(num_drivers):
        reposition_data = reposition(i)
        state = (
            {
                'has_session': True,
                'mode': reposition_data.mode,
                'submode': None,
                'active': True,
                'bonus': None,
                'session_id': i,
                'start_point': {
                    'longitude': reposition_data.geopoint.lon,
                    'latitude': reposition_data.geopoint.lat,
                },
                'point': {
                    'longitude': reposition_data.geopoint.lon,
                    'latitude': reposition_data.geopoint.lat,
                },
            }
            if reposition_data.enabled
            else {'has_session': False}
        )

        profile = generate_id('dbid', i) + '_' + generate_id('uuid', i)
        ans[profile] = state

    return ans


def generate_taximeter_versions(
        num_drivers: int,
) -> Optional[driver_info.TaximeterVersion]:
    if num_drivers == 0:
        return driver_info.TaximeterVersion(
            'brand0', 'taximeter_platform0', 'ver0', '0',
        )

    return None
