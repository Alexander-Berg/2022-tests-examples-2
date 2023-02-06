# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

from django import test as django_test
import jsonschema
import pytest
from taxiadmin.api.views import parks

from taxi.internal import dbh

from taxi.core import async
from taxi.core import db

from taxiadmin.api import apiutils


@pytest.fixture
def ticket_check_is_successful(patch):
    @patch('taxiadmin.audit.check_ticket')
    def check_ticket(ticket, login, **kwargs):
        return


@pytest.fixture
def taxirate_check_is_successful(patch):
    @patch('taxiadmin.audit.check_taxirate')
    def check_taxirate(ticket, login, **kwargs):
        return


@pytest.fixture
def billing_create_partner_mock(patch):
    @patch('taxi.external.billing.create_partner')
    @async.inline_callbacks
    def create_partner(billing_service, operator_uid, billing_client_id, name,
                       email, phone, region_id, url=None, log_extra=None):
        yield async.return_value(billing_client_id)


@pytest.fixture
def billing_create_product_mock(patch):
    @patch('taxi.external.billing.create_service_product')
    @async.inline_callbacks
    def create_service_product(billing_service, partner_id, product_id,
                               product_name, service_fee=None, log_extra=None):
        yield async.return_value()


@pytest.fixture
def mock_statuses_park(areq_request):
    @areq_request
    def requests_request(method, url, **kwargs):
        data = {'free': 1, 'busy': 2, 'onorder': 3}
        return areq_request.response(200, body=json.dumps(data))


@pytest.fixture
def parks_list_response_data():
    return [
        {
            'id': 'test_parks_list_1',
            'name': 'test_name_1',
            'type': 'test_type',
            'city': 'test_city_1',
            'inn': '123456',
            'drivers_online': 12,  # two active park ids for clid
            'coupon': True,
            'creditcard': True,
            'corp': False,
            'real_clids': [{'name': 'Диспетчерская', 'clid': 'clid'}],
            'account_offer_confirmed': u'2016-10-06T14:04:27+0300'
        },
        {
            'id': 'test_parks_list_2',
            'name': 'test_name_2',
            'type': 'test_type',
            'city': 'test_city_1',
            'drivers_online': 6,  # one active park ids for clid
            'coupon': False,
            'creditcard': False,
            'corp': False,
            'real_clids': [],
            'account_offer_confirmed': u'2016-10-06T18:04:27+0300'
        },
        {
            'id': 'test_parks_list_3',
            'name': 'test_name_3',
            'type': 'test_type',
            'city': 'test_city_2',
            'drivers_online': 18,  # three active park ids for clid
            'coupon': False,
            'creditcard': False,
            'corp': False,
            'real_clids': []
        },
        {
            'id': 'test_parks_list_4',
            'name': 'test_name_4',
            'type': 'test_type',
            'city': 'test_city_2',
            'drivers_online': 0,  # no active park ids for clid
            'coupon': False,
            'creditcard': False,
            'corp': False,
            'real_clids': []
        },
        {
            'id': '000000000123',
            'name': 'tEst_Name_3',
            'type': 'test_type',
            'city': 'test_city_2',
            'drivers_online': 0,  # no park ids for clid
            'coupon': False,
            'creditcard': False,
            'corp': False,
            'real_clids': []
        }
    ]


@pytest.mark.parametrize('data,expected_indexes,code', [
    ({'city': 'test_city_1'}, [0, 1], 200),
    ({'city': 'test_city_1', 'sort': 'creditcard'}, [1, 0], 200),
    ({'name': 'test_name_3'}, [4, 2], 200),
    ({'id': 'test_parks_list_4'}, [3], 200),
    ({'id': 'test_parks_list'}, [0, 1, 2, 3], 200),
    ({'id': 'test_parks_list', 'skip': 1, 'limit': 2}, [1, 2], 200),
    ({'id': ''}, None, 400),
    ({'name': ''}, None, 400),
    ({'city': ''}, None, 400),
    ({'id': ' test_parks_list    ', 'skip': 1, 'limit': 2}, [1, 2], 200),
    ({'city': ' test_City_1  '}, [0, 1], 200,),
    ({'name': 'test_name', 'skip': 1, 'limit': 2}, [1, 4], 200),
    ({'skip': 'one', 'limit': 'two'}, None, 400),
    ({'inn': '123'}, [0], 200),
    ({'inn': '456'}, [0], 200),
    ({'inn': '   '}, None, 400),
    ({'sort': 'account_offer_confirmed', 'name': 'test_'}, [4, 2, 3, 0, 1], 200)
])
@pytest.mark.now('2017-07-20T10:00:00.0')
@pytest.mark.usefixtures('mock_statuses_park')
@pytest.mark.asyncenv('blocking')
def test_get_parks_list(data, expected_indexes, code, parks_list_response_data):
    url = '/api/parks/get_parks_list/'
    response = django_test.Client().get(url, data)
    assert response.status_code == code, response.content
    if expected_indexes is not None:
        assert json.loads(response.content) == [
            parks_list_response_data[index] for index in expected_indexes
        ]


@pytest.mark.parametrize(
    'clid,expected_filename',
    [
        (
            'test_get_park_info_1',
            'expected_park_info_test_get_park_info_1.json',
        ),
        (
            'test_get_park_info_2',
            'expected_park_info_test_get_park_info_2.json',
        ),
        (
            'test_get_park_info_3',
            'expected_park_info_test_get_park_info_3.json',
        ),
    ],
)
@pytest.mark.asyncenv('blocking')
def test_get_park_info(load, clid, expected_filename):
    expected_data = json.loads(load(expected_filename).decode('utf-8'))
    response = django_test.Client().get(
        '/api/parks/get_park_info/?id={0}'.format(clid)
    )
    assert response.status_code == 200
    response_content = response.content.decode('utf-8')
    response_data = json.loads(response_content)
    assert response_data == expected_data, response_content


@pytest.mark.now('2017-07-30T10:00:00.0')
@pytest.mark.parametrize(
    'clid,expected_periods',
    [
        (
            'test_confirmed_log_1',
            [{'date_from': '2017-07-20', 'date_to': '2017-07-25'}],
        ),
        (
            'test_confirmed_log_2',
            [],
        ),
        (
            'test_confirmed_log_3',
            [],
        ),
        (
            'test_confirmed_log_4',
            [{'date_from': '2017-07-20', 'date_to': '2017-07-25'}],
        ),
        (
            'test_confirmed_log_5',
            [{'date_from': '2017-07-20', 'date_to': '2017-07-30'}],
        ),
    ],
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_render_periods_of_not_confirmed_offers(clid, expected_periods):
    park = yield dbh.parks.Doc.find_one_by_id(clid)
    periods = parks._render_periods_of_not_confirmed_offers(park)
    assert periods == expected_periods


@pytest.mark.config(PARKS_ENABLE_DEFAULT_CHILDCHAIR_RENTS=True)
@pytest.mark.asyncenv('blocking')
def test_get_api_usage_metadata(load, patch):
    @patch('uuid.uuid4')
    def uuid_stub():
        class Hex(object):
            hex = 'randomuuid1234'
        return Hex

    def _sort_descriptions(descriptions):
        return sorted(descriptions, key=lambda description: description['name'])

    def _get_json_validator(schema, fragment):
        resolver = jsonschema.RefResolver('', schema, store={})
        return jsonschema.Draft4Validator(
            fragment,
            resolver=resolver,
            format_checker=jsonschema.FormatChecker(),
            types={'array': (list, tuple)}
        )

    def _validate_default_values(schema_path, descriptions):
        schema = apiutils.get_yaml_schema(schema_path)
        for field_description in descriptions:
            if 'default_value' not in field_description:
                continue
            name = field_description['name']
            value = field_description['default_value']
            field_schema = schema['properties'][name]
            validator = _get_json_validator(schema, field_schema)
            validator.validate(value)

    filename = 'usage_metadata_answer.json'
    expected_data = json.loads(load(filename).decode('utf-8'))
    response = django_test.Client().get('/api/parks/usage_metadata/')
    assert response.status_code == 200
    response_content = response.content.decode('utf-8')
    response_data = json.loads(response_content)
    common_fields = _sort_descriptions(
        response_data['fields']['common_fields'])
    expected_common_fields = _sort_descriptions(
        expected_data['fields']['common_fields'])
    assert common_fields == expected_common_fields, common_fields
    audit_fields = _sort_descriptions(
        response_data['fields']['audit_fields'])
    expected_audit_fields = _sort_descriptions(
        expected_data['fields']['audit_fields'])
    assert audit_fields == expected_audit_fields, audit_fields

    # Validate default values against schemas
    _validate_default_values(
        'parks.yaml#/definitions/ParkCommonFields',
        common_fields,
    )
    _validate_default_values(
        'parks.yaml#/definitions/ParkAuditFields',
        audit_fields,
    )


COMMON_PARK_DATA = [
(
    # Nonexistent park, should return 404
    {
        'id': 'test_put_common_fields_1',
        'fields': {
            'city': 'Москва',
            'type': 'taxipark',
            'name': 'Лещ',
            'phone': '+79261234567',
            'marketing_agreement': True,
            'enable_grade_for_lightbox': False,
            'enable_grade_for_full_branding': True,
            'enable_grade_for_sticker': True,
            'takes_urgent': True,
            'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
            'yandex_login': 'boba_fett',
            'email': 'boba_fett@yandex.ru',
            'billing_email': 'boba_fett@yandex.ru',
            'creditcard': True,
            'coupon': False,
            'enable_branding_sticker': False,
            'enable_branding_lightbox': False,
            'enable_branding_co_branding': False,
            'franchise_zones': ['moscow', 'spb'],
            'automate_marketing_payments': True,
            'pay_donations_without_offer': True,
            'additional_compensation_by_card': 230,
            'additional_compensation_by_cash': 120,
            'balance_threshold': -5000.0,
        },
    },
    404,
    None,
),
(
    # Existing park. Test that fields can be unset. Test that legacy fields
    # are not unset.
    {
        'id': 'test_put_common_fields_2',
        'fields': {
            'city': 'Москва',
            'type': 'taxipark',
            'name': 'Лещ',
            'phone': '+7 (926) 123-45-67',
            'marketing_agreement': True,
            'enable_grade_for_lightbox': False,
            'enable_grade_for_full_branding': True,
            'enable_grade_for_sticker': True,
            'takes_urgent': True,
            'email': 'darth-vader@yandex.ru',
            'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
            'creditcard': False,
            'coupon': False,
            'enable_branding_sticker': False,
            'enable_branding_lightbox': False,
            'enable_branding_co_branding': False,
            'franchise_zones': ['moscow', 'spb'],
            'automate_marketing_payments': True,
            'pay_donations_without_offer': True,
            'additional_compensation_by_card': 230,
            'additional_compensation_by_cash': 120,
            'balance_threshold': -5000.0
        },
    },
    200,
    {
        '_id': 'test_put_common_fields_2',
        'city': 'Москва',
        '_type': 'taxipark',
        'apikey': 'random12',
        'name': 'Лещ',
        'phone': '+79261234567',
        'marketing_agreement': True,
        'enable_grade_for_lightbox': False,
        'enable_grade_for_full_branding': True,
        'enable_grade_for_sticker': True,
        'min_delayed': 30,
        'takes_delayed': False,
        'takes_urgent': True,
        'email': 'darth-vader@yandex.ru',
        'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
        'updated': datetime.datetime(2017, 7, 20, 10, 0),
        'franchise_zones': [{
            'ts': datetime.datetime(2017, 7, 20, 10, 0),
            'v': ['moscow', 'spb'],
        }],
        'billing_client_ids': [],
        'billing_cargo_product_ids': [],
        'billing_corp_product_ids': [],
        'billing_donate_product_ids': [],
        'billing_product_ids': [],
        'billing_uber_product_ids': [],
        'billing_uber_roaming_product_ids': [],
        'billing_vezet_product_ids': [],
        'enable_branding_co_branding': [],
        'enable_branding_lightbox': [],
        'enable_branding_sticker': [],
        'account': {
            'threshold': -5000.0,
            'additional_compensation_by_card': 230,
            'additional_compensation_by_cash': 120,
        },
        'pay_donations_without_offer': True,
        'automate_marketing_payments': True,
    },
),
(
    {
        'id': 'test_put_common_fields_2',
        'fields': {
            'email': 'darth vader@yandex.ru',
        },
    },
    400,
    None,
),
(
    # Test that city must exist
    {
        'id': 'test_put_common_fields_2',
        'fields': {
            'city': 'Анк-Морпорк',
            'type': 'taxipark',
            'name': 'Лещ',
            'phone': '+79261234567',
            'marketing_agreement': True,
            'enable_grade_for_lightbox': False,
            'enable_grade_for_full_branding': True,
            'enable_grade_for_sticker': True,
            'takes_urgent': True,
            'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
            'creditcard': True,
            'coupon': False,
            'enable_branding_sticker': True,
            'enable_branding_lightbox': False,
            'enable_branding_co_branding': False,
            'franchise_zones': ['moscow', 'spb'],
            'automate_marketing_payments': False,
            'pay_donations_without_offer': True,
            'additional_compensation_by_card': 230,
            'additional_compensation_by_cash': 120,
            'balance_threshold': -5000.0,
        },
    },
    400,
    None,
),
(
    # Test that region_id must be present in country
    {
        'id': 'test_put_common_fields_2',
        'fields': {
            'city': 'Вовулинск',
            'type': 'taxipark',
            'name': 'Лещ',
            'phone': '+79261234567',
            'marketing_agreement': True,
            'enable_grade_for_lightbox': False,
            'enable_grade_for_full_branding': True,
            'enable_grade_for_sticker': True,
            'takes_urgent': True,
            'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
            'creditcard': False,
            'coupon': False,
            'enable_branding_sticker': False,
            'enable_branding_lightbox': False,
            'enable_branding_co_branding': False,
            'franchise_zones': [],
            'automate_marketing_payments': False,
            'pay_donations_without_offer': False,
            'additional_compensation_by_card': 0,
            'additional_compensation_by_cash': 0,
            'balance_threshold': -5000.0,
        },
    },
    400,
    None,
),
(
    # Test phone validation
    {
        'id': 'test_put_common_fields_2',
        'fields': {
            'city': 'Москва',
            'type': 'taxipark',
            'name': 'Лещ',
            'phone': '+109261234567',
            'marketing_agreement': True,
            'enable_grade_for_lightbox': False,
            'enable_grade_for_full_branding': True,
            'enable_grade_for_sticker': True,
            'takes_urgent': True,
            'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
            'creditcard': False,
            'coupon': False,
            'enable_branding_sticker': False,
            'enable_branding_lightbox': False,
            'enable_branding_co_branding': False,
            'franchise_zones': [],
            'automate_marketing_payments': False,
            'pay_donations_without_offer': False,
            'additional_compensation_by_card': 0,
            'additional_compensation_by_cash': 0,
            'balance_threshold': -5000.0,
        },
    },
    400,
    None,
),
(
    # Check that billing client ID is not unset
    {
        'id': 'test_put_audit_fields_1',
        'fields': {
            'creditcard': True,
            'coupon': False,
            'enable_branding_sticker': True,
            'enable_branding_lightbox': False,
            'enable_branding_co_branding': False,
            'franchise_zones': ['moscow', 'spb'],
            'automate_marketing_payments': True,
            'pay_donations_without_offer': True,
            'additional_compensation_by_card': 230,
            'additional_compensation_by_cash': 120,
            'city': 'Москва',
            'type': 'taxipark',
            'name': 'Лещ',
            'phone': '+7 (926) 123-45-67',
            'marketing_agreement': True,
            'enable_grade_for_lightbox': False,
            'enable_grade_for_full_branding': True,
            'enable_grade_for_sticker': True,
            'takes_urgent': True,
            'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
            'email': 'boba_fett@yandex.ru',
            'billing_email': 'boba_fett@yandex.ru',
            'balance_threshold': -5000.0,
        },
    },
    200,
    {
        'requirements': {
            'creditcard': True,
            'animaltransport': True,
            'corp': True
        },
        'enable_branding_sticker': [{
            'v': True, 'ts': datetime.datetime(2017, 7, 20, 10, 0)
        }],
        'enable_branding_lightbox': [
            {'v': False, 'ts': datetime.datetime(2017, 7, 20, 10, 0)},
            {'v': True, 'ts': datetime.datetime(2017, 7, 10, 10, 0)},
        ],
        'enable_branding_co_branding': [
            {'v': False, 'ts': datetime.datetime(2017, 7, 20, 10, 0)},
            {'v': True, 'ts': datetime.datetime(2017, 7, 10, 10, 0)},
        ],
        'franchise_zones': [{
            'ts': datetime.datetime(2017, 7, 20, 10, 0),
            'v': ['moscow', 'spb'],
        }],
        'automate_marketing_payments': True,
        'pay_donations_without_offer': True,
        'account': {
            'threshold': -5000.0,
            'additional_compensation_by_card': 230.0,
            'additional_compensation_by_cash': 120.0,
        },
        'childchair_rents': [
            [
                datetime.datetime(2017, 7, 10, 10, 0),
                None,
                {'active': True, 'rental_rate': 10},
            ],
        ],
        'billing_client_ids': [
            [
                datetime.datetime(2017, 7, 10, 10, 0),
                None,
                '1234567',
            ],
        ],
        '_id': 'test_put_audit_fields_1',
        'city': 'Москва',
        '_type': 'taxipark',
        'apikey': 'random1234',
        'name': 'Лещ',
        'phone': '+79261234567',
        'marketing_agreement': True,
        'enable_grade_for_lightbox': False,
        'enable_grade_for_full_branding': True,
        'enable_grade_for_sticker': True,
        'takes_urgent': True,
        'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
        'email': 'boba_fett@yandex.ru',
        'billing_email': 'boba_fett@yandex.ru',
        'created': datetime.datetime(2017, 7, 20, 10, 0),
        'updated': datetime.datetime(2017, 7, 20, 10, 0),
    },
),
(
    # Check that billing client ID can be set to the same value
    {
        'id': 'test_put_audit_fields_1',
        'fields': {
            'creditcard': True,
            'coupon': False,
            'enable_branding_sticker': True,
            'enable_branding_lightbox': False,
            'enable_branding_co_branding': False,
            'franchise_zones': ['moscow', 'spb'],
            'automate_marketing_payments': True,
            'pay_donations_without_offer': True,
            'additional_compensation_by_card': 230,
            'additional_compensation_by_cash': 120,
            'billing_client_id': {
                'client_id': '1234567',
                'start_date': '2017-07-20T20:00:00.000000+0000'
            },
            'city': 'Москва',
            'type': 'taxipark',
            'name': 'Лещ',
            'phone': '+7 (926) 123-45-67',
            'marketing_agreement': True,
            'enable_grade_for_lightbox': False,
            'enable_grade_for_full_branding': True,
            'enable_grade_for_sticker': True,
            'takes_urgent': True,
            'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
            'email': 'boba_fett@yandex.ru',
            'billing_email': 'boba_fett@yandex.ru',
            'yandex_login': 'boba_fett',
            'balance_threshold': -5000.0,
        },
    },
    200,
    {
        'requirements': {
            'creditcard': True,
            'animaltransport': True,
            'corp': True
        },
        'enable_branding_sticker': [{
            'v': True, 'ts': datetime.datetime(2017, 7, 20, 10, 0)
        }],
        'enable_branding_lightbox': [
            {'v': False, 'ts': datetime.datetime(2017, 7, 20, 10, 0)},
            {'v': True, 'ts': datetime.datetime(2017, 7, 10, 10, 0)},
        ],
        'enable_branding_co_branding': [
            {'v': False, 'ts': datetime.datetime(2017, 7, 20, 10, 0)},
            {'v': True, 'ts': datetime.datetime(2017, 7, 10, 10, 0)},
        ],
        'franchise_zones': [{
            'ts': datetime.datetime(2017, 7, 20, 10, 0),
            'v': ['moscow', 'spb'],
        }],
        'automate_marketing_payments': True,
        'pay_donations_without_offer': True,
        'account': {
            'threshold': -5000.0,
            'additional_compensation_by_card': 230.0,
            'additional_compensation_by_cash': 120.0,
        },
        'childchair_rents': [
            [
                datetime.datetime(2017, 7, 10, 10, 0),
                None,
                {'active': True, 'rental_rate': 10},
            ],
        ],
        'billing_client_ids': [
            [
                datetime.datetime(2017, 7, 10, 10, 0),
                None,
                '1234567',
            ],
        ],
        '_id': 'test_put_audit_fields_1',
        'city': 'Москва',
        '_type': 'taxipark',
        'apikey': 'random1234',
        'name': 'Лещ',
        'phone': '+79261234567',
        'marketing_agreement': True,
        'enable_grade_for_lightbox': False,
        'enable_grade_for_full_branding': True,
        'enable_grade_for_sticker': True,
        'takes_urgent': True,
        'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
        'yandex_login': 'boba_fett',
        'email': 'boba_fett@yandex.ru',
        'billing_email': 'boba_fett@yandex.ru',
        'created': datetime.datetime(2017, 7, 20, 10, 0),
        'updated': datetime.datetime(2017, 7, 20, 10, 0),
    },
),
(
    # Check that billing client ID is required to set creditcard
    {
        'id': 'test_put_audit_fields_2',
        'fields': {
            'creditcard': True,
            'coupon': False,
            'enable_branding_sticker': True,
            'enable_branding_lightbox': False,
            'enable_branding_co_branding': False,
            'franchise_zones': ['moscow', 'spb'],
            'automate_marketing_payments': True,
            'pay_donations_without_offer': True,
            'additional_compensation_by_card': 230,
            'additional_compensation_by_cash': 120,
            'city': 'Москва',
            'type': 'taxipark',
            'name': 'Лещ',
            'phone': '+7 (926) 123-45-67',
            'marketing_agreement': True,
            'enable_grade_for_lightbox': False,
            'enable_grade_for_full_branding': True,
            'enable_grade_for_sticker': True,
            'takes_urgent': True,
            'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
            'email': 'boba_fett@yandex.ru',
            'billing_email': 'boba_fett@yandex.ru',
            'yandex_login': 'boba_fett',
            'balance_threshold': -5000.0,
        },
    },
    400,
    None,
),
(
    # Check that we can set creditcard with billing client ID
    {
        'id': 'test_put_audit_fields_2',
        'fields': {
            'creditcard': True,
            'coupon': False,
            'enable_branding_sticker': True,
            'enable_branding_lightbox': False,
            'enable_branding_co_branding': False,
            'franchise_zones': ['moscow', 'spb'],
            'automate_marketing_payments': True,
            'pay_donations_without_offer': True,
            'additional_compensation_by_card': 230,
            'additional_compensation_by_cash': 120,
            'billing_client_id': {
                'client_id': '123456',
                'start_date': '2017-07-21T10:00:00.000000+0000',
            },
            'city': 'Москва',
            'type': 'taxipark',
            'name': 'Лещ',
            'phone': '+7 (926) 123-45-67',
            'marketing_agreement': True,
            'enable_grade_for_lightbox': False,
            'enable_grade_for_full_branding': True,
            'enable_grade_for_sticker': True,
            'takes_urgent': True,
            'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
            'email': 'boba_fett@yandex.ru',
            'billing_email': 'boba_fett@yandex.ru',
            'yandex_login': 'boba_fett',
            'balance_threshold': -5000.0,
        },
    },
    200,
    {
        'requirements': {
            'creditcard': True,
            'animaltransport': True,
        },
        'enable_branding_sticker': [{
            'v': True, 'ts': datetime.datetime(2017, 7, 20, 10, 0)
        }],
        'enable_branding_lightbox': [
            {'v': False, 'ts': datetime.datetime(2017, 7, 20, 10, 0)},
            {'v': True, 'ts': datetime.datetime(2017, 7, 10, 10, 0)},
        ],
        'enable_branding_co_branding': [
            {'v': False, 'ts': datetime.datetime(2017, 7, 20, 10, 0)},
            {'v': True, 'ts': datetime.datetime(2017, 7, 10, 10, 0)},
        ],
        'franchise_zones': [{
            'ts': datetime.datetime(2017, 7, 20, 10, 0),
            'v': ['moscow', 'spb'],
        }],
        'automate_marketing_payments': True,
        'pay_donations_without_offer': True,
        'account': {
            'threshold': -5000.0,
            'additional_compensation_by_card': 230.0,
            'additional_compensation_by_cash': 120.0,
        },
        'childchair_rents': [
            [
                datetime.datetime(2017, 7, 10, 10, 0),
                None,
                {'active': True, 'rental_rate': 10},
            ],
        ],
        'billing_client_ids': [
            [datetime.datetime(2017, 7, 21, 10), None, '123456']
        ],
        'billing_cargo_product_ids': [
            [
                datetime.datetime(2017, 7, 21, 10, 0),
                None,
                {
                    'ride': 'test_put_audit_fields_2_123456_ride',
                    'tips': 'test_put_audit_fields_2_123456_tips',
                    'toll_road': 'test_put_audit_fields_2_123456_toll_road',
                },
            ],
        ],
        'billing_corp_product_ids': [
            [
                datetime.datetime(2017, 7, 21, 10, 0),
                None,
                {
                    'rebate': 'test_put_audit_fields_2_123456_rebate',
                    'ride': 'test_put_audit_fields_2_123456_ride',
                    'tips': 'test_put_audit_fields_2_123456_tips',
                    'toll_road': 'test_put_audit_fields_2_123456_toll_road',
                },
            ],
        ],
        'billing_donate_product_ids': [
            [
                datetime.datetime(2017, 7, 21, 10, 0),
                None,
                {
                    'promocode': (
                        'test_put_audit_fields_2_123456_promocode'
                    ),
                    'subvention': (
                        'test_put_audit_fields_2_123456_subvention'
                    ),
                }
            ],
        ],
        'billing_product_ids': [
            [
                datetime.datetime(2017, 7, 21, 10, 0),
                None,
                {
                    'ride': 'test_put_audit_fields_2_123456_ride',
                    'tips': 'test_put_audit_fields_2_123456_tips',
                    'toll_road': 'test_put_audit_fields_2_123456_toll_road',
                },
            ],
        ],
        'billing_uber_product_ids': [
            [
                datetime.datetime(2017, 7, 21, 10, 0),
                None,
                {
                    'ride': 'test_put_audit_fields_2_123456_ride',
                    'tips': 'test_put_audit_fields_2_123456_tips',
                    'toll_road': 'test_put_audit_fields_2_123456_toll_road',
                },
            ]
        ],
        'billing_uber_roaming_product_ids': [
            [
                datetime.datetime(2017, 7, 21, 10, 0),
                None,
                {
                    'ride': 'test_put_audit_fields_2_123456_ride',
                    'tips': 'test_put_audit_fields_2_123456_tips',
                    'toll_road': 'test_put_audit_fields_2_123456_toll_road',
                },
            ]
        ],
        'billing_vezet_product_ids': [
            [
                datetime.datetime(2017, 7, 21, 10, 0),
                None,
                {
                    'ride': 'test_put_audit_fields_2_123456_ride',
                    'tips': 'test_put_audit_fields_2_123456_tips',
                    'toll_road': 'test_put_audit_fields_2_123456_toll_road',
                },
            ],
        ],
        '_id': 'test_put_audit_fields_2',
        'city': 'Москва',
        '_type': 'taxipark',
        'apikey': 'random1234',
        'name': 'Лещ',
        'phone': '+79261234567',
        'marketing_agreement': True,
        'enable_grade_for_lightbox': False,
        'enable_grade_for_full_branding': True,
        'enable_grade_for_sticker': True,
        'takes_urgent': True,
        'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
        'yandex_login': 'boba_fett',
        'email': 'boba_fett@yandex.ru',
        'billing_email': 'boba_fett@yandex.ru',
        'created': datetime.datetime(2017, 7, 20, 10, 0),
        'updated': datetime.datetime(2017, 7, 20, 10, 0),
    },
),
(
    # Check that billing client ID is NOT required to set coupon
    {
        'id': 'test_put_audit_fields_2',
        'ticket': 'TAXIRATE-2020',
        'fields': {
            'creditcard': False,
            'coupon': True,
            'enable_branding_sticker': True,
            'enable_branding_lightbox': False,
            'enable_branding_co_branding': False,
            'franchise_zones': ['moscow', 'spb'],
            'automate_marketing_payments': True,
            'pay_donations_without_offer': True,
            'additional_compensation_by_card': 230,
            'additional_compensation_by_cash': 120,
            'city': 'Москва',
            'type': 'taxipark',
            'name': 'Лещ',
            'phone': '+7 (926) 123-45-67',
            'marketing_agreement': True,
            'enable_grade_for_lightbox': False,
            'enable_grade_for_full_branding': True,
            'enable_grade_for_sticker': True,
            'takes_urgent': True,
            'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
            'email': 'boba_fett@yandex.ru',
            'billing_email': 'boba_fett@yandex.ru',
            'yandex_login': 'boba_fett',
            'balance_threshold': -5000.0,
            'account_offer_confirmed': '2017-07-21T20:00:00+0000',
        },
    },
    200,
    {
        'requirements': {'coupon': True, 'animaltransport': True},
        'enable_branding_sticker': [{
            'v': True, 'ts': datetime.datetime(2017, 7, 20, 10, 0)
        }],
        'enable_branding_lightbox': [
            {'v': False, 'ts': datetime.datetime(2017, 7, 20, 10, 0)},
            {'v': True, 'ts': datetime.datetime(2017, 7, 10, 10, 0)},
        ],
        'enable_branding_co_branding': [
            {'v': False, 'ts': datetime.datetime(2017, 7, 20, 10, 0)},
            {'v': True, 'ts': datetime.datetime(2017, 7, 10, 10, 0)},
        ],
        'franchise_zones': [{
            'ts': datetime.datetime(2017, 7, 20, 10, 0),
            'v': ['moscow', 'spb'],
        }],
        'automate_marketing_payments': True,
        'pay_donations_without_offer': True,
        'account': {
            'threshold': -5000.0,
            'additional_compensation_by_card': 230.0,
            'additional_compensation_by_cash': 120.0,
            'details': {
                'confirmed': datetime.datetime(2017, 7, 21, 20, 0)
            },
            'offer_confirmed': datetime.datetime(2017, 7, 21, 20, 0),
        },
        'childchair_rents': [
            [
                datetime.datetime(2017, 7, 10, 10, 0),
                None,
                {'active': True, 'rental_rate': 10},
            ],
        ],
        'billing_client_ids': [],
        'billing_cargo_product_ids': [],
        'billing_corp_product_ids': [],
        'billing_donate_product_ids': [],
        'billing_product_ids': [],
        'billing_uber_product_ids': [],
        'billing_uber_roaming_product_ids': [],
        'billing_vezet_product_ids': [],
        '_id': 'test_put_audit_fields_2',
        'city': 'Москва',
        '_type': 'taxipark',
        'apikey': 'random1234',
        'name': 'Лещ',
        'phone': '+79261234567',
        'marketing_agreement': True,
        'enable_grade_for_lightbox': False,
        'enable_grade_for_full_branding': True,
        'enable_grade_for_sticker': True,
        'takes_urgent': True,
        'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
        'yandex_login': 'boba_fett',
        'email': 'boba_fett@yandex.ru',
        'billing_email': 'boba_fett@yandex.ru',
        'created': datetime.datetime(2017, 7, 20, 10, 0),
        'updated': datetime.datetime(2017, 7, 20, 10, 0),
    },
),
(
    # Check negative additional_compensation_by_card
    {
        'id': 'test_put_audit_fields_1',
        'fields': {
            'creditcard': True,
            'coupon': False,
            'enable_branding_sticker': True,
            'enable_branding_lightbox': False,
            'enable_branding_co_branding': False,
            'franchise_zones': ['moscow', 'spb'],
            'automate_marketing_payments': True,
            'pay_donations_without_offer': True,
            'additional_compensation_by_card': -100,
            'additional_compensation_by_cash': 120,
            'city': 'Москва',
            'type': 'taxipark',
            'name': 'Лещ',
            'phone': '+7 (926) 123-45-67',
            'marketing_agreement': True,
            'enable_grade_for_lightbox': False,
            'enable_grade_for_full_branding': True,
            'enable_grade_for_sticker': True,
            'takes_urgent': True,
            'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
            'email': 'boba_fett@yandex.ru',
            'billing_email': 'boba_fett@yandex.ru',
            'balance_threshold': -5000.0
        },
    },
    400,
    None,
),
]


@pytest.mark.now('2017-07-20T10:00:00.0')
@pytest.mark.parametrize(
    'request_data,expected_code,expected_db_contents',
    COMMON_PARK_DATA,
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(PARKS_ENABLE_TOLL_ROAD_PRODUCT_CREATION=True)
@pytest.inline_callbacks
def test_put_common_fields(billing_create_partner_mock,
                           billing_create_product_mock,
                           request_data, expected_code, expected_db_contents):
    response = django_test.Client().put(
        '/api/park/common_fields/',
        json.dumps(request_data),
        'application/json',
    )
    assert response.status_code == expected_code, response.content
    if expected_db_contents is not None:
        park = yield db.parks.find_one({'_id': request_data['id']})
        for key in expected_db_contents:
            if key != 'updated_ts':
                assert park[key] == expected_db_contents[key]
        for key in park:
            if key != 'updated_ts':
                assert park[key] == expected_db_contents[key]


@pytest.mark.asyncenv('blocking')
def test_invalid_decreasce_balance(billing_create_partner_mock,
                           billing_create_product_mock):
    request_data = {
        'id': 'test_put_common_fields_2',
        'fields': {
            'city': 'Москва',
            'type': 'taxipark',
            'name': 'Лещ',
            'phone': '+7 (926) 123-45-67',
            'marketing_agreement': True,
            'enable_grade_for_lightbox': False,
            'enable_grade_for_full_branding': True,
            'enable_grade_for_sticker': True,
            'takes_urgent': True,
            'email': 'darth-vader@yandex.ru',
            'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
            'creditcard': False,
            'coupon': False,
            'enable_branding_sticker': False,
            'enable_branding_lightbox': False,
            'enable_branding_co_branding': False,
            'franchise_zones': ['moscow', 'spb'],
            'automate_marketing_payments': True,
            'pay_donations_without_offer': True,
            'additional_compensation_by_card': 230,
            'additional_compensation_by_cash': 120,
            'balance_threshold': -6000.0
        },
    }

    response = django_test.Client().put(
        '/api/park/common_fields/',
        json.dumps(request_data),
        'application/json',
    )
    assert response.status_code == 400, response.content


@pytest.mark.now('2017-07-20T10:00:00.0')
@pytest.mark.parametrize(
    'request_data,expected_code,expected_db_contents',
    COMMON_PARK_DATA,
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(PARKS_ENABLE_TOLL_ROAD_PRODUCT_CREATION=True)
@pytest.inline_callbacks
def test_put_common_fields_approved(billing_create_partner_mock,
                           billing_create_product_mock,
                           request_data, expected_code, expected_db_contents):
    response = django_test.Client().post(
        '/api/approvals/park_common_fields_edit/apply/',
        json.dumps(request_data),
        'application/json',
        HTTP_X_YANDEX_LOGIN='spriymenko',
    )
    assert response.status_code == expected_code, response.content
    if expected_db_contents is not None:
        park = yield db.parks.find_one({'_id': request_data['id']})
        for key in expected_db_contents:
            if key != 'updated_ts':
                assert park[key] == expected_db_contents[key]
        for key in park:
            if key != 'updated_ts':
                assert park[key] == expected_db_contents[key]


@pytest.mark.now('2017-07-20T10:00:00.0')
@pytest.mark.parametrize(
    'request_data,expected_code,expected_db_contents',
    [
        (
            {
                'id': 'test_put_audit_fields_1',
                'ticket': 'TAXIRATE-2020',
                'fields': {
                    'promised_payment': {
                        'enabled': True,
                        'end_date': '2017-07-22T11:00:00.000000+0000'
                    },
                    'childchair_rent': {'enabled': False},
                }
            },
            200,
            {
                'requirements': {
                    'coupon': True,
                    'animaltransport': True,
                    'corp': True
                },
                'enable_branding_sticker': [],
                'enable_branding_lightbox': [
                    {'v': True, 'ts': datetime.datetime(2017, 7, 10, 10, 0)},
                ],
                'enable_branding_co_branding': [
                    {'v': True, 'ts': datetime.datetime(2017, 7, 10, 10, 0)},
                ],
                'franchise_zones': [],
                'automate_marketing_payments': False,
                'account': {
                    'promised_payment_till': datetime.datetime(2017, 7, 22, 11),
                    'threshold': -5000.0
                },
                'childchair_rents': [
                    [
                        datetime.datetime(2017, 7, 10, 10, 0),
                        datetime.datetime(2017, 7, 20, 10, 5),
                        {'active': True, 'rental_rate': 10},
                    ],
                    [
                        datetime.datetime(2017, 7, 20, 10, 5),
                        None,
                        {'active': False, 'rental_rate': 0},
                    ],
                ],
                'billing_client_ids': [
                    [
                        datetime.datetime(2017, 7, 10, 10, 0),
                        None,
                        '1234567',
                    ],
                ],
                '_id': 'test_put_audit_fields_1',
                'city': 'Москва',
                '_type': 'taxipark',
                'apikey': 'random1234',
                'name': 'Лещ',
                'phone': '+79261234567',
                'marketing_agreement': True,
                'enable_grade_for_lightbox': False,
                'enable_grade_for_full_branding': True,
                'enable_grade_for_sticker': True,
                'takes_urgent': True,
                'host': (
                    'https://taximeter-xservice.yandex.net/xservice/yandex'
                ),
                'yandex_login': 'boba_fett',
                'email': 'boba_fett@yandex.ru',
                'billing_email': 'boba_fett@yandex.ru',
                'created': datetime.datetime(2017, 7, 20, 10, 0),
                'updated': datetime.datetime(2017, 7, 20, 10, 0),
            }
        ),
        (
            # Check that promised payment must not end too late
            {
                'id': 'test_put_audit_fields_1',
                'ticket': 'TAXIRATE-2020',
                'fields': {
                    'promised_payment': {
                        'enabled': True,
                        'end_date': '2017-08-22T11:00:00.000000+0000'
                    },
                    'childchair_rent': {'enabled': False}
                }
            },
            400,
            None,
        ),
        (
            {
                'id': 'test_put_audit_fields_3',
                'ticket': 'TAXIRATE-2020',
                'fields': {
                    'promised_payment': {'enabled': False},
                    'childchair_rent': {'enabled': True, 'rate': 20}
                }
            },
            200,
            {
                'requirements': {
                    'animaltransport': True,
                    'corp': True,
                    'coupon': True,
                    'creditcard': True
                },
                'enable_branding_sticker': [],
                'enable_branding_lightbox': [
                    {'v': False, 'ts': datetime.datetime(2017, 7, 10, 10, 0)},
                ],
                'enable_branding_co_branding': [
                    {'v': True, 'ts': datetime.datetime(2017, 7, 10, 10, 0)},
                ],
                'franchise_zones': [
                    {
                        'v': ['moscow', 'spb'],
                        'ts': datetime.datetime(2017, 7, 10, 10, 0),
                    },
                ],
                'automate_marketing_payments': True,
                'account': {
                    'threshold': -5000.0,
                    'additional_compensation_by_card': 200.0,
                    'additional_compensation_by_cash': 400.0,
                },
                'childchair_rents': [
                    [
                        datetime.datetime(2017, 7, 10, 10, 0),
                        datetime.datetime(2017, 7, 20, 10, 5),
                        {'active': True, 'rental_rate': 10},
                    ],
                    [
                        datetime.datetime(2017, 7, 20, 10, 5),
                        None,
                        {'active': True, 'rental_rate': 20},
                    ]
                ],
                'billing_client_ids': [],
                '_id': 'test_put_audit_fields_3',
                'city': 'Москва',
                '_type': 'taxipark',
                'apikey': 'random1234',
                'name': 'Лещ',
                'phone': '+79261234567',
                'marketing_agreement': True,
                'enable_grade_for_lightbox': False,
                'enable_grade_for_full_branding': True,
                'enable_grade_for_sticker': True,
                'takes_urgent': True,
                'host': (
                    'https://taximeter-xservice.yandex.net/xservice/yandex'
                ),
                'yandex_login': 'boba_fett',
                'email': 'boba_fett@yandex.ru',
                'billing_email': 'boba_fett@yandex.ru',
                'created': datetime.datetime(2017, 7, 20, 10, 0),
                'updated': datetime.datetime(2017, 7, 20, 10, 0),
            }
        ),
    ],
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_put_audit_fields(ticket_check_is_successful,
                          request_data, expected_code, expected_db_contents):
    response = django_test.Client().put(
        '/api/park/audit_fields/',
        json.dumps(request_data),
        'application/json',
    )
    assert response.status_code == expected_code, response.content
    if expected_db_contents is not None:
        park = yield db.parks.find_one({'_id': request_data['id']})
        for key in expected_db_contents:
            if key != 'updated_ts':
                assert park[key] == expected_db_contents[key]
        for key in park:
            if key != 'updated_ts':
                assert park[key] == expected_db_contents[key]


@pytest.mark.now('2017-07-20T10:00:00.0')
@pytest.mark.config(PARKS_ENABLE_DEFAULT_CHILDCHAIR_RENTS=True)
@pytest.mark.config(ADMIN_USE_TRESHOLD_LIMIT=True)
@pytest.mark.parametrize(
    'request_data,expected_code,expected_db_contents',
    [
        (
            {
                'common_fields': {
                    'city': 'Москва',
                    'type': 'taxipark',
                    'name': 'Шум осин',
                    'phone': '+79261234567',
                    'marketing_agreement': True,
                    'enable_grade_for_lightbox': False,
                    'enable_grade_for_full_branding': False,
                    'enable_grade_for_sticker': False,
                    'takes_urgent': True,
                    'host': (
                        'https://taximeter-xservice.yandex.net/xservice/yandex'
                    ),
                    'yandex_login': 'valentin',
                    'email': 'valentin@yandex.ru',
                    'additional_compensation_by_card': 0,
                    'additional_compensation_by_cash': 0,
                    'billing_client_id': {
                        'client_id': '81789894',
                        'start_date': '2017-07-21T20:00:00.000000+0000',
                    },
                    'creditcard': True,
                    'coupon': True,
                    'enable_branding_sticker': False,
                    'enable_branding_lightbox': False,
                    'enable_branding_co_branding': False,
                    'franchise_zones': [],
                    'automate_marketing_payments': True,
                    'pay_donations_without_offer': False,
                    'balance_threshold': -5000.0
                },
                'audit_fields': {
                        "promised_payment": {'enabled': False},
                        "childchair_rent": {'enabled': True, 'rate': 10},
                },
            },
            200,
            {
                '_id': '1',
                'automate_marketing_payments': True,
                'marketing_agreement': True,
                '_type': 'taxipark',
                'city': 'Москва',
                'requirements': {'coupon': True, 'creditcard': True},
                'enable_branding_sticker': [],
                'enable_branding_lightbox': [],
                'enable_branding_co_branding': [],
                'franchise_zones': [],
                'billing_corp_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'ride': '1_81789894_ride',
                            'tips': '1_81789894_tips',
                            'rebate': '1_81789894_rebate',
                            'toll_road': '1_81789894_toll_road'
                        }
                    ]
                ],
                'billing_cargo_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'ride': '1_81789894_ride',
                            'tips': '1_81789894_tips',
                            'toll_road': '1_81789894_toll_road'
                        }
                    ]
                ],
                'billing_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'ride': '1_81789894_ride',
                            'tips': '1_81789894_tips',
                            'toll_road': '1_81789894_toll_road'
                        }
                    ]
                ],
                'email': 'valentin@yandex.ru',
                'updated': datetime.datetime(2017, 7, 20, 10),
                'billing_uber_roaming_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'ride': '1_81789894_ride',
                            'tips': '1_81789894_tips',
                            'toll_road': '1_81789894_toll_road'
                        }
                    ]
                ],
                'billing_vezet_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'ride': '1_81789894_ride',
                            'tips': '1_81789894_tips',
                            'toll_road': '1_81789894_toll_road'
                        }
                    ]
                ],
                'billing_donate_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'subvention': '1_81789894_subvention',
                            'promocode': '1_81789894_promocode'
                        }
                    ]
                ],
                'phone': '+79261234567',
                'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
                'takes_urgent': True,
                'billing_uber_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'ride': '1_81789894_ride',
                            'tips': '1_81789894_tips',
                            'toll_road': '1_81789894_toll_road'
                        }
                    ]
                ],
                'yandex_login': 'valentin',
                'account': {
                    'threshold': -5000.0,
                    'additional_compensation_by_card': 0,
                    'additional_compensation_by_cash': 0,
                },
                'apikey': 'randomuuid1234',
                'name': 'Шум осин',
                'created': datetime.datetime(2017, 7, 20, 10),
                'billing_client_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        '81789894'
                    ]
                ],
                'childchair_rents': [
                    [
                        datetime.datetime(2017, 7, 20, 10, 5),
                        None,
                        {'active': True, 'rental_rate': 10},
                    ],
                ],
                'enable_grade_for_lightbox': False,
                'enable_grade_for_full_branding': False,
                'enable_grade_for_sticker': False,
                'pay_donations_without_offer': False,
            }
        ),
        # check set empty dict in requirements
        # if not provided any requirements fields
        (
            {
                'common_fields': {
                    'city': 'Москва',
                    'type': 'taxipark',
                    'name': 'Шум осин',
                    'phone': '+79261234567',
                    'marketing_agreement': True,
                    'enable_grade_for_lightbox': False,
                    'enable_grade_for_full_branding': False,
                    'enable_grade_for_sticker': False,
                    'takes_urgent': True,
                    'host': (
                        'https://taximeter-xservice.yandex.net/xservice/yandex'
                    ),
                    'yandex_login': 'valentin',
                    'email': 'valentin@yandex.ru',
                    'additional_compensation_by_card': 0,
                    'additional_compensation_by_cash': 0,
                    'billing_client_id': {
                        'client_id': '81789894',
                        'start_date': '2017-07-21T20:00:00.000000+0000',
                    },
                    'creditcard': False,
                    'coupon': False,
                    'enable_branding_sticker': False,
                    'enable_branding_lightbox': False,
                    'enable_branding_co_branding': False,
                    'franchise_zones': [],
                    'automate_marketing_payments': True,
                    'pay_donations_without_offer': False,
                    'balance_threshold': -5000.0,
                    'account_offer_confirmed': '2017-07-21T20:00:00+0000',
                },
                'audit_fields': {
                        "promised_payment": {'enabled': False},
                        "childchair_rent": {'enabled': True, 'rate': 10},
                },
            },
            200,
            {
                '_id': '1',
                'automate_marketing_payments': True,
                'marketing_agreement': True,
                '_type': 'taxipark',
                'city': 'Москва',
                'requirements': {},
                'enable_branding_sticker': [],
                'enable_branding_lightbox': [],
                'enable_branding_co_branding': [],
                'franchise_zones': [],
                'billing_corp_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'ride': '1_81789894_ride',
                            'tips': '1_81789894_tips',
                            'rebate': '1_81789894_rebate',
                            'toll_road': '1_81789894_toll_road'
                        }
                    ]
                ],
                'billing_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'ride': '1_81789894_ride',
                            'tips': '1_81789894_tips',
                            'toll_road': '1_81789894_toll_road'
                        }
                    ]
                ],
                'email': 'valentin@yandex.ru',
                'updated': datetime.datetime(2017, 7, 20, 10),
                'billing_uber_roaming_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'ride': '1_81789894_ride',
                            'tips': '1_81789894_tips',
                            'toll_road': '1_81789894_toll_road'
                        }
                    ]
                ],
                'billing_vezet_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'ride': '1_81789894_ride',
                            'tips': '1_81789894_tips',
                            'toll_road': '1_81789894_toll_road'
                        }
                    ]
                ],
                'billing_cargo_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'ride': '1_81789894_ride',
                            'tips': '1_81789894_tips',
                            'toll_road': '1_81789894_toll_road'
                        }
                    ]
                ],
                'billing_donate_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'subvention': '1_81789894_subvention',
                            'promocode': '1_81789894_promocode'
                        }
                    ]
                ],
                'phone': '+79261234567',
                'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
                'takes_urgent': True,
                'billing_uber_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'ride': '1_81789894_ride',
                            'tips': '1_81789894_tips',
                            'toll_road': '1_81789894_toll_road'
                        }
                    ]
                ],
                'yandex_login': 'valentin',
                'account': {
                    'threshold': -5000.0,
                    'additional_compensation_by_card': 0,
                    'additional_compensation_by_cash': 0,
                    'contracts': [{
                        'acquiring_percent': None,
                        'begin': datetime.datetime(1, 1, 1, 0, 0),
                        'currency': 'RUB',
                        'end': datetime.datetime(
                            9999, 12, 31, 23, 59, 59, 999000
                        ),
                        'external_id': None,
                        'id': 100500,
                        'ind_bel_nds_percent': None,
                        'is_cancelled': False,
                        'is_deactivated': False,
                        'is_faxed': False,
                        'is_active': False,
                        'is_of_card': False,
                        'is_of_cash': False,
                        'is_of_corp': True,
                        'is_of_uber': False,
                        'is_prepaid': True,
                        'is_signed': False,
                        'is_suspended': False,
                        'link_contract_id': None,
                        'nds_for_receipt': None,
                        'netting': False,
                        'netting_pct': None,
                        'offer_accepted': True,
                        'person_id': 'None',
                        'rebate_percent': None,
                        'services': [135],
                        'type': None,
                        'vat': None
                    }],
                    'details': {
                        'confirmed': datetime.datetime(2017, 7, 21, 20, 0)
                    },
                    'offer_confirmed': datetime.datetime(2017, 7, 21, 20, 0)
                },
                'apikey': 'randomuuid1234',
                'name': 'Шум осин',
                'created': datetime.datetime(2017, 7, 20, 10),
                'billing_client_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        '81789894'
                    ]
                ],
                'childchair_rents': [
                    [
                        datetime.datetime(2017, 7, 20, 10, 5),
                        None,
                        {'active': True, 'rental_rate': 10},
                    ],
                ],
                'enable_grade_for_lightbox': False,
                'enable_grade_for_full_branding': False,
                'enable_grade_for_sticker': False,
                'pay_donations_without_offer': False,
            }
        ),
        (
            {
                'common_fields': {
                    'city': 'Москва',
                    'type': 'taxipark',
                    'name': 'Шум осин',
                    'phone': '+79261234567',
                    'marketing_agreement': True,
                    'enable_grade_for_lightbox': False,
                    'enable_grade_for_full_branding': False,
                    'enable_grade_for_sticker': False,
                    'takes_urgent': True,
                    'host': (
                        'https://taximeter-xservice.yandex.net/xservice/yandex'
                    ),
                    'yandex_login': 'valentin',
                    'email': 'valentin@yandex.ru',
                    'additional_compensation_by_card': 0,
                    'additional_compensation_by_cash': 0,
                    'billing_client_id': {
                        'client_id': '81789894',
                        'start_date': '2017-07-21T20:00:00.000000+0000',
                    },
                    'creditcard': False,
                    'coupon': False,
                    'enable_branding_sticker': False,
                    'enable_branding_lightbox': False,
                    'enable_branding_co_branding': False,
                    'franchise_zones': [],
                    'automate_marketing_payments': True,
                    'pay_donations_without_offer': False,
                    'balance_threshold': -5000.0,
                    'account_offer_confirmed': '2017-07-21T20:00:00+0000',
                },
                'audit_fields': {
                        "promised_payment": {'enabled': False},
                        "childchair_rent": {'enabled': True, 'rate': 9},
                },
                'ticket': 'TAXIRATE-20'
            },
            200,
            {
                '_id': '1',
                'automate_marketing_payments': True,
                'marketing_agreement': True,
                '_type': 'taxipark',
                'city': 'Москва',
                'requirements': {},
                'enable_branding_sticker': [],
                'enable_branding_lightbox': [],
                'enable_branding_co_branding': [],
                'franchise_zones': [],
                'billing_corp_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'ride': '1_81789894_ride',
                            'tips': '1_81789894_tips',
                            'rebate': '1_81789894_rebate',
                            'toll_road': '1_81789894_toll_road'
                        }
                    ]
                ],
                'billing_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'ride': '1_81789894_ride',
                            'tips': '1_81789894_tips',
                            'toll_road': '1_81789894_toll_road'
                        }
                    ]
                ],
                'email': 'valentin@yandex.ru',
                'updated': datetime.datetime(2017, 7, 20, 10),
                'billing_cargo_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'ride': '1_81789894_ride',
                            'tips': '1_81789894_tips',
                            'toll_road': '1_81789894_toll_road'
                        }
                    ]
                ],
                'billing_uber_roaming_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'ride': '1_81789894_ride',
                            'tips': '1_81789894_tips',
                            'toll_road': '1_81789894_toll_road'
                        }
                    ]
                ],
                'billing_vezet_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'ride': '1_81789894_ride',
                            'tips': '1_81789894_tips',
                            'toll_road': '1_81789894_toll_road'
                        }
                    ]
                ],
                'billing_donate_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'subvention': '1_81789894_subvention',
                            'promocode': '1_81789894_promocode'
                        }
                    ]
                ],
                'phone': '+79261234567',
                'host': 'https://taximeter-xservice.yandex.net/xservice/yandex',
                'takes_urgent': True,
                'billing_uber_product_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        {
                            'ride': '1_81789894_ride',
                            'tips': '1_81789894_tips',
                            'toll_road': '1_81789894_toll_road'
                        }
                    ]
                ],
                'yandex_login': 'valentin',
                'account': {
                    'threshold': -5000.0,
                    'additional_compensation_by_card': 0,
                    'additional_compensation_by_cash': 0,
                    'contracts': [{
                        'acquiring_percent': None,
                        'begin': datetime.datetime(1, 1, 1, 0, 0),
                        'currency': 'RUB',
                        'end': datetime.datetime(
                            9999, 12, 31, 23, 59, 59, 999000
                        ),
                        'external_id': None,
                        'id': 100500,
                        'ind_bel_nds_percent': None,
                        'is_active': False,
                        'is_cancelled': False,
                        'is_deactivated': False,
                        'is_faxed': False,
                        'is_of_card': False,
                        'is_of_cash': False,
                        'is_of_corp': True,
                        'is_of_uber': False,
                        'is_prepaid': True,
                        'is_signed': False,
                        'is_suspended': False,
                        'link_contract_id': None,
                        'nds_for_receipt': None,
                        'netting': False,
                        'netting_pct': None,
                        'offer_accepted': True,
                        'person_id': 'None',
                        'rebate_percent': None,
                        'services': [135],
                        'type': None,
                        'vat': None
                    }],
                    'details': {
                        'confirmed': datetime.datetime(2017, 7, 21, 20, 0)
                    },
                    'offer_confirmed': datetime.datetime(2017, 7, 21, 20, 0)
                },
                'apikey': 'randomuuid1234',
                'name': 'Шум осин',
                'created': datetime.datetime(2017, 7, 20, 10),
                'billing_client_ids': [
                    [
                        datetime.datetime(2017, 7, 21, 20),
                        None,
                        '81789894'
                    ]
                ],
                'childchair_rents': [
                    [
                        datetime.datetime(2017, 7, 20, 10, 5),
                        None,
                        {'active': True, 'rental_rate': 9},
                    ],
                ],
                'enable_grade_for_lightbox': False,
                'enable_grade_for_full_branding': False,
                'enable_grade_for_sticker': False,
                'pay_donations_without_offer': False,
            }
        ),
        # check invalid personal data
        (
            {
                'common_fields': {
                    'city': 'Москва',
                    'type': 'taxipark',
                    'name': 'Шум осин',
                    'phone': '+79261234567',
                    'marketing_agreement': True,
                    'enable_grade_for_lightbox': False,
                    'enable_grade_for_full_branding': False,
                    'enable_grade_for_sticker': False,
                    'takes_urgent': True,
                    'host': (
                        'https://taximeter-xservice.yandex.net/xservice/yandex'
                    ),
                    'yandex_login': 'valentin',
                    'email': 'valentin@@yandex.ru',
                    'additional_compensation_by_card': 0,
                    'additional_compensation_by_cash': 0,
                    'billing_client_id': {
                        'client_id': '81789894',
                        'start_date': '2017-07-21T20:00:00.000000+0000',
                    },
                    'creditcard': True,
                    'coupon': True,
                    'enable_branding_sticker': False,
                    'enable_branding_lightbox': False,
                    'enable_branding_co_branding': False,
                    'franchise_zones': [],
                    'automate_marketing_payments': True,
                    'pay_donations_without_offer': False,
                    'balance_threshold': -5000.0
                },
                'audit_fields': {
                        "promised_payment": {'enabled': False},
                        "childchair_rent": {'enabled': True, 'rate': 10},
                },
            },
            400,
            {
                'status': 'error',
                'message': 'api-over-data : can not retrieve personal data '
                    'for consumer taxiadmin_api_views_parks can not get '
                    'email_pd_id for park with clid 1',
                'code': 'general',
            }
        ),
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(PARKS_ENABLE_TOLL_ROAD_PRODUCT_CREATION=True)
@pytest.inline_callbacks
def test_create_park(patch,
                     billing_create_partner_mock,
                     billing_create_product_mock,
                     request_data, expected_code, expected_db_contents,
                     taxirate_check_is_successful):
    @patch('uuid.uuid4')
    def uuid_stub():
        class Hex(object):
            hex = 'randomuuid1234'
        return Hex

    @patch('taxi.external.billing.get_client_contracts')
    @async.inline_callbacks
    def get_client_contracts(billing_client_id, dt=None, contract_kind=None,
                             contract_signed=True, log_extra=None):
        yield
        async.return_value([
            {
                'IS_ACTIVE': 1,
                'CURRENCY': 'RUR',
                'SERVICES': [135],
                'ID': 100500,
                'PAYMENT_TYPE': 2
            }
        ])

    if expected_code == 400:
        @patch('taxi.internal.personal.get_taxi_parks_personal_data_write_mode')
        @async.inline_callbacks
        def mock_personal_write(consumer):
            yield
            async.return_value('both_no_fallback')

        @patch('taxi.internal.personal.get_pd_id')
        @async.inline_callbacks
        def mock_personal_get(raw_data, personal_type, personal_consumer):
            if personal_type == 'emails':
                result = None
            else:
                result = 'test_data'
            yield
            async.return_value(result)

    response = django_test.Client().post(
        '/api/parks/create_park/',
        json.dumps(request_data),
        'application/json',
    )
    assert response.status_code == expected_code, response.content
    if expected_db_contents is not None:
        if response.status_code == 200:
            park = yield db.parks.find_one(
                {'_id': json.loads(response.content)['id']}
            )
            for key in expected_db_contents:
                if key != 'updated_ts':
                    assert park[key] == expected_db_contents[key]
            for key in park:
                if key != 'updated_ts':
                    assert park[key] == expected_db_contents[key]
        if response.status_code == 400:
            assert json.loads(response.content) == expected_db_contents


@pytest.mark.asyncenv('blocking')
def test_get_cities_list(load, patch):
    response = django_test.Client().get('/api/parks/cities/')
    assert response.status_code == 200
    response_content = response.content.decode('utf-8')
    response_data = json.loads(response_content)
    assert response_data['cities'] == [
        'test', 'test_city_1', 'test_city_2', 'Москва', 'Санкт-Петербург'
    ]
