# coding: utf-8

from __future__ import unicode_literals

import datetime
import json
from collections import namedtuple

from django import test as django_test
import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal import admin_restrictions
from taxi.internal import dbh
from taxi.util import evlog
from taxiadmin.api.views import tariff_settings

import helpers

DEFAULT_CONFIG = {
    admin_restrictions.COUNTRY_ACCESS_CONFIG_NAME: {
        'rus': {
            'logins': [
                'karachevda',
            ],
        },
    },
}


def _patch_internals(patch, config):

    @patch('taxi.external.experiments3.get_config_values')
    @async.inline_callbacks
    def _get_experiments(consumer, config_name, *args, **kwargs):
        yield
        if config_name in config:
            resp = [
                admin_restrictions.experiments3.ExperimentsValue(
                    config_name, config[config_name],
                ),
            ]
        else:
            resp = []
        async.return_value(resp)


@pytest.mark.load_data(countries='test')
@pytest.mark.asyncenv('blocking')
@pytest.mark.disable_territories_api_mock
@pytest.mark.config(ALL_CATEGORIES=['econom', 'vip'])
@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en'])
@pytest.mark.parametrize('request_tariff_type', ['econom', 'vip', 'pool'])
@pytest.mark.translations([
    ('tariff', 'name.econom', 'ru', 'Эконом'),
    ('tariff', 'name.econom', 'en', 'Economy'),
    ('tariff', 'name.vip', 'en', 'Business'),
    ('geoareas', 'moscow', 'ru', 'Москва'),
    ('geoareas', 'moscow', 'en', 'Moscow'),
    ('geoareas', 'rus', 'ru', 'Россия'),
    ('geoareas', 'rus', 'en', 'Russia'),
])
def test_using_wrong_tariff_category(request_tariff_type, patch, areq_request):
    @patch('taxi.internal.dbh.tariffs.Doc.find_active')
    @async.inline_callbacks
    def find_active(home_zone_name, due=None, park_id=None, fields=None):

        yield

    @patch('taxiadmin.tariff_checks.check_consistency')
    def check_consistency(tariff, tariff_settings):
        return

    @patch('uuid.uuid4')
    def uuid4():
        return namedtuple('uuid4', 'hex')('test-request-uuid')

    @areq_request
    def countries(*args, **kwargs):
        assert kwargs['headers']['X-YaRequestId'] == 'test-request-uuid'
        return areq_request.response(200, body=json.dumps({
            'countries': [{"_id": "rus", "vat": 11800}]
        }))

    response = django_test.Client().post(
        '/api/set_tariff_settings/moscow/', json.dumps(
        {
            'tz': 'Europe/Moscow',
            'city_id': 'Москва',
            'country': 'rus',
            'client_exact_order_round_minutes': 10,
            'layout': 'h',
            'payment_options': ['cash'],
            'for_wizard': True,
            'is_beta': False,
            'categories': [{
                'category_name': request_tariff_type,
                'tanker_key': 'name.{}'.format(request_tariff_type),
                'service_levels': [10],
                'is_default': True,
                'can_be_default': True,
                'client_constraints': [],
                'only_for_soon_orders': True,
                'legal_entities_enabled': True,
                'transfers_config': [],
                'persistent_requirements': [],
                'client_requirements': [],
            }],
            'show_onboarding': False,
            'paid_cancel_enabled': True,
            'ticket': 'TAXIRATE-0001',
        }),
        content_type='application/json')

    if request_tariff_type == 'econom':
        assert response.status_code == 200, response.content
    else:
        assert response.status_code == 400, response.content


@pytest.mark.load_data(countries='test')
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en'])
@pytest.mark.translations([
    ('tariff', 'name.econom', 'ru', 'Эконом'),
    ('tariff', 'name.econom', 'en', 'Economy'),
    ('tariff', 'name.vip', 'en', 'Business'),
    ('geoareas', 'some_home_zone', 'ru', 'КакаятоЗона'),
    ('geoareas', 'some_home_zone', 'en', 'SomeHomeZone'),
    ('geoareas', 'rus', 'ru', 'Россия'),
    ('geoareas', 'rus', 'en', 'Russia'),
])
@pytest.mark.parametrize('zone_cost', [
    None,
    {
        'step': 12.3456,
        'max_delta': 123.4567,
    },
])
@pytest.mark.parametrize('category_cost', [
    None,
    {
        'step': 22.3456,
        'max_delta': 223.4567,
    },
    {}
])
@pytest.inline_callbacks
def test_set_driver_change_cost(zone_cost, category_cost, patch):
    data = {
        'tz': 'Europe/Moscow',
        'city_id': 'Москва',
        'country': 'rus',
        'client_exact_order_round_minutes': 10,
        'layout': 'h',
        'payment_options': ['cash'],
        'for_wizard': True,
        'is_beta': False,
        'categories': [{
            'category_name': 'econom',
            'tanker_key': 'name.econom',
            'service_levels': [10],
            'is_default': True,
            'can_be_default': True,
            'client_constraints': [],
            'only_for_soon_orders': True,
            'legal_entities_enabled': True,
            'transfers_config': [],
            'persistent_requirements': [],
            'client_requirements': [],
        }],
        'show_onboarding': False,
        'paid_cancel_enabled': True,
        'ticket': 'TAXIRATE-0001',
    }
    if zone_cost:
        data['driver_change_cost'] = zone_cost
    if category_cost is not None:
        data['categories'][0]['driver_change_cost'] = category_cost

    response = django_test.Client().post(
        '/api/set_tariff_settings/some_home_zone/', json.dumps(data),
        content_type='application/json')

    assert response.status_code == 200, response.content

    response = django_test.Client().get('/api/tariff_settings/some_home_zone/')

    assert response.status_code == 200, response.content

    tariff_zone = json.loads(response.content)
    tariff_dbh = dbh.tariff_settings.Doc.find_by_home_zone('some_home_zone')
    tariff_db = yield db.tariff_settings.find_one({'hz': 'some_home_zone'})

    def _check_dict(cost_dict, exp_cost):
        assert 'driver_change_cost' in cost_dict
        assert cost_dict['driver_change_cost'] == exp_cost

    if zone_cost is not None:
        _check_dict(tariff_zone, zone_cost)
        _check_dict(tariff_db, zone_cost)
        _check_dict(tariff_dbh, zone_cost)

    if category_cost is not None:
        _check_dict(tariff_zone['categories'][0], category_cost)
        _check_dict(tariff_db['s'][0], category_cost)
        _check_dict(tariff_dbh.categories[0], category_cost)


@pytest.mark.load_data(countries='test')
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en'])
@pytest.mark.translations([
    ('tariff', 'name.econom', 'ru', 'Эконом'),
    ('tariff', 'name.econom', 'en', 'Economy'),
    ('tariff', 'name.vip', 'en', 'Business'),
    ('geoareas', 'some_home_zone', 'ru', 'КакаятоЗона'),
    ('geoareas', 'some_home_zone', 'en', 'SomeHomeZone'),
    ('geoareas', 'rus', 'ru', 'Россия'),
    ('geoareas', 'rus', 'en', 'Russia'),
])
@pytest.mark.parametrize('charter_contract', [
    None,
    True,
    False
])
@pytest.inline_callbacks
def test_set_charter_contract(charter_contract):
    data = {
        'tz': 'Europe/Moscow',
        'city_id': 'Москва',
        'country': 'rus',
        'client_exact_order_round_minutes': 10,
        'layout': 'h',
        'payment_options': ['cash'],
        'for_wizard': True,
        'is_beta': False,
        'categories': [{
            'category_name': 'econom',
            'tanker_key': 'name.econom',
            'service_levels': [10],
            'is_default': True,
            'can_be_default': True,
            'client_constraints': [],
            'only_for_soon_orders': True,
            'legal_entities_enabled': True,
            'transfers_config': [],
            'persistent_requirements': [],
            'client_requirements': [],
        }],
        'show_onboarding': False,
        'paid_cancel_enabled': True,
        'ticket': 'TAXIRATE-0001',
    }
    if charter_contract is not None:
        data['categories'][0]['charter_contract'] = charter_contract

    response = django_test.Client().post(
        '/api/set_tariff_settings/some_home_zone/', json.dumps(data),
        content_type='application/json')

    assert response.status_code == 200, response.content

    response = django_test.Client().get('/api/tariff_settings/some_home_zone/')

    assert response.status_code == 200, response.content

    tariff_zone = json.loads(response.content)
    tariff_dbh = dbh.tariff_settings.Doc.find_by_home_zone('some_home_zone')
    tariff_db = yield db.tariff_settings.find_one({'hz': 'some_home_zone'})

    def _check_dict(tariff_dict, charter_contract):
        category = None
        if 'categories' in tariff_dict:
            category = tariff_dict['categories'][0]

        if category:
            if charter_contract is not None:
                assert category
                assert 'charter_contract' in category
                assert category['charter_contract'] == charter_contract
            else:
                if category:
                    assert 'charter_contract' not in category

    _check_dict(tariff_zone, charter_contract)
    _check_dict(tariff_db, charter_contract)
    _check_dict(tariff_dbh, charter_contract)


@pytest.mark.load_data(countries='test')
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en'])
@pytest.mark.translations([
    ('tariff', 'name.econom', 'ru', 'Эконом'),
    ('tariff', 'name.econom', 'en', 'Economy'),
    ('tariff', 'name.vip', 'en', 'Business'),
    ('geoareas', 'some_home_zone', 'ru', 'КакаятоЗона'),
    ('geoareas', 'some_home_zone', 'en', 'SomeHomeZone'),
    ('geoareas', 'rus', 'ru', 'Россия'),
    ('geoareas', 'rus', 'en', 'Russia'),
])
@pytest.mark.parametrize(
    'is_disabled',
    [  # if None, this field is not passed in the request
        None, False, True
    ]
)
def test_disable_tariff_zone(is_disabled, patch):
    data = {
        'tz': 'Europe/Moscow',
        'city_id': 'Москва',
        'country': 'rus',
        'client_exact_order_round_minutes': 10,
        'layout': 'h',
        'payment_options': ['cash'],
        'for_wizard': True,
        'is_beta': False,
        'categories': [{
            'category_name': 'econom',
            'tanker_key': 'name.econom',
            'service_levels': [10],
            'is_default': True,
            'can_be_default': True,
            'client_constraints': [],
            'only_for_soon_orders': True,
            'legal_entities_enabled': True,
            'transfers_config': [],
            'persistent_requirements': [],
            'client_requirements': [],
        }],
        'show_onboarding': False,
        'paid_cancel_enabled': True,
        'ticket': 'TAXIRATE-0001',
    }
    if is_disabled is not None:
        data['is_disabled'] = is_disabled

    response = django_test.Client().post(
        '/api/set_tariff_settings/some_home_zone/', json.dumps(data),
        content_type='application/json')

    assert response.status_code == 200, response.content

    tariff_zone = dbh.tariff_settings.Doc.find_by_home_zone('some_home_zone')
    assert 'is_disabled' in tariff_zone
    if is_disabled is None:
        assert tariff_zone['is_disabled'] is False
    else:
        assert tariff_zone['is_disabled'] == is_disabled


@pytest.mark.load_data(countries='test')
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en'])
@pytest.mark.translations([
    ('tariff', 'name.econom', 'ru', 'Эконом'),
    ('tariff', 'name.econom', 'en', 'Economy'),
    ('tariff', 'name.vip', 'en', 'Business'),
    ('geoareas', 'permissions_home_zone', 'ru', 'ЗонаТест'),
    ('geoareas', 'permissions_home_zone', 'en', 'ZoneTest'),
    ('geoareas', 'rus', 'ru', 'Россия'),
    ('geoareas', 'rus', 'en', 'Russia'),
])
@pytest.mark.parametrize('permissions,values,expected_code', [
    (
        {
            'set_tariff_licenses': {
                'mode': 'unrestricted'
            }
        },
        {
            'required_licenses': [1, 2, 3]
        },
        200
    ),
    (
        {
            'set_tariff_licenses': {
                'mode': 'unrestricted'
            }
        },
        {
            'required_licenses': [1, 2, 3],
            'is_beta': True
        },
        403
    ),
    (
        {
            'set_tariff_settings': {
                'mode': 'unrestricted'
            },
            'set_tariff_licenses': {
                'mode': 'unrestricted'
            }
        },
        {
            'required_licenses': [1, 2, 3],
            'is_beta': True
        },
        200
    ),
    (
        {
            'set_tariff_settings': {
                'mode': 'unrestricted'
            }
        },
        {
            'required_licenses': [1, 2, 3],
            'is_beta': True,
            'classifier_name': 'name',
        },
        200
    )
])
def test_permissions_set_tariff_zone(permissions, values, expected_code, patch):
    @patch('taxiadmin.permissions.get_user_permissions')
    @async.inline_callbacks
    def get_user_permissions(request):
        request.permissions = permissions
        yield
        async.return_value(permissions)

    data = {
        'tz': 'Europe/Moscow',
        'city_id': 'Москва',
        'country': 'rus',
        'client_exact_order_round_minutes': 10,
        'layout': 'h',
        'payment_options': ['cash'],
        'for_wizard': True,
        'is_beta': False,
        "point_settings_a": {
          "taximeter_waiting_params": {
            "enable": True,
            "max_order_distance": 400,
            "max_order_pedestrian_distance": 500
          }
        },
        'categories': [{
            'category_name': 'econom',
            'tanker_key': 'name.econom',
            'service_levels': [10],
            'is_default': True,
            'can_be_default': True,
            'client_constraints': [],
            'only_for_soon_orders': True,
            'legal_entities_enabled': True,
            'toll_roads_enabled': False,
            'transfers_config': [],
            'persistent_requirements': [],
            'client_requirements': [],
            'visibility_settings': {
                "visible_by_default": True,
                "show_experiment": "show_experiment_sample",
                "hide_experiment": "hide_experiment_sample",
                "visible_on_site": True
            }
        }],
        'show_onboarding': False,
        'paid_cancel_enabled': True,
        'ticket': 'TAXIRATE-0002',
    }
    data.update(values)
    request = django_test.RequestFactory().post(
        path='/api/set_tariff_settings/permissions_home_zone/',
        data=json.dumps(data),
        content_type='application/json'
    )
    request.login = 'some_login'
    request.time_storage = evlog.new_time_storage('')
    request.superuser = False
    request.groups = []

    response = tariff_settings.set_tariff_settings(
        request,
        zone_name='permissions_home_zone'
    )

    assert response.status_code == expected_code


@pytest.mark.load_data(countries='test')
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en'])
@pytest.mark.translations([
    ('tariff', 'name.econom', 'ru', 'Эконом'),
    ('tariff', 'name.econom', 'en', 'Economy'),
    ('tariff', 'name.vip', 'en', 'Business'),
    ('geoareas', 'some_home_zone', 'ru', 'КакаятоЗона'),
    ('geoareas', 'some_home_zone', 'en', 'SomeHomeZone'),
    ('geoareas', 'rus', 'ru', 'Россия'),
    ('geoareas', 'rus', 'en', 'Russia'),
])
@pytest.mark.parametrize(
    'skip_main_screen',
    [  # if None, this field is not passed in the request
        None, False, True
    ]
)
def test_skip_main_screen(skip_main_screen):
    data = {
        'tz': 'Europe/Moscow',
        'city_id': 'Москва',
        'country': 'rus',
        'client_exact_order_round_minutes': 10,
        'layout': 'h',
        'payment_options': ['cash'],
        'for_wizard': True,
        'is_beta': False,
        'categories': [{
            'category_name': 'econom',
            'tanker_key': 'name.econom',
            'service_levels': [10],
            'is_default': True,
            'can_be_default': True,
            'client_constraints': [],
            'only_for_soon_orders': True,
            'legal_entities_enabled': True,
            'transfers_config': [],
            'persistent_requirements': [],
            'client_requirements': [],
        }],
        'show_onboarding': False,
        'paid_cancel_enabled': True,
        'ticket': 'TAXIRATE-0001',
    }
    if skip_main_screen is not None:
        data['skip_main_screen'] = skip_main_screen
    response = django_test.Client().post(
        '/api/set_tariff_settings/some_home_zone/', json.dumps(data),
        content_type='application/json')
    assert response.status_code == 200, response.content

    tariff_zone = dbh.tariff_settings.Doc.find_by_home_zone('some_home_zone')
    if skip_main_screen is not None:
        assert tariff_zone['skip_main_screen'] == skip_main_screen

    response = django_test.Client().get(
        '/api/tariff_settings/some_home_zone/'
    )
    assert response.status_code == 200, response.content
    tariff_zone = json.loads(response.content)
    if skip_main_screen is None:
        assert tariff_zone['skip_main_screen'] is False
    else:
        assert tariff_zone['skip_main_screen'] == skip_main_screen


@pytest.mark.load_data(countries='test')
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en'])
@pytest.mark.translations([
    ('tariff', 'name.econom', 'ru', 'Эконом'),
    ('tariff', 'name.econom', 'en', 'Economy'),
    ('tariff', 'name.vip', 'en', 'Business'),
    ('geoareas', 'some_home_zone', 'ru', 'КакаятоЗона'),
    ('geoareas', 'some_home_zone', 'en', 'SomeHomeZone'),
    ('geoareas', 'rus', 'ru', 'Россия'),
    ('geoareas', 'rus', 'en', 'Russia'),
])
@pytest.mark.parametrize(
    'toll_roads_enabled',
    [  # if None, this field is not passed in the request
        None, False, True
    ]
)
def test_toll_roads_enabled(toll_roads_enabled):
    data = {
        'tz': 'Europe/Moscow',
        'city_id': 'Москва',
        'country': 'rus',
        'client_exact_order_round_minutes': 10,
        'layout': 'h',
        'payment_options': ['cash'],
        'for_wizard': True,
        'is_beta': False,
        'categories': [{
            'category_name': 'econom',
            'tanker_key': 'name.econom',
            'service_levels': [10],
            'is_default': True,
            'can_be_default': True,
            'client_constraints': [],
            'only_for_soon_orders': True,
            'legal_entities_enabled': True,
            'transfers_config': [],
            'persistent_requirements': [],
            'client_requirements': [],
        }],
        'show_onboarding': False,
        'paid_cancel_enabled': True,
        'ticket': 'TAXIRATE-0001',
    }

    if toll_roads_enabled is not None:
        data['categories'][0]['toll_roads_enabled'] = toll_roads_enabled

    response = django_test.Client().post(
        '/api/set_tariff_settings/some_home_zone/', json.dumps(data),
        content_type='application/json')
    assert response.status_code == 200, response.content

    cat = dbh.tariff_settings.Doc.find_by_home_zone('some_home_zone').categories[0]
    assert cat.get('toll_roads_enabled') == toll_roads_enabled


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('home_zone', [
    ('another_home_zone'),
    ('third_home_zone'),
])
@pytest.mark.translations([
    ('tariff', 'name.econom', 'ru', 'Эконом'),
    ('tariff', 'name.econom', 'en', 'Economy'),
    ('tariff', 'name.vip', 'en', 'Business'),
    ('geoareas', 'third_home_zone', 'ru', 'ТретьяЗона'),
    ('geoareas', 'third_home_zone', 'en', 'third_home_zone'),
    ('geoareas', 'another_home_zone', 'ru', 'ДругаяЗона'),
    ('geoareas', 'another_home_zone', 'en', 'AnotherZone'),
    ('geoareas', 'rus', 'ru', 'Россия'),
    ('geoareas', 'rus', 'en', 'Russia'),
])
def test_get_driver_change_cost(home_zone):
    response = django_test.Client().get(
        '/api/tariff_settings/{}/'.format(home_zone),
    )
    assert response.status_code == 200, response.content

    tariff_zone = json.loads(response.content)
    expected_tariff_zone = dbh.tariff_settings.Doc.find_by_home_zone(home_zone)

    assert 'is_disabled' in tariff_zone
    if 'driver_change_cost' in expected_tariff_zone:
        assert 'driver_change_cost' in tariff_zone
        assert (tariff_zone['driver_change_cost']['step'] ==
                expected_tariff_zone.driver_change_cost.step)
        assert (tariff_zone['driver_change_cost']['max_delta'] ==
                expected_tariff_zone.driver_change_cost.max_delta)
    else:
        assert 'driver_change_cost' not in tariff_zone


@pytest.mark.load_data(countries='test')
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en'])
@pytest.mark.translations([
    ('tariff', 'name.econom', 'ru', 'Эконом'),
    ('tariff', 'name.econom', 'en', 'Economy'),
    ('tariff', 'name.vip', 'en', 'Business'),
    ('geoareas', 'some_home_zone', 'ru', 'КакаятоЗона'),
    ('geoareas', 'some_home_zone', 'en', 'SomeHomeZone'),
    ('geoareas', 'rus', 'ru', 'Россия'),
    ('geoareas', 'rus', 'en', 'Russia'),
])
@pytest.mark.parametrize(
    'bad_request,field_name,field_value',
    [
        (True, 'name_with_typos', {'econom': True}),
        (True, 'hide_dest_for_driver_by_class', {'eCoNom': True}),
        (True, 'hide_dest_for_driver_by_class', {'econom': 'true'}),
        (False, 'hide_dest_for_driver_by_class', None),
        (False, 'hide_dest_for_driver_by_class', {}),
        (False, 'hide_dest_for_driver_by_class', {'econom': True}),
        (True, 'city_id', '_totally_not_a_city')
    ],
)
def test_db_write_and_validation(
        bad_request,
        field_name,
        field_value
):
    data = {
        'tz': 'Europe/Moscow',
        'city_id': 'Москва',
        'country': 'rus',
        'client_exact_order_round_minutes': 10,
        'layout': 'h',
        'payment_options': ['cash'],
        'for_wizard': True,
        'is_beta': False,
        'categories': [{
            'category_name': 'econom',
            'tanker_key': 'name.econom',
            'service_levels': [10],
            'is_default': True,
            'can_be_default': True,
            'client_constraints': [],
            'only_for_soon_orders': True,
            'legal_entities_enabled': True,
            'transfers_config': [],
            'persistent_requirements': [],
            'client_requirements': [],
            'max_card_payment': 10,
            'max_corp_payment': 10,
            'card_payment_settings': {
                'max_refund': 10,
                'max_compensation': 10,
                'max_manual_charge': 10
            }
        }],
        'show_onboarding': False,
        'paid_cancel_enabled': True,
        'ticket': 'TAXIRATE-0001',
    }
    if field_value is not None:
        data[field_name] = field_value

    response = django_test.Client().post(
        '/api/set_tariff_settings/some_home_zone/', json.dumps(data),
        content_type='application/json')

    if bad_request:
        assert response != 200
    else:
        assert response.status_code == 200, response.content
        tariff_zone = dbh.tariff_settings.Doc.find_by_home_zone(
            'some_home_zone'
        )
        assert (getattr(tariff_zone, field_name) == field_value)


@pytest.mark.config(ALL_CATEGORIES=['child_tariff', 'econom', 'business',
                                    'vip', 'uberx', 'uberselect', 'uberkids'])
@pytest.mark.filldb(tariff_settings='csv')
@pytest.mark.filldb(requirements='csv')
@pytest.mark.parametrize('request_body, status_code, expected', [
    ({"zones": 'spb'}, 200, 'spb.csv'),
    ({
         "zones": ['moscow', 'spb']
     },
     400,
     {
         "status": "error",
         "code": "zones_not_found",
         "not_found_zones": ["moscow"]
     }),
])
@pytest.mark.asyncenv('blocking')
def test_get_tariffs_list_csv(load, request_body, status_code, expected):
    response = django_test.Client().post(
        '/api/tariff_settings/generate_tariff_settings_csv/',
        json.dumps(request_body),
        content_type='application/json'
    )
    assert response.status_code == status_code
    if response.status_code == 200:
        result = response.content.decode('utf-8').replace('\r', '').encode(
            'utf-8')
        assert result == load(expected)
    if response.status_code == 400:
        assert json.loads(response.content) == expected


@pytest.mark.config(ALL_CATEGORIES=['child_tariff', 'econom', 'business',
                                    'vip', 'uberx', 'uberselect', 'uberkids'])
@pytest.mark.filldb(tariff_settings='fixed_price_flag')
@pytest.mark.parametrize('zone_name', ['spb', 'spb_old_format'])
@pytest.mark.asyncenv('blocking')
def test_get_tariff_settings(zone_name):
    response = django_test.Client().get(
        '/api/tariff_settings/{}/'.format(zone_name),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert 'fixed_price_enabled' in data
    for cat in data['categories']:
        if zone_name == 'spb':
            assert 'visibility_settings' in cat
            settings = cat['visibility_settings']
            assert 'fixed_price_enabled' in cat
            assert 'visible_by_default' in settings
            assert 'show_experiment' in settings
            assert 'hide_experiment' in settings
            assert 'visible_on_site' in settings
        else:
            assert 'visibility_settings' not in cat


# @pytest.mark.load_data(countries='test')
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en'])
@pytest.mark.translations([
    ('tariff', 'name.econom', 'ru', 'Эконом'),
    ('tariff', 'name.econom', 'en', 'Economy'),
    ('tariff', 'name.vip', 'en', 'Business'),
    ('geoareas', 'some_home_zone', 'ru', 'КакаятоЗона'),
    ('geoareas', 'some_home_zone', 'en', 'SomeHomeZone'),
    ('geoareas', 'rus', 'ru', 'Россия'),
    ('geoareas', 'rus', 'en', 'Russia'),
])
@pytest.mark.parametrize('global_val', [None, False, True])
@pytest.mark.parametrize('category_val', [None, False, True])
@pytest.inline_callbacks
def test_set_fixed_price_enabled(global_val, category_val, patch):
    data = {
        'tz': 'Europe/Moscow',
        'city_id': 'Москва',
        'country': 'rus',
        'client_exact_order_round_minutes': 10,
        'layout': 'h',
        'payment_options': ['cash'],
        'for_wizard': True,
        'is_beta': False,
        'categories': [{
            'category_name': 'econom',
            'tanker_key': 'name.econom',
            'service_levels': [10],
            'is_default': True,
            'can_be_default': True,
            'client_constraints': [],
            'only_for_soon_orders': True,
            'legal_entities_enabled': True,
            'transfers_config': [],
            'persistent_requirements': [],
            'client_requirements': [],
        }],
        'show_onboarding': False,
        'paid_cancel_enabled': True,
        'ticket': 'TAXIRATE-0001',
    }
    if global_val is not None:
        data['fixed_price_enabled'] = global_val
    if category_val is not None:
        data['categories'][0]['fixed_price_enabled'] = category_val

    response = django_test.Client().post(
        '/api/set_tariff_settings/some_home_zone/', json.dumps(data),
        content_type='application/json')

    assert response.status_code == 200, response.content

    tariff_zone = yield db.tariff_settings.find_one({'hz': 'some_home_zone'})
    assert 'is_disabled' in tariff_zone
    assert tariff_zone.get('fixed_price_enabled') == global_val
    for cat in tariff_zone['s']:
        assert cat.get('fixed_price_enabled') == category_val


def _create_category(category, is_default=True,
                     visible_by_default=None,
                     show_experiment=None,
                     hide_experiment=None,
                     visible_on_site=None,
                     service_levels=None
):
    result = {
        'category_name': category,
        'tanker_key': 'name.{}'.format(category),
        'service_levels': [10],
        'is_default': is_default,
        'can_be_default': True,
        'client_constraints': [],
        'only_for_soon_orders': True,
        'legal_entities_enabled': True,
        'toll_roads_enabled': True,
        'transfers_config': [],
        'client_requirements': ['childchair_v2'],
        'glued_requirements': ['childchair_v2'],
        'persistent_requirements': ['childchair_v2'],
        'requirement_flavor': {'childchair_v2': '1_1_1'},
        'tariff_specific_overrides': {'childchair_v2': False},
        'visibility_settings': {}
    }
    if service_levels:
        result['service_levels'] = service_levels
    if visible_by_default is not None:
        result['visibility_settings']['visible_by_default'] = visible_by_default
    if show_experiment is not None:
        result['visibility_settings']['show_experiment'] = show_experiment
    if hide_experiment is not None:
        result['visibility_settings']['hide_experiment'] = hide_experiment
    if visible_on_site is not None:
        result['visibility_settings']['visible_on_site'] = visible_on_site
    return result

case = helpers.case_getter(
    'update_data,expected_status,file_expected,user_login',
    user_login='karachevda',
)


@pytest.mark.filldb(tariff_settings='check')
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(ALL_CATEGORIES=['econom', 'vip'])
@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en'])
@pytest.mark.translations([
    ('tariff', 'name.econom', 'ru', 'Эконом'),
    ('tariff', 'name.econom', 'en', 'Economy'),
    ('tariff', 'name.vip', 'en', 'Business'),
    ('tariff', 'name.vip', 'ru', 'Бизнес'),
    ('geoareas', 'some_home_zone', 'ru', 'Москва'),
    ('geoareas', 'some_home_zone', 'en', 'Moscow'),
    ('geoareas', 'rus', 'ru', 'Россия'),
    ('geoareas', 'rus', 'en', 'Russia'),
    ('geoareas', 'not_existed', 'ru', 'not_existed'),
    ('geoareas', 'not_existed', 'en', 'not_existed'),
    ('geoareas', 'not_existed_zone', 'ru', 'not_existed_zone'),
    ('geoareas', 'not_existed_zone', 'en', 'not_existed_zone'),
    ('geoareas', 'permissions_home_zone', 'ru', 'Москва'),
    ('geoareas', 'permissions_home_zone', 'en', 'Moscow'),
    ('geoareas', 'existing_home_zone_1', 'ru', 'existing_home_zone_1'),
    ('geoareas', 'existing_home_zone_1', 'en', 'existing_home_zone_1'),
    ('geoareas', 'existing_home_zone_2', 'ru', 'existing_home_zone_2'),
    ('geoareas', 'existing_home_zone_2', 'en', 'existing_home_zone_2'),
])
@pytest.mark.parametrize(case.params, [
    # not existing country
    case(
        {
            'country': 'not_existed',
        },
        400,
        None,
    ),
    # user has no access to checking
    case(
        update_data={
            'home_zone': 'permissions_home_zone',
            'max_eta': 200,
        },
        expected_status=400,
        file_expected='set_tariff_settings_error_400.json',
        user_login='anyone_else',
    ),
    # user has no access to checking
    case(
        {
            'categories':
                [_create_category('econom', is_default=False)],
        },
        400,
        None,
    ),
    # create new home zone without tariffs
    case(
        {
            'home_zone': 'not_existed_zone',
            'fix_charge_callcenter': 10000
        },
        200,
        'set_tariff_settings_create_new_draft_check_without_tariff.json',
    ),
    # create new home zone with tariffs
    case(
        {
            'home_zone': 'not_existed_zone',
            'categories': [_create_category('econom')],
            'hide_dest_for_driver_by_class': {
                'econom': True
            },
        },
        200,
        'set_tariff_settings_create_new_draft.json',
    ),
    # edit existing home zone change only tariffs
    case(
        {
            'home_zone': 'existing_home_zone_1',
            'categories': [_create_category('econom')],
        },
        200,
        'set_tariff_settings_edit_draft_only_tariffs.json'
    ),
    # edit existing home zone change only global section
    case(
        {
            'home_zone': 'existing_home_zone_1',
            'max_eta': 200,
        },
        200,
        'set_tariff_settings_edit_draft_only_global.json'
    ),
    # edit existing home zone remove tariff from categories
    case(
        {
            'home_zone': 'existing_home_zone_2',
            'city_id': 'Киров',
            'categories': []
        },
        200,
        'set_tariff_settings_remove_old_draft.json',
    ),
    # edit existing home zone change categories and globals
    case(
        {
            'home_zone': 'existing_home_zone_1',
            'max_eta': 200,
            'categories': [_create_category('econom')],
        },
        200,
        'set_tariff_settings_edit_draft_globals_and_tariffs.json',
    ),
    # no  changes
    case(
        {
            'home_zone': 'existing_home_zone_2',
            'city_id': 'Киров',
            'categories': [
                _create_category('econom'),
                _create_category('vip')
            ],
        },
        200,
        'set_tariff_settings_edit_draft_no_changes.json',
    ),
])
def test_set_tariff_settings_check(patch, load, update_data, expected_status,
                                   file_expected, user_login):

    _patch_internals(patch, DEFAULT_CONFIG)

    @patch('taxi.external.tvm.check_ticket')
    def check_ticket(dst_service_name, ticket_body, log_extra=None):
        assert ticket_body == 'tvm_ticket'
        return True

    data = {
        'home_zone': 'some_home_zone',
        'tz': 'Europe/Moscow',
        'city_id': 'Москва',
        'country': 'rus',
        'client_exact_order_round_minutes': 10,
        'layout': 'h',
        'payment_options': ['cash'],
        'for_wizard': True,
        'is_beta': False,
        'categories': [],
        'show_onboarding': False,
        'paid_cancel_enabled': True,
    }
    if update_data:
        data.update(update_data)

    response = django_test.Client().post(
        '/api/approvals/set_tariff_settings/check/',
        json.dumps(data),
        content_type='application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN=user_login,
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == expected_status
    if expected_status == 200:
        content = json.loads(response.content)
        expected_data = json.loads(load(file_expected))
        if content.get('diff', {}).get('current', {}).get('_id', False):
            content['diff']['current'].pop('_id')
            content['diff']['current'].pop('updated')
        if content.get('diff', {}).get('new', {}).get('updated', False):
            content['diff']['new'].pop('updated')
        assert content == expected_data
    elif file_expected is not None:
        expected_data = json.loads(load(file_expected))
        content = json.loads(response.content)
        assert content == expected_data


@pytest.mark.filldb(tariff_settings='check')
@pytest.mark.now('2019-07-01T12:00:00')
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(ALL_CATEGORIES=['econom', 'vip', 'business'])
@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en'])
@pytest.mark.translations([
    ('tariff', 'name.econom', 'ru', 'Эконом'),
    ('tariff', 'name.econom', 'en', 'Economy'),
    ('tariff', 'name.vip', 'en', 'Business'),
    ('tariff', 'name.business', 'ru', 'Бизнес'),
    ('tariff', 'name.business', 'en', 'Business'),
    ('geoareas', 'some_home_zone', 'ru', 'Москва'),
    ('geoareas', 'some_home_zone', 'en', 'Moscow'),
    ('geoareas', 'rus', 'ru', 'Россия'),
    ('geoareas', 'rus', 'en', 'Russia'),
    ('geoareas', 'not_existed', 'ru', 'not_existed'),
    ('geoareas', 'not_existed', 'en', 'not_existed'),
    ('geoareas', 'existing_home_zone_1', 'ru', 'existing_home_zone_1'),
    ('geoareas', 'existing_home_zone_1', 'en', 'existing_home_zone_1'),
    ('geoareas', 'existing_home_zone_2', 'ru', 'existing_home_zone_2'),
    ('geoareas', 'existing_home_zone_2', 'en', 'existing_home_zone_2'),
])
@pytest.mark.parametrize('update_data,'
                         'categories_patch,'
                         'global_settings_patch,'
                         'expected_status,'
                         'expected_data', [
    (
        {'home_zone': 'not_existed_zone'},
        {},
        {},
        404,
        None,
    ),
    # create new category according to patch
    (
        {
            'home_zone': 'existing_home_zone_1',
            'categories': [
                _create_category(
                'econom',
                is_default=True,
                visible_by_default=True,
                show_experiment='show_experiment_sample',
                hide_experiment='hide_experiment_sample',
                visible_on_site=False
                )
            ]
        },
        {
            "created": [0],
        },
        {
            "changed": [
                "hz",
                "payment_options",
                "tz",
                "city_id",
                "country",
                "paid_cancel_enabled",
                "is_disabled",
                "for_wizard",
                "layout",
                "show_onboarding",
                "client_exact_order_round_minutes",
                "is_beta"
            ],
        },
        200,
        {
            'hz': 'existing_home_zone_1',
            'payment_options': ['cash'],
            'tz': 'Europe/Moscow',
            'city_id': 'Москва',
            'country': 'rus',
            'paid_cancel_enabled': True,
            'is_disabled': False,
            'updated': datetime.datetime(2019, 7, 1, 12, 0, 0),
            's': [{
                'e_leg_ent': True,
                'd': True,
                'cc': [],
                'n': u'econom',
                'r': True,
                't': u'name.econom',
                'oso': True,
                'sl': [10],
                'client_requirements': ['childchair_v2'],
                'persistent_reqs': ['childchair_v2'],
                'glued_requirements': ['childchair_v2'],
                'requirement_flavor': {
                    'childchair_v2': '1_1_1'
                },
                'tariff_specific_overrides': {'childchair_v2': False},
                'tc': [],
                'toll_roads_enabled': True,
                'visibility_settings':{
                    'visible_by_default': True,
                    'show_experiment': 'show_experiment_sample',
                    'hide_experiment': 'hide_experiment_sample',
                    'visible_on_site': False
                }
            }],
            'for_wizard': True,
            'layout': 'h',
            'show_onboarding': False,
            'client_exact_order_round_minutes': 10,
            'is_beta': False,
        },
    ),
    # update existing category according to patch
    (
            {
                'home_zone': 'existing_home_zone_2',
                'categories': [
                    _create_category(
                        'econom',
                        is_default=True,
                        visible_by_default=True,
                        show_experiment='',
                        hide_experiment='',
                        visible_on_site=False
                    )
                ]
            },
            {
                "updated": [0],
                "removed": [1]
            },
            {},
            200,
            {
                'hz': 'existing_home_zone_2',
                'payment_options': ['cash'],
                'tz': 'Europe/Moscow',
                'city_id': 'Киров',
                'country': 'rus',
                'paid_cancel_enabled': True,
                'is_disabled': False,
                'updated': datetime.datetime(2019, 7, 1, 12, 0, 0),
                's': [{
                    'e_leg_ent': True,
                    'd': True,
                    'cc': [],
                    'n': u'econom',
                    'r': True,
                    't': u'name.econom',
                    'oso': True,
                    'sl': [10],
                    'client_requirements': ['childchair_v2'],
                    'persistent_reqs': ['childchair_v2'],
                    'glued_requirements': ['childchair_v2'],
                    'requirement_flavor': {
                        'childchair_v2': '1_1_1'
                    },
                    'tariff_specific_overrides': {'childchair_v2': False},
                    'tc': [],
                    'toll_roads_enabled': True,
                    'visibility_settings': {
                        'visible_by_default': True,
                        'visible_on_site': False
                    }
                }],
                'for_wizard': True,
                'layout': 'h',
                'show_onboarding': False,
                'client_exact_order_round_minutes': 10,
                'is_beta': False,
            },
    ),
    #remove existing categories
    (
            {
                'home_zone': 'existing_home_zone_2',
                'categories': []
            },
            {
                "removed": [0, 1]
            },
            {},
            200,
            {
                'hz': 'existing_home_zone_2',
                'payment_options': ['cash'],
                'tz': 'Europe/Moscow',
                'city_id': 'Киров',
                'country': 'rus',
                'paid_cancel_enabled': True,
                'is_disabled': False,
                'updated': datetime.datetime(2019, 7, 1, 12, 0, 0),
                's': [],
                'for_wizard': True,
                'layout': 'h',
                'show_onboarding': False,
                'client_exact_order_round_minutes': 10,
                'is_beta': False,
            },
    ),
    # combo scenario
    (
            {
                'home_zone': 'existing_home_zone_2',
                'categories': [
                    _create_category('business', service_levels=[10]),
                    _create_category('econom', service_levels=[11])
                ]
            },
            {
                'updated': [0, 1],
            },
            {
                "removed": ['is_disabled']
            },
            200,
            {
                'hz': 'existing_home_zone_2',
                'payment_options': ['cash'],
                'tz': 'Europe/Moscow',
                'city_id': 'Киров',
                'country': 'rus',
                'paid_cancel_enabled': True,
                'updated': datetime.datetime(2019, 7, 1, 12, 0, 0),
                's': [{
                    'e_leg_ent': True,
                    'd': True,
                    'cc': [],
                    'n': u'business',
                    'r': True,
                    't': u'name.business',
                    'oso': True,
                    'sl': [10],
                    'client_requirements': ['childchair_v2'],
                    'persistent_reqs': ['childchair_v2'],
                    'glued_requirements': ['childchair_v2'],
                    'requirement_flavor': {
                        'childchair_v2': '1_1_1'
                    },
                    'tariff_specific_overrides': {'childchair_v2': False},
                    'tc': [],
                    'toll_roads_enabled': True,
                    'visibility_settings': {'visible_by_default': False}
                },
                {
                    'e_leg_ent': True,
                    'd': True,
                    'cc': [],
                    'n': u'econom',
                    'r': True,
                    't': u'name.econom',
                    'oso': True,
                    'sl': [11],
                    'client_requirements': ['childchair_v2'],
                    'persistent_reqs': ['childchair_v2'],
                    'glued_requirements': ['childchair_v2'],
                    'requirement_flavor': {
                        'childchair_v2': '1_1_1'
                    },
                    'tariff_specific_overrides': {'childchair_v2': False},
                    'tc': [],
                    'toll_roads_enabled': True,
                    'visibility_settings': {'visible_by_default': False}
                }
                ],
                'for_wizard': True,
                'layout': 'h',
                'show_onboarding': False,
                'client_exact_order_round_minutes': 10,
                'is_beta': False,
            },
    ),
])
@pytest.inline_callbacks
def test_set_tariff_settings_apply(
    update_data, categories_patch, global_settings_patch,
    expected_status, expected_data, patch
):

    @patch('taxi.external.tvm.check_ticket')
    def check_ticket(dst_service_name, ticket_body, log_extra=None):
        assert ticket_body == 'tvm_ticket'
        return True

    data = {
        'home_zone': 'some_home_zone',
        'tz': 'Europe/Moscow',
        'city_id': 'Москва',
        'country': 'rus',
        'client_exact_order_round_minutes': 10,
        'layout': 'h',
        'payment_options': ['cash'],
        'for_wizard': True,
        'is_beta': False,
        'categories': [],
        'show_onboarding': False,
        'paid_cancel_enabled': True,
        'patches': {
            'global_settings': global_settings_patch,
            'categories': categories_patch
        },
        'ticket': 'TAXIRATE-35',
    }
    data.update(update_data)
    home_zone = data.get('home_zone')
    response = django_test.Client().post(
        '/api/approvals/set_tariff_settings/apply/',
        json.dumps(data),
        content_type='application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='karachevda',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == expected_status
    if expected_status == 200:
        assert json.loads(response.content) == {}
        doc = yield dbh.tariff_settings.Doc.find_by_home_zone(home_zone)
        assert doc.pop('_id')
        assert dict(**doc) == expected_data
