import datetime
import typing as tp

from taxi.util import dates

from workforce_management.common import utils


START = dates.localize(
    datetime.datetime(2020, 7, 26, 12, 0, 0, 0, tzinfo=datetime.timezone.utc),
)


def add_minutes(minutes: float):
    return START + datetime.timedelta(minutes=minutes)


def expected_fields(
        actual_rows: tp.List[tp.Dict],
        expected_rows: tp.Optional[tp.List[tp.Dict]],
) -> tp.List[tp.Dict]:
    for row in actual_rows:
        if 'marker_type' in row:
            row['marker_type'] = row['marker_type'].value
        if 'state_type' in row:
            row['state_type'] = row['state_type'].value

    return utils.expected_fields(actual_rows, expected_rows)


MARKERS_SHIFT_START = [
    {'marker_type': 'shift_start', 'start': START, 'shift_id': 1},
    {'marker_type': 'break_start', 'start': START, 'shift_id': 1},
]
MARKERS_CONSECUTIVE_SHIFTS = [
    {'marker_type': 'shift_start', 'start': START, 'shift_id': 1},
    {'marker_type': 'break_start', 'start': START, 'shift_id': 1},
    {'marker_type': 'break_end', 'start': add_minutes(30), 'shift_id': 1},
    {'marker_type': 'shift_end', 'start': add_minutes(60), 'shift_id': 1},
    {'marker_type': 'shift_start', 'start': add_minutes(60), 'shift_id': 3},
    {'marker_type': 'shift_end', 'start': add_minutes(120), 'shift_id': 3},
    {'marker_type': 'shift_start', 'start': add_minutes(120), 'shift_id': 2},
]
MARKERS_REVERSE = [
    {'marker_type': 'shift_start', 'start': START, 'shift_id': 10},
    {'marker_type': 'event_start', 'start': START, 'shift_id': 10},
    {'marker_type': 'event_end', 'start': add_minutes(30), 'shift_id': 10},
    {'marker_type': 'break_start', 'start': add_minutes(30), 'shift_id': 10},
    {'marker_type': 'break_end', 'start': add_minutes(60), 'shift_id': 10},
    {'marker_type': 'shift_end', 'start': add_minutes(60), 'shift_id': 10},
]
MARKERS_CONNECT = [{'marker_type': 'connect', 'start': add_minutes(5)}]
EVENTS_CONNECT = [
    {
        'yandex_uid': 'uid1',
        'type': 'connected',
        'start': add_minutes(5),
        'meta_queues': ['pokemon'],
    },
]
EVENTS_ALL_TYPES = [
    {
        'yandex_uid': 'uid1',
        'type': 'disconnected',
        'start': add_minutes(5),
        'meta_queues': ['pokemon'],
    },
    {
        'yandex_uid': 'uid1',
        'type': 'connected',
        'start': add_minutes(15),
        'meta_queues': ['pokemon'],
    },
    {
        'yandex_uid': 'uid1',
        'type': 'paused',
        'sub_type': 'toilet',
        'start': add_minutes(25),
        'meta_queues': ['pokemon'],
    },
]
EVENTS_FLAP = [
    {
        'yandex_uid': 'uid1',
        'type': 'connected',
        'start': add_minutes(5),
        'meta_queues': ['pokemon'],
    },
    {
        'yandex_uid': 'uid1',
        'type': 'disconnected',
        'start': add_minutes(15),
        'meta_queues': ['pokemon'],
    },
    {
        'yandex_uid': 'uid1',
        'type': 'connected',
        'start': add_minutes(15.25),
        'meta_queues': ['pokemon'],
    },
]
EVENTS_FLAP_START = [
    {
        'yandex_uid': 'uid4',
        'type': 'connected',
        'start': add_minutes(0.25),
        'meta_queues': ['pokemon'],
    },
    {
        'yandex_uid': 'uid4',
        'type': 'disconnected',
        'start': add_minutes(15),
        'meta_queues': ['pokemon'],
    },
    {
        'yandex_uid': 'uid4',
        'type': 'connected',
        'start': add_minutes(15.25),
        'meta_queues': ['pokemon'],
    },
]
EVENTS_DISCONNECT_UID3 = [
    {
        'yandex_uid': 'uid3',
        'type': 'disconnected',
        'start': add_minutes(-5),
        'meta_queues': ['pokemon'],
    },
]
EVENTS_CONNECT_UID5 = [
    {
        'yandex_uid': 'uid5',
        'type': 'connected',
        'start': add_minutes(10),
        'meta_queues': ['pokemon'],
    },
]
