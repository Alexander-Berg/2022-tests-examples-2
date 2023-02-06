# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import bson.json_util
import datetime
import json
import pytest
from django import test as django_test
from django.test import Client

from taxi.conf import settings
from taxi.core import arequests
from taxi.core import async
from taxi.util import dates
from taxi.util import evlog
from taxiadmin.api.views import drivers
from taxi.internal import personal
from taxi.external import taximeter
from taxi.external import tracker
from taxi.external import reposition
from taxi.external import tvm


NOW = datetime.datetime(2020, 9, 14, 22, 00, 00)
EPOCH = datetime.datetime.utcfromtimestamp(0)
NOW_MS = (NOW - EPOCH).total_seconds() * 1000

TEST_TVM_TICKET = 'test_ticket'

TST_HISTORY_RESPONSE = {
    'id': '5b7b0c694f007eaf8578b531',
    'activity_value_change': -10,
    'activity_value_before': 55,
    'timestamp': '2018-08-21T08:50:36.230000Z',
    'driver_id': '999010_2eaf04fe6dec4330a6f29a6a7701c459',
    'db_id': '',
    'time_to_a': 300,
    'distance_to_a': 1000,
    'order_id': '1',
    'order_alias_id': 'alias_1',
    'zone': 'moscow',
    'event_type': 'order',
    'event_descriptor': {
        'name': 'auto_reorder',
        'tags': None
    },
}


@pytest.mark.config(
    DRIVER_CARD_YANDEX_ID_SETTINGS={
        'enabled': True,
        'alias_types': {'21': 'neophonish'},
    }
)
@pytest.mark.config(DRIVER_CARD_SHOW_PERSONAL_DATA=True)
@pytest.mark.parametrize('request_data, expected', [
    ({'phone': '+79001111111'}, 'expected_1.json'),
    ({'clid': '000000000001'}, 'expected_1.json'),
    ({'driver_license': 'LICENSE_2'}, 'expected_2.json'),
    ({'uuid': '000000000001'}, 'expected_3.json'),
    ({'car_number': 'Е236КА750'}, 'expected_1.json'),
    ({'driver_license': 'LICENSE_1'}, 'expected_1.json'),
    ({'phone': '+79004444444'}, 'expected_empty.json'),
    ({'clid': '000000000001', 'offset': 1, 'limit': 1}, 'expected_4.json'),
    ({'clid': '000000000001', 'uuid': '000000000002',
      'order_id': 'order_id_1'}, 'expected_5.json'),
    ({'unique_driver_id': '000000000000000000000001'}, 'expected_1.json'),
    ({'unique_driver_id': '000000000000000000000001',
      'driver_license': 'LICENSE_1'}, 'expected_1.json'),
    ({'unique_driver_id': '000000000000000000000001',
      'driver_license': 'LICENSE_2'}, 'expected_empty.json'),
    ({'unique_driver_id': 'invalid'}, 'expected_empty.json'),
    ({'platform_uid': '1122334455'}, 'expected_1.json'),
    ({'platform_uid': '6677889900'}, 'expected_empty.json'),
])
@pytest.mark.parametrize('tags_error', (False, True))
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(TAXI_FLEET_DEVICE_MODEL_MAPPING={'iPhone9,1': 'iPhone 7'})
def test_get_driver_card(areq_request, monkeypatch, load, request_data, expected,
                         tags_error, patch):
    _test_get_driver_card_impl(areq_request, monkeypatch, load, request_data, expected, tags_error, patch)


@pytest.mark.config(
    DRIVER_CARD_YANDEX_ID_SETTINGS={
        'enabled': True,
        'alias_types': {'21': 'neophonish'},
    }
)
@pytest.mark.config(DRIVER_CARD_SHOW_PERSONAL_DATA=False, TAXI_FLEET_DEVICE_MODEL_MAPPING={'iPhone9,1': 'iPhone 7'})
@pytest.mark.parametrize('request_data, expected', [
    ({'phone': '+79001111111'}, 'expected_without_personal_data.json')])
@pytest.mark.parametrize('tags_error', (False, True))
@pytest.mark.asyncenv('blocking')
def test_get_driver_card_without_personal_data(areq_request, monkeypatch, load, request_data, expected,
                         tags_error, patch):
    _test_get_driver_card_impl(areq_request, monkeypatch, load, request_data, expected, tags_error, patch)


def _test_get_driver_card_impl(areq_request, monkeypatch, load, request_data, expected,
                         tags_error, patch):
    def fake_fetch_driver_tags(dbid, uuid, tvm_service_name):
        if tags_error:
            return None
        if uuid == '000000000003':
            return ['vip']
        else:
            return []

    monkeypatch.setattr(
        'taxi.internal.subvention_kit.tags_helpers.fetch_driver_tags',
        fake_fetch_driver_tags,
    )

    @patch('blackbox.JsonBlackbox')
    def bb_patched(*args, **kwargs):
        class BBPatched(object):
            def userinfo(*args, **kwargs):
                return {'users': [{'aliases': {'21': 'nphne-6463zf3n'}}]}
        return BBPatched()

    @patch('taxi.internal.personal.bulk_store')
    @async.inline_callbacks
    def bulk_store(data_type, request_ids, log_extra=None):
        assert data_type == personal.PERSONAL_TYPE_DRIVER_LICENSES
        yield
        async.return_value([{'id': 'pd_id_' + i, 'license': i} for i in request_ids])

    @patch('taxi.internal.personal.store')
    @async.inline_callbacks
    def store(data_type, request_value):
        assert data_type == personal.PERSONAL_TYPE_DRIVER_LICENSES
        yield
        async.return_value({'id': 'pd_id_' + request_value, 'license': request_value})

    @patch('taxi.internal.driver_manager._get_all_countries')
    @async.inline_callbacks
    def _get_all_countries():
        yield
        async.return_value(
            []
        )

    @patch('taxi.external.cars_catalog.get_brand_model')
    @async.inline_callbacks
    def get_brand_model(brand, model):
        yield
        async.return_value({'corrected_model': model})

    @patch('taxi.internal.import_drivers_utils.get_car_display_model')
    def get_car_display_model(normalized_model):
        return 'Cee\'dMINE' if normalized_model['model'] == 'Kia Cee\'d' else normalized_model['model']

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @patch('taxi.external.driver_metrics_client.driver_activity_value')
    @async.inline_callbacks
    def driver_activity_value(src_service_name, tvm_src_service_name, udid, log_extra=None):
        udid_without_activity = '000000000000000000000002'
        yield
        async.return_value(
            80 if str(udid) != udid_without_activity else None
        )

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))
        if url == "http://personal.taxi.yandex.net/v1/phones/find":
            phone = kwargs['json']['value']
            response = {'value': phone, 'id': 'id_' + phone}
            return areq_request.response(200, body=json.dumps(response))

    @patch('taxi.core.arequests.request')
    @async.inline_callbacks
    def request(method, url, **kwargs):
        response = arequests.Response(
            status_code=200,
            content=bson.json_util.dumps({
                'items': [TST_HISTORY_RESPONSE]
            }))
        yield async.return_value(response)

    response = Client().post(
        '/api/driver_card/',
        json.dumps(request_data),
        'application/json'
    )

    assert response.status_code == 200
    expected = json.loads(load(expected))
    if tags_error:
        for driver in expected['drivers']:
            driver['tags'] = []
    response_data = json.loads(response.content)
    assert response_data == expected


@pytest.mark.config(
    DRIVER_CARD_YANDEX_ID_SETTINGS={
        'enabled': True,
        'alias_types': {'21': 'neophonish'},
    }
)
@pytest.mark.config(DRIVERS_ACCESS_BY_COUNTRY=True, TAXI_FLEET_DEVICE_MODEL_MAPPING={'iPhone9,1': 'iPhone 7'})
@pytest.mark.parametrize('permissions, request_data, expected_code, '
                         'expected', [
    (
        {}, {'phone': '+79001111111'}, 403, None
    ),
    (
        {
            'view_drivers': {
                'mode': 'unrestricted'
            },
            'search_by_driver_phone': {
                'mode': 'unrestricted'
            },
        },
        {'phone': '+79003333333'},
        200,
        [{'uuid': '000000000003'}]
    ),
    (
            {
                'view_drivers': {
                    'mode': 'countries_filter',
                    'countries_filter': {'ukr'}
                },
                'search_by_driver_license': {
                    'mode': 'countries_filter',
                    'countries_filter': {'ukr'}
                },

            },
            {'driver_license': 'LICENSE_2'},
            200,
            []
    ),
    (
            {
                'view_drivers': {
                    'mode': 'countries_filter',
                    'countries_filter': {'rus'}
                },
            },
            {'clid': '000000000001'},
            200,
            [
                {'uuid': '000000000001'},
                {'uuid': '000000000002'},
            ]
    ),
    (
        {
            'view_drivers': {
                'mode': 'countries_filter',
                'countries_filter': {'blr'}
            },
        },
        {'clid': '000000000001'},
        200,
        []
    )
])
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(TAXI_FLEET_DEVICE_MODEL_MAPPING={'iPhone9,1': 'iPhone 7'})
def test_drivers_access_by_country(patch, permissions, request_data,
                                   expected_code, expected, areq_request):
    @patch('blackbox.JsonBlackbox')
    def bb_patched(*args, **kwargs):
        class BBPatched(object):
            def userinfo(*args, **kwargs):
                return {'users': [{'aliases': {'21': 'nphne-6463zf3n'}}]}
        return BBPatched()

    @patch('taxi.internal.dbh.admin_groups.Doc.get_groups_permissions')
    @async.inline_callbacks
    def get_groups_permissions(groups):
        yield
        async.return_value(
            permissions
        )

    @patch('taxi.internal.driver_manager._get_all_countries')
    @async.inline_callbacks
    def _get_all_countries():
        yield
        async.return_value(
            []
        )

    @patch('taxi.external.driver_metrics_client.driver_activity_value')
    @async.inline_callbacks
    def driver_activity_value(src_service_name, tvm_src_service_name, udid, log_extra=None):
        udid_without_activity = '000000000000000000000002'
        yield
        async.return_value(
            80 if str(udid) != udid_without_activity else None
        )

    @patch('taxi.external.cars_catalog.get_brand_model')
    @async.inline_callbacks
    def get_brand_model(brand, model):
        yield
        async.return_value({'corrected_model': model})

    @patch('taxi.internal.import_drivers_utils.get_car_display_model')
    def get_car_display_model(normalized_model):
        return 'Cee\'dMINE' if normalized_model['model'] == 'Kia Cee\'d' else normalized_model['model']

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/find":
            phone = kwargs['json']['value']
            response = {'value': phone, 'id': 'id_' + phone}
            return areq_request.response(200, body=json.dumps(response))
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    request = django_test.RequestFactory().post(
        path='',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    request.login = 'some_login'
    request.time_storage = evlog.new_time_storage('')
    request.superuser = False
    request.groups = []
    request.remote_addr = '1.2.3.4'
    response = drivers.get_driver_card(request)

    assert response.status_code == expected_code
    if response.status_code == 200:
        result = json.loads(response.content)['drivers']
        assert len(result) == len(expected)
        for res_elem, expected_elem in zip(result, expected):
            assert res_elem['uuid'] == expected_elem['uuid']


@pytest.mark.config(
    DRIVER_CARD_YANDEX_ID_SETTINGS={
        'enabled': True,
        'alias_types': {'21': 'neophonish'},
    }
)
@pytest.mark.config(
    EATS_COURIER_SERVICE_MAPPING={
        "1": {
            "1": "000000000001",
            "101": "000000000001",
        },
        "107": {
            "1": "000000000003",
            "2": "000000000001",
        },
        "selfemployed": "000000000004",
    }
)
@pytest.mark.parametrize('permissions, request_data, expected_code, '
                         'expected', [
    (
        {
            'view_eda_lavka_couriers': {
                'mode': 'unrestricted'
            },
            'search_by_driver_phone': {
                'mode': 'unrestricted'
            },
        },
        {'phone': '+79003333333'},
        200,
        [{'uuid': '000000000003'}]
    ),
    (
        {
            'view_eda_lavka_couriers': {
                'mode': 'unrestricted'
            },
            'search_by_driver_license': {
                'mode': 'unrestricted'
            },
        },
        {'driver_license': 'LICENSE_2'},
        200,
        [{'uuid': '000000000003'}]
    ),
    (
        {
            'view_eda_lavka_couriers': {
                'mode': 'unrestricted'
            },
        },
        {'clid': '000000000001'},
        200,
        [
            {'uuid': '000000000001'},
        ]
    ),
    (
        {
            'view_eda_lavka_couriers': {
                'mode': 'unrestricted'
            },
            'view_drivers': {
                'mode': 'unrestricted'
            },
        },
        {'clid': '000000000001'},
        200,
        [
            {'uuid': '000000000001'},
            {'uuid': '000000000002'},
        ]
    ),
    (
        {
            'view_eda_lavka_couriers': {
                'mode': 'unrestricted'
            },
            'search_by_driver_license': {
                'mode': 'unrestricted'
            },
        },
        {
            'clid': '000000000003',
            'driver_license': 'LICENSE_7'
        },
        200,
        []
    )
])
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(TAXI_FLEET_DEVICE_MODEL_MAPPING={'iPhone9,1': 'iPhone 7'})
def test_drivers_view_eda_lavka_permissions(patch, permissions, request_data,
                                   expected_code, expected, areq_request):
    @patch('blackbox.JsonBlackbox')
    def bb_patched(*args, **kwargs):
        class BBPatched(object):
            def userinfo(*args, **kwargs):
                return {'users': [{'aliases': {'21': 'nphne-6463zf3n'}}]}
        return BBPatched()

    @patch('taxi.internal.dbh.admin_groups.Doc.get_groups_permissions')
    @async.inline_callbacks
    def get_groups_permissions(groups):
        yield
        async.return_value(
            permissions
        )

    @patch('taxi.internal.driver_manager._get_all_countries')
    @async.inline_callbacks
    def _get_all_countries():
        yield
        async.return_value(
            []
        )

    @patch('taxi.external.driver_metrics_client.driver_activity_value')
    @async.inline_callbacks
    def driver_activity_value(src_service_name, tvm_src_service_name, udid, log_extra=None):
        udid_without_activity = '000000000000000000000002'
        yield
        async.return_value(
            80 if str(udid) != udid_without_activity else None
        )

    @patch('taxi.external.cars_catalog.get_brand_model')
    @async.inline_callbacks
    def get_brand_model(brand, model):
        yield
        async.return_value({'corrected_model': model})

    @patch('taxi.internal.import_drivers_utils.get_car_display_model')
    def get_car_display_model(normalized_model):
        return 'Cee\'dMINE' if normalized_model['model'] == 'Kia Cee\'d' else normalized_model['model']

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @patch('taxi.internal.personal.bulk_store')
    @async.inline_callbacks
    def bulk_store(data_type, request_ids, log_extra=None):
        assert data_type == personal.PERSONAL_TYPE_DRIVER_LICENSES
        yield
        async.return_value([{'id': 'pd_id_' + i, 'license': i} for i in request_ids])

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/find":
            phone = kwargs['json']['value']
            response = {'value': phone, 'id': 'id_' + phone}
            return areq_request.response(200, body=json.dumps(response))
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    request = django_test.RequestFactory().post(
        path='',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    request.login = 'some_login'
    request.time_storage = evlog.new_time_storage('')
    request.superuser = False
    request.groups = []
    request.remote_addr = '1.2.3.4'
    response = drivers.get_driver_card(request)

    assert response.status_code == expected_code
    if response.status_code == 200:
        result = json.loads(response.content)['drivers']
        assert len(result) == len(expected)
        for res_elem, expected_elem in zip(result, expected):
            assert res_elem['uuid'] == expected_elem['uuid']


@pytest.mark.config(
    DRIVER_CARD_YANDEX_ID_SETTINGS={
        'enabled': True,
        'alias_types': {'21': 'neophonish'},
    }
)
@pytest.mark.config(STATUS_MAX_AGE_HOURS=4)
@pytest.mark.parametrize('permissions, request_data, expected_code', [
    (
        {
            'view_drivers': {
                'mode': 'unrestricted'
            }
        },
        {'driver_license': 'LICENSE_4'},
        200,
    ),
])
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(TAXI_FLEET_DEVICE_MODEL_MAPPING={'iPhone9,1': 'iPhone 7'})
def test_drivers_old_status(monkeypatch, patch, permissions, request_data,
                            expected_code, areq_request):
    @patch('blackbox.JsonBlackbox')
    def bb_patched(*args, **kwargs):
        class BBPatched(object):
            def userinfo(*args, **kwargs):
                return {'users': [{'aliases': {'21': 'nphne-6463zf3n'}}]}
        return BBPatched()

    @patch('taxi.internal.driver_manager._get_all_countries')
    @async.inline_callbacks
    def _get_all_countries():
        yield
        async.return_value(
            []
        )

    @patch('taxi.external.cars_catalog.get_brand_model')
    @async.inline_callbacks
    def get_brand_model(brand, model):
        yield
        async.return_value({'corrected_model': model})

    @patch('taxi.internal.import_drivers_utils.get_car_display_model')
    def get_car_display_model(normalized_model):
        return 'Cee\'dMINE' if normalized_model['model'] == 'Kia Cee\'d' else normalized_model['model']

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @patch('taxi.external.driver_metrics_client.driver_activity_value')
    @async.inline_callbacks
    def driver_activity_value(src_service_name, tvm_src_service_name, udid, log_extra=None):
        udid_without_activity = '000000000000000000000002'
        yield
        async.return_value(
            80 if str(udid) != udid_without_activity else None
        )

    @patch('taxi.internal.personal.bulk_store')
    @async.inline_callbacks
    def bulk_store(data_type, request_ids, log_extra=None):
        assert data_type == personal.PERSONAL_TYPE_DRIVER_LICENSES
        yield
        async.return_value([{'id': 'pd_id_' + i, 'license': i} for i in request_ids])

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    response = Client().post(
        '/api/driver_card/',
        json.dumps(request_data),
        'application/json'
    )

    assert response.status_code == expected_code
    if response.status_code == 200:
        driver_with_status_expired = 0
        result = json.loads(response.content)['drivers']
        for driver in result:
            if 'status' in driver and 'status_updated' in driver:
                assert driver['is_status_expired']
                driver_with_status_expired += 1
            else:
                assert 'is_status_expired' not in driver

        assert len(result) == 2
        assert driver_with_status_expired == 2


@pytest.mark.config(
    DRIVER_CARD_YANDEX_ID_SETTINGS={
        'enabled': True,
        'alias_types': {'21': 'neophonish'},
    }
)
@pytest.mark.parametrize('request_data, expected, code', [
    (
        {
            "limit": 50,
            "offset": 0,
            "car_number": "Е236КА750"
        },
        'expected_1.json',
        200
    ),
    (
        {
            "limit": 50,
            "offset": 0,
            "car_number": "Е*36КА750"
        },
        'expected_1.json',
        200
    ),
    (
        {
            "limit": 50,
            "offset": 0,
            "car_number": "E236КА75*"
        },
        'expected_1.json',
        200
    ),
    (
        {
            "limit": 50,
            "offset": 0,
            "car_number": "E*36КА**"
        },
        'expected_1.json',
        200
    ),
    (
        {
            "limit": 50,
            "offset": 0,
            "car_number": "*236КА750"
        },
        'expected_regex.json',
        200
    ),
    (
        {
            "limit": 50,
            "offset": 0,
            "car_number": "*236**750"
        },
        'expected_regex.json',
        200
    ),
    (
        {
            "limit": 50,
            "offset": 0,
            "car_number": "*236*****"
        },
        'expected_regex.json',
        200
    ),
])
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(TAXI_FLEET_DEVICE_MODEL_MAPPING={'iPhone9,1': 'iPhone 7'})
def test_find_car_number_regex(load, request_data, expected, code, patch, areq_request):
    @patch('blackbox.JsonBlackbox')
    def bb_patched(*args, **kwargs):
        class BBPatched(object):
            def userinfo(*args, **kwargs):
                return {'users': [{'aliases': {'21': 'nphne-6463zf3n'}}]}
        return BBPatched()

    @patch('taxi.internal.driver_manager._get_all_countries')
    @async.inline_callbacks
    def _get_all_countries():
        yield
        async.return_value(
            []
        )

    @patch('taxi.external.cars_catalog.get_brand_model')
    @async.inline_callbacks
    def get_brand_model(brand, model):
        yield
        async.return_value({'corrected_model': model})

    @patch('taxi.internal.import_drivers_utils.get_car_display_model')
    def get_car_display_model(normalized_model):
        return 'Cee\'dMINE' if normalized_model['model'] == 'Kia Cee\'d' else normalized_model['model']

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @patch('taxi.external.driver_metrics_client.driver_activity_value')
    @async.inline_callbacks
    def driver_activity_value(src_service_name, tvm_src_service_name, udid, log_extra=None):
        udid_without_activity = '000000000000000000000002'
        yield
        async.return_value(
            80 if str(udid) != udid_without_activity else None
        )

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    response = Client().post(
        '/api/driver_card/',
        json.dumps(request_data),
        'application/json'
    )

    assert response.status_code == 200
    result = json.loads(response.content)

    expected = json.loads(load(expected))
    assert result == expected


@pytest.mark.config(
    DRIVER_CARD_YANDEX_ID_SETTINGS={
        'enabled': True,
        'alias_types': {'21': 'neophonish'},
    }
)
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{
        'dst': settings.REPOSITION_TVM_SERVICE_NAME,
        'src': settings.ADMIN_TVM_SERVICE_NAME,
    }]
)
@pytest.mark.parametrize('request_data, tracker_is_ok, '
                         'taximeter_is_ok, reposition_is_ok, '
                         'expected_code', [
    ({"driver_id": "000000000003_000000000005", 'point': [3, 4]},
     False, False, False, 404),
    ({"driver_id": "000000000003_000000000005", 'point': [3, 4]},
     True, False, False, 406),
    ({"driver_id": "000000000003_000000000005", 'point': [3, 4]},
     True, True, False, 200),
    ({"driver_id": "000000000003_000000000005", 'point': [3, 4]},
     True, True, True, 200),
])
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(TAXI_FLEET_DEVICE_MODEL_MAPPING={'iPhone9,1': 'iPhone 7'})
def test_drivers_diagnostics(monkeypatch, load, patch,
                             request_data, tracker_is_ok,
                             taximeter_is_ok, reposition_is_ok,
                             expected_code, areq_request):
    tracker_data = json.loads(load('tracker-diagnostics.json'))
    reposition_data = json.loads(load('reposition-state.json'))
    taximeter_data = json.loads(load('taximeter-diagnostics.json'))

    @patch('blackbox.JsonBlackbox')
    def bb_patched(*args, **kwargs):
        class BBPatched(object):
            def userinfo(*args, **kwargs):
                return {'users': [{'aliases': {'21': 'nphne-6463zf3n'}}]}
        return BBPatched()

    @patch('taxi.internal.driver_manager._get_all_countries')
    @async.inline_callbacks
    def _get_all_countries():
        yield
        async.return_value(
            []
        )

    @patch('taxi.external.cars_catalog.get_brand_model')
    @async.inline_callbacks
    def get_brand_model(brand, model):
        yield
        async.return_value({'corrected_model': model})

    @patch('taxi.internal.import_drivers_utils.get_car_display_model')
    def get_car_display_model(normalized_model):
        return 'Cee\'dMINE' if normalized_model['model'] == 'Kia Cee\'d' else normalized_model['model']

    @patch('taxi.external.tracker.get_driver_tariffs_diagnostics')
    @async.inline_callbacks
    def get_driver_tariffs_diagnostics(*args, **kwargs):
        if not tracker_is_ok:
            raise tracker.NotFoundError('track not found')
        data = yield tracker_data
        async.return_value(data)

    @patch('taxi.external.tvm.get_ticket')
    @async.inline_callbacks
    def get_ticket(src_service_name, dst_service_name, log_extra=None):
        assert src_service_name == settings.ADMIN_TVM_SERVICE_NAME
        assert dst_service_name == settings.REPOSITION_TVM_SERVICE_NAME
        yield async.return_value(TEST_TVM_TICKET)

    @patch('taxi.external.driver_metrics_client.driver_activity_value')
    @async.inline_callbacks
    def driver_activity_value(src_service_name, tvm_src_service_name, udid, log_extra=None):
        udid_without_activity = '000000000000000000000002'
        yield
        async.return_value(
            80 if str(udid) != udid_without_activity else None
        )

    @patch('taxi.external.reposition._request')
    @async.inline_callbacks
    def _request(*args, **kwargs):
        headers = kwargs.get('headers')
        assert headers == {tvm.TVM_TICKET_HEADER: TEST_TVM_TICKET}
        if not reposition_is_ok:
            raise reposition.NotFoundError('driver session not found')
        data = yield reposition_data
        async.return_value(data)

    @patch('taxi.external.taximeter.get_driver_taximeter_diagnostics')
    @async.inline_callbacks
    def get_driver_taximeter_diagnostics(*args, **kwargs):
        if not taximeter_is_ok:
            raise taximeter.TaximeterRequestError('request error')
        data = yield taximeter_data
        async.return_value(data)

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    response = Client().post(
        '/api/driver_card/diagnostics/',
        json.dumps(request_data),
        'application/json'
    )

    assert response.status_code == expected_code
    if response.status_code == 200:
        response_json = json.loads(response.content)
        data = {}
        data['tracker'] = tracker_data
        data['taximeter'] = taximeter_data
        if 'reposition' in response_json:
            data['reposition'] = reposition_data
        assert response_json == data


@pytest.mark.config(
    DRIVER_CARD_YANDEX_ID_SETTINGS={
        'enabled': True,
        'alias_types': {'21': 'neophonish'},
    }
)
@pytest.mark.config(DRIVER_STATUS_USE_IN_TAXIADMIN=True)
@pytest.mark.parametrize(
    'request_data, ds_response, expected_status, expected_ts',
    [
        (
            {'uuid': '000000000007'},
            [
                {
                    'park_id': '000000000007',
                    'driver_id': '000000000007',
                    'status': 'online',
                    'updated_ts': NOW_MS,
                },
            ],
            'online',
            NOW,
        ),
        (
            {'uuid': '000000000007'},
            [
                {
                    'park_id': '000000000007',
                    'driver_id': '000000000007',
                    'status': 'busy',
                    'updated_ts': NOW_MS,
                },
            ],
            'busy',
            NOW,
        ),
        (
            {'uuid': '000000000007'},
            [
                {
                    'park_id': '000000000007',
                    'driver_id': '000000000007',
                    'status': 'offline',
                    'updated_ts': NOW_MS,
                },
            ],
            'offline',
            NOW,
        ),
        (
            {'uuid': '000000000007'},
            [
                {
                    'park_id': '000000000007',
                    'driver_id': '000000000007',
                    'status': 'offline',
                },
            ],
            'offline',
            None,
        ),
        (
            {'uuid': '000000000007'},
            [
                {
                    'park_id': '000000000007',
                    'driver_id': '000000000007',
                    'status': 'online',
                    'updated_ts': NOW_MS,
                    'orders': [{'id': 'some_order', 'status': 'transporting'}],
                },
            ],
            'online',
            NOW,
        ),
        (
            {'uuid': '000000000007'},
            [
                {
                    'park_id': '000000000007',
                    'driver_id': '000000000007',
                    'status': 'online',
                    'updated_ts': NOW_MS,
                    'orders': [{'id': 'some_order', 'status': 'complete'}],
                },
            ],
            'online',
            NOW,
        ),
        (
            {'uuid': '000000000007'},
            [
                {
                    'park_id': '000000000007',
                    'driver_id': '000000000007',
                    'status': 'busy',
                    'updated_ts': NOW_MS,
                    'orders': [{'id': 'some_order', 'status': 'transporting'}],
                },
            ],
            'busy',
            NOW,
        ),
        (
            {'uuid': '000000000007'},
            [
                {
                    'park_id': '000000000007',
                    'driver_id': '000000000007',
                    'status': 'busy',
                    'updated_ts': NOW_MS,
                    'orders': [{'id': 'some_order', 'status': 'complete'}],
                },
            ],
            'busy',
            NOW,
        ),
    ],
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(TAXI_FLEET_DEVICE_MODEL_MAPPING={'iPhone9,1': 'iPhone 7'})
def test_use_driver_status(
        patch, request_data, ds_response, expected_status, expected_ts
):
    @patch('blackbox.JsonBlackbox')
    def bb_patched(*args, **kwargs):
        class BBPatched(object):
            def userinfo(*args, **kwargs):
                return {'users': [{'aliases': {'21': 'nphne-6463zf3n'}}]}
        return BBPatched()

    @patch('taxi.external.cars_catalog.get_brand_model')
    @async.inline_callbacks
    def get_brand_model(brand, model):
        yield
        async.return_value({'corrected_model': model})

    @patch('taxi.core.arequests._api._request')
    @async.inline_callbacks
    def _request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            resp = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            yield async.return_value(
                arequests.Response(status_code=200, content=json.dumps(resp))
            )

        assert method == 'POST'
        assert 'v2/statuses' in url
        response = {'statuses': ds_response}
        yield async.return_value(
            arequests.Response(status_code=200, content=json.dumps(response)),
        )

    response = Client().post(
        '/api/driver_card/', json.dumps(request_data), 'application/json',
    )

    assert response.status_code == 200
    drivers = json.loads(response.content)['drivers']
    assert drivers[0]['status'] == expected_status
    if expected_ts is not None:
        assert dates.parse_timestring(
            drivers[0]['status_updated'],
        ) == expected_ts
    else:
        assert 'status_updated' not in drivers[0]
