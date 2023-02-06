import copy
import datetime
import typing as tp

ALL_ORDER_IDS = ('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', '1')


BASIC_EVENT = {
    'order_id': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'user_phone_id': '6141a81573872fb3b53037ed',
    'zone_id': 'moscow',
    'tariff_class': 'vip',
    'event_key': 'handle_assigning',
    'event_timestamp': {'$date': '2020-01-01T12:00:00.000Z'},
    'performer': {
        'uuid': '11111111111111111111111111111111',
        'dbid': '00000000000000000000000000000000',
        'distance': 5000,
        'time': 300,
    },
    'point_a': [20, 30],
    'destinations': [],
    'requirements': {},
}


EVENT_PERFORMER_CHANGED = {
    'order_id': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'user_phone_id': '6141a81573872fb3b53037ed',
    'zone_id': 'moscow',
    'tariff_class': 'vip',
    'event_key': 'handle_assigning',
    'event_timestamp': {'$date': '2020-01-01T12:05:00.000Z'},
    'performer': {
        'uuid': '11111111111111111111111111111112',
        'dbid': '00000000000000000000000000000001',
        'distance': 3000,
        'time': 200,
    },
    'point_a': [20, 30],
    'destinations': [],
    'requirements': {},
}


TEST_ITEMS: tp.List[tp.Dict[str, tp.Any]] = [
    # this driver didn't accept the order
    {
        'event': {
            'performer': {
                'uuid': '00000000000000000000000000000000',
                'dbid': 'df98ffa680714291882343e7df1ca5ab',
                'distance': 300,
                'time': 40,
            },
            'event_key': 'new_driver_found',
            'order_id': '1',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'zone_id': 'moscow',
            'event_timestamp': {'$date': '2019-09-10T03:22:37.733Z'},
            'tariff_class': 'vip',
            'point_a': [20.123123, 30.123123],
            'destinations': [[21.123123, 31.123123]],
            'requirements': {'door_to_door': True},
        },
        'database_order_state': {
            'order_id': '1',
            'zone_id': 'moscow',
            'tariff_class': 'vip',
            'last_event_handled': datetime.datetime(
                2019, 9, 10, 3, 22, 37, 733000,
            ),
            'performer_dbid_uuid': (
                'df98ffa680714291882343e7df1ca5ab_'
                '00000000000000000000000000000000'
            ),
            'performer_assigned': None,
            'performer_initial_eta': datetime.timedelta(seconds=40),
            'performer_initial_distance': 300.0,
            'first_performer_assigned': None,
            'first_performer_initial_eta': datetime.timedelta(seconds=40),
            'first_performer_initial_distance': 300.0,
            'eta_autoreorders_count': 0,
            'last_autoreorder_detected': None,
            'autoreorder_in_progress': False,
            'reorder_situation_detected': False,
            'last_event': 'new_driver_found',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'performer_cp_id': None,
            'point_a': [20.123123, 30.123123],
            'destinations': [[21.123123, 31.123123]],
            'requirements': '{"door_to_door":true}',
        },
    },
    # first performer found
    {
        'event': {
            'performer': {
                'uuid': '957600cda6b74ca58fe20963d61ff060',
                'dbid': 'df98ffa680714291882343e7df1ca5ab',
                'distance': 982,
                'time': 296,
            },
            'event_key': 'new_driver_found',
            'order_id': '1',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'zone_id': 'moscow',
            'event_timestamp': {'$date': '2019-09-10T03:23:37.733Z'},
            'tariff_class': 'vip',
            'point_a': [20.123123, 30.123123],
            'destinations': [[21.123123, 31.123123]],
            'requirements': {'door_to_door': True},
        },
        'database_order_state': {
            'order_id': '1',
            'zone_id': 'moscow',
            'tariff_class': 'vip',
            'last_event_handled': datetime.datetime(
                2019, 9, 10, 3, 23, 37, 733000,
            ),
            'performer_dbid_uuid': (
                'df98ffa680714291882343e7df1ca5ab_'
                '957600cda6b74ca58fe20963d61ff060'
            ),
            'performer_assigned': None,
            'performer_initial_eta': datetime.timedelta(seconds=296),
            'performer_initial_distance': 982.0,
            'first_performer_assigned': None,
            'first_performer_initial_eta': datetime.timedelta(seconds=296),
            'first_performer_initial_distance': 982.0,
            'eta_autoreorders_count': 0,
            'last_autoreorder_detected': None,
            'autoreorder_in_progress': False,
            'reorder_situation_detected': False,
            'last_event': 'new_driver_found',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'performer_cp_id': None,
            'point_a': [20.123123, 30.123123],
            'destinations': [[21.123123, 31.123123]],
            'requirements': '{"door_to_door":true}',
        },
    },
    # first performer driving to A
    {
        'event': {
            'performer': {
                'uuid': '957600cda6b74ca58fe20963d61ff060',
                'dbid': 'df98ffa680714291882343e7df1ca5ab',
                'distance': 982,
                'time': 296,
            },
            'event_key': 'handle_assigning',
            'order_id': '1',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'zone_id': 'moscow',
            'event_timestamp': {'$date': '2019-09-10T03:24:37.733Z'},
            'tariff_class': 'vip',
            'point_a': [20.123123, 30.123123],
            'destinations': [[21.123123, 31.123123]],
            'requirements': {'door_to_door': True},
        },
        'database_order_state': {
            'order_id': '1',
            'zone_id': 'moscow',
            'tariff_class': 'vip',
            'last_event_handled': datetime.datetime(
                2019, 9, 10, 3, 24, 37, 733000,
            ),
            'performer_dbid_uuid': (
                'df98ffa680714291882343e7df1ca5ab_'
                '957600cda6b74ca58fe20963d61ff060'
            ),
            'performer_assigned': datetime.datetime(
                2019, 9, 10, 3, 24, 37, 733000,
            ),
            'performer_initial_eta': datetime.timedelta(seconds=296),
            'performer_initial_distance': 982.0,
            'first_performer_assigned': datetime.datetime(
                2019, 9, 10, 3, 24, 37, 733000,
            ),
            'first_performer_initial_eta': datetime.timedelta(seconds=296),
            'first_performer_initial_distance': 982.0,
            'eta_autoreorders_count': 0,
            'last_autoreorder_detected': None,
            'autoreorder_in_progress': False,
            'reorder_situation_detected': False,
            'last_event': 'handle_driving',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'performer_cp_id': None,
            'point_a': [20.123123, 30.123123],
            'destinations': [[21.123123, 31.123123]],
            'requirements': '{"door_to_door":true}',
        },
    },
    # second driver is found
    {
        'event': {
            'performer': {
                'uuid': 'ca5ed75b30de4a748da0db193a7092a2',
                'dbid': 'df98ffa680714291882343e7df1ca5ab',
                'distance': 200,
                'time': 50,
            },
            'event_key': 'new_driver_found',
            'order_id': '1',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'zone_id': 'moscow',
            'event_timestamp': {'$date': '2019-09-10T03:25:37.733Z'},
            'tariff_class': 'vip',
            'point_a': [20.123123, 30.123123],
            'destinations': [[21.123123, 31.123123]],
            'requirements': {'door_to_door': True},
        },
        'database_order_state': {
            'order_id': '1',
            'zone_id': 'moscow',
            'tariff_class': 'vip',
            'last_event_handled': datetime.datetime(
                2019, 9, 10, 3, 25, 37, 733000,
            ),
            'performer_dbid_uuid': (
                'df98ffa680714291882343e7df1ca5ab_'
                'ca5ed75b30de4a748da0db193a7092a2'
            ),
            'performer_assigned': None,
            'performer_initial_eta': datetime.timedelta(seconds=50),
            'performer_initial_distance': 200.0,
            'first_performer_assigned': datetime.datetime(
                2019, 9, 10, 3, 24, 37, 733000,
            ),
            'first_performer_initial_eta': datetime.timedelta(seconds=296),
            'first_performer_initial_distance': 982.0,
            'eta_autoreorders_count': 0,
            'last_autoreorder_detected': None,
            'autoreorder_in_progress': False,
            'reorder_situation_detected': False,
            'last_event': 'new_driver_found',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'performer_cp_id': None,
            'point_a': [20.123123, 30.123123],
            'destinations': [[21.123123, 31.123123]],
            'requirements': '{"door_to_door":true}',
        },
    },
    # second performer driving to A after autoreorder
    {
        'event': {
            'performer': {
                'uuid': 'ca5ed75b30de4a748da0db193a7092a2',
                'dbid': 'df98ffa680714291882343e7df1ca5ab',
                'distance': 200,
                'time': 50,
            },
            'event_key': 'handle_driving',
            'order_id': '1',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'zone_id': 'moscow',
            'event_timestamp': {'$date': '2019-09-10T03:26:37.733Z'},
            'tariff_class': 'vip',
            'point_a': [20.123123, 30.123123],
            'destinations': [[21.123123, 31.123123]],
            'requirements': {'door_to_door': True},
        },
        'database_order_state': {
            'order_id': '1',
            'zone_id': 'moscow',
            'tariff_class': 'vip',
            'last_event_handled': datetime.datetime(
                2019, 9, 10, 3, 26, 37, 733000,
            ),
            'performer_dbid_uuid': (
                'df98ffa680714291882343e7df1ca5ab_'
                'ca5ed75b30de4a748da0db193a7092a2'
            ),
            'performer_assigned': datetime.datetime(
                2019, 9, 10, 3, 26, 37, 733000,
            ),
            'performer_initial_eta': datetime.timedelta(seconds=50),
            'performer_initial_distance': 200.0,
            'first_performer_assigned': datetime.datetime(
                2019, 9, 10, 3, 24, 37, 733000,
            ),
            'first_performer_initial_eta': datetime.timedelta(seconds=296),
            'first_performer_initial_distance': 982.0,
            'eta_autoreorders_count': 0,
            'last_autoreorder_detected': None,
            'autoreorder_in_progress': False,
            'reorder_situation_detected': False,
            'last_event': 'handle_driving',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'performer_cp_id': None,
            'point_a': [20.123123, 30.123123],
            'destinations': [[21.123123, 31.123123]],
            'requirements': '{"door_to_door":true}',
        },
    },
    # destinations changed event
    {
        'event': {
            'performer': {
                'uuid': 'ca5ed75b30de4a748da0db193a7092a2',
                'dbid': 'df98ffa680714291882343e7df1ca5ab',
                'distance': 200,
                'time': 50,
            },
            'event_key': 'destinations_changed',
            'order_id': '1',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'zone_id': 'moscow',
            'event_timestamp': {'$date': '2019-09-10T03:26:40.733Z'},
            'tariff_class': 'vip',
            'point_a': [20.123123, 30.123123],
            'destinations': [[21.123123, 31.123123], [22.123123, 32.123123]],
            'requirements': {'door_to_door': True},
        },
        'database_order_state': {
            'order_id': '1',
            'zone_id': 'moscow',
            'tariff_class': 'vip',
            'last_event_handled': datetime.datetime(
                2019, 9, 10, 3, 26, 37, 733000,
            ),
            'performer_dbid_uuid': (
                'df98ffa680714291882343e7df1ca5ab_'
                'ca5ed75b30de4a748da0db193a7092a2'
            ),
            'performer_assigned': datetime.datetime(
                2019, 9, 10, 3, 26, 37, 733000,
            ),
            'performer_initial_eta': datetime.timedelta(seconds=50),
            'performer_initial_distance': 200.0,
            'first_performer_assigned': datetime.datetime(
                2019, 9, 10, 3, 24, 37, 733000,
            ),
            'first_performer_initial_eta': datetime.timedelta(seconds=296),
            'first_performer_initial_distance': 982.0,
            'eta_autoreorders_count': 0,
            'last_autoreorder_detected': None,
            'autoreorder_in_progress': False,
            'reorder_situation_detected': False,
            'last_event': 'handle_driving',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'performer_cp_id': None,
            'point_a': [20.123123, 30.123123],
            'destinations': [[21.123123, 31.123123], [22.123123, 32.123123]],
            'requirements': '{"door_to_door":true}',
        },
    },
    # second performer waiting client at A
    {
        'event': {
            'performer': {
                'uuid': 'ca5ed75b30de4a748da0db193a7092a2',
                'dbid': 'df98ffa680714291882343e7df1ca5ab',
                'distance': 200,
                'time': 50,
            },
            'event_key': 'handle_waiting',
            'order_id': '1',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'zone_id': 'moscow',
            'event_timestamp': {'$date': '2019-09-10T03:27:37.733Z'},
            'tariff_class': 'vip',
            'point_a': [20.123123, 30.123123],
            'destinations': [[21.123123, 31.123123], [22.123123, 32.123123]],
            'requirements': {'door_to_door': True},
        },
        'database_order_state': {
            'order_id': '1',
            'zone_id': 'moscow',
            'tariff_class': 'vip',
            'last_event_handled': datetime.datetime(
                2019, 9, 10, 3, 26, 37, 733000,
            ),
            'performer_dbid_uuid': (
                'df98ffa680714291882343e7df1ca5ab_'
                'ca5ed75b30de4a748da0db193a7092a2'
            ),
            'performer_assigned': datetime.datetime(
                2019, 9, 10, 3, 26, 37, 733000,
            ),
            'performer_initial_eta': datetime.timedelta(seconds=50),
            'performer_initial_distance': 200.0,
            'first_performer_assigned': datetime.datetime(
                2019, 9, 10, 3, 24, 37, 733000,
            ),
            'first_performer_initial_eta': datetime.timedelta(seconds=296),
            'first_performer_initial_distance': 982.0,
            'eta_autoreorders_count': 0,
            'last_autoreorder_detected': None,
            'autoreorder_in_progress': False,
            'reorder_situation_detected': False,
            'last_event': 'handle_driving',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'performer_cp_id': None,
            'point_a': [20.123123, 30.123123],
            'destinations': [[21.123123, 31.123123], [22.123123, 32.123123]],
            'requirements': '{"door_to_door":true}',
        },
    },
    # second performer transporting client to B
    {
        'event': {
            'performer': {
                'uuid': 'ca5ed75b30de4a748da0db193a7092a2',
                'dbid': 'df98ffa680714291882343e7df1ca5ab',
                'distance': 200,
                'time': 50,
            },
            'event_key': 'handle_transporting',
            'order_id': '1',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'zone_id': 'moscow',
            'event_timestamp': {'$date': '2019-09-10T03:28:37.733Z'},
            'tariff_class': 'vip',
            'point_a': [20.123123, 30.123123],
            'destinations': [[21.123123, 31.123123], [22.123123, 32.123123]],
            'requirements': {'door_to_door': True},
        },
        'database_order_state': {
            'order_id': '1',
            'zone_id': 'moscow',
            'tariff_class': 'vip',
            'last_event_handled': datetime.datetime(
                2019, 9, 10, 3, 26, 37, 733000,
            ),
            'performer_dbid_uuid': (
                'df98ffa680714291882343e7df1ca5ab_'
                'ca5ed75b30de4a748da0db193a7092a2'
            ),
            'performer_assigned': datetime.datetime(
                2019, 9, 10, 3, 26, 37, 733000,
            ),
            'performer_initial_eta': datetime.timedelta(seconds=50),
            'performer_initial_distance': 200.0,
            'first_performer_assigned': datetime.datetime(
                2019, 9, 10, 3, 24, 37, 733000,
            ),
            'first_performer_initial_eta': datetime.timedelta(seconds=296),
            'first_performer_initial_distance': 982.0,
            'eta_autoreorders_count': 0,
            'last_autoreorder_detected': None,
            'autoreorder_in_progress': False,
            'reorder_situation_detected': False,
            'last_event': 'handle_driving',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'performer_cp_id': None,
            'point_a': [20.123123, 30.123123],
            'destinations': [[21.123123, 31.123123], [22.123123, 32.123123]],
            'requirements': '{"door_to_door":true}',
        },
    },
    # order complete
    {
        'event': {
            'performer': {
                'uuid': 'ca5ed75b30de4a748da0db193a7092a2',
                'dbid': 'df98ffa680714291882343e7df1ca5ab',
                'distance': 200,
                'time': 50,
            },
            'event_key': 'handle_finish',
            'order_id': '1',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'zone_id': 'moscow',
            'event_timestamp': {'$date': '2019-09-10T03:29:37.733Z'},
            'tariff_class': 'vip',
            'point_a': [20.123123, 30.123123],
            'destinations': [[21.123123, 31.123123], [22.123123, 32.123123]],
            'requirements': {'door_to_door': True},
        },
        'database_order_state': {
            'order_id': '1',
            'zone_id': 'moscow',
            'tariff_class': 'vip',
            'last_event_handled': datetime.datetime(
                2019, 9, 10, 3, 26, 37, 733000,
            ),
            'performer_dbid_uuid': (
                'df98ffa680714291882343e7df1ca5ab_'
                'ca5ed75b30de4a748da0db193a7092a2'
            ),
            'performer_assigned': datetime.datetime(
                2019, 9, 10, 3, 26, 37, 733000,
            ),
            'performer_initial_eta': datetime.timedelta(seconds=50),
            'performer_initial_distance': 200.0,
            'first_performer_assigned': datetime.datetime(
                2019, 9, 10, 3, 24, 37, 733000,
            ),
            'first_performer_initial_eta': datetime.timedelta(seconds=296),
            'first_performer_initial_distance': 982.0,
            'eta_autoreorders_count': 0,
            'last_autoreorder_detected': None,
            'autoreorder_in_progress': False,
            'reorder_situation_detected': False,
            'last_event': 'handle_driving',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'performer_cp_id': None,
            'point_a': [20.123123, 30.123123],
            'destinations': [[21.123123, 31.123123], [22.123123, 32.123123]],
            'requirements': '{"door_to_door":true}',
        },
    },
]


def get_event_with_transformed_tp(event):
    transformed_event = copy.deepcopy(event)
    transformed_event['event_timestamp'] = str(
        datetime.datetime.strptime(
            transformed_event['event_timestamp']['$date'],
            '%Y-%m-%dT%H:%M:%S.%fZ',
        )
        .replace(tzinfo=datetime.timezone.utc)
        .isoformat(timespec='milliseconds'),
    )
    return transformed_event


def database_order_state_to_list(order_state):
    return [value for _, value in order_state.items()]


def erase_real_time_timestamp(order_state):
    order_state.pop(1)


def make_driver_id(dbid, uuid):
    return dbid + '_' + uuid


def get_one_order_from_db_as_list(pgsql):
    cursor = pgsql['eta_autoreorder'].cursor()
    cursor.execute('SELECT * from eta_autoreorder.orders')
    result = [row for row in cursor]
    assert len(result) == 1
    order = list(result[0])
    erase_real_time_timestamp(order)
    return order
