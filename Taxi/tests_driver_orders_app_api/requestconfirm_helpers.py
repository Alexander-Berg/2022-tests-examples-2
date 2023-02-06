# pylint: disable=import-error
import datetime
import json
import urllib

from .plugins import taximeter_version_helpers as tvh


STATUS_VALUES = {
    'undefined': 0,
    'assigned': 1,
    'driving': 2,
    'waiting': 3,
    'calling': 4,
    'transporting': 5,
    'cancelled': 6,
    'complete': 7,
    'failed': 8,
    'reject': 9,
}

REV_STATUS_VALUES = {v: k for k, v in STATUS_VALUES.items()}

SHORT_TAXIMETER_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.000000Z'
TAXIMETER_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
TAXIMETER_DELIMETERLESS_FORMAT = '%Y%m%d%H%M%S'

HAS_SETCAR_DATA = {
    'phone_options': [
        {
            'call_dialog_message_prefix': 'Телефон пассажира',
            'label': 'Телефон пассажира.',
            'type': 'main',
        },
    ],
}

CONTENT_HEADER_FORM = {'Content-Type': 'application/x-www-form-urlencoded'}
CONTENT_HEADER_JSON = {'Content-Type': 'application/json'}

OLD_API_VERSIONS = {'compatible'}
NEW_API_VERSIONS = {'requestconfirm_status_v2'}


def _data_to_json(data_dict):
    string_fields = {'imei'}
    res = dict()
    for key, value in data_dict.items():
        value = urllib.parse.unquote(value)
        try:
            value = json.loads(value)
            value = str(value) if key in string_fields else value
            res[key] = value
        except (TypeError, json.JSONDecodeError):
            res[key] = value

    return json.dumps(res)


def process_data(api_schema, data_dict, data):
    if api_schema in ('requestconfirm_status_v2', 'internal_order_status_v1'):
        return _data_to_json(data_dict)
    return data


def _get_dap_headers(park_id, driver_id, user_agent):
    return {
        'Accept-Language': 'ru',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': driver_id,
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': tvh.match_taximeter_version(
            user_agent,
        ),
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'User-Agent': user_agent,
    }


def get_headers(user_agent, park_id, driver_id):
    return _get_dap_headers(park_id, driver_id, user_agent)


def get_reject_url(api_schema, status):
    if api_schema == 'requestconfirm_status_v2':
        url = 'driver/v1/orders-app-api/v2/requestconfirm/{}'.format(
            REV_STATUS_VALUES.get(int(status)),
        )
    elif api_schema == 'external_cancel_v1':
        url = 'external/v1/order/cancel'
    elif api_schema == 'internal_order_status_v1':
        url = 'internal/v1/order/status/{}'.format(
            REV_STATUS_VALUES.get(int(status)),
        )
    return url


def get_requestconfirm_url(api_schema, status):
    if api_schema == 'compatible':
        url = 'driver/v1/orders-app-api/v1/requestconfirm'
    elif api_schema == 'requestconfirm_status_v2':
        str_status = REV_STATUS_VALUES.get(int(status))
        if not str_status:
            return None
        url = 'driver/v1/orders-app-api/v2/requestconfirm/{}'.format(
            str_status,
        )
    elif api_schema == 'internal_order_status_v1':
        url = 'internal/v1/order/status/{}'.format(
            REV_STATUS_VALUES.get(int(status)),
        )
    return url


def zero_retry_lock_settings():
    return {
        '__default__': {
            'min_sleep_delay': 1,
            'max_sleep_delay': 1,
            'max_retries': 1,
            'max_lock_obtaining_duration': 30000,
            'redis_lock_key_ttl': 30000,
        },
    }


def pg_update_settings():
    return {'use_single_update': True}


def self_employment_settings(**overrides):
    return {
        'account_hint': '00000 00000 00000 00000',
        'account_mask': '[00000] [00000] [00000] [00000]',
        'bik_hint': '000000000',
        'bik_mask': '[000000000]',
        'block_unbounded': True,
        'client_polling_delay_ms': 1000,
        'disable_full_flow': False,
        'disable_receipt_daemon': False,
        'drivercheck_restrictions_action': (
            'taximeter://open_app?package=com.gnivts.selfemployed'
        ),
        'drivercheck_restrictions_ver': '8.83',
        'enable': True,
        'enable_unbounded_sync_job': True,
        'fns_auth_cache_refresh_sec': 60,
        'fns_auth_update_gap': 600,
        'fns_package_name': 'com.gnivts.selfemployed',
        'fns_response_retries': 10,
        'fns_retry_delay_ms': 150,
        'fns_server_timeout_ms': 1500,
        'max_income': 2400000,
        'offline_mode': False,
        'requisites_required': False,
        'sms_retry_timeout_ms': 60000,
        'yandex_inn': '7704340310',
        'yandex_org_name': (
            'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ «ЯНДЕКС.ТАКСИ»'
        ),
        **overrides,
    }


def get_content_type(api_version):
    return (
        CONTENT_HEADER_FORM
        if api_version in OLD_API_VERSIONS
        else CONTENT_HEADER_JSON
    )


def date_to_taximeter(date):
    """
    Converts date in iso-like string to taximeter format
    :param date: string in format "2020-04-01T15:55:36.259396Z",
    :return: date (string) in taximeter format
    """
    setcar_date = datetime.datetime.strptime(date, TAXIMETER_DATE_FORMAT)
    return setcar_date.strftime(TAXIMETER_DELIMETERLESS_FORMAT)
