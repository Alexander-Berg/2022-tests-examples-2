import copy
import datetime
import time

import pytest

from antifraud import utils


def _sleep(seconds=0.1):
    time.sleep(seconds)


class Base(object):
    def _set(self, inner_name, value):
        tmp = copy.deepcopy(self)
        tmp.__dict__[inner_name] = value
        return tmp

    def __getattr__(self, name):
        inner_name = '_%s' % name
        if inner_name in self.__dict__:
            return lambda value: self._set(inner_name, value)
        return object.__getattribute__(self, name)

    def to_dict(self):
        return {
            k[1:]: v
            for k, v in self.__dict__.items()
            if len(k) > 1 and k[0] == '_' and k[1] != '_' and v is not None
        }


class Input(Base):
    def __init__(self):
        super().__init__()
        self._order_id = 'order_id'
        self._status = 'finished'
        self._taxi_status = 'complete'
        self._user_id = 'user_id'
        self._user_phone_id = 'user_phone_id'
        self._device_id = 'device_id'
        self._zone = 'zone'
        self._request = {'due': '2019-01-10T09:30:00+0300'}

    def with_performer(self):
        return self._set('_performer', {'uuid': 'uuid'})


class Aggregate(Base):
    def __init__(self):
        super().__init__()
        self._device_id = 'device_id'
        self._due = datetime.datetime(2019, 1, 10, 0, 0)
        self._hash = '88249f148ad942234bd27cd41de7f98b'
        self._total_in_all_statuses = 1
        self._processed = ['order_id']
        self._user_id = 'user_id'
        self._user_phone_id = 'user_phone_id'
        self._complete = None
        self._total = None

    def status(self, key, value=1):
        int_key = '_' + key
        return self._set(int_key, value)


class Stat(Base):
    def __init__(self):
        super().__init__()
        self._processed = ['order_id']
        self._complete = None
        self._total = None
        self._total_in_all_statuses = 1


@pytest.mark.config(
    AFS_CUSTOM_USERS_STATISTICS=True, AFS_SAVE_STATISTICS_BY_USER_ID=True,
)
@pytest.mark.parametrize(
    'input,expected_aggregates_raw,expected_stat_user_raw',
    [
        (
            {
                'order_id': '081ce6f32b0c14088bb59fe2b9faf89c',
                'status': 'finished',
                'taxi_status': 'complete',
                'calc': {
                    'dist': 12817.094903945923,
                    'time': 1541.9899696073867,
                },
                'city': 'does_not_matter',
                'zone': 'zone',
                'cost': 138.0,
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'fixed_price': {
                    'destination': [37.59495899698706, 55.73779738195956],
                    'driver_price': 173.0,
                    'price': 138.0,
                    'price_original': 138.0,
                },
                'request': {
                    'destinations': [
                        {'geopoint': [37.59495899698706, 55.73779738195956]},
                    ],
                    'due': '2018-11-20T08:28:00+0300',
                    'requirements': {},
                    'payment': {'type': 'googlepay'},
                },
                'statistics': {
                    'complete_time': '2018-11-20T08:28:08+0300',
                    'driver_delay': 0,
                    'start_transporting_time': '2018-11-20T08:24:59+0300',
                    'start_waiting_time': '2018-11-20T08:24:57+0300',
                    'travel_time': 189.152,
                },
                'status_updates': [
                    {
                        'created': '2018-11-20T08:15:00+0300',
                        'reason_code': 'create',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:15:32+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:15:33+0300',
                        'lookup_generation': 1,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:15:33+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:16:40+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:24:35+0300',
                        'reason': 'manual',
                        'reason_code': 'autoreorder',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:42+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:42+0300',
                        'lookup_generation': 3,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:42+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:57+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:59+0300',
                        'taxi_status': 'transporting',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:28:08+0300',
                        'status': 'finished',
                        'taxi_status': 'complete',
                    },
                ],
                'user_id': '564d49a5d252b097f94eacea37353f4f',
                'user_phone_id': '5bcd7548030553e658298f6c',
                'performer': {'uuid': 'uuid'},
                'payment_tech': {'type': 'card'},
            },
            {
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'due': datetime.datetime(2018, 11, 20, 0, 0),
                'hash': 'f474fdde3f5b665b724409da6d5d5143',
                'total_in_all_statuses': 1,
                'cancelled_by_driver_auto_reorder': 1,
                'complete': 1,
                'complete_cost': 138.0,
                'complete_time': 189,
                'intermediate_points_count': 1,
                'intervals': [
                    [
                        datetime.datetime(2018, 11, 20, 5, 15),
                        datetime.datetime(2018, 11, 20, 5, 28, 8),
                    ],
                ],
                'planned_cost': 138.0,
                'planned_time': 1541,
                'processed': ['081ce6f32b0c14088bb59fe2b9faf89c'],
                'total': 1,
                'waiting_time': 477,
                'user_id': '564d49a5d252b097f94eacea37353f4f',
                'user_phone_id': '5bcd7548030553e658298f6c',
                'payment': {'type': {'card': {'complete': 1, 'total': 1}}},
                'request_payment': {
                    'type': {'googlepay': {'complete': 1, 'total': 1}},
                },
                'geo_zone': {'zone': {'total': 1}},
            },
            {
                'total_in_all_statuses': 1,
                'total': 1,
                'complete': 1,
                'autoreorders': 1,
                'processed': ['081ce6f32b0c14088bb59fe2b9faf89c'],
            },
        ),
        (
            {
                'order_id': '9f4bc25bf45e1f1dabb4e8f2d35dc7b8',
                'status': 'finished',
                'taxi_status': 'complete',
                'calc': {'dist': 15406.26344883442, 'time': 1809.021292377607},
                'cost': 80.0,
                'city': 'does_not_matter',
                'zone': 'zone',
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'fixed_price': {
                    'destination': [37.59495899698706, 55.73779738195956],
                    'driver_price': 173.0,
                    'price': 138.0,
                    'price_original': 138.0,
                },
                'request': {
                    'destinations': [
                        {'geopoint': [37.59495899698706, 55.73779738195956]},
                    ],
                    'due': '2018-11-20T09:24:00+0300',
                    'requirements': {},
                },
                'statistics': {
                    'complete_time': '2018-11-20T09:21:09+0300',
                    'driver_delay': 0,
                    'start_transporting_time': '2018-11-20T09:20:59+0300',
                    'start_waiting_time': '2018-11-20T09:20:55+0300',
                    'travel_distance': 0.8256282806396484,
                    'travel_time': 9.148,
                },
                'status_updates': [
                    {
                        'created': '2018-11-20T09:20:07+0300',
                        'reason_code': 'create',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T09:20:40+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T09:20:42+0300',
                        'lookup_generation': 1,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T09:20:42+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T09:20:55+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T09:20:59+0300',
                        'taxi_status': 'transporting',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T09:21:09+0300',
                        'status': 'finished',
                        'taxi_status': 'complete',
                    },
                ],
                'multiorder_order_number': 2,
                'user_id': '564d49a5d252b097f94eacea37353f4f',
                'user_phone_id': '5bcd7548030553e658298f6c',
                'performer': {'uuid': 'uuid'},
            },
            {
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'due': datetime.datetime(2018, 11, 20, 0, 0),
                'hash': 'f474fdde3f5b665b724409da6d5d5143',
                'total_in_all_statuses': 1,
                'complete': 1,
                'complete_cost': 80.0,
                'complete_time': 9,
                'intermediate_points_count': 1,
                'intervals': [
                    [
                        datetime.datetime(2018, 11, 20, 6, 20, 7),
                        datetime.datetime(2018, 11, 20, 6, 21, 9),
                    ],
                ],
                'planned_cost': 138.0,
                'planned_time': 1809,
                'processed': ['9f4bc25bf45e1f1dabb4e8f2d35dc7b8'],
                'total': 1,
                'waiting_time': 4,
                'user_id': '564d49a5d252b097f94eacea37353f4f',
                'user_phone_id': '5bcd7548030553e658298f6c',
                'geo_zone': {'zone': {'total': 1}},
            },
            {
                'total_in_all_statuses': 1,
                'complete': 1,
                'total': 1,
                'multiorder_complete': 1,
                'multiorder_total': 1,
                'processed': ['9f4bc25bf45e1f1dabb4e8f2d35dc7b8'],
            },
        ),
        (
            {
                'order_id': 'b63cbecd55be19118e9eac43d455044b',
                'status': 'cancelled',
                'taxi_status': 'driving',
                'calc': {
                    'dist': 15300.189468502998,
                    'time': 2084.991586796098,
                },
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'city': 'does_not_matter',
                'zone': 'zone',
                'fixed_price': {
                    'destination': [37.59495899698706, 55.73779738195956],
                    'driver_price': 609.0,
                    'price': 609.0,
                    'price_original': 609.0,
                },
                'request': {
                    'destinations': [
                        {'geopoint': [37.59495899698706, 55.73779738195956]},
                    ],
                    'due': '2018-11-20T10:54:00+0300',
                    'payment': {'type': 'googlepay'},
                },
                'statistics': {
                    'cancel_distance': 104.57167864797431,
                    'cancel_dt': '2018-11-20T10:50:21+0300',
                    'cancel_time': 48.265,
                },
                'status_updates': [
                    {
                        'created': '2018-11-20T10:49:33+0300',
                        'reason_code': 'create',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:10+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:11+0300',
                        'lookup_generation': 1,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:11+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'created': '2018-11-20T10:50:21+0300',
                        'status': 'cancelled',
                    },
                ],
                'multiorder_order_number': 0,
                'user_id': '564d49a5d252b097f94eacea37353f4f',
                'user_phone_id': '5bcd7548030553e658298f6c',
                'performer': {'uuid': 'uuid'},
                'payment_tech': {'type': 'cash'},
            },
            {
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'due': datetime.datetime(2018, 11, 20, 0, 0),
                'hash': 'f474fdde3f5b665b724409da6d5d5143',
                'total_in_all_statuses': 1,
                'cancelled_before_transporting_drivers_time': 10,
                'cancelled_by_user': 1,
                'intermediate_points_count': 1,
                'planned_cost': 609.0,
                'planned_time': 2084,
                'processed': ['b63cbecd55be19118e9eac43d455044b'],
                'total': 1,
                'user_id': '564d49a5d252b097f94eacea37353f4f',
                'user_phone_id': '5bcd7548030553e658298f6c',
                'payment': {'type': {'cash': {'total': 1}}},
                'request_payment': {'type': {'googlepay': {'total': 1}}},
                'geo_zone': {'zone': {'total': 1}},
            },
            {
                'total_in_all_statuses': 1,
                'total': 1,
                'multiorder_total': 1,
                'processed': ['b63cbecd55be19118e9eac43d455044b'],
            },
        ),
        (
            {
                'order_id': '585c30a6bcc2101e9a4248efd962b832',
                'status': 'finished',
                'taxi_status': 'cancelled',
                'calc': {
                    'dist': 11495.609219789505,
                    'time': 903.9327143781272,
                },
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'city': 'does_not_matter',
                'zone': 'zone',
                'fixed_price': {
                    'destination': [37.59357206501252, 55.73582802392552],
                    'driver_price': 294.0,
                    'price': 235.0,
                    'price_original': 235.0,
                },
                'request': {
                    'destinations': [
                        {'geopoint': [37.59357206501252, 55.73582802392552]},
                    ],
                    'due': '2018-11-19T22:52:00+0300',
                },
                'statistics': {
                    'cancel_dt': '2018-11-19T22:48:39+0300',
                    'cancel_time': 93.16,
                    'driver_delay': 0,
                    'late_cancel': True,
                    'start_waiting_time': '2018-11-19T22:48:00+0300',
                },
                'status_updates': [
                    {
                        'created': '2018-11-19T22:47:06+0300',
                        'reason_code': 'create',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-19T22:47:44+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-19T22:47:46+0300',
                        'lookup_generation': 1,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-19T22:47:46+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-19T22:48:00+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'created': '2018-11-19T22:48:39+0300',
                        'reason': '123',
                        'status': 'finished',
                        'taxi_status': 'cancelled',
                    },
                ],
                'user_id': '6106d89e9ba760d5c497a9ab92f78572',
                'user_phone_id': '5bcd7548030553e658298f6c',
                'performer': {'uuid': 'uuid'},
                'payment_tech': {'type': 'googlepay'},
            },
            {
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'due': datetime.datetime(2018, 11, 19, 0, 0),
                'hash': 'aab80d50aaeb4a0dc1621de597fc9f3c',
                'total_in_all_statuses': 1,
                'cancelled_by_park': 1,
                'intermediate_points_count': 1,
                'planned_cost': 235.0,
                'planned_time': 903,
                'processed': ['585c30a6bcc2101e9a4248efd962b832'],
                'total': 1,
                'waiting_time': 39,
                'user_id': '6106d89e9ba760d5c497a9ab92f78572',
                'user_phone_id': '5bcd7548030553e658298f6c',
                'payment': {'type': {'googlepay': {'total': 1}}},
                'geo_zone': {'zone': {'total': 1}},
            },
            {
                'total_in_all_statuses': 1,
                'total': 1,
                'processed': ['585c30a6bcc2101e9a4248efd962b832'],
            },
        ),
        (
            {
                'order_id': 'b63cbecd55be19118e9eac43d455044b',
                'status': 'cancelled',
                'taxi_status': 'driving',
                'calc': {
                    'dist': 15300.189468502998,
                    'time': 2084.991586796098,
                },
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'city': 'does_not_matter',
                'zone': 'zone',
                'fixed_price': {
                    'destination': [37.59495899698706, 55.73779738195956],
                    'driver_price': 609.0,
                    'price': 609.0,
                    'price_original': 609.0,
                },
                'request': {
                    'destinations': [
                        {'geopoint': [37.59495899698706, 55.73779738195956]},
                    ],
                    'due': '2018-11-20T10:54:00+0300',
                },
                'statistics': {
                    'cancel_distance': 104.57167864797431,
                    'cancel_dt': '2018-11-20T10:50:21+0300',
                    'cancel_time': 48.265,
                },
                'status_updates': [
                    {
                        'created': '2018-11-20T10:49:33+0300',
                        'reason_code': 'create',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:10+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:11+0300',
                        'lookup_generation': 1,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:11+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'created': '2018-11-20T10:50:21+0300',
                        'status': 'cancelled',
                    },
                ],
                'user_id': '564d49a5d252b097f94eacea37353f4f',
                'user_phone_id': '5bcd7548030553e658298f6c',
                'performer': {'uuid': 'uuid'},
            },
            {
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'due': datetime.datetime(2018, 11, 20, 0, 0),
                'hash': 'f474fdde3f5b665b724409da6d5d5143',
                'total_in_all_statuses': 1,
                'cancelled_by_user': 1,
                'intermediate_points_count': 1,
                'planned_cost': 609.0,
                'planned_time': 2084,
                'processed': ['b63cbecd55be19118e9eac43d455044b'],
                'total': 1,
                'user_id': '564d49a5d252b097f94eacea37353f4f',
                'user_phone_id': '5bcd7548030553e658298f6c',
                'cancelled_before_transporting_drivers_time': 10,
                'geo_zone': {'zone': {'total': 1}},
            },
            {
                'total_in_all_statuses': 1,
                'total': 1,
                'processed': ['b63cbecd55be19118e9eac43d455044b'],
            },
        ),
        (
            {
                'order_id': '0819953dab7063d0b46b15d9295bcf8f',
                'status': 'finished',
                'taxi_status': 'complete',
                'calc': {'dist': 46073.39288640022, 'time': 6733.002616620512},
                'cost': 1634.0,
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'city': 'does_not_matter',
                'zone': 'zone',
                'fixed_price': {
                    'destination': [37.56414175768225, 55.72468390881436],
                    'driver_price': 1634.0,
                    'price': 1634.0,
                    'price_original': 1634.0,
                },
                'request': {
                    'destinations': [
                        {'geopoint': [37.57380003148046, 55.79313088487496]},
                        {'geopoint': [37.70467300058783, 55.76339138789917]},
                        {'geopoint': [37.56414175768225, 55.72468390881436]},
                    ],
                    'due': '2018-11-22T10:44:00+0300',
                    'requirements': {'animaltransport': True},
                },
                'statistics': {
                    'complete_time': '2018-11-22T10:40:59+0300',
                    'driver_delay': 0,
                    'start_transporting_time': '2018-11-22T10:39:39+0300',
                    'start_waiting_time': '2018-11-22T10:39:36+0300',
                    'travel_time': 80.336,
                },
                'status_updates': [
                    {
                        'created': '2018-11-22T10:39:16+0300',
                        'reason_code': 'create',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-22T10:39:34+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-22T10:39:34+0300',
                        'lookup_generation': 1,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-22T10:39:34+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-22T10:39:36+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-22T10:39:39+0300',
                        'taxi_status': 'transporting',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-22T10:40:59+0300',
                        'status': 'finished',
                        'taxi_status': 'complete',
                    },
                ],
                'user_id': '8c1e0c51fefcfb21eab6b2f36e532e2d',
                'user_phone_id': '5bcd7548030553e658298f6c',
                'performer': {'uuid': 'uuid'},
            },
            {
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'due': datetime.datetime(2018, 11, 22, 0, 0),
                'hash': '809dae3027eecef4c84b1f6866cb4ddb',
                'total_in_all_statuses': 1,
                'complete': 1,
                'complete_cost': 1634.0,
                'complete_time': 80,
                'intermediate_points_count': 3,
                'intervals': [
                    [
                        datetime.datetime(2018, 11, 22, 7, 39, 16),
                        datetime.datetime(2018, 11, 22, 7, 40, 59),
                    ],
                ],
                'planned_cost': 1634.0,
                'planned_time': 6733,
                'processed': ['0819953dab7063d0b46b15d9295bcf8f'],
                'requirements_count': 1,
                'total': 1,
                'waiting_time': 3,
                'user_id': '8c1e0c51fefcfb21eab6b2f36e532e2d',
                'user_phone_id': '5bcd7548030553e658298f6c',
                'geo_zone': {'zone': {'total': 1}},
            },
            {
                'total_in_all_statuses': 1,
                'total': 1,
                'complete': 1,
                'processed': ['0819953dab7063d0b46b15d9295bcf8f'],
            },
        ),
        (
            {
                'order_id': 'e62f3e7e76245928b4c5175181ba9dac',
                'status': 'finished',
                'taxi_status': 'failed',
                'calc': {'dist': 3645.655643939972, 'time': 508.6911123277801},
                'device_id': 'D509090E-33A0-4080-A9B4-E76E6569FD51',
                'city': 'does_not_matter',
                'zone': 'zone',
                'fixed_price': {
                    'destination': [37.51760799999999, 55.672935],
                    'driver_price': 297.0,
                    'price': 297.0,
                    'price_original': 297.0,
                },
                'request': {
                    'destinations': [
                        {'geopoint': [37.51760799999999, 55.672935]},
                    ],
                    'due': '2018-11-29T13:44:00+0300',
                    'requirements': {'childchair_for_child_tariff': [1]},
                },
                'statistics': {
                    'cancel_distance': 1370.6143531579269,
                    'cancel_dt': '2018-11-29T13:34:25+0300',
                    'cancel_time': 475.321,
                },
                'status_updates': [
                    {
                        'created': '2018-11-29T13:26:29+0300',
                        'reason_code': 'create',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:26:55+0300',
                        'reason_code': 'seen_timeout',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-29T13:27:02+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-29T13:27:03+0300',
                        'lookup_generation': 1,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-29T13:27:03+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-29T13:31:32+0300',
                        'reason': 'manual',
                        'reason_code': 'autoreorder',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 2,
                        'created': '2018-11-29T13:31:36+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 2,
                        'created': '2018-11-29T13:31:41+0300',
                        'lookup_generation': 3,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 2,
                        'created': '2018-11-29T13:31:41+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 2,
                        'created': '2018-11-29T13:34:25+0300',
                        'reason': 'manual',
                        'status': 'finished',
                        'taxi_status': 'failed',
                    },
                ],
                'user_id': '93a0ca006343463baaced3adf0ace71b',
                'user_phone_id': '539eabf3e7e5b1f5397db606',
                'performer': {'uuid': 'uuid'},
            },
            {
                'device_id': 'D509090E-33A0-4080-A9B4-E76E6569FD51',
                'due': datetime.datetime(2018, 11, 29, 0, 0),
                'hash': 'ec30828f35b3c2da889dd0b9eb9678cb',
                'total_in_all_statuses': 1,
                'cancelled_by_driver_finished': 1,
                'intermediate_points_count': 1,
                'planned_cost': 297.0,
                'planned_time': 508,
                'processed': ['e62f3e7e76245928b4c5175181ba9dac'],
                'requirements_count': 1,
                'user_id': '93a0ca006343463baaced3adf0ace71b',
                'user_phone_id': '539eabf3e7e5b1f5397db606',
            },
            {
                'total_in_all_statuses': 1,
                'bad_driver_cancels': 1,
                'processed': ['e62f3e7e76245928b4c5175181ba9dac'],
            },
        ),
        (
            {
                'order_id': 'c0894301496c57fea905ecc6be323fca',
                'status': 'finished',
                'taxi_status': 'failed',
                'calc': {'dist': 4980.590409994125, 'time': 1115.329607646207},
                'device_id': '4BA653FE-FEF0-41FA-9B85-FD8D7EAC87AB',
                'city': 'does_not_matter',
                'zone': 'zone',
                'fixed_price': {
                    'destination': [50.800367, 61.65476],
                    'driver_price': 117.0,
                    'price': 117.0,
                    'price_original': 117.0,
                },
                'request': {
                    'destinations': [
                        {'geopoint': [50.810947, 61.675453]},
                        {'geopoint': [50.800367, 61.65476]},
                    ],
                    'due': '2018-11-29T13:46:00+0300',
                },
                'statistics': {
                    'cancel_dt': '2018-11-29T13:42:28+0300',
                    'cancel_time': 199.029,
                },
                'status_updates': [
                    {
                        'created': '2018-11-29T13:39:10+0300',
                        'reason_code': 'create',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:39:17+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:39:26+0300',
                        'lookup_generation': 1,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:39:26+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:40:05+0300',
                        'reason': 'manual',
                        'reason_code': 'autoreorder',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-29T13:40:08+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-29T13:40:47+0300',
                        'reason_code': 'offer_timeout',
                    },
                    {
                        'candidate_index': 2,
                        'created': '2018-11-29T13:40:49+0300',
                        'reason_code': 'unset_unconfirmed_performer',
                    },
                    {
                        'candidate_index': 3,
                        'created': '2018-11-29T13:40:55+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 3,
                        'created': '2018-11-29T13:40:57+0300',
                        'lookup_generation': 3,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 3,
                        'created': '2018-11-29T13:40:57+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 3,
                        'created': '2018-11-29T13:42:28+0300',
                        'reason': 'manual',
                        'status': 'finished',
                        'taxi_status': 'failed',
                    },
                ],
                'user_id': '30d2b1b65c174a6ab4b0c257dab031ed',
                'user_phone_id': '5936d68e43d523c4a214a9ac',
                'performer': {'uuid': 'uuid'},
            },
            {
                'device_id': '4BA653FE-FEF0-41FA-9B85-FD8D7EAC87AB',
                'due': datetime.datetime(2018, 11, 29, 0, 0),
                'hash': '35aac76808e21bb25bf82dd5a65135f4',
                'total_in_all_statuses': 1,
                'cancelled_by_driver_finished': 1,
                'intermediate_points_count': 2,
                'planned_cost': 117.0,
                'planned_time': 1115,
                'processed': ['c0894301496c57fea905ecc6be323fca'],
                'user_id': '30d2b1b65c174a6ab4b0c257dab031ed',
                'user_phone_id': '5936d68e43d523c4a214a9ac',
            },
            {
                'total_in_all_statuses': 1,
                'bad_driver_cancels': 1,
                'processed': ['c0894301496c57fea905ecc6be323fca'],
            },
        ),
        (
            {
                'order_id': '86ff622b57075595bfa33d3241e80022',
                'status': 'finished',
                'taxi_status': 'failed',
                'calc': {
                    'dist': 11217.660965323448,
                    'time': 1188.1429259498118,
                },
                'device_id': '2EA11CBA-8C75-4E7A-BFF1-CDBCEEACD345',
                'city': 'does_not_matter',
                'zone': 'zone',
                'fixed_price': {
                    'destination': [51.429542093706985, 51.247210752607536],
                    'driver_price': 1020.0,
                    'price': 1020.0,
                    'price_original': 1020.0,
                },
                'request': {
                    'destinations': [
                        {'geopoint': [51.429542093706985, 51.247210752607536]},
                    ],
                    'due': '2018-11-29T13:36:00+0300',
                },
                'statistics': {
                    'cancel_dt': '2018-11-29T13:42:08+0300',
                    'cancel_time': 779.949,
                    'driver_delay': 0,
                    'start_waiting_time': '2018-11-29T13:34:57+0300',
                },
                'status_updates': [
                    {
                        'created': '2018-11-29T13:29:08+0300',
                        'reason_code': 'create',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:29:18+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:29:21+0300',
                        'lookup_generation': 1,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:29:21+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:34:57+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:42:08+0300',
                        'reason': 'manual',
                        'status': 'finished',
                        'taxi_status': 'failed',
                    },
                ],
                'multiorder_order_number': 119,
                'user_id': '6a68e9dc382047cba006b5ac4d641789',
                'user_phone_id': '59b3bfbd460c39ed56a00ff3',
                'performer': {'uuid': 'uuid'},
            },
            {
                'device_id': '2EA11CBA-8C75-4E7A-BFF1-CDBCEEACD345',
                'due': datetime.datetime(2018, 11, 29, 0, 0),
                'hash': 'c6ae382b35d6473616042637dbb2f0dd',
                'total_in_all_statuses': 1,
                'cancelled_by_driver_finished': 1,
                'intermediate_points_count': 1,
                'planned_cost': 1020.0,
                'planned_time': 1188,
                'processed': ['86ff622b57075595bfa33d3241e80022'],
                'waiting_time': 431,
                'user_id': '6a68e9dc382047cba006b5ac4d641789',
                'user_phone_id': '59b3bfbd460c39ed56a00ff3',
            },
            {
                'total_in_all_statuses': 1,
                'bad_driver_cancels': 1,
                'processed': ['86ff622b57075595bfa33d3241e80022'],
            },
        ),
        (Input().to_dict(), Aggregate().to_dict(), Stat().to_dict()),
        (
            Input().with_performer().to_dict(),
            Aggregate()
            .status('complete')
            .status('total')
            ._set('_geo_zone', {'zone': {'total': 1}})
            .to_dict(),
            Stat().complete(1).total(1).to_dict(),
        ),
        (
            Input().with_performer().taxi_status('failed').to_dict(),
            Aggregate().to_dict(),
            Stat().to_dict(),
        ),
        (
            Input().with_performer().taxi_status('expired').to_dict(),
            Aggregate()
            .status('complete')
            .status('total')
            .status('expired')
            ._set('_geo_zone', {'zone': {'total': 1}})
            .to_dict(),
            Stat().complete(1).total(1).to_dict(),
        ),
    ],
)
def test_order_finish_post_base(
        taxi_antifraud,
        db,
        testpoint,
        input,
        expected_aggregates_raw,
        expected_stat_user_raw,
):
    @testpoint('after_update_aggregates_in_new_db')
    def after_update_new_aggregates(_):
        pass

    @testpoint('after_update_statistics_users')
    def after_update_stats_users(_):
        pass

    @testpoint('after_update_statistics_phones')
    def after_update_stats_phones(_):
        pass

    @testpoint('after_update_statistics_devices')
    def after_update_stats_devices(_):
        pass

    response = taxi_antifraud.post('events/order_finish_post', json=input)

    assert response.status_code == 200
    assert response.json() == {}

    after_update_new_aggregates.wait_call()
    after_update_stats_users.wait_call()
    after_update_stats_phones.wait_call()
    after_update_stats_devices.wait_call()

    records_aggregates = db.antifraud_users_orders_aggregates.find(
        {}, {'_id': 0, 'created': 0, 'updated': 0},
    )
    assert records_aggregates.count() == 1
    records_aggregates = records_aggregates[0]
    assert records_aggregates == expected_aggregates_raw

    collections_list = list()
    collections_list.append(db.antifraud_stat_users)
    if 'user_phone_id' in input:
        collections_list.append(db.antifraud_stat_phones)
    if 'device_id' in input:
        collections_list.append(db.antifraud_stat_devices)

    for cur_collection in collections_list:
        records_stat_user = cur_collection.find(
            {}, {'_id': 0, 'created': 0, 'updated': 0},
        )

        assert records_stat_user.count() == 1
        record_stat_user = records_stat_user[0]
        assert (
            record_stat_user == expected_stat_user_raw
        ), 'user stat compare failed (order_id: {})'.format(input['order_id'])


@pytest.mark.config(
    AFS_CUSTOM_USERS_STATISTICS=True, AFS_SAVE_STATISTICS_BY_USER_ID=True,
)
@pytest.mark.filldb(antifraud_users_orders_aggregates='too_many_processed')
@pytest.mark.filldb(antifraud_stat_users='too_many_processed')
@pytest.mark.filldb(antifraud_stat_phones='too_many_processed')
@pytest.mark.filldb(antifraud_stat_devices='too_many_processed')
@pytest.mark.parametrize(
    'input,expected_aggregates_raw,expected_stat_user_raw',
    [
        (
            {
                'calc': {
                    'dist': 11217.660965323448,
                    'time': 1188.1429259498118,
                },
                'device_id': '2EA11CBA-8C75-4E7A-BFF1-CDBCEEACD345',
                'city': 'does_not_matter',
                'zone': 'zone',
                'fixed_price': {
                    'destination': [51.429542093706985, 51.247210752607536],
                    'driver_price': 1020.0,
                    'price': 1020.0,
                    'price_original': 1020.0,
                },
                'order_id': '86ff622b57075595bfa33d3241e80022',
                'request': {
                    'destinations': [
                        {'geopoint': [51.429542093706985, 51.247210752607536]},
                    ],
                    'due': '2018-11-29T13:36:00+0300',
                },
                'statistics': {
                    'cancel_dt': '2018-11-29T13:42:08+0300',
                    'cancel_time': 779.949,
                    'driver_delay': 0,
                    'start_waiting_time': '2018-11-29T13:34:57+0300',
                },
                'status': 'finished',
                'status_updates': [
                    {
                        'created': '2018-11-29T13:29:08+0300',
                        'reason_code': 'create',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:29:18+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:29:21+0300',
                        'lookup_generation': 1,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:29:21+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:34:57+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:42:08+0300',
                        'reason': 'manual',
                        'status': 'finished',
                        'taxi_status': 'failed',
                    },
                ],
                'taxi_status': 'failed',
                'multiorder_order_number': 119,
                'user_id': '6a68e9dc382047cba006b5ac4d641789',
                'user_phone_id': '59b3bfbd460c39ed56a00ff3',
                'performer': {'uuid': 'uuid'},
            },
            {
                'device_id': '2EA11CBA-8C75-4E7A-BFF1-CDBCEEACD345',
                'due': datetime.datetime(2018, 11, 29, 0, 0),
                'hash': 'c6ae382b35d6473616042637dbb2f0dd',
                'total_in_all_statuses': 1,
                'cancelled_by_driver_finished': 1,
                'intermediate_points_count': 1,
                'planned_cost': 1020.0,
                'planned_time': 1188,
                'processed': [
                    '1',
                    '2',
                    '3',
                    '4',
                    '5',
                    '6',
                    '7',
                    '8',
                    '9',
                    '86ff622b57075595bfa33d3241e80022',
                ],
                'waiting_time': 431,
                'user_id': '6a68e9dc382047cba006b5ac4d641789',
                'user_phone_id': '59b3bfbd460c39ed56a00ff3',
            },
            {
                'total_in_all_statuses': 1,
                'bad_driver_cancels': 1,
                'processed': [
                    '1',
                    '2',
                    '3',
                    '4',
                    '5',
                    '6',
                    '7',
                    '8',
                    '9',
                    '86ff622b57075595bfa33d3241e80022',
                ],
            },
        ),
    ],
)
def test_too_many_processed_orders(
        taxi_antifraud,
        db,
        testpoint,
        input,
        expected_aggregates_raw,
        expected_stat_user_raw,
):
    @testpoint('after_update_statistics_users')
    def after_update_stats_users(_):
        pass

    @testpoint('after_update_statistics_phones')
    def after_update_stats_phones(_):
        pass

    @testpoint('after_update_statistics_devices')
    def after_update_stats_devices(_):
        pass

    @testpoint('after_update_aggregates_in_new_db')
    def after_update_new_aggregates(_):
        pass

    collections_list = [
        db.antifraud_stat_users,
        db.antifraud_stat_phones,
        db.antifraud_stat_devices,
    ]

    response = taxi_antifraud.post('events/order_finish_post', json=input)

    assert response.status_code == 200
    assert response.json() == {}

    after_update_stats_users.wait_call()
    after_update_stats_phones.wait_call()
    after_update_stats_devices.wait_call()
    after_update_new_aggregates.wait_call()

    records_aggregates = db.antifraud_users_orders_aggregates.find(
        {}, {'_id': 0, 'created': 0, 'updated': 0},
    )
    assert records_aggregates.count() == 1
    records_aggregates = records_aggregates[0]
    assert records_aggregates == expected_aggregates_raw

    for el in collections_list:
        records_stat_user = el.find({}, {'_id': 0, 'created': 0, 'updated': 0})

        assert records_stat_user.count() == 1
        record_stat_user = records_stat_user[0]
        assert record_stat_user == expected_stat_user_raw


@pytest.mark.config(
    AFS_CUSTOM_USERS_STATISTICS=True, AFS_SAVE_STATISTICS_BY_USER_ID=False,
)
@pytest.mark.parametrize(
    'input',
    [
        (
            {
                'calc': {
                    'dist': 12817.094903945923,
                    'time': 1541.9899696073867,
                },
                'cost': 138.0,
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'city': 'does_not_matter',
                'zone': 'zone',
                'fixed_price': {
                    'destination': [37.59495899698706, 55.73779738195956],
                    'driver_price': 173.0,
                    'price': 138.0,
                    'price_original': 138.0,
                },
                'order_id': '081ce6f32b0c14088bb59fe2b9faf89c',
                'request': {
                    'destinations': [
                        {'geopoint': [37.59495899698706, 55.73779738195956]},
                    ],
                    'due': '2018-11-20T08:28:00+0300',
                    'requirements': {},
                },
                'statistics': {
                    'complete_time': '2018-11-20T08:28:08+0300',
                    'driver_delay': 0,
                    'start_transporting_time': '2018-11-20T08:24:59+0300',
                    'start_waiting_time': '2018-11-20T08:24:57+0300',
                    'travel_time': 189.152,
                },
                'status': 'finished',
                'status_updates': [
                    {
                        'created': '2018-11-20T08:15:00+0300',
                        'reason_code': 'create',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:15:32+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:15:33+0300',
                        'lookup_generation': 1,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:15:33+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:16:40+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:24:35+0300',
                        'reason': 'manual',
                        'reason_code': 'autoreorder',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:42+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:42+0300',
                        'lookup_generation': 3,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:42+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:57+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:59+0300',
                        'taxi_status': 'transporting',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:28:08+0300',
                        'status': 'finished',
                        'taxi_status': 'complete',
                    },
                ],
                'taxi_status': 'complete',
                'user_id': '564d49a5d252b097f94eacea37353f4f',
                'user_phone_id': '5bcd7548030553e658298f6c',
            }
        ),
    ],
)
def test_do_not_save_user_id(taxi_antifraud, db, testpoint, input):
    @testpoint('afs_stats_updated')
    def after_update_stats(_):
        pass

    @testpoint('after_update_statistics_phones')
    def after_update_stats_phones(_):
        pass

    @testpoint('after_update_statistics_devices')
    def after_update_stats_devices(_):
        pass

    @testpoint('after_update_aggregates_in_new_db')
    def after_update_new_aggregates(_):
        pass

    response = taxi_antifraud.post('events/order_finish_post', json=input)

    assert response.status_code == 200
    assert response.json() == {}

    after_update_stats.wait_call()
    after_update_stats_phones.wait_call()
    after_update_stats_devices.wait_call()
    after_update_new_aggregates.wait_call()

    records_aggregates = db.antifraud_users_orders_aggregates.find(
        {}, {'_id': 0, 'created': 0, 'updated': 0},
    )
    assert records_aggregates.count() == 1

    collections_list = []
    if 'user_phone_id' in input:
        collections_list.append(db.antifraud_stat_phones)
    if 'device_id' in input:
        collections_list.append(db.antifraud_stat_devices)

    for cur_collection in collections_list:
        records_stat_user = cur_collection.find(
            {}, {'_id': 0, 'created': 0, 'updated': 0},
        )

        assert records_stat_user.count() == 1

    assert (
        db.antifraud_stat_users.find(
            {}, {'_id': 0, 'created': 0, 'updated': 0},
        ).count()
        == 0
    )


@pytest.mark.config(
    AFS_CUSTOM_USERS_STATISTICS=False, AFS_SAVE_STATISTICS_BY_USER_ID=True,
)
@pytest.mark.parametrize(
    'input',
    [
        (
            {
                'calc': {
                    'dist': 12817.094903945923,
                    'time': 1541.9899696073867,
                },
                'cost': 138.0,
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'city': 'does_not_matter',
                'zone': 'zone',
                'fixed_price': {
                    'destination': [37.59495899698706, 55.73779738195956],
                    'driver_price': 173.0,
                    'price': 138.0,
                    'price_original': 138.0,
                },
                'order_id': '081ce6f32b0c14088bb59fe2b9faf89c',
                'request': {
                    'destinations': [
                        {'geopoint': [37.59495899698706, 55.73779738195956]},
                    ],
                    'due': '2018-11-20T08:28:00+0300',
                    'requirements': {},
                },
                'statistics': {
                    'complete_time': '2018-11-20T08:28:08+0300',
                    'driver_delay': 0,
                    'start_transporting_time': '2018-11-20T08:24:59+0300',
                    'start_waiting_time': '2018-11-20T08:24:57+0300',
                    'travel_time': 189.152,
                },
                'status': 'finished',
                'status_updates': [
                    {
                        'created': '2018-11-20T08:15:00+0300',
                        'reason_code': 'create',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:15:32+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:15:33+0300',
                        'lookup_generation': 1,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:15:33+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:16:40+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:24:35+0300',
                        'reason': 'manual',
                        'reason_code': 'autoreorder',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:42+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:42+0300',
                        'lookup_generation': 3,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:42+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:57+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:59+0300',
                        'taxi_status': 'transporting',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:28:08+0300',
                        'status': 'finished',
                        'taxi_status': 'complete',
                    },
                ],
                'taxi_status': 'complete',
                'user_id': '564d49a5d252b097f94eacea37353f4f',
                'user_phone_id': '5bcd7548030553e658298f6c',
            }
        ),
    ],
)
def test_save_custom_statistics_config1(taxi_antifraud, db, testpoint, input):
    @testpoint('after_update_aggregates_in_new_db')
    def after_update_new_aggregates(_):
        pass

    @testpoint('afs_stats_updated')
    def after_update_stats(_):
        pass

    response = taxi_antifraud.post('events/order_finish_post', json=input)

    assert response.status_code == 200
    assert response.json() == {}

    after_update_new_aggregates.wait_call()
    after_update_stats.wait_call()

    records_aggregates = db.antifraud_users_orders_aggregates.find(
        {}, {'_id': 0, 'created': 0, 'updated': 0},
    )
    assert records_aggregates.count() == 1

    collections_list = []
    collections_list.append(db.antifraud_stat_users)
    if 'user_phone_id' in input:
        collections_list.append(db.antifraud_stat_phones)
    if 'device_id' in input:
        collections_list.append(db.antifraud_stat_devices)

    for cur_collection in collections_list:
        records_stat_user = cur_collection.find(
            {}, {'_id': 0, 'created': 0, 'updated': 0},
        )

        assert records_stat_user.count() == 0


@pytest.mark.config(
    AFS_CUSTOM_USERS_STATISTICS=False, AFS_SAVE_STATISTICS_BY_USER_ID=False,
)
@pytest.mark.parametrize(
    'input',
    [
        (
            {
                'calc': {
                    'dist': 12817.094903945923,
                    'time': 1541.9899696073867,
                },
                'cost': 138.0,
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'city': 'does_not_matter',
                'zone': 'zone',
                'fixed_price': {
                    'destination': [37.59495899698706, 55.73779738195956],
                    'driver_price': 173.0,
                    'price': 138.0,
                    'price_original': 138.0,
                },
                'order_id': '081ce6f32b0c14088bb59fe2b9faf89c',
                'request': {
                    'destinations': [
                        {'geopoint': [37.59495899698706, 55.73779738195956]},
                    ],
                    'due': '2018-11-20T08:28:00+0300',
                    'requirements': {},
                },
                'statistics': {
                    'complete_time': '2018-11-20T08:28:08+0300',
                    'driver_delay': 0,
                    'start_transporting_time': '2018-11-20T08:24:59+0300',
                    'start_waiting_time': '2018-11-20T08:24:57+0300',
                    'travel_time': 189.152,
                },
                'status': 'finished',
                'status_updates': [
                    {
                        'created': '2018-11-20T08:15:00+0300',
                        'reason_code': 'create',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:15:32+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:15:33+0300',
                        'lookup_generation': 1,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:15:33+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:16:40+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-20T08:24:35+0300',
                        'reason': 'manual',
                        'reason_code': 'autoreorder',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:42+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:42+0300',
                        'lookup_generation': 3,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:42+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:57+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:24:59+0300',
                        'taxi_status': 'transporting',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T08:28:08+0300',
                        'status': 'finished',
                        'taxi_status': 'complete',
                    },
                ],
                'taxi_status': 'complete',
                'user_id': '564d49a5d252b097f94eacea37353f4f',
                'user_phone_id': '5bcd7548030553e658298f6c',
            }
        ),
    ],
)
def test_save_custom_statistics_config2(taxi_antifraud, db, testpoint, input):
    @testpoint('after_update_aggregates_in_new_db')
    def after_update_new_aggregates(_):
        pass

    @testpoint('afs_stats_updated')
    def after_update_stats(_):
        pass

    response = taxi_antifraud.post('events/order_finish_post', json=input)

    assert response.status_code == 200
    assert response.json() == {}

    after_update_new_aggregates.wait_call()
    after_update_stats.wait_call()

    records_aggregates = db.antifraud_users_orders_aggregates.find(
        {}, {'_id': 0, 'created': 0, 'updated': 0},
    )
    assert records_aggregates.count() == 1

    collections_list = []
    collections_list.append(db.antifraud_stat_users)
    if 'user_phone_id' in input:
        collections_list.append(db.antifraud_stat_phones)
    if 'device_id' in input:
        collections_list.append(db.antifraud_stat_devices)

    for cur_collection in collections_list:
        records_stat_user = cur_collection.find(
            {}, {'_id': 0, 'created': 0, 'updated': 0},
        )

        assert records_stat_user.count() == 0


@pytest.mark.config(
    AFS_CUSTOM_USERS_STATISTICS=True, AFS_SAVE_STATISTICS_BY_USER_ID=True,
)
@pytest.mark.filldb(antifraud_users_orders_aggregates='same_orders_processed')
@pytest.mark.filldb(antifraud_stat_users='same_orders_processed')
@pytest.mark.filldb(antifraud_stat_phones='same_orders_processed')
@pytest.mark.filldb(antifraud_stat_devices='same_orders_processed')
@pytest.mark.parametrize(
    'input,expected_aggregates_raw,expected_stat_user_raw',
    [
        (
            {
                'calc': {
                    'dist': 11217.660965323448,
                    'time': 1188.1429259498118,
                },
                'device_id': '2EA11CBA-8C75-4E7A-BFF1-CDBCEEACD345',
                'city': 'does_not_matter',
                'zone': 'zone',
                'fixed_price': {
                    'destination': [51.429542093706985, 51.247210752607536],
                    'driver_price': 1020.0,
                    'price': 1020.0,
                    'price_original': 1020.0,
                },
                'order_id': '86ff622b57075595bfa33d3241e80022',
                'request': {
                    'destinations': [
                        {'geopoint': [51.429542093706985, 51.247210752607536]},
                    ],
                    'due': '2018-11-29T13:36:00+0300',
                },
                'statistics': {
                    'cancel_dt': '2018-11-29T13:42:08+0300',
                    'cancel_time': 779.949,
                    'driver_delay': 0,
                    'start_waiting_time': '2018-11-29T13:34:57+0300',
                },
                'status': 'finished',
                'status_updates': [
                    {
                        'created': '2018-11-29T13:29:08+0300',
                        'reason_code': 'create',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:29:18+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:29:21+0300',
                        'lookup_generation': 1,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:29:21+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:34:57+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 0,
                        'created': '2018-11-29T13:42:08+0300',
                        'reason': 'manual',
                        'status': 'finished',
                        'taxi_status': 'failed',
                    },
                ],
                'taxi_status': 'failed',
                'multiorder_order_number': 119,
                'user_id': '6a68e9dc382047cba006b5ac4d641789',
                'user_phone_id': '59b3bfbd460c39ed56a00ff3',
            },
            {
                'device_id': '2EA11CBA-8C75-4E7A-BFF1-CDBCEEACD345',
                'due': datetime.datetime(2018, 11, 29, 0, 0),
                'hash': 'c6ae382b35d6473616042637dbb2f0dd',
                'processed': ['86ff622b57075595bfa33d3241e80022'],
                'user_id': '6a68e9dc382047cba006b5ac4d641789',
                'user_phone_id': '59b3bfbd460c39ed56a00ff3',
            },
            {'processed': ['86ff622b57075595bfa33d3241e80022']},
        ),
    ],
)
def test_same_processed_orders(
        taxi_antifraud,
        db,
        testpoint,
        input,
        expected_aggregates_raw,
        expected_stat_user_raw,
):
    @testpoint('while_updating_new_collection_aggregates_key_duplication')
    def duplication_key_while_updating_new_collection_aggregates(_):
        pass

    @testpoint('while_updating_stats_key_duplication')
    def after_update_stats_users(_):
        pass

    collections_list = [
        db.antifraud_stat_users,
        db.antifraud_stat_phones,
        db.antifraud_stat_devices,
    ]

    response = taxi_antifraud.post('events/order_finish_post', json=input)

    assert response.status_code == 200
    assert response.json() == {}

    for _ in range(2):
        duplication_key_while_updating_new_collection_aggregates.wait_call()
        for __ in range(len(collections_list)):
            after_update_stats_users.wait_call()

    records_aggregates = db.antifraud_users_orders_aggregates.find(
        {}, {'_id': 0, 'created': 0, 'updated': 0},
    )
    assert records_aggregates.count() == 1
    records_aggregates = records_aggregates[0]
    assert records_aggregates == expected_aggregates_raw

    for el in collections_list:
        records_stat_user = el.find({}, {'_id': 0, 'created': 0, 'updated': 0})

        assert records_stat_user.count() == 1
        record_stat_user = records_stat_user[0]
        assert record_stat_user == expected_stat_user_raw


@pytest.mark.config(
    AFS_CUSTOM_USERS_STATISTICS=True,
    AFS_SAVE_STATISTICS_BY_USER_ID=True,
    AFS_FAKERS_BY_GEOZONE_REALTIMES_ENABLED=True,
)
@pytest.mark.parametrize(
    'input,aggregates_output,stat_users_output,'
    'stat_phones_output,stat_devices_output,redis_values',
    [
        (
            [
                {
                    'calc': {
                        'dist': 36923.316524624825,
                        'time': 3081.47226698002,
                    },
                    'payment_tech': {'type': 'card'},
                    'cost': 1320.0,
                    'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                    'city': 'does_not_matter',
                    'zone': 'zone',
                    'fixed_price': {
                        'destination': [37.423615, 55.96412],
                        'driver_price': 1320.0,
                        'price': 1320.0,
                        'price_original': 1320.0,
                    },
                    'order_id': '88b14ea4293650cf9431925fb0bd662a',
                    'request': {
                        'destinations': [{'geopoint': [37.423615, 55.96412]}],
                        'source': {'locality': 'moscow'},
                        'class': 'econom',
                        'due': '2018-11-29T14:50:00+0300',
                        'requirements': {'animaltransport': True},
                        'payment': {'type': 'googlepay'},
                    },
                    'statistics': {
                        'complete_time': '2018-11-29T14:50:08+0300',
                        'driver_delay': 0,
                        'start_transporting_time': '2018-11-29T14:42:18+0300',
                        'start_waiting_time': '2018-11-29T14:42:16+0300',
                        'travel_time': 469.943,
                    },
                    'status': 'finished',
                    'status_updates': [
                        {
                            'created': '2018-11-29T14:40:31+0300',
                            'reason_code': 'create',
                            'status': 'pending',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T14:41:00+0300',
                            'reason_code': 'seen',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T14:41:00+0300',
                            'reason': 'seenimpossible',
                            'reason_code': 'reject',
                        },
                        {
                            'candidate_index': 1,
                            'created': '2018-11-29T14:41:08+0300',
                            'reason_code': 'seen',
                        },
                        {
                            'candidate_index': 1,
                            'created': '2018-11-29T14:41:09+0300',
                            'lookup_generation': 1,
                            'status': 'assigned',
                        },
                        {
                            'candidate_index': 1,
                            'created': '2018-11-29T14:41:09+0300',
                            'taxi_status': 'driving',
                        },
                        {
                            'created': '2018-11-29T14:41:36+0300',
                            'reason': '333',
                            'reason_code': 'autoreorder',
                            'status': 'pending',
                        },
                        {
                            'candidate_index': 2,
                            'created': '2018-11-29T14:41:44+0300',
                            'reason_code': 'seen',
                        },
                        {
                            'candidate_index': 2,
                            'created': '2018-11-29T14:41:44+0300',
                            'lookup_generation': 3,
                            'status': 'assigned',
                        },
                        {
                            'candidate_index': 2,
                            'created': '2018-11-29T14:41:44+0300',
                            'taxi_status': 'driving',
                        },
                        {
                            'candidate_index': 2,
                            'created': '2018-11-29T14:42:16+0300',
                            'taxi_status': 'waiting',
                        },
                        {
                            'candidate_index': 2,
                            'created': '2018-11-29T14:42:18+0300',
                            'taxi_status': 'transporting',
                        },
                        {
                            'candidate_index': 2,
                            'created': '2018-11-29T14:50:08+0300',
                            'status': 'finished',
                            'taxi_status': 'complete',
                        },
                    ],
                    'taxi_status': 'complete',
                    'user_id': 'b066f8f895df7d6d1d762795c888bcbd',
                    'user_phone_id': '5bcd7548030553e658298f6c',
                    'performer': {'uuid': 'uuid'},
                },
                {
                    'calc': {
                        'dist': 36923.316524624825,
                        'time': 3081.47226698002,
                    },
                    'payment_tech': {'type': 'cash'},
                    'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                    'city': 'does_not_matter',
                    'zone': 'zone',
                    'fixed_price': {
                        'destination': [37.423615, 55.96412],
                        'driver_price': 1320.0,
                        'price': 1320.0,
                        'price_original': 1320.0,
                    },
                    'order_id': '88b14ea4293650cf9431925fb0bd667f',
                    'request': {
                        'destinations': [{'geopoint': [37.423615, 55.96412]}],
                        'class': 'econom',
                        'source': {'locality': 'moscow'},
                        'due': '2018-11-29T14:50:00+0300',
                        'requirements': {'animaltransport': True},
                        'payment': {'type': 'cache'},
                    },
                    'statistics': {
                        'cancel_dt': '2018-11-29T14:53:40+0300',
                        'cancel_time': 602.377,
                        'driver_delay': 0,
                        'start_waiting_time': '2018-11-29T14:42:16+0300',
                    },
                    'status': 'finished',
                    'status_updates': [
                        {
                            'created': '2018-11-29T14:40:31+0300',
                            'reason_code': 'create',
                            'status': 'pending',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T14:41:00+0300',
                            'reason_code': 'seen',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T14:41:00+0300',
                            'reason': 'seenimpossible',
                            'reason_code': 'reject',
                        },
                        {
                            'candidate_index': 1,
                            'created': '2018-11-29T14:41:08+0300',
                            'reason_code': 'seen',
                        },
                        {
                            'candidate_index': 1,
                            'created': '2018-11-29T14:41:09+0300',
                            'lookup_generation': 1,
                            'status': 'assigned',
                        },
                        {
                            'candidate_index': 1,
                            'created': '2018-11-29T14:41:09+0300',
                            'taxi_status': 'driving',
                        },
                        {
                            'created': '2018-11-29T14:41:36+0300',
                            'reason': '333',
                            'reason_code': 'autoreorder',
                            'status': 'pending',
                        },
                        {
                            'candidate_index': 2,
                            'created': '2018-11-29T14:41:44+0300',
                            'reason_code': 'seen',
                        },
                        {
                            'candidate_index': 2,
                            'created': '2018-11-29T14:41:44+0300',
                            'lookup_generation': 3,
                            'status': 'assigned',
                        },
                        {
                            'candidate_index': 2,
                            'created': '2018-11-29T14:41:44+0300',
                            'taxi_status': 'driving',
                        },
                        {
                            'candidate_index': 2,
                            'created': '2018-11-29T14:42:16+0300',
                            'taxi_status': 'waiting',
                        },
                        {
                            'candidate_index': 2,
                            'created': '2018-11-29T14:50:08+0300',
                            'status': 'finished',
                            'taxi_status': 'failed',
                        },
                    ],
                    'taxi_status': 'failed',
                    'user_id': 'b066f8f895df7d6d1d762795c888bcbd',
                    'user_phone_id': '5bcd7548030553e658298f6c',
                    'performer': {'uuid': 'uuid'},
                },
                {
                    'calc': {
                        'dist': 15440.113509893417,
                        'time': 4482.031489839252,
                    },
                    'payment_tech': {'type': 'corp'},
                    'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                    'city': 'does_not_matter',
                    'zone': 'zone',
                    'fixed_price': {
                        'destination': [37.62725518753359, 55.77720085404297],
                        'driver_price': 1399.0,
                        'price': 1399.0,
                        'price_original': 1399.0,
                    },
                    'order_id': '672f2a4401b15454a4a2045e3ef06866',
                    'request': {
                        'destinations': [
                            {
                                'geopoint': [
                                    37.653170649870134,
                                    55.705967511509336,
                                ],
                            },
                            {
                                'geopoint': [
                                    37.62725518753359,
                                    55.77720085404297,
                                ],
                            },
                        ],
                        'due': '2018-11-29T15:49:28+0300',
                        'requirements': {
                            'animaltransport': True,
                            'childchair_for_child_tariff': [1, 7],
                        },
                        'payment': {'type': 'cache'},
                    },
                    'statistics': {
                        'cancel_dt': '2018-11-29T15:40:42+0300',
                        'cancel_time': 74.26,
                    },
                    'status': 'cancelled',
                    'status_updates': [
                        {
                            'created': '2018-11-29T15:39:28+0300',
                            'reason_code': 'create',
                            'status': 'pending',
                        },
                        {
                            'created': '2018-11-29T15:40:42+0300',
                            'status': 'cancelled',
                        },
                    ],
                    'user_id': 'b066f8f895df7d6d1d762795c888bcbd',
                    'user_phone_id': '5bcd7548030553e658298f6c',
                    'performer': {'uuid': 'uuid'},
                },
                {
                    'calc': {
                        'dist': 15486.713542699814,
                        'time': 4936.142128267554,
                    },
                    'payment_tech': {'type': 'cash'},
                    'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                    'city': 'does_not_matter',
                    'zone': 'zone',
                    'fixed_price': {
                        'destination': [37.62725518753359, 55.77720085404297],
                        'driver_price': 173.0,
                        'price': 173.0,
                        'price_original': 173.0,
                    },
                    'order_id': '6bb2340f9f935f64a72a454187803e43',
                    'request': {
                        'destinations': [
                            {
                                'geopoint': [
                                    37.65317064987013,
                                    55.70596751150934,
                                ],
                            },
                            {
                                'geopoint': [
                                    37.62725518753359,
                                    55.77720085404297,
                                ],
                            },
                        ],
                        'source': {'locality': 'moscow'},
                        'class': 'econom',
                        'due': '2018-11-29T15:52:00+0300',
                        'payment': {'type': 'card'},
                    },
                    'statistics': {
                        'cancel_distance': 136.9580201936777,
                        'cancel_dt': '2018-11-29T15:47:33+0300',
                        'cancel_time': 43.672,
                    },
                    'status': 'cancelled',
                    'status_updates': [
                        {
                            'created': '2018-11-29T15:46:49+0300',
                            'reason_code': 'create',
                            'status': 'pending',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T15:47:20+0300',
                            'reason_code': 'seen',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T15:47:20+0300',
                            'lookup_generation': 1,
                            'status': 'assigned',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T15:47:20+0300',
                            'taxi_status': 'driving',
                        },
                        {
                            'created': '2018-11-29T15:47:33+0300',
                            'status': 'cancelled',
                        },
                    ],
                    'taxi_status': 'driving',
                    'user_id': 'b066f8f895df7d6d1d762795c888bcbd',
                    'user_phone_id': '5bcd7548030553e658298f6c',
                    'performer': {'uuid': 'uuid'},
                },
                {
                    'calc': {
                        'dist': 15392.113531589508,
                        'time': 5036.486144542201,
                    },
                    'payment_tech': {'type': 'card'},
                    'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                    'city': 'does_not_matter',
                    'zone': 'zone',
                    'fixed_price': {
                        'destination': [37.62725518753359, 55.77720085404297],
                        'driver_price': 273.0,
                        'price': 273.0,
                        'price_original': 273.0,
                    },
                    'order_id': 'fac17464795762e68cf254d1cb1c4055',
                    'request': {
                        'destinations': [
                            {
                                'geopoint': [
                                    37.65317064987013,
                                    55.70596751150934,
                                ],
                            },
                            {
                                'geopoint': [
                                    37.62725518753359,
                                    55.77720085404297,
                                ],
                            },
                        ],
                        'source': {'locality': 'moscow'},
                        'class': 'econom',
                        'due': '2018-11-29T16:02:00+0300',
                        'requirements': {
                            'animaltransport': True,
                            'bicycle': True,
                            'conditioner': True,
                        },
                        'payment': {'type': 'cache'},
                    },
                    'statistics': {
                        'cancel_distance': 3865.9602830043505,
                        'cancel_dt': '2018-11-29T15:49:33+0300',
                        'cancel_time': 46.668,
                    },
                    'status': 'cancelled',
                    'status_updates': [
                        {
                            'created': '2018-11-29T15:48:47+0300',
                            'reason_code': 'create',
                            'status': 'pending',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T15:49:20+0300',
                            'reason_code': 'seen',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T15:49:20+0300',
                            'lookup_generation': 1,
                            'status': 'assigned',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T15:49:20+0300',
                            'taxi_status': 'driving',
                        },
                        {
                            'created': '2018-11-29T15:49:33+0300',
                            'status': 'cancelled',
                        },
                    ],
                    'taxi_status': 'driving',
                    'user_id': 'b066f8f895df7d6d1d762795c888bcbd',
                    'user_phone_id': '5bcd7548030553e658298f6c',
                    'performer': {'uuid': 'uuid'},
                },
                {
                    'calc': {
                        'dist': 15665.613516330719,
                        'time': 4656.497249525844,
                    },
                    'payment_tech': {'type': 'card'},
                    'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                    'city': 'does_not_matter',
                    'zone': 'zone',
                    'fixed_price': {
                        'destination': [37.62725518753359, 55.77720085404297],
                        'driver_price': 273.0,
                        'price': 273.0,
                        'price_original': 273.0,
                    },
                    'order_id': '8a11c40a3a36593b9f5238f058311496',
                    'request': {
                        'destinations': [
                            {
                                'geopoint': [
                                    37.65317064987013,
                                    55.70596751150934,
                                ],
                            },
                            {
                                'geopoint': [
                                    37.62725518753359,
                                    55.77720085404297,
                                ],
                            },
                        ],
                        'source': {'locality': 'moscow'},
                        'class': 'econom',
                        'due': '2018-11-29T15:56:00+0300',
                        'requirements': {
                            'animaltransport': True,
                            'bicycle': True,
                            'conditioner': True,
                        },
                        'payment': {'type': 'googlepay'},
                    },
                    'statistics': {
                        'cancel_dt': '2018-11-29T16:02:39+0300',
                        'cancel_time': 738.862,
                    },
                    'status': 'cancelled',
                    'status_updates': [
                        {
                            'created': '2018-11-29T15:50:21+0300',
                            'reason_code': 'create',
                            'status': 'pending',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T15:50:52+0300',
                            'reason_code': 'seen',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T15:50:54+0300',
                            'lookup_generation': 1,
                            'status': 'assigned',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T15:50:54+0300',
                            'taxi_status': 'driving',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T15:51:07+0300',
                            'taxi_status': 'waiting',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:02:27+0300',
                            'reason': 'manual',
                            'reason_code': 'autoreorder',
                            'status': 'pending',
                        },
                        {
                            'created': '2018-11-29T16:02:39+0300',
                            'status': 'cancelled',
                        },
                    ],
                    'user_id': 'b066f8f895df7d6d1d762795c888bcbd',
                    'user_phone_id': '5bcd7548030553e658298f6c',
                    'performer': {'uuid': 'uuid'},
                },
                {
                    'calc': {
                        'dist': 19609.26798903942,
                        'time': 4624.717621215134,
                    },
                    'payment_tech': {'type': 'card'},
                    'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                    'city': 'does_not_matter',
                    'zone': 'zone',
                    'fixed_price': {
                        'destination': [37.59497720242143, 55.74013859862732],
                        'driver_price': 273.0,
                        'price': 273.0,
                        'price_original': 273.0,
                    },
                    'order_id': 'd881d08f395774cea5a167dce8acc025',
                    'request': {
                        'destinations': [
                            {
                                'geopoint': [
                                    37.63675021569759,
                                    55.75194254501805,
                                ],
                            },
                            {
                                'geopoint': [
                                    37.59497720242143,
                                    55.74013859862732,
                                ],
                            },
                        ],
                        'source': {'locality': 'moscow'},
                        'class': 'econom',
                        'due': '2018-11-29T16:14:00+0300',
                        'requirements': {
                            'animaltransport': True,
                            'bicycle': True,
                            'conditioner': True,
                        },
                        'payment': {'type': 'cache'},
                    },
                    'statistics': {
                        'cancel_dt': '2018-11-29T16:20:40+0300',
                        'cancel_time': 602.377,
                        'driver_delay': 0,
                        'start_waiting_time': '2018-11-29T16:11:07+0300',
                    },
                    'status': 'finished',
                    'status_updates': [
                        {
                            'created': '2018-11-29T16:10:38+0300',
                            'reason_code': 'create',
                            'status': 'pending',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:10:51+0300',
                            'reason_code': 'seen',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:10:53+0300',
                            'lookup_generation': 1,
                            'status': 'assigned',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:10:53+0300',
                            'taxi_status': 'driving',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:11:07+0300',
                            'taxi_status': 'waiting',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:20:40+0300',
                            'reason': 'manual',
                            'status': 'finished',
                            'taxi_status': 'failed',
                        },
                    ],
                    'taxi_status': 'failed',
                    'user_id': '1beea04b93b406070cf3ee4b87cb2f64',
                    'user_phone_id': '5bcd7548030553e658298f6c',
                    'performer': {'uuid': 'uuid'},
                },
                {
                    'calc': {
                        'dist': 16060.667935609818,
                        'time': 5290.119823947917,
                    },
                    'payment_tech': {'type': 'card'},
                    'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                    'city': 'does_not_matter',
                    'zone': 'zone',
                    'fixed_price': {
                        'destination': [37.59497720242143, 55.74013859862732],
                        'driver_price': 273.0,
                        'price': 273.0,
                        'price_original': 273.0,
                    },
                    'order_id': '0391e29f274d5747a49e41b54d5e04a1',
                    'request': {
                        'destinations': [
                            {
                                'geopoint': [
                                    37.63675021569759,
                                    55.75194254501805,
                                ],
                            },
                            {
                                'geopoint': [
                                    37.59497720242143,
                                    55.74013859862732,
                                ],
                            },
                        ],
                        'source': {'locality': 'moscow'},
                        'class': 'econom',
                        'due': '2018-11-29T16:31:28+0300',
                        'requirements': {
                            'animaltransport': True,
                            'bicycle': True,
                            'conditioner': True,
                        },
                        'payment': {'type': 'googlepay'},
                    },
                    'statistics': {
                        'cancel_dt': '2018-11-29T16:31:23+0300',
                        'cancel_time': 595.179,
                    },
                    'status': 'cancelled',
                    'status_updates': [
                        {
                            'created': '2018-11-29T16:21:28+0300',
                            'reason_code': 'create',
                            'status': 'pending',
                        },
                        {
                            'created': '2018-11-29T16:31:23+0300',
                            'status': 'cancelled',
                        },
                    ],
                    'user_id': '1beea04b93b406070cf3ee4b87cb2f64',
                    'user_phone_id': '5bcd7548030553e658298f6c',
                    'performer': {'uuid': 'uuid'},
                },
                {
                    'calc': {
                        'dist': 17829.367928385735,
                        'time': 5733.514055483058,
                    },
                    'payment_tech': {'type': 'card'},
                    'cost': 100.0,
                    'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                    'city': 'does_not_matter',
                    'zone': 'zone',
                    'fixed_price': {
                        'destination': [37.59497720242143, 55.74013859862732],
                        'driver_price': 273.0,
                        'price': 273.0,
                        'price_original': 273.0,
                    },
                    'order_id': '066d4185be4a52be929e216b5bbf4c65',
                    'request': {
                        'destinations': [
                            {
                                'geopoint': [
                                    37.63675021569759,
                                    55.75194254501805,
                                ],
                            },
                            {
                                'geopoint': [
                                    37.59497720242143,
                                    55.74013859862732,
                                ],
                            },
                        ],
                        'source': {'locality': 'moscow'},
                        'class': 'econom',
                        'due': '2018-11-29T16:36:00+0300',
                        'requirements': {
                            'animaltransport': True,
                            'bicycle': True,
                            'conditioner': True,
                        },
                    },
                    'statistics': {
                        'complete_time': '2018-11-29T16:33:22+0300',
                        'driver_delay': 0,
                        'start_transporting_time': '2018-11-29T16:33:13+0300',
                        'start_waiting_time': '2018-11-29T16:33:04+0300',
                        'travel_distance': 0.73095703125,
                        'travel_time': 8.982,
                    },
                    'status': 'finished',
                    'status_updates': [
                        {
                            'created': '2018-11-29T16:32:18+0300',
                            'reason_code': 'create',
                            'status': 'pending',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:32:56+0300',
                            'reason_code': 'seen',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:32:59+0300',
                            'lookup_generation': 1,
                            'status': 'assigned',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:32:59+0300',
                            'taxi_status': 'driving',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:33:04+0300',
                            'taxi_status': 'waiting',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:33:13+0300',
                            'taxi_status': 'transporting',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:33:22+0300',
                            'status': 'finished',
                            'taxi_status': 'complete',
                        },
                    ],
                    'taxi_status': 'complete',
                    'user_id': '1beea04b93b406070cf3ee4b87cb2f64',
                    'user_phone_id': '5bcd7548030553e658298f6c',
                    'performer': {'uuid': 'uuid'},
                },
                {
                    'calc': {
                        'dist': 26282.973979234695,
                        'time': 5090.489927373245,
                    },
                    'payment_tech': {'type': 'card'},
                    'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                    'city': 'does_not_matter',
                    'zone': 'zone',
                    'fixed_price': {
                        'destination': [37.66459515017939, 55.67910084252381],
                        'driver_price': 273.0,
                        'price': 273.0,
                        'price_original': 273.0,
                    },
                    'order_id': '399c238ad1736b07a341e12ee2913e56',
                    'request': {
                        'destinations': [
                            {
                                'geopoint': [
                                    37.59497720242143,
                                    55.74013859862732,
                                ],
                            },
                            {
                                'geopoint': [
                                    37.66459515017939,
                                    55.67910084252381,
                                ],
                            },
                        ],
                        'source': {'locality': 'moscow'},
                        'class': 'econom',
                        'due': '2018-11-29T16:38:00+0300',
                        'requirements': {
                            'animaltransport': True,
                            'conditioner': True,
                        },
                    },
                    'statistics': {
                        'cancel_dt': '2018-11-29T16:35:29+0300',
                        'cancel_time': 75.214,
                        'driver_delay': 0,
                        'late_cancel': True,
                        'start_waiting_time': '2018-11-29T16:34:51+0300',
                    },
                    'status': 'finished',
                    'status_updates': [
                        {
                            'created': '2018-11-29T16:34:14+0300',
                            'reason_code': 'create',
                            'status': 'pending',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:34:26+0300',
                            'reason_code': 'seen',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:34:26+0300',
                            'lookup_generation': 1,
                            'status': 'assigned',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:34:26+0300',
                            'taxi_status': 'driving',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:34:51+0300',
                            'taxi_status': 'waiting',
                        },
                        {
                            'created': '2018-11-29T16:35:29+0300',
                            'reason': 'man, sry',
                            'status': 'finished',
                            'taxi_status': 'cancelled',
                        },
                    ],
                    'taxi_status': 'cancelled',
                    'user_id': '1beea04b93b406070cf3ee4b87cb2f64',
                    'user_phone_id': '5bcd7548030553e658298f6c',
                    'performer': {'uuid': 'uuid'},
                },
                {
                    'calc': {
                        'dist': 26835.97397327423,
                        'time': 4931.172414623512,
                    },
                    'cost': 273.0,
                    'payment_tech': {'type': 'cash'},
                    'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                    'city': 'does_not_matter',
                    'zone': 'zone',
                    'fixed_price': {
                        'destination': [37.66459515017939, 55.67910084252381],
                        'driver_price': 273.0,
                        'price': 273.0,
                        'price_original': 273.0,
                    },
                    'order_id': '0c0292b5e09c727f8240358a5c7d2ecb',
                    'request': {
                        'destinations': [
                            {
                                'geopoint': [
                                    37.59497720242143,
                                    55.74013859862732,
                                ],
                            },
                            {
                                'geopoint': [
                                    37.66459515017939,
                                    55.67910084252381,
                                ],
                            },
                        ],
                        'source': {'locality': 'moscow'},
                        'class': 'econom',
                        'due': '2018-11-29T17:02:00+0300',
                        'requirements': {
                            'animaltransport': True,
                            'conditioner': True,
                        },
                    },
                    'statistics': {
                        'complete_time': '2018-11-29T16:59:15+0300',
                        'driver_delay': 0,
                        'start_transporting_time': '2018-11-29T16:59:05+0300',
                        'start_waiting_time': '2018-11-29T16:56:48+0300',
                        'travel_time': 9.829,
                    },
                    'status': 'finished',
                    'status_updates': [
                        {
                            'created': '2018-11-29T16:53:06+0300',
                            'reason_code': 'create',
                            'status': 'pending',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:53:26+0300',
                            'reason_code': 'seen_timeout',
                        },
                        {
                            'candidate_index': 1,
                            'created': '2018-11-29T16:53:32+0300',
                            'reason_code': 'seen',
                        },
                        {
                            'candidate_index': 1,
                            'created': '2018-11-29T16:53:33+0300',
                            'lookup_generation': 1,
                            'status': 'assigned',
                        },
                        {
                            'candidate_index': 1,
                            'created': '2018-11-29T16:53:33+0300',
                            'taxi_status': 'driving',
                        },
                        {
                            'candidate_index': 1,
                            'created': '2018-11-29T16:56:48+0300',
                            'taxi_status': 'waiting',
                        },
                        {
                            'candidate_index': 1,
                            'created': '2018-11-29T16:59:05+0300',
                            'taxi_status': 'transporting',
                        },
                        {
                            'candidate_index': 1,
                            'created': '2018-11-29T16:59:15+0300',
                            'status': 'finished',
                            'taxi_status': 'complete',
                        },
                    ],
                    'taxi_status': 'complete',
                    'user_id': '1beea04b93b406070cf3ee4b87cb2f64',
                    'user_phone_id': '5bcd7548030553e658298f6c',
                    'performer': {'uuid': 'uuid'},
                },
                {
                    'calc': {
                        'dist': 17829.367928385735,
                        'time': 5733.514055483058,
                    },
                    'payment_tech': {'type': 'card'},
                    'cost': 100.0,
                    'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                    'city': 'does_not_matter',
                    'zone': 'zone',
                    'fixed_price': {
                        'destination': [37.59497720242143, 55.74013859862732],
                        'driver_price': 273.0,
                        'price': 273.0,
                        'price_original': 273.0,
                    },
                    'order_id': '066d4185be4a52be929e216b5bbf4c00',
                    'request': {
                        'destinations': [
                            {
                                'geopoint': [
                                    37.63675021569759,
                                    55.75194254501805,
                                ],
                            },
                            {
                                'geopoint': [
                                    37.59497720242143,
                                    55.74013859862732,
                                ],
                            },
                        ],
                        'source': {'locality': 'moscow'},
                        'class': 'econom',
                        'due': '2018-11-29T02:36:00+0300',
                        'requirements': {
                            'animaltransport': True,
                            'bicycle': True,
                            'conditioner': True,
                        },
                    },
                    'statistics': {
                        'complete_time': '2018-11-29T16:33:22+0300',
                        'driver_delay': 0,
                        'start_transporting_time': '2018-11-29T16:33:13+0300',
                        'start_waiting_time': '2018-11-29T16:33:04+0300',
                        'travel_distance': 0.73095703125,
                        'travel_time': 8.982,
                    },
                    'status': 'finished',
                    'status_updates': [
                        {
                            'created': '2018-11-29T16:32:18+0300',
                            'reason_code': 'create',
                            'status': 'pending',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:32:56+0300',
                            'reason_code': 'seen',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:32:59+0300',
                            'lookup_generation': 1,
                            'status': 'assigned',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:32:59+0300',
                            'taxi_status': 'driving',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:33:04+0300',
                            'taxi_status': 'waiting',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:33:13+0300',
                            'taxi_status': 'transporting',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:33:22+0300',
                            'status': 'finished',
                            'taxi_status': 'complete',
                        },
                    ],
                    'taxi_status': 'complete',
                    'user_id': '1beea04b93b406070cf3ee4b87cb2f64',
                    'user_phone_id': '5bcd7548030553e658298f6c',
                    'performer': {'uuid': 'uuid'},
                },
                {
                    'calc': {
                        'dist': 26282.973979234695,
                        'time': 5090.489927373245,
                    },
                    'payment_tech': {'type': 'card'},
                    'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                    'city': 'does_not_matter',
                    'zone': 'zone',
                    'fixed_price': {
                        'destination': [37.66459515017939, 55.67910084252381],
                        'driver_price': 273.0,
                        'price': 273.0,
                        'price_original': 273.0,
                    },
                    'order_id': '399c238ad1736b07a341e12ee2913e01',
                    'request': {
                        'destinations': [
                            {
                                'geopoint': [
                                    37.59497720242143,
                                    55.74013859862732,
                                ],
                            },
                            {
                                'geopoint': [
                                    37.66459515017939,
                                    55.67910084252381,
                                ],
                            },
                        ],
                        'source': {'locality': 'moscow'},
                        'class': 'econom',
                        'due': '2018-11-29T02:38:00+0300',
                        'requirements': {
                            'animaltransport': True,
                            'conditioner': True,
                        },
                    },
                    'statistics': {
                        'cancel_dt': '2018-11-29T16:35:29+0300',
                        'cancel_time': 75.214,
                        'driver_delay': 0,
                        'late_cancel': True,
                        'start_waiting_time': '2018-11-29T16:34:51+0300',
                    },
                    'status': 'finished',
                    'status_updates': [
                        {
                            'created': '2018-11-29T16:34:14+0300',
                            'reason_code': 'create',
                            'status': 'pending',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:34:26+0300',
                            'reason_code': 'seen',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:34:26+0300',
                            'lookup_generation': 1,
                            'status': 'assigned',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:34:26+0300',
                            'taxi_status': 'driving',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:34:51+0300',
                            'taxi_status': 'waiting',
                        },
                        {
                            'created': '2018-11-29T16:35:29+0300',
                            'reason': 'man, sry',
                            'status': 'finished',
                            'taxi_status': 'cancelled',
                        },
                    ],
                    'taxi_status': 'cancelled',
                    'user_id': '1beea04b93b406070cf3ee4b87cb2f64',
                    'user_phone_id': '5bcd7548030553e658298f6c',
                    'performer': {'uuid': 'uuid'},
                },
                {
                    'calc': {
                        'dist': 26835.97397327423,
                        'time': 4931.172414623512,
                    },
                    'cost': 273.0,
                    'payment_tech': {'type': 'cash'},
                    'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                    'city': 'does_not_matter',
                    'zone': 'zone',
                    'fixed_price': {
                        'destination': [37.66459515017939, 55.67910084252381],
                        'driver_price': 273.0,
                        'price': 273.0,
                        'price_original': 273.0,
                    },
                    'order_id': '0c0292b5e09c727f8240358a5c7d2e02',
                    'request': {
                        'destinations': [
                            {
                                'geopoint': [
                                    37.59497720242143,
                                    55.74013859862732,
                                ],
                            },
                            {
                                'geopoint': [
                                    37.66459515017939,
                                    55.67910084252381,
                                ],
                            },
                        ],
                        'source': {'locality': 'moscow'},
                        'class': 'econom',
                        'due': '2018-11-29T02:02:00+0300',
                        'requirements': {
                            'animaltransport': True,
                            'conditioner': True,
                        },
                    },
                    'statistics': {
                        'complete_time': '2018-11-29T16:59:15+0300',
                        'driver_delay': 0,
                        'start_transporting_time': '2018-11-29T16:59:05+0300',
                        'start_waiting_time': '2018-11-29T16:56:48+0300',
                        'travel_time': 9.829,
                    },
                    'status': 'finished',
                    'status_updates': [
                        {
                            'created': '2018-11-29T16:53:06+0300',
                            'reason_code': 'create',
                            'status': 'pending',
                        },
                        {
                            'candidate_index': 0,
                            'created': '2018-11-29T16:53:26+0300',
                            'reason_code': 'seen_timeout',
                        },
                        {
                            'candidate_index': 1,
                            'created': '2018-11-29T16:53:32+0300',
                            'reason_code': 'seen',
                        },
                        {
                            'candidate_index': 1,
                            'created': '2018-11-29T16:53:33+0300',
                            'lookup_generation': 1,
                            'status': 'assigned',
                        },
                        {
                            'candidate_index': 1,
                            'created': '2018-11-29T16:53:33+0300',
                            'taxi_status': 'driving',
                        },
                        {
                            'candidate_index': 1,
                            'created': '2018-11-29T16:56:48+0300',
                            'taxi_status': 'waiting',
                        },
                        {
                            'candidate_index': 1,
                            'created': '2018-11-29T16:59:05+0300',
                            'taxi_status': 'transporting',
                        },
                        {
                            'candidate_index': 1,
                            'created': '2018-11-29T16:59:15+0300',
                            'status': 'finished',
                            'taxi_status': 'complete',
                        },
                    ],
                    'taxi_status': 'complete',
                    'user_id': '1beea04b93b406070cf3ee4b87cb2f64',
                    'user_phone_id': '5bcd7548030553e658298f6c',
                    'performer': {'uuid': 'uuid'},
                },
            ],
            [
                {
                    'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                    'due': datetime.datetime(2018, 11, 29, 0, 0),
                    'hash': '31412728383d1041002feeed268b8922',
                    'total_in_all_statuses': 6,
                    'cancelled_by_driver_auto_reorder': 1,
                    'cancelled_by_driver_finished': 1,
                    'cancelled_by_user': 4,
                    'complete': 1,
                    'complete_cost': 1320.0,
                    'complete_time': 469,
                    'intermediate_points_count': 10,
                    'intervals': [
                        [
                            datetime.datetime(2018, 11, 29, 11, 40, 31),
                            datetime.datetime(2018, 11, 29, 11, 50, 8),
                        ],
                    ],
                    'planned_cost': 4758.0,
                    'planned_time': 25272,
                    'processed': [
                        '88b14ea4293650cf9431925fb0bd662a',
                        '672f2a4401b15454a4a2045e3ef06866',
                        '88b14ea4293650cf9431925fb0bd667f',
                        '6bb2340f9f935f64a72a454187803e43',
                        'fac17464795762e68cf254d1cb1c4055',
                        '8a11c40a3a36593b9f5238f058311496',
                    ],
                    'requirements_count': 10,
                    'cancelled_before_transporting_drivers_time': 719,
                    'total': 5,
                    'waiting_time': 1154,
                    'user_id': 'b066f8f895df7d6d1d762795c888bcbd',
                    'user_phone_id': '5bcd7548030553e658298f6c',
                    'payment': {
                        'type': {
                            'card': {'complete': 1, 'total': 3},
                            'cash': {'total': 1},
                            'corp': {'total': 1},
                        },
                    },
                    'request_payment': {
                        'type': {
                            'cache': {'total': 2},
                            'card': {'total': 1},
                            'googlepay': {'complete': 1, 'total': 2},
                        },
                    },
                    'geo_zone': {'zone': {'total': 5}},
                },
                {
                    'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                    'due': datetime.datetime(2018, 11, 29, 0, 0),
                    'hash': '60e1bb42b0d20e76fe6ee8c09eebbf72',
                    'total_in_all_statuses': 5,
                    'cancelled_by_driver_finished': 1,
                    'cancelled_by_park': 1,
                    'cancelled_by_user': 1,
                    'complete': 2,
                    'complete_cost': 373.0,
                    'complete_time': 17,
                    'intermediate_points_count': 10,
                    'intervals': [
                        [
                            datetime.datetime(2018, 11, 29, 13, 32, 18),
                            datetime.datetime(2018, 11, 29, 13, 33, 22),
                        ],
                        [
                            datetime.datetime(2018, 11, 29, 13, 53, 6),
                            datetime.datetime(2018, 11, 29, 13, 59, 15),
                        ],
                    ],
                    'planned_cost': 1365.0,
                    'planned_time': 25668,
                    'processed': [
                        'd881d08f395774cea5a167dce8acc025',
                        '0391e29f274d5747a49e41b54d5e04a1',
                        '399c238ad1736b07a341e12ee2913e56',
                        '066d4185be4a52be929e216b5bbf4c65',
                        '0c0292b5e09c727f8240358a5c7d2ecb',
                    ],
                    'requirements_count': 13,
                    'total': 4,
                    'waiting_time': 757,
                    'user_id': '1beea04b93b406070cf3ee4b87cb2f64',
                    'user_phone_id': '5bcd7548030553e658298f6c',
                    'payment': {
                        'type': {
                            'card': {'complete': 1, 'total': 3},
                            'cash': {'complete': 1, 'total': 1},
                        },
                    },
                    'request_payment': {'type': {'googlepay': {'total': 1}}},
                    'geo_zone': {'zone': {'total': 4}},
                },
                {
                    'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                    'due': datetime.datetime(2018, 11, 28, 0, 0),
                    'hash': '60e1bb42b0d20e76fe6ee8c09eebbf72',
                    'total_in_all_statuses': 3,
                    'cancelled_by_park': 1,
                    'complete': 2,
                    'complete_cost': 373.0,
                    'complete_time': 17,
                    'intermediate_points_count': 6,
                    'intervals': [
                        [
                            datetime.datetime(2018, 11, 29, 13, 32, 18),
                            datetime.datetime(2018, 11, 29, 13, 33, 22),
                        ],
                        [
                            datetime.datetime(2018, 11, 29, 13, 53, 6),
                            datetime.datetime(2018, 11, 29, 13, 59, 15),
                        ],
                    ],
                    'planned_cost': 819.0,
                    'planned_time': 15754,
                    'processed': [
                        '066d4185be4a52be929e216b5bbf4c00',
                        '399c238ad1736b07a341e12ee2913e01',
                        '0c0292b5e09c727f8240358a5c7d2e02',
                    ],
                    'requirements_count': 7,
                    'total': 3,
                    'waiting_time': 184,
                    'user_id': '1beea04b93b406070cf3ee4b87cb2f64',
                    'user_phone_id': '5bcd7548030553e658298f6c',
                    'payment': {
                        'type': {
                            'card': {'complete': 1, 'total': 2},
                            'cash': {'complete': 1, 'total': 1},
                        },
                    },
                    'geo_zone': {'zone': {'total': 3}},
                },
            ],
            [
                {
                    '_id': 'b066f8f895df7d6d1d762795c888bcbd',
                    'autoreorders': 1,
                    'complete': 1,
                    'processed': [
                        '88b14ea4293650cf9431925fb0bd662a',
                        '88b14ea4293650cf9431925fb0bd667f',
                        '672f2a4401b15454a4a2045e3ef06866',
                        '6bb2340f9f935f64a72a454187803e43',
                        'fac17464795762e68cf254d1cb1c4055',
                        '8a11c40a3a36593b9f5238f058311496',
                    ],
                    'total': 5,
                    'total_in_all_statuses': 6,
                    'bad_driver_cancels': 1,
                },
                {
                    '_id': '1beea04b93b406070cf3ee4b87cb2f64',
                    'bad_driver_cancels': 1,
                    'processed': [
                        'd881d08f395774cea5a167dce8acc025',
                        '0391e29f274d5747a49e41b54d5e04a1',
                        '066d4185be4a52be929e216b5bbf4c65',
                        '399c238ad1736b07a341e12ee2913e56',
                        '0c0292b5e09c727f8240358a5c7d2ecb',
                        '066d4185be4a52be929e216b5bbf4c00',
                        '399c238ad1736b07a341e12ee2913e01',
                        '0c0292b5e09c727f8240358a5c7d2e02',
                    ],
                    'total': 7,
                    'total_in_all_statuses': 8,
                    'complete': 4,
                },
            ],
            [
                {
                    '_id': '5bcd7548030553e658298f6c',
                    'bad_driver_cancels': 2,
                    'processed': [
                        'fac17464795762e68cf254d1cb1c4055',
                        '8a11c40a3a36593b9f5238f058311496',
                        'd881d08f395774cea5a167dce8acc025',
                        '0391e29f274d5747a49e41b54d5e04a1',
                        '066d4185be4a52be929e216b5bbf4c65',
                        '399c238ad1736b07a341e12ee2913e56',
                        '0c0292b5e09c727f8240358a5c7d2ecb',
                        '066d4185be4a52be929e216b5bbf4c00',
                        '399c238ad1736b07a341e12ee2913e01',
                        '0c0292b5e09c727f8240358a5c7d2e02',
                    ],
                    'total': 12,
                    'total_in_all_statuses': 14,
                    'autoreorders': 1,
                    'complete': 5,
                },
            ],
            [
                {
                    '_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                    'bad_driver_cancels': 2,
                    'processed': [
                        'fac17464795762e68cf254d1cb1c4055',
                        '8a11c40a3a36593b9f5238f058311496',
                        'd881d08f395774cea5a167dce8acc025',
                        '0391e29f274d5747a49e41b54d5e04a1',
                        '066d4185be4a52be929e216b5bbf4c65',
                        '399c238ad1736b07a341e12ee2913e56',
                        '0c0292b5e09c727f8240358a5c7d2ecb',
                        '066d4185be4a52be929e216b5bbf4c00',
                        '399c238ad1736b07a341e12ee2913e01',
                        '0c0292b5e09c727f8240358a5c7d2e02',
                    ],
                    'total': 12,
                    'total_in_all_statuses': 14,
                    'autoreorders': 1,
                    'complete': 5,
                },
            ],
            {
                'zone:card:econom:total:': 9,
                'zone:cash:econom:total:': 4,
                'zone:cash:econom:bad_driver_cancels:': 1,
                'zone:corp::total:': 1,
                'zone:corp::user_cancels:': 1,
                'zone:cash:econom:user_cancels:': 1,
                'zone:card:econom:user_cancels:': 3,
                'zone:card:econom:bad_driver_cancels:': 1,
            },
        ),
    ],
)
@pytest.mark.now('2020-10-01T09:00:00+0000')
def test_order_finish_post_multi(
        taxi_antifraud,
        db,
        testpoint,
        input,
        aggregates_output,
        stat_users_output,
        stat_phones_output,
        stat_devices_output,
        redis_store,
        now,
        redis_values,
):
    @testpoint('after_update_aggregates_in_new_db')
    def after_update_new_aggregates(_):
        pass

    @testpoint('after_update_statistics_users')
    def after_update_stats_users(_):
        pass

    @testpoint('after_update_statistics_phones')
    def after_update_stats_phones(_):
        pass

    @testpoint('after_update_statistics_devices')
    def after_update_stats_devices(_):
        pass

    _REALTIME_METRICS_CANCELS = 'realtime_metrics:cancels:444873'

    for i in input:
        response = taxi_antifraud.post('events/order_finish_post', json=i)

        assert response.status_code == 200
        assert response.json() == {}

        after_update_new_aggregates.wait_call()
        after_update_stats_users.wait_call()
        after_update_stats_phones.wait_call()
        after_update_stats_devices.wait_call()

    for expected_out in aggregates_output:
        new_record_aggregates = db.antifraud_users_orders_aggregates.find_one(
            {'hash': expected_out['hash'], 'due': expected_out['due']},
            {'_id': 0, 'created': 0, 'updated': 0},
        )

        [
            rec.get(field, []).sort()
            for rec in [expected_out, new_record_aggregates]
            for field in ['intervals', 'processed']
        ]

        assert new_record_aggregates == expected_out

    for expected_out in stat_users_output:
        record_stat = db.antifraud_stat_users.find_one(
            {'_id': expected_out['_id']}, {'created': 0, 'updated': 0},
        )
        assert expected_out == record_stat

    for expected_out in stat_phones_output:
        record_stat = db.antifraud_stat_phones.find_one(
            {'_id': expected_out['_id']}, {'created': 0, 'updated': 0},
        )
        assert expected_out == record_stat

    for expected_out in stat_devices_output:
        record_stat = db.antifraud_stat_devices.find_one(
            {'_id': expected_out['_id']}, {'created': 0, 'updated': 0},
        )
        assert expected_out == record_stat

    _ts = utils.to_timestamp(now, utils.Units.MINUTES)
    print(utils.to_timestamp(now, utils.Units.HOURS))

    for key in list(redis_values.keys()):
        redis_values[(key + str(_ts)).encode()] = redis_values.pop(key)

    for _ in range(3):
        alright = True
        if (
                len(
                    set(redis_store.hkeys(_REALTIME_METRICS_CANCELS))
                    - set(redis_values.keys()),
                )
                != 0
        ):
            alright = False
        if alright:
            for key, value in redis_values.items():
                assert (
                    3590
                    < int(redis_store.ttl(_REALTIME_METRICS_CANCELS))
                    <= 3600
                )
                if (
                        int(redis_store.hget(_REALTIME_METRICS_CANCELS, key))
                        != value
                ):
                    alright = False
                    break
        if alright:
            return
        _sleep()

    assert False


_DUE_IN_FUTURE = '2030-11-20T10:54:00+0300'


@pytest.mark.parametrize(
    'input',
    [
        {
            'order_id': 'b63cbecd55be19118e9eac43d455044b',
            'status': 'cancelled',
            'taxi_status': 'driving',
            'calc': {'dist': 15300.189468502998, 'time': 2084.991586796098},
            'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
            'city': 'does_not_matter',
            'zone': 'zone',
            'fixed_price': {
                'destination': [37.59495899698706, 55.73779738195956],
                'driver_price': 609.0,
                'price': 609.0,
                'price_original': 609.0,
            },
            'request': {
                'destinations': [
                    {'geopoint': [37.59495899698706, 55.73779738195956]},
                ],
                'due': _DUE_IN_FUTURE,
            },
            'statistics': {
                'cancel_distance': 104.57167864797431,
                'cancel_dt': '2018-11-20T10:50:21+0300',
                'cancel_time': 48.265,
            },
            'status_updates': [
                {
                    'created': '2018-11-20T10:49:33+0300',
                    'reason_code': 'create',
                    'status': 'pending',
                },
                {
                    'candidate_index': 1,
                    'created': '2018-11-20T10:50:10+0300',
                    'reason_code': 'seen',
                },
                {
                    'candidate_index': 1,
                    'created': '2018-11-20T10:50:11+0300',
                    'lookup_generation': 1,
                    'status': 'assigned',
                },
                {
                    'candidate_index': 1,
                    'created': '2018-11-20T10:50:11+0300',
                    'taxi_status': 'driving',
                },
                {'created': '2018-11-20T10:50:21+0300', 'status': 'cancelled'},
            ],
            'multiorder_order_number': 0,
            'user_id': '564d49a5d252b097f94eacea37353f4f',
            'user_phone_id': '5bcd7548030553e658298f6c',
            'performer': {'uuid': 'uuid'},
        },
    ],
)
@pytest.mark.now('2020-10-01T09:00:00+0000')
def test_request_with_due_in_future(taxi_antifraud, db, testpoint, input, now):
    @testpoint('after_update_aggregates_in_new_db')
    def after_update_new_aggregates(_):
        pass

    response = taxi_antifraud.post('events/order_finish_post', json=input)

    assert response.status_code == 200
    assert response.json() == {}

    after_update_new_aggregates.wait_call()

    record_aggregates = db.antifraud_users_orders_aggregates.find_one()
    assert utils.to_timestamp(now, utils.Units.DAYS) == utils.to_timestamp(
        record_aggregates['due'], utils.Units.DAYS,
    )


@pytest.mark.parametrize(
    'input',
    [
        {
            'order_id': 'b63cbecd55be19118e9eac43d455044b',
            'status': 'cancelled',
            'taxi_status': 'driving',
            'calc': {'dist': 15300.189468502998, 'time': 2084.991586796098},
            'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
            'city': 'does_not_matter',
            'zone': 'zone',
            'fixed_price': {
                'destination': [37.59495899698706, 55.73779738195956],
                'driver_price': 609.0,
                'price': 609.0,
                'price_original': 609.0,
            },
            'request': {
                'destinations': [
                    {'geopoint': [37.59495899698706, 55.73779738195956]},
                ],
                'due': _DUE_IN_FUTURE,
            },
            'statistics': {
                'cancel_distance': 104.57167864797431,
                'cancel_dt': '2018-11-20T10:50:21+0300',
                'cancel_time': 48.265,
            },
            'status_updates': [
                {
                    'created': '2018-11-20T10:49:33+0300',
                    'reason_code': 'create',
                    'status': 'pending',
                },
                {
                    'candidate_index': 1,
                    'created': '2018-11-20T10:50:10+0300',
                    'reason_code': 'seen',
                },
                {
                    'candidate_index': 1,
                    'created': '2018-11-20T10:50:11+0300',
                    'lookup_generation': 1,
                    'status': 'assigned',
                },
                {
                    'candidate_index': 1,
                    'created': '2018-11-20T10:50:11+0300',
                    'taxi_status': 'driving',
                },
                {'created': '2018-11-20T10:50:21+0300', 'status': 'cancelled'},
            ],
            'multiorder_order_number': 0,
            'user_id': '564d49a5d252b097f94eacea37353f4f',
            'user_phone_id': '5bcd7548030553e658298f6c',
            'performer': {'uuid': 'uuid'},
        },
    ],
)
@pytest.mark.now('2020-10-01T09:00:00+0000')
@pytest.mark.config(AFS_STORE_APPLICATION_AGGREGATES=True)
def test_application_aggregation(
        taxi_antifraud, db, testpoint, input, now, mockserver,
):
    @mockserver.json_handler('/user-api/users/get')
    def mock_user_get(_):
        return {'id': 'user_id', 'application': 'app'}

    @testpoint('after_update_aggregates_in_new_db')
    def after_update_new_aggregates(_):
        pass

    response = taxi_antifraud.post('events/order_finish_post', json=input)

    assert response.status_code == 200
    assert response.json() == {}

    after_update_new_aggregates.wait_call()

    record_aggregates = db.antifraud_users_orders_aggregates.find_one()
    assert record_aggregates['application'] == {'app': {'total': 1}}


@pytest.mark.parametrize(
    'input',
    [
        {
            'order_id': 'b63cbecd55be19118e9eac43d455044b',
            'status': 'cancelled',
            'taxi_status': 'driving',
            'calc': {'dist': 15300.189468502998, 'time': 2084.991586796098},
            'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
            'city': 'does_not_matter',
            'zone': 'zone',
            'fixed_price': {
                'destination': [37.59495899698706, 55.73779738195956],
                'driver_price': 609.0,
                'price': 609.0,
                'price_original': 609.0,
            },
            'request': {
                'destinations': [
                    {'geopoint': [37.59495899698706, 55.73779738195956]},
                ],
                'due': _DUE_IN_FUTURE,
            },
            'statistics': {
                'cancel_distance': 104.57167864797431,
                'cancel_dt': '2018-11-20T10:50:21+0300',
                'cancel_time': 48.265,
            },
            'status_updates': [
                {
                    'created': '2018-11-20T10:49:33+0300',
                    'reason_code': 'create',
                    'status': 'pending',
                },
                {
                    'candidate_index': 1,
                    'created': '2018-11-20T10:50:10+0300',
                    'reason_code': 'seen',
                },
                {
                    'candidate_index': 1,
                    'created': '2018-11-20T10:50:11+0300',
                    'lookup_generation': 1,
                    'status': 'assigned',
                },
                {
                    'candidate_index': 1,
                    'created': '2018-11-20T10:50:11+0300',
                    'taxi_status': 'driving',
                },
                {'created': '2018-11-20T10:50:21+0300', 'status': 'cancelled'},
            ],
            'multiorder_order_number': 0,
            'user_id': '564d49a5d252b097f94eacea37353f4f',
            'user_phone_id': '5bcd7548030553e658298f6c',
            'performer': {'uuid': 'uuid'},
        },
    ],
)
@pytest.mark.now('2020-10-01T09:00:00+0000')
@pytest.mark.config(AFS_STORE_APPLICATION_AGGREGATES=True)
def test_no_application(taxi_antifraud, db, testpoint, input, now, mockserver):
    @mockserver.json_handler('/user-api/users/get')
    def mock_user_get(_):
        return {'id': 'user_id'}

    @testpoint('after_update_aggregates_in_new_db')
    def after_update_new_aggregates(_):
        pass

    response = taxi_antifraud.post('events/order_finish_post', json=input)

    assert response.status_code == 200
    assert response.json() == {}

    after_update_new_aggregates.wait_call()

    record_aggregates = db.antifraud_users_orders_aggregates.find_one()
    assert 'application' not in record_aggregates


@pytest.mark.parametrize(
    'input,expected_subdict',
    [
        (
            {
                'order_id': 'b63cbecd55be19118e9eac43d455044b',
                'status': 'cancelled',
                'taxi_status': 'driving',
                'calc': {
                    'dist': 15300.189468502998,
                    'time': 2084.991586796098,
                },
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'city': 'does_not_matter',
                'zone': 'zone',
                'fixed_price': {
                    'destination': [37.59495899698706, 55.73779738195956],
                    'driver_price': 609.0,
                    'price': 609.0,
                    'price_original': 609.0,
                },
                'request': {
                    'destinations': [
                        {'geopoint': [37.59495899698706, 55.73779738195956]},
                    ],
                    'due': _DUE_IN_FUTURE,
                },
                'statistics': {
                    'cancel_distance': 104.57167864797431,
                    'cancel_dt': '2018-11-20T10:50:21+0300',
                    'cancel_time': 48.265,
                },
                'status_updates': [
                    {
                        'created': '2018-11-20T10:49:33+0300',
                        'reason_code': 'create',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:10+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:11+0300',
                        'lookup_generation': 1,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:11+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:31+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:41+0300',
                        'taxi_status': 'autoreorder',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:45+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:50+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'created': '2018-11-20T10:50:53+0300',
                        'status': 'cancelled',
                    },
                ],
                'multiorder_order_number': 0,
                'user_id': '564d49a5d252b097f94eacea37353f4f',
                'user_phone_id': '5bcd7548030553e658298f6c',
                'performer': {'uuid': 'uuid'},
            },
            {'cancelled_before_transporting_drivers_time': 38},
        ),
        (
            {
                'order_id': 'b63cbecd55be19118e9eac43d455044b',
                'status': 'cancelled',
                'taxi_status': 'driving',
                'calc': {
                    'dist': 15300.189468502998,
                    'time': 2084.991586796098,
                },
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'city': 'does_not_matter',
                'zone': 'zone',
                'fixed_price': {
                    'destination': [37.59495899698706, 55.73779738195956],
                    'driver_price': 609.0,
                    'price': 609.0,
                    'price_original': 609.0,
                },
                'request': {
                    'destinations': [
                        {'geopoint': [37.59495899698706, 55.73779738195956]},
                    ],
                    'due': _DUE_IN_FUTURE,
                },
                'statistics': {
                    'cancel_distance': 104.57167864797431,
                    'cancel_dt': '2018-11-20T10:50:21+0300',
                    'cancel_time': 48.265,
                },
                'status_updates': [
                    {
                        'created': '2018-11-20T10:49:33+0300',
                        'reason_code': 'create',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:10+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:11+0300',
                        'lookup_generation': 1,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:11+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:31+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:41+0300',
                        'taxi_status': 'autoreorder',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:45+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:50+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:56+0300',
                        'taxi_status': 'transporting',
                    },
                    {
                        'created': '2018-11-20T10:50:59+0300',
                        'status': 'cancelled',
                    },
                ],
                'multiorder_order_number': 0,
                'user_id': '564d49a5d252b097f94eacea37353f4f',
                'user_phone_id': '5bcd7548030553e658298f6c',
                'performer': {'uuid': 'uuid'},
            },
            {'cancelled_transporting_drivers_time': 44},
        ),
    ],
)
@pytest.mark.now('2020-10-01T09:00:00+0000')
def test_driver_waste_time(
        taxi_antifraud, db, testpoint, input, expected_subdict,
):
    @testpoint('after_update_aggregates_in_new_db')
    def after_update_new_aggregates(_):
        pass

    response = taxi_antifraud.post('events/order_finish_post', json=input)

    assert response.status_code == 200
    assert response.json() == {}

    record_aggregates = db.antifraud_users_orders_aggregates.find_one()

    print(record_aggregates)

    utils.check_dict_is_subdict(record_aggregates, expected_subdict)


@pytest.mark.parametrize(
    'input,expected_subdict',
    [
        (
            {
                'order_id': 'b63cbecd55be19118e9eac43d455044b',
                'status': 'cancelled',
                'taxi_status': 'driving',
                'calc': {
                    'dist': 15300.189468502998,
                    'time': 2084.991586796098,
                },
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'city': 'does_not_matter',
                'zone': 'zone',
                'fixed_price': {
                    'destination': [37.59495899698706, 55.73779738195956],
                    'driver_price': 609.0,
                    'price': 609.0,
                    'price_original': 609.0,
                },
                'request': {
                    'destinations': [
                        {'geopoint': [37.59495899698706, 55.73779738195956]},
                    ],
                    'due': _DUE_IN_FUTURE,
                },
                'statistics': {
                    'cancel_distance': 104.57167864797431,
                    'cancel_dt': '2018-11-20T10:50:21+0300',
                    'cancel_time': 48.265,
                },
                'status_updates': [
                    {
                        'created': '2018-11-20T10:49:33+0300',
                        'reason_code': 'create',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:10+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:11+0300',
                        'lookup_generation': 1,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:11+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:31+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:41+0300',
                        'taxi_status': 'autoreorder',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:45+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:50+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'created': '2018-11-20T10:50:53+0300',
                        'status': 'cancelled',
                    },
                ],
                'multiorder_order_number': 0,
                'user_id': '564d49a5d252b097f94eacea37353f4f',
                'user_phone_id': '5bcd7548030553e658298f6c',
                'performer': {'uuid': 'uuid'},
            },
            {'cancelled_by_user': 1},
        ),
        (
            {
                'order_id': 'b63cbecd55be19118e9eac43d455044b',
                'status': 'cancelled',
                'taxi_status': 'driving',
                'calc': {
                    'dist': 15300.189468502998,
                    'time': 2084.991586796098,
                },
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'city': 'does_not_matter',
                'zone': 'zone',
                'fixed_price': {
                    'destination': [37.59495899698706, 55.73779738195956],
                    'driver_price': 609.0,
                    'price': 609.0,
                    'price_original': 609.0,
                },
                'request': {
                    'destinations': [
                        {'geopoint': [37.59495899698706, 55.73779738195956]},
                    ],
                    'due': _DUE_IN_FUTURE,
                },
                'statistics': {
                    'cancel_distance': 104.57167864797431,
                    'cancel_dt': '2018-11-20T10:50:21+0300',
                    'cancel_time': 48.265,
                },
                'status_updates': [
                    {
                        'created': '2018-11-20T10:49:33+0300',
                        'reason_code': 'create',
                        'status': 'pending',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:10+0300',
                        'reason_code': 'seen',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:11+0300',
                        'lookup_generation': 1,
                        'status': 'assigned',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:11+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:31+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:41+0300',
                        'taxi_status': 'autoreorder',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:45+0300',
                        'taxi_status': 'driving',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:50+0300',
                        'taxi_status': 'waiting',
                    },
                    {
                        'candidate_index': 1,
                        'created': '2018-11-20T10:50:56+0300',
                        'taxi_status': 'transporting',
                    },
                    {
                        'created': '2018-11-20T10:50:59+0300',
                        'status': 'cancelled',
                    },
                ],
                'multiorder_order_number': 0,
                'user_id': '564d49a5d252b097f94eacea37353f4f',
                'user_phone_id': '5bcd7548030553e658298f6c',
            },
            {'cancelled_by_user_without_performer': 1},
        ),
    ],
)
@pytest.mark.now('2020-10-01T09:00:00+0000')
def test_user_cancells_separation(
        taxi_antifraud, db, testpoint, input, expected_subdict,
):
    @testpoint('after_update_aggregates_in_new_db')
    def after_update_new_aggregates(_):
        pass

    response = taxi_antifraud.post('events/order_finish_post', json=input)

    assert response.status_code == 200
    assert response.json() == {}

    record_aggregates = db.antifraud_users_orders_aggregates.find_one()

    print(record_aggregates)

    utils.check_dict_is_subdict(record_aggregates, expected_subdict)
