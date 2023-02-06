import base64
import datetime
import itertools
import typing

from Crypto.Cipher import AES
from Crypto.Util import Padding
import dateutil.parser
import pytz

PASSWORDS_AES256_KEY = base64.b64decode(
    b'emFpMW5haDN0aGFlQ2hhaXNoMG9oanVrZWk4cGF3YWg=',
)
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'


def convert_datetime_in_tz(
        time: typing.Union[str, datetime.datetime], timezone: str,
):
    if isinstance(time, str):
        time = dateutil.parser.parse(time)
    return time.astimezone(pytz.timezone(timezone))


def date_str_to_sec(date_str):
    return int(convert_datetime_in_tz(date_str, 'UTC').timestamp())


def is_datetime_start_day(time: datetime.datetime):
    return time.hour == time.minute == time.second == time.microsecond == 0


def to_base64(src):
    return base64.b64encode(src.encode()).decode()


def decode_password(db_password):
    raw = base64.b64decode(db_password)
    assert AES.block_size == 16
    cipher = AES.new(PASSWORDS_AES256_KEY, AES.MODE_CBC, raw[:16])
    return Padding.unpad(cipher.decrypt(raw[16:]), 16).decode('utf-8')


def make_table_snapshot(pgsql, table_name, fields=None, order_by=None):
    db = pgsql['signal_device_api_meta_db'].cursor()
    order_by = f'ORDER BY {order_by}' if order_by else ''
    fields = ','.join(fields) if fields else '*'
    db.execute(
        'SELECT {} FROM signal_device_api.{} {}'.format(
            fields, table_name, order_by,
        ),
    )
    return list(db)


def add_park_critical_types_in_db(pgsql, *, park_id, critical_types):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        f"""
        INSERT INTO signal_device_api.park_critical_event_types
        (
            park_id, critical_event_types, created_at, updated_at
        )
        VALUES (
            '{park_id}', ARRAY{critical_types},
            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        );
        """,
    )


def check_table_not_changed(pgsql, table_name):
    def check_table_not_changed_dec(func):
        def function_wrapper(x):
            before = make_table_snapshot(pgsql, table_name)
            func(x)
            after = make_table_snapshot(pgsql, table_name)
            assert before == after

        return function_wrapper

    return check_table_not_changed_dec


def assert_now(actual):
    assert isinstance(actual, datetime.datetime)
    assert actual.tzinfo is not None
    delta = datetime.datetime.now(datetime.timezone.utc) - actual
    assert (
        datetime.timedelta() <= delta < datetime.timedelta(minutes=1)
    ), f'found too big time delta {delta}'


def get_encoded_events_cursor(event_at, event_id):
    event_at = datetime.datetime.fromisoformat(event_at).strftime(
        DATETIME_FORMAT,
    )
    return to_base64(f'{event_at}|{event_id}').rstrip('=')


def get_encoded_groups_list_cursor(created_at, group_id):
    return _get_encoded_common_group_cursor(created_at, group_id)


def get_encoded_group_devices_list_cursor(  # pylint: disable=invalid-name
        updated_at, public_id,
):
    return _get_encoded_common_group_cursor(updated_at, public_id)


def get_encoded_internal_devices_list_cursor(  # pylint: disable=invalid-name
        created_at, public_id,
):
    return _get_encoded_common_group_cursor(created_at, public_id)


def get_encoded_external_devices_list_cursor(  # pylint: disable=invalid-name
        public_id,
):
    return to_base64(public_id).rstrip('=')


def _get_encoded_common_group_cursor(timestamptz_from_db, id_from_db):
    timestamptz_from_db = datetime.datetime.fromisoformat(
        timestamptz_from_db,
    ).strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    return to_base64(f'{timestamptz_from_db}|{id_from_db}').rstrip('=')


def get_encoded_dev_stathist_cursor(status_at):
    return to_base64(status_at).rstrip('=')


def get_encoded_chart_cursor(event_at):
    if isinstance(event_at, datetime.datetime):
        event_at = event_at.isoformat()
    return to_base64(event_at).rstrip('=')


def get_decoded_cursor(cursor):
    cursor_encoded = (cursor + '=' * (4 - len(cursor) % 4)).encode('UTF-8')
    return base64.urlsafe_b64decode(cursor_encoded).decode('UTF-8')


def unordered_lists_are_equal(list1, list2):
    if len(list2) != len(list1):
        return False

    def _check_one_list_is_sublist_of_other(first, second):
        for element in first:
            if element not in second:
                return False

        return True

    return _check_one_list_is_sublist_of_other(
        list1, list2,
    ) and _check_one_list_is_sublist_of_other(list2, list1)


def lists_are_equal_ignore_order_in_slices(  # pylint: disable=invalid-name
        list1, list2, ignored_slices: typing.List[slice], key: typing.Callable,
) -> bool:
    if len(list1) != len(list2):
        return False

    if not ignored_slices:
        return list1 == list2

    prev_index = 0
    for ignored_slice in ignored_slices:
        if (
                list1[prev_index : ignored_slice.start]
                != list2[prev_index : ignored_slice.start]
                or sorted(list1[ignored_slice], key=key)
                != sorted(list2[ignored_slice], key=key)
        ):
            return False
        prev_index = ignored_slice.stop
    if ignored_slices[-1].stop < len(list1):
        return (
            list1[ignored_slices[-1].stop :]
            == list2[ignored_slices[-1].stop :]
        )
    return True


def chunks(iterable, chunk_size):
    iterator = iter(iterable)
    while True:
        chunk = list(itertools.islice(iterator, chunk_size))
        if chunk:
            yield chunk
        else:
            break


def decode_cursor_from_event(event):
    event_at = datetime.datetime.fromisoformat(event['event_at']).strftime(
        DATETIME_FORMAT,
    )
    event_id = event['id']
    return f'{event_at}|{event_id}'


def decode_cursor_from_resp_json(response_json):
    cursor_json = response_json.get('cursor')
    assert cursor_json is not None
    return get_decoded_cursor(cursor_json)
