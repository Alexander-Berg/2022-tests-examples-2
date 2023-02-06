import enum

from dateutil import parser
import pytz

DELETE_KEY = object()
MAX_COST_TOLL_ROADS = 1500


def parse_date_str(date_str):
    return parser.parse(date_str).astimezone(pytz.UTC)


def date_to_taximeter_str(datetime_or_str):
    input_date = (
        parse_date_str(datetime_or_str)
        if isinstance(datetime_or_str, str)
        else datetime_or_str
    )
    return input_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def add_accents(setcar_json):
    setcar_json['ui']['acceptance_items'][0]['left']['accent_title'] = True
    setcar_json['ui']['acceptance_items'][0]['right']['accent_title'] = True


def normalize_setcar(setcar_json):
    if 'requirement_list' in setcar_json:
        setcar_json['requirement_list'].sort(key=lambda x: x['id'])
    return setcar_json


def add_booking_time_settings(setcar_json, settings):
    if 'expected_date_drive' in settings:
        setcar_json['date_drive'] = settings['expected_date_drive']
    if 'expected_date_last_change' in settings:
        setcar_json['date_last_change'] = settings['expected_date_last_change']
    if 'expected_kind' in settings:
        setcar_json['kind'] = settings['expected_kind']


def copy_patch(source):
    if isinstance(source, dict):
        return {k: copy_patch(v) for k, v in source.items() if v != DELETE_KEY}
    if isinstance(source, list):
        return [copy_patch(x) for x in source]
    return source


def apply_patch(target, source):
    for key, value in source.items():
        if key.startswith('$insert'):
            params = key.split('-')
            pos = int(params[1]) if len(params) > 1 else len(params)
            target[pos:pos] = value
        elif key.startswith('$patch'):
            params = key.split('-')
            if len(params) > 2:
                start, end = int(params[1]), int(params[2]) + 1
            elif len(params) > 1:
                start, end = int(params[1]), int(params[1]) + 1
            else:
                start, end = 0, len(params)
            for x in range(start, end):
                apply_patch(target[x], value)
        elif isinstance(value, dict) and key in target:
            apply_patch(target[key], value)
        elif value == DELETE_KEY:
            target.pop(key, None)
        else:
            target[key] = copy_patch(value)


def kill_patch(target, source):
    for key, value in source.items():
        if key not in target:
            continue
        if isinstance(value, dict):
            kill_patch(target[key], value)
        else:
            del target[key]


def fields_filter(source, fields, drop_nones=True):
    fields = set(fields)

    # It's not optimal, but it's compact, nice and enough for tests
    def __copy(source, path):
        if '.'.join(path) in fields:
            return source
        if isinstance(source, dict):
            temp = {k: __copy(v, path + [k]) for k, v in source.items()}
            return {
                k: v
                for k, v in temp.items()
                if ((v is not None) or (not drop_nones))
            }
        if isinstance(source, list):
            return [__copy(x, path) for x in source]
        return None

    return __copy(source, [])


class OrderStatus(enum.Enum):
    None_ = 0
    Driving = 10
    Waiting = 20
    Calling = 30
    Transporting = 40
    Complete = 50
    Failed = 60
    Cancelled = 70
    Expired = 80


def set_order_status(redis_store, park_id, order_id, status):
    if status is None:
        return
    redis_store.hset(
        'Order:RequestConfirm:Items' + ':' + park_id, order_id, status.value,
    )
