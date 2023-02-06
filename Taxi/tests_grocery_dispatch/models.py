# pylint: disable=import-only-modules
# flake8: noqa F401
import dataclasses
from tests_grocery_dispatch import constants as const
from typing import List
from typing import Optional
from typing import Sequence


@dataclasses.dataclass
class TimeInterval:
    interval_type: str
    time_from: str
    time_to: str

    def as_object(self):
        result = {
            'type': self.interval_type,
            'from': self.time_from,
            'to': self.time_to,
        }
        return result


@dataclasses.dataclass
class CargoRoutePoint:
    point_id: int
    short_order_id: str
    visit_order: int
    type: str

    coordinates: Sequence[float]
    country: Optional[str]
    city: Optional[str]
    street: Optional[str]
    building: Optional[str]
    floor: Optional[str]
    flat: Optional[str]
    door_code: Optional[str]
    phone: str
    name: str
    comment: Optional[str]
    place_id: Optional[str]
    time_intervals: List[TimeInterval]
    additional_phone_code: Optional[str] = None
    door_code_extra: Optional[str] = None
    doorbell_name: Optional[str] = None
    building_name: Optional[str] = None
    leave_under_door: Optional[bool] = None
    meet_outside: Optional[bool] = None
    no_door_call: Optional[bool] = None
    visited_at_expected_ts: Optional[str] = None
    entrance: Optional[str] = None
    visit_status: str = 'pending'
    postal_code: Optional[str] = None
    modifier_age_check: Optional[bool] = None

    def as_object(self):
        result = {
            'point_id': self.point_id,
            'type': self.type,
            'visit_order': self.visit_order,
            'external_order_id': self.short_order_id,
            'skip_confirmation': True,
            'address': {'coordinates': self.coordinates},
            'contact': {'phone': self.phone, 'name': self.name},
        }
        if self.additional_phone_code:
            result['contact'][
                'phone_additional_code'
            ] = self.additional_phone_code
        if self.time_intervals:
            result['time_intervals'] = [
                item.as_object() for item in self.time_intervals
            ]
        if self.comment:
            result['address']['comment'] = self.comment
        if self.leave_under_door:
            result['leave_under_door'] = self.leave_under_door
        if self.meet_outside:
            result['meet_outside'] = self.meet_outside
        if self.no_door_call:
            result['no_door_call'] = self.no_door_call
        if self.modifier_age_check:
            result['modifier_age_check'] = self.modifier_age_check
        address_parts = []
        if self.country:
            result['address']['country'] = self.country
            address_parts.append(self.country)
        if self.city:
            result['address']['city'] = self.city
            address_parts.append(self.city)
        if self.postal_code:
            address_parts.append(self.postal_code)
        if self.street:
            result['address']['street'] = self.street
            address_parts.append(self.street)
        if self.building:
            result['address']['building'] = self.building
            address_parts.append(self.building)
        if self.floor:
            result['address']['sfloor'] = self.floor
        if self.flat:
            result['address']['sflat'] = self.flat
            address_parts.append(self.flat)
        if self.door_code:
            result['address']['door_code'] = self.door_code
        if self.door_code_extra:
            result['address']['door_code_extra'] = self.door_code_extra
        if self.doorbell_name:
            result['address']['doorbell_name'] = self.doorbell_name
        if self.building_name:
            result['address']['building_name'] = self.building_name
        if self.place_id:
            result['address']['uri'] = self.place_id
        if self.entrance is not None:
            result['address']['porch'] = self.entrance

        full_address = ', '.join(address_parts)
        result['address']['fullname'] = full_address
        result['address']['shortname'] = full_address

        return result

    def as_response_object(self):
        result = self.as_object()
        result['id'] = result['point_id']
        del result['point_id']
        result['visit_status'] = self.visit_status
        if self.visited_at_expected_ts:
            result['visited_at'] = {'expected': self.visited_at_expected_ts}
        return result


NOW = '2020-10-05T16:28:00+00:00'
NOW_TS = 1601915280
DELIVERY_ETA_TS = '2020-10-05T16:38:00.000Z'

DELIVERY_PERFECT_TIME = '2020-10-05T16:58:00+00:00'
# now + max_eta + time_intervals_endpoint_strict_span
DELIVERY_STRICT_TIME = '2020-10-05T17:03:00+00:00'

SHORT_ORDER_ID = 'short-order-id-42'

FAKE_ITEM = {
    'cost_currency': 'RUB',
    'cost_value': '0',
    'droppof_point': 3,
    'extra_id': 'PullDispatchFakeItemId',
    'pickup_point': 1,
    'quantity': 1,
    'title': 'PullDispatchFakeItem',
}

FIRST_POINT = CargoRoutePoint(
    point_id=1,
    visit_order=1,
    type='source',
    coordinates=[37.601295, 55.585286],
    country='Russia',
    city='Moscow',
    street='Varshavskoye Highway',
    building='141Ак1',
    floor=None,
    flat=None,
    door_code=None,
    phone='+78005553535',
    name='ЯндексЛавка',
    comment='dispatch_depot_comment',
    short_order_id=SHORT_ORDER_ID,
    place_id='ymapsbm1://geo?ll=37.601%2C55.585&spn=0.001%2C0.001&'
    'text=%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%2C%20%D0%9C'
    '%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C%20%D0%92%D0%B0%D1%80'
    '%D1%88%D0%B0%D0%B2%D1%81%D0%BA%D0%BE%D0%B5%20%D1%88%D0%'
    'BE%D1%81%D1%81%D0%B5%2C%20141%D0%90%D0%BA1%2C%20%D0%BF'
    '%D0%BE%D0%B4%D1%8A%D0%B5%D0%B7%D0%B4%201%20%7B3457696635%7D',
    time_intervals=[],
)

CLIENT_POINT = CargoRoutePoint(
    point_id=2,
    visit_order=2,
    type='destination',
    coordinates=[39.60258, 52.569089],
    country=None,
    city='city',
    street='street',
    building=None,
    floor='floor',
    flat='flat',
    door_code='doorcode',
    door_code_extra='door_code_extra',
    doorbell_name='doorbell_name',
    building_name='building_name',
    phone='+79991012345',
    name='Клиент',
    comment='user comment',
    short_order_id=SHORT_ORDER_ID,
    place_id=None,
    time_intervals=[
        TimeInterval(
            interval_type='perfect_match',
            time_from=NOW,
            time_to=DELIVERY_PERFECT_TIME,
        ),
        TimeInterval(
            interval_type='strict_match',
            time_from=NOW,
            time_to=DELIVERY_STRICT_TIME,
        ),
    ],
)

CLIENT_POINT_LEAVE_UNDER_DOOR = CargoRoutePoint(
    point_id=2,
    visit_order=2,
    type='destination',
    coordinates=[39.60258, 52.569089],
    country=None,
    city='city',
    street='street',
    building=None,
    floor='floor',
    flat='flat',
    door_code='doorcode',
    door_code_extra='door_code_extra',
    doorbell_name='doorbell_name',
    building_name='building_name',
    leave_under_door=True,
    phone='+79991012345',
    name='Клиент',
    comment='leave_under_door_comment user comment',
    short_order_id=SHORT_ORDER_ID,
    place_id=None,
    time_intervals=[
        TimeInterval(
            interval_type='perfect_match',
            time_from=NOW,
            time_to=DELIVERY_PERFECT_TIME,
        ),
        TimeInterval(
            interval_type='strict_match',
            time_from=NOW,
            time_to=DELIVERY_STRICT_TIME,
        ),
    ],
)

RETURN_POINT = CargoRoutePoint(
    point_id=3,
    visit_order=3,
    type='destination',
    coordinates=[37.601295, 55.585286],
    country='Russia',
    city='Moscow',
    street='Varshavskoye Highway',
    building='141Ак1',
    floor=None,
    flat=None,
    door_code=None,
    phone='+78005553535',
    name='ЯндексЛавка',
    comment=None,
    short_order_id=SHORT_ORDER_ID,
    place_id='ymapsbm1://geo?ll=37.601%2C55.585&spn=0.001%2C0.001&'
    'text=%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%2C%20%D0%9C'
    '%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C%20%D0%92%D0%B0%D1%80'
    '%D1%88%D0%B0%D0%B2%D1%81%D0%BA%D0%BE%D0%B5%20%D1%88%D0%'
    'BE%D1%81%D1%81%D0%B5%2C%20141%D0%90%D0%BA1%2C%20%D0%BF'
    '%D0%BE%D0%B4%D1%8A%D0%B5%D0%B7%D0%B4%201%20%7B3457696635%7D',
    time_intervals=[],
)


CREATE_REQUEST_DATA = {
    'order_id': const.ORDER_ID,
    'short_order_id': const.SHORT_ORDER_ID,
    'depot_id': const.DEPOT_ID,
    'location': {'lon': 39.60258, 'lat': 52.569089},
    'zone_type': 'pedestrian',
    'created_at': '2020-10-05T16:28:00+00:00',
    'max_eta': 900,
    'exact_eta': 500,
    'items': [
        {
            'item_id': 'item_id_1',
            'title': 'some product',
            'price': '12.99',
            'currency': 'RUB',
            'quantity': '1',
        },
        {
            'item_id': 'item_id_2',
            'title': 'some product_2',
            'price': '13.88',
            'currency': 'RUB',
            'quantity': '1',
        },
    ],
    'user_locale': 'ru',
    'personal_phone_id': const.PERSONAL_PHONE_ID,
    'comment': 'user comment',
    'door_code': 'doorcode',
    'door_code_extra': 'door_code_extra',
    'doorbell_name': 'doorbell_name',
    'building_name': 'building_name',
    'floor': 'floor',
    'flat': 'flat',
    'city': 'city',
    'street': 'street',
}
