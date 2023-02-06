import base64
import copy
import datetime
import enum
import functools
from typing import Any
from typing import Callable
from typing import Dict

import pytest

TIMEOUT = 599
DEFAULT_YANDEX_UIDS = ['uid']

PAYMENT_METHODS_MAP = {
    'paymentmethods1': '\"Наличные\", \"Банковская карта\", \"applepay\"',
    'bizpaymentmethod1': '\"Бизнес аккаунт\"',
    'emptypaymentmethods1': '',
}

PHONE_ID = '5bbb5faf15870bd76635d5e2'


class ServiceErrors(enum.Enum):
    ERROR_LAVKA_PROMOCODE = 'ERROR_LAVKA_PROMOCODE'


def utc_datetime_from_str(time_string: str):
    current_date = datetime.datetime.fromisoformat(time_string)
    offset = current_date.utcoffset() or datetime.timedelta()
    current_date = current_date - offset
    return current_date.replace(tzinfo=None)


def check_coupon(code, description_string, valid, coupon_response):
    # Check descriptions
    methods = PAYMENT_METHODS_MAP.get(code)
    if methods:
        description_string += f' для методов оплаты: {methods}'

    descriptions = [{'text': description_string}]
    if not valid:
        descriptions.append({'text': '<red>Неверный способ оплаты</red>'})
    assert coupon_response['action']['descriptions'] == descriptions

    # Check error code
    if not valid:
        error = coupon_response['error']
        assert error['code'] == 'ERROR_INVALID_PAYMENT_METHOD'
        assert error['description'] == 'Неверный способ оплаты'


def toggle_use_cardstorage(func):
    @pytest.mark.parametrize('use_cardstorage', [True, False])
    @pytest.mark.usefixtures('setup_test')
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    return wrapper


def sort_json_inplace(obj, paths_to_sort, current_path=''):
    if isinstance(obj, list):
        if current_path in paths_to_sort:
            obj.sort()
            return
        for item in obj:
            sort_json_inplace(item, paths_to_sort, current_path)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            sort_json_inplace(
                value,
                paths_to_sort,
                current_path + '.' + key if current_path else key,
            )


def sort_json(json, paths_to_sort):
    result = copy.deepcopy(json)
    sort_json_inplace(result, paths_to_sort)
    return result


def mock_authorization_data(
        app_name='iphone',
        yandex_uids=DEFAULT_YANDEX_UIDS.copy(),
        yandex_uid='uid',
        phone_id='phone_id',
        user_id='user_id',
):
    pa_headers = {
        'application': {
            'name': app_name,
            'version': [4, 47, 0],
            'platform_version': [11, 1, 0],
        },
        'yandex_uids': yandex_uids,
        'current_yandex_uid': yandex_uid,
        'locale': 'ru',
        'user_ip': 'user_ip',
        'user_id': 'user_id',
    }
    if phone_id:
        pa_headers['phone_id'] = phone_id
    return pa_headers


def mock_request_activate(
        yandex_uids,
        yandex_uid,
        coupon,
        phone_id,
        app_name='iphone',
        payment_type='card',
        payment_method_id='card_id',
        version=None,
):
    request = {
        'coupon': coupon,
        'zone_name': 'moscow',
        'payment': {
            'type': payment_type,
            'payment_method_id': payment_method_id,
        },
        'selected_class': 'econom',
    }

    if version:
        request['version'] = version

    pa_headers = mock_authorization_data(
        app_name, yandex_uids, yandex_uid, phone_id,
    )
    request.update(pa_headers)

    return request


def mock_request_activate_v1(
        yandex_uids,
        yandex_uid,
        coupon,
        phone_id,
        payment_info,
        locale='ru',
        service=None,
        app_name='iphone',
        version=None,
):
    request = {
        'coupon': coupon,
        'zone_name': 'moscow',
        'current_yandex_uid': yandex_uid,
        'bounded_uids': yandex_uids,
        'apns_token': 'apns_token',
        'gcm_token': 'gcm_token',
        'device_id': 'device_id',
        'locale': locale,
        'user_ip': 'user_ip',
        'service_type': (
            'service_type'
        ),  # TODO remove this field in EFFICIENCYDEV-4818
        'country': 'rus',
        'time_zone': 'Europe/Moscow',
        'payment_info': payment_info,
        'application': {
            'name': app_name,
            'version': [4, 47, 0],
            'platform_version': [11, 1, 0],
        },
        'zone_classes': [
            {'class': 'econom', 'tanker_key': 'name.econom'},
            {'class': 'business', 'tanker_key': 'name.comfort'},
            {'class': 'vip', 'tanker_key': 'name.business'},
            {'class': 'maybach', 'tanker_key': 'name.maybach'},
        ],
        'payment_options': ['card', 'coupon'],
        'selected_class': 'econom',
    }

    if version:
        request['version'] = version

    if service:
        request['service'] = service

    if phone_id:
        request['phone_id'] = phone_id

    return request


APPLICATION_MAP_BRAND = {
    '__default__': 'unknown',
    'iphone': 'yataxi',
    'yango_android': 'yango',
    'yango_iphone': 'yango',
    'uber_iphone': 'yauber',
    'uber_android': 'yauber',
    'eats_iphone': 'eats',
}


def make_pa_headers(data, headers):
    if not data:
        data = mock_authorization_data()

    app_versions = enumerate(data['application']['version'])
    params_list = [
        f'app_ver{num + 1}={version}' for num, version in app_versions
    ]
    platform_versions = enumerate(data['application']['platform_version'])
    params_list += [
        f'platform_ver{num + 1}={version}'
        for num, version in platform_versions
    ]
    app_name = data['application']['name']
    app_brand = APPLICATION_MAP_BRAND.get(app_name)
    if not app_brand:
        app_brand = APPLICATION_MAP_BRAND['__default__']
    params_list += [f'app_name={app_name}', f'app_brand={app_brand}']

    current_uid = data['current_yandex_uid']
    bound_uids = data['yandex_uids'].copy()
    bound_uids.remove(current_uid)
    new_headers = {
        'X-Request-Application': ','.join(params_list),
        'X-Request-Language': data['locale'],
        'X-YaTaxi-UserId': data['user_id'],
        'X-Yandex-UID': current_uid,
        'X-YaTaxi-Bound-Uids': ','.join(bound_uids),
        'X-Remote-IP': data['user_ip'],
    }
    if 'phone_id' in data:
        new_headers['X-YaTaxi-PhoneId'] = data['phone_id']
    if headers:
        new_headers.update(headers)

    return new_headers


def make_superapp_headers(data, headers):
    new_headers = make_pa_headers(data, headers)
    new_headers['X-YaTaxi-Session'] = 'taxi:' + new_headers['X-YaTaxi-UserId']
    new_headers['X-YaTaxi-Bound-Sessions'] = new_headers['X-YaTaxi-Session']

    if 'X-YaTaxi-PhoneId' in new_headers:
        phone_id = new_headers['X-YaTaxi-PhoneId']
        user_info = f'personal_phone_id={phone_id}'
        new_headers['X-YaTaxi-User'] = user_info

    return new_headers


def remove_pa_request_data(data):
    if data is None:
        return None
    json = copy.deepcopy(data)
    for k in mock_authorization_data():
        json.pop(k, None)
    return json


ConvertFunc = Callable[[Any], Dict[str, Any]]
ConverterMap = Dict[str, ConvertFunc]


def deep_rename(new_name: str, fields_map: ConverterMap) -> ConvertFunc:
    def rename(inner_obj) -> Dict[str, Any]:
        inner_json = {}
        for k, value in inner_obj.items():
            if k in fields_map:
                inner_json.update(fields_map[k](value))
        return {new_name: inner_json}

    return rename


def simple_rename(new_name: str) -> ConvertFunc:
    def rename(value) -> Dict[str, Any]:
        return {new_name: value}

    return rename


def convert_v1_request_to_3_0(data):
    if not data:
        return None
    fields_to_move = {
        'code': simple_rename('coupon'),
        'version': simple_rename('version'),
        'payment_info': deep_rename(
            'payment',
            {
                'method_id': simple_rename('payment_method_id'),
                'type': simple_rename('type'),
            },
        ),
        'zone_name': simple_rename('zone_name'),
        'selected_class': simple_rename('selected_class'),
        'service': simple_rename('service'),
        'payload': simple_rename('payload'),
        'services': simple_rename('services'),
    }
    json = deep_rename('root', fields_to_move)(data)
    return json['root']


async def make_activate_request(taxi_coupons, data, headers=None):
    return await taxi_coupons.post(
        '3.0/couponactivate',
        json=remove_pa_request_data(data),
        headers=make_pa_headers(data, headers),
    )


async def make_activate_request_v1(taxi_coupons, data, headers=None):
    return await taxi_coupons.post(
        'v1/couponactivate', json=data, headers=headers,
    )


def decode_version(version):
    return base64.b64decode(version.encode('UTF-8')).decode('UTF-8')


def encode_version(version):
    return base64.b64encode(version.encode('UTF-8')).decode('UTF-8')


def generate_virtual_user_coupons(codes, brand_name, db):
    virtual_yandex_uid = '5555'

    def generate_code(code, activated):
        return {'code': code, 'activated': activated}

    def generate_promocodes(codes):
        code_list = []
        day = 31
        for code in codes:
            code_list.append(
                generate_code(code, datetime.datetime(2019, 1, day, 0, 0)),
            )
            day = day - 1
        return code_list

    entry = {
        'id': 'some_id',
        'yandex_uid': virtual_yandex_uid,
        'version': 1,
        'updated': datetime.datetime(2019, 1, 1, 0, 0),
        'brand_name': brand_name,
        'promocodes': generate_promocodes(codes),
    }
    db.user_coupons.insert(entry)
    return virtual_yandex_uid


def mock_request_list(
        yandex_uids,
        application_name='iphone',
        zone_name='moscow',
        services=None,
        payment_type='card',
        payment_method_id='card_id',
        version=None,
        phone_id='5bbb5faf15870bd76635d5e2',
        service=None,
        brand_names=None,
):
    request = {
        'zone_name': zone_name,
        'payment': {
            'type': payment_type,
            'payment_method_id': payment_method_id,
        },
        'selected_class': 'econom',
    }
    if service:
        request['service'] = service

    if services is not None:
        request['services'] = services

    if version:
        request['version'] = version

    if brand_names is not None:
        request['brand_names'] = brand_names

    pa_headers = mock_authorization_data(
        application_name, yandex_uids, yandex_uids[0], phone_id=phone_id,
    )
    request.update(pa_headers)

    return request


def mock_request_internal_list(
        yandex_uids,
        phone_id,
        application_name='iphone',
        zone_name='moscow',
        services=None,
        payment_type='card',
        payment_method_id='card_id',
        version=None,
        service='taxi',
        brand_names=None,
):
    request = mock_request_list(
        yandex_uids,
        application_name,
        zone_name,
        services,
        payment_type,
        payment_method_id,
        version,
        phone_id,
        service,
        brand_names=brand_names,
    )
    if 'services' not in request:
        request['services'] = ['taxi']

    return request


def mock_request_couponcheck(
        code,
        payment_info,
        locale='ru',
        app_name='iphone',
        yandex_uid='123',
        phone_id='5bbb5faf15870bd76635d5e2',
        service=None,
):
    request = {
        'code': code,
        'format_currency': True,
        'yandex_uids': [yandex_uid],
        'current_yandex_uid': yandex_uid,
        'apns_token': 'apns_token',
        'gcm_token': 'gcm_token',
        'device_id': 'device_id',
        'locale': locale,
        'user_ip': 'user_ip',
        'service_type': (
            'service_type'
        ),  # TODO remove this field in EFFICIENCYDEV-4818
        'zone_name': 'moscow',
        'country': 'rus',
        'time_zone': 'Europe/Moscow',
        'payment_info': payment_info,
        'application': {
            'name': app_name,
            'version': [4, 47, 0],
            'platform_version': [11, 1, 0],
        },
        'zone_classes': [
            {'class': 'econom', 'tanker_key': 'name.econom'},
            {'class': 'business', 'tanker_key': 'name.comfort'},
            {'class': 'vip', 'tanker_key': 'name.business'},
            {'class': 'maybach', 'tanker_key': 'name.maybach'},
        ],
        'payment_options': ['card', 'coupon'],
        'selected_class': 'econom',
    }
    if service:
        request['service'] = service

    if phone_id:
        request['phone_id'] = phone_id

    return request


def mock_request_couponcheck_bulk(
        coupons,
        payment_info,
        locale='ru',
        app_name='iphone',
        yandex_uid='123',
        phone_id='5bbb5faf15870bd76635d5e2',
        service=None,
):
    request = {
        'coupons': coupons,
        'format_currency': True,
        'yandex_uids': [yandex_uid],
        'current_yandex_uid': yandex_uid,
        'apns_token': 'apns_token',
        'gcm_token': 'gcm_token',
        'device_id': 'device_id',
        'locale': locale,
        'user_ip': 'user_ip',
        'service_type': (
            'service_type'
        ),  # TODO remove this field in EFFICIENCYDEV-4818
        'zone_name': 'moscow',
        'country': 'rus',
        'time_zone': 'Europe/Moscow',
        'payment_info': payment_info,
        'application': {
            'name': app_name,
            'version': [4, 47, 0],
            'platform_version': [11, 1, 0],
        },
        'zone_classes': [
            {'class': 'econom', 'tanker_key': 'name.econom'},
            {'class': 'business', 'tanker_key': 'name.comfort'},
            {'class': 'vip', 'tanker_key': 'name.business'},
            {'class': 'maybach', 'tanker_key': 'name.maybach'},
        ],
        'payment_options': ['card', 'coupon'],
        'selected_class': 'econom',
    }
    if service:
        request['service'] = service

    if phone_id:
        request['phone_id'] = phone_id

    return request


def mock_request_reserve(
        code='code',
        app_name='iphone',
        service=None,
        order_id='order_id',
        check_type='full',
        zone_name='moscow',
        phone_id='5bbb5faf15870bd76635d5e2',
        yandex_uid='yandex_uid',
):
    request = {
        'code': code,
        'order_id': order_id,
        'check_type': check_type,
        'current_yandex_uid': yandex_uid,
        'apns_token': 'apns_token',
        'gcm_token': 'gcm_token',
        'device_id': 'device_id',
        'locale': 'ru',
        'user_ip': 'user_ip',
        'service_type': (
            'service_type'
        ),  # TODO remove this field in EFFICIENCYDEV-4818
        'zone_name': zone_name,
        'country': 'rus',
        'time_zone': 'Europe/Moscow',
        'payment_info': {'type': 'card', 'method_id': 'card_id'},
        'application': {
            'name': app_name,
            'version': [4, 47, 0],
            'platform_version': [11, 1, 0],
        },
        'zone_classes': [
            {'class': 'econom', 'tanker_key': 'name.econom'},
            {'class': 'business', 'tanker_key': 'name.comfort'},
            {'class': 'vip', 'tanker_key': 'name.business'},
            {'class': 'maybach', 'tanker_key': 'name.maybach'},
        ],
        'payment_options': ['card', 'coupon'],
        'selected_class': 'econom',
    }

    if service:
        request['service'] = service

    if phone_id:
        request['phone_id'] = phone_id

    return request


async def make_list_request(taxi_coupons, data, headers=None):
    return await taxi_coupons.post(
        '3.0/couponlist',
        json=remove_pa_request_data(data),
        headers=make_pa_headers(data, headers),
    )


async def make_internal_list_request(taxi_coupons, data, headers=None):
    return await taxi_coupons.post(
        'internal/couponlist',
        json=remove_pa_request_data(data),
        headers=make_superapp_headers(data, headers),
    )


def check_cardstorage_requests(
        requests,
        expected_num_requests,
        expected_num_requests_wo_renew_after,
        expected_timeout_ms,
):
    assert len(requests) == expected_num_requests
    assert all(
        request['timeout_ms'] == expected_timeout_ms for request in requests
    )

    request_with_renew_after = [
        'renew_after' in request for request in requests
    ]
    assert (
        request_with_renew_after.count(False)
        == expected_num_requests_wo_renew_after
    )
    assert request_with_renew_after.count(True) == (
        expected_num_requests - expected_num_requests_wo_renew_after
    )


def collection_promocode_usages(
        db, service, separate_flows_enabled, grocery_new_flow=False,
):
    if not separate_flows_enabled:
        return db.promocode_usages

    if service == 'eats' or grocery_new_flow:
        return db.mdb_promocode_usages
    return db.promocode_usages


def collection_promocode_usages2(
        db, service, separate_flows_enabled, grocery_new_flow=False,
):
    if not separate_flows_enabled:
        return db.promocode_usages2

    if service == 'eats' or grocery_new_flow:
        return db.mdb_promocode_usages2
    return db.promocode_usages2


PROMOCODES_DB_MODE_PARAMS = [
    pytest.param(
        'old_db_only',
        marks=[pytest.mark.config(COUPONS_PROMOCODES_DB_MODE='old_db_only')],
        id='old_db_only',
    ),
    pytest.param(
        'write_old_new_read_old',
        marks=[
            pytest.mark.config(
                COUPONS_PROMOCODES_DB_MODE='write_old_new_read_old',
            ),
        ],
        id='write_old_new_read_old',
    ),
    pytest.param(
        'write_old_new_read_new',
        marks=[
            pytest.mark.config(
                COUPONS_PROMOCODES_DB_MODE='write_old_new_read_new',
            ),
        ],
        id='write_old_new_read_new',
    ),
    pytest.param(
        'new_db_only',
        marks=[pytest.mark.config(COUPONS_PROMOCODES_DB_MODE='new_db_only')],
        id='new_db_only',
    ),
]


def tag_to_promocodes_for_write(mongodb, tag):
    tag_to_collections = {
        'old_db_only': [mongodb.promocodes],
        'write_old_new_read_old': [mongodb.promocodes, mongodb.promocodes_mdb],
        'write_old_new_read_new': [mongodb.promocodes, mongodb.promocodes_mdb],
        'new_db_only': [mongodb.promocodes_mdb],
    }
    return tag_to_collections[tag]


def tag_to_promocodes_for_read(mongodb, tag):
    tag_to_collections = {
        'old_db_only': mongodb.promocodes,
        'write_old_new_read_old': mongodb.promocodes,
        'write_old_new_read_new': mongodb.promocodes_mdb,
        'new_db_only': mongodb.promocodes_mdb,
    }
    return tag_to_collections[tag]


def mock_request(*args, **kwargs):
    kwargs['phone_id'] = kwargs.get('phone_id', PHONE_ID)
    return mock_request_activate(*args, **kwargs)


def mock_request_v1(*args, **kwargs):
    kwargs['phone_id'] = kwargs.get('phone_id', PHONE_ID)
    return mock_request_activate_v1(*args, **kwargs)


USER_COUPONS_DB_MODE_PARAMS = [
    pytest.param(
        'old_db_only',
        marks=[pytest.mark.config(COUPONS_USER_COUPONS_DB_MODE='old_db_only')],
        id='old_db_only',
    ),
    pytest.param(
        'write_old_new_read_old',
        marks=[
            pytest.mark.config(
                COUPONS_USER_COUPONS_DB_MODE='write_old_new_read_old',
            ),
        ],
        id='write_old_new_read_old',
    ),
    pytest.param(
        'write_old_new_read_new',
        marks=[
            pytest.mark.config(
                COUPONS_USER_COUPONS_DB_MODE='write_old_new_read_new',
            ),
        ],
        id='write_old_new_read_new',
    ),
    pytest.param(
        'new_db_only',
        marks=[pytest.mark.config(COUPONS_USER_COUPONS_DB_MODE='new_db_only')],
        id='new_db_only',
    ),
]


def tag_to_user_coupons_for_write(mongodb, tag):
    tag_to_collections = {
        'old_db_only': [mongodb.user_coupons],
        'write_old_new_read_old': [
            mongodb.user_coupons,
            mongodb.user_coupons_mdb,
        ],
        'write_old_new_read_new': [
            mongodb.user_coupons,
            mongodb.user_coupons_mdb,
        ],
        'new_db_only': [mongodb.user_coupons_mdb],
    }
    return tag_to_collections[tag]


def tag_to_user_coupons_for_read(mongodb, tag):
    tag_to_collections = {
        'old_db_only': mongodb.user_coupons,
        'write_old_new_read_old': mongodb.user_coupons,
        'write_old_new_read_new': mongodb.user_coupons_mdb,
        'new_db_only': mongodb.user_coupons_mdb,
    }
    return tag_to_collections[tag]
