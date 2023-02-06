from __future__ import unicode_literals

import datetime

import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.external import agglomerations
from taxi.external import candidate_meta as candidate_meta_client
from taxi.external import experiments3
from taxi.external import taxi_protocol
from taxi.external import metadata_storage
from taxi.internal import archive
from taxi.internal import dbh
from taxi.internal import order_events


@pytest.fixture
def mocked_send_event(patch):
    @patch('taxi.external.billing_orders.send_event')
    @async.inline_callbacks
    def send_event(order_event_ref, type_, data, **kwargs):
        yield

    return send_event


@pytest.fixture
def mocked_prepare_event(patch):
    @patch('taxi_stq.client.prepare_order_event')
    @async.inline_callbacks
    def prepare_order_event(order_id, order_version, event_type, eta=0,
                            reason=None,
                            log_extra=None):
        yield

    return prepare_order_event


@pytest.fixture
def mocked_min_due(monkeypatch):
    monkeypatch.setattr(
        order_events,
        'MIN_DUE_TO_SEND_EVENTS',
        datetime.datetime(2018, 10, 1, 0, 0))


@pytest.fixture
def mocked_metadata_storage(patch):
    @patch('taxi.external.metadata_storage.v1_metadata_retrieve')
    @async.inline_callbacks
    def v1_metadata_retrieve(
        meta_id, namespace, last_known_updated=None, try_archive=False, log_extra=None):
        if namespace == 'taxi:order_agglomeration':
            yield async.return_value({
                'value': {
                    'additional_data': {
                        'geo_nodes': [
                            'br_moscow_adm', 'br_moscow', 'br_root'
                        ],
                        'mvp': 'MSKc'
                    }
                },
                'updated': '2020-06-19T06:39:26.898+00:00'
            })
        elif namespace == 'taxi:subvention_geoareas':
            yield async.return_value({
                    'value': {
                        'additional_data': {
                            'subvention_geoareas': [
                                {
                                    '_id': '2',
                                    'name': 'geoarea_2',
                                    'area': '2',
                                },
                                {
                                    '_id': '3',
                                    'name': 'geoarea_no_area',
                                },
                                {
                                    '_id': '1',
                                    'name': 'geoarea_1',
                                    'area': '1',
                                },
                            ]
                        }
                    },
                    'updated': '2020-06-19T06:39:26.898+00:00'
            })

    return v1_metadata_retrieve


@pytest.mark.parametrize(
    'event_type,proc_id,reason,candidate_meta,expected_event_data,'
    'expected_workshift_usages, add_rebate_to_decoupling, retrieve_cargo_info',
    [
      (
          'order_completed',
          'order_id_1',
          {'kind': 'completed', 'data': {}},
          None,
          {
              'accepted_by_driver_at': '2018-10-17T16:10:53.921000+00:00',
              'billing_at': '2018-10-17T16:10:53.921000+00:00',
              'alias_id': 'alias_id_1',
              'billing_contract_is_set': True,
              'billing_contract': {
                  'donate_multiplier': '1',
                  'offer_currency': 'RUB',
                  'currency_rate': '1',
                  'offer_currency_rate': '1',
                  'currency': 'RUB',
                  'acquiring_percent': '0',
                  'rebate_percent': '0',
                  'ind_bel_nds_percent': None,
                  'subventions_hold_delay': 0
              },
              'closed_without_accept': False,
              'completed_at': '2018-10-17T17:59:38.834000+00:00',
              'completed_by_dispatcher': False,
              'cost': {'amount': '1041.0', 'currency': 'RUB'},
              'created': '2018-10-17T16:10:42.631000+00:00',
              'discount': {
                  'method': 'subvention-fix',
                  'rate': 0.01,
              },
              'driver_cost': None,
              'due': '2018-10-17T16:14:00.000000+00:00',
              'has_co_branding': False,
              'has_lightbox': True,
              'has_sticker': True,
              'is_mqc': False,
              'order_id': 'order_id_1',
              'payment_type': 'card',
              'park': {
                  'brandings': ["lightbox", "franchise"]
              },
              'performer': {
                  'activity_points': 82,
                  'unique_driver_id': '5bcf22169830073fda1ebc2c',
                  'driver_license': 'AAA007X',
                  'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                  'driver_id': 'park-with-several-brandings_driveruuid',
                  'db_id': 'dead0000food0000beef0000dead0000',
                  'tariff_category_id': 'category_id',
                  'hired_at': '2018-09-19T18:19:14.743000+00:00',
                  'hiring_type': 'commercial',
                  'available_tariff_classes': [
                      "econom",
                      "comfort"
                  ],
                  'profile_payment_type_restrictions': 'none',
                  'zone': 'some_geoarea_from_db',
                  'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
              },
              'source': None,
              'status': 'finished',
              'subvention_geoareas': [
                  'geoarea_1',
                  'geoarea_2',
                  'geoarea_no_area',
              ],
              'tags': ["some_tag", "fleet_park_rating"],
              'tariff_class': 'econom',
              'taxi_status': 'complete',
              'total_distance': 41882.9765625,
              'total_time': 6107.596,
              'park_corp_vat': None,
              'zone': 'moscow',
              'price_modifiers': [],
              'updated': '2018-10-17T17:14:00.000000+00:00',
              'park_ride_sum': '100',
              'coupon': {
                  'amount': '75.6',
                  'currency': 'RUB',
                  'netting_allowed': False,
                  'for_support': None,
              },
              'reason': {
                  'kind': 'completed',
                  'data': {}
              },
              'childseat_rental': {
                  'count': 1,
                  'cost': "51"
              },
              'driver_workshift_ids': [],
              'fleet_subscription_level': (
                  'fleet_subscription_level'
              ),
              'oebs_mvp_id': 'MSKc',
              'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
          },
          {},
          False,
          False,
      ),
      (
          'order_completed',
          'order_id_1',
          {'kind': 'completed', 'data': {}},
          {'payment_type_restrictions': 'cash'},
          {
              'accepted_by_driver_at': '2018-10-17T16:10:53.921000+00:00',
              'billing_at': '2018-10-17T16:10:53.921000+00:00',
              'alias_id': 'alias_id_1',
              'billing_contract_is_set': True,
              'billing_contract': {
                  'donate_multiplier': '1',
                  'offer_currency': 'RUB',
                  'currency_rate': '1',
                  'offer_currency_rate': '1',
                  'currency': 'RUB',
                  'acquiring_percent': '0',
                  'rebate_percent': '0',
                  'ind_bel_nds_percent': None,
                  'subventions_hold_delay': 0
              },
              'closed_without_accept': False,
              'completed_at': '2018-10-17T17:59:38.834000+00:00',
              'completed_by_dispatcher': False,
              'cost': {'amount': '1041.0', 'currency': 'RUB'},
              'created': '2018-10-17T16:10:42.631000+00:00',
              'discount': {
                  'method': 'subvention-fix',
                  'rate': 0.01,
              },
              'driver_cost': None,
              'due': '2018-10-17T16:14:00.000000+00:00',
              'has_co_branding': False,
              'has_lightbox': True,
              'has_sticker': True,
              'is_mqc': False,
              'order_id': 'order_id_1',
              'payment_type': 'card',
              'park': {
                  'brandings': ["lightbox", "franchise"]
              },
              'performer': {
                  'activity_points': 82,
                  'unique_driver_id': '5bcf22169830073fda1ebc2c',
                  'driver_license': 'AAA007X',
                  'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                  'driver_id': 'park-with-several-brandings_driveruuid',
                  'db_id': 'dead0000food0000beef0000dead0000',
                  'tariff_category_id': 'category_id',
                  'hired_at': '2018-09-19T18:19:14.743000+00:00',
                  'hiring_type': 'commercial',
                  'available_tariff_classes': [
                      "econom",
                      "comfort"
                  ],
                  'profile_payment_type_restrictions': 'cash',
                  'zone': 'some_geoarea_from_db',
                  'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
              },
              'source': None,
              'status': 'finished',
              'subvention_geoareas': [
                  'geoarea_1',
                  'geoarea_2',
                  'geoarea_no_area',
              ],
              'tags': ["some_tag", "fleet_park_rating"],
              'tariff_class': 'econom',
              'taxi_status': 'complete',
              'total_distance': 41882.9765625,
              'total_time': 6107.596,
              'park_corp_vat': None,
              'zone': 'moscow',
              'price_modifiers': [],
              'updated': '2018-10-17T17:14:00.000000+00:00',
              'park_ride_sum': '100',
              'coupon': {
                  'amount': '75.6',
                  'currency': 'RUB',
                  'netting_allowed': False,
                  'for_support': None,
              },
              'reason': {
                  'kind': 'completed',
                  'data': {}
              },
              'childseat_rental': {
                  'count': 1,
                  'cost': "51"
              },
              'driver_workshift_ids': [],
              'fleet_subscription_level': (
                  'fleet_subscription_level'
              ),
              'oebs_mvp_id': 'MSKc',
              'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
          },
          {},
          False,
          False,
      ),
      (
          'order_completed',
          'order_id_2',
          None,
          None,
          {
              'accepted_by_driver_at': '2018-10-01T00:00:10.000000+00:00',
              'billing_at': '2018-10-01T00:00:10.000000+00:00',
              'alias_id': 'alias_id_2',
              'billing_contract_is_set': False,
              'closed_without_accept': False,
              'completed_at': '2018-10-01T00:06:47.977000+00:00',
              'completed_by_dispatcher': False,
              'cost': {'amount': '1041.0', 'currency': 'RUB'},
              'created': '2018-10-17T16:10:42.631000+00:00',
              'discount': {
                  'method': 'subvention-fix',
                  'rate': 0.01,
              },
              'driver_cost': None,
              'due': '2018-10-17T16:14:00.000000+00:00',
              'has_co_branding': False,
              'has_lightbox': False,
              'has_sticker': False,
              'is_mqc': False,
              'order_id': 'order_id_2',
              'payment_type': 'card',
              'park': {
                  'brandings': []
              },
              'performer': {
                  'activity_points': 82,
                  'unique_driver_id': '5bcf22169830073fda1ebc2c',
                  'driver_license': 'AAA007X',
                  'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                  'driver_id': 'park-without-active-brandings_driveruuid',
                  'db_id': 'dead0000food0000beef0000dead0000',
                  'tariff_category_id': 'category_id',
                  'available_tariff_classes': [],
                  'profile_payment_type_restrictions': 'none',
                  'zone': 'some_geoarea_from_db',
                  'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
              },
              'source': None,
              'status': 'finished',
              'subvention_geoareas': [
                  'geoarea_1',
                  'geoarea_2',
                  'geoarea_no_area',
              ],
              'tags': ['fleet_park_rating'],
              'tariff_class': 'econom',
              'taxi_status': 'complete',
              'total_distance': 0,
              'total_time': 0,
              'park_corp_vat': None,
              'zone': 'moscow',
              'price_modifiers': [],
              'updated': '2019-01-01T00:00:00.000000+00:00',
              'park_ride_sum': '0',
              'coupon': {
                  'amount': '0',
                  'currency': 'RUB',
                  'netting_allowed': True,
                  'for_support': None,
              },
              'reason': None,
              'driver_workshift_ids': [],
              'cancel_distance': 28.51897408578054,
              'cancelled_at': '2018-10-01T00:06:47.977000+00:00',
              'fleet_subscription_level': (
                  'fleet_subscription_level'
              ),
              'oebs_mvp_id': 'MSKc',
              'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
          },
          {},
          False,
          False,
      ),
      (
          'order_completed',
          'order_id_3',
          None,
          None,
          {
              'alias_id': 'alias_id_3',
              'billing_at': '2018-10-17T16:14:00.000000+00:00',
              'billing_contract_is_set': False,
              'closed_without_accept': False,
              'completed_at': '2018-10-12T23:05:39.404000+00:00',
              'completed_by_dispatcher': False,
              'cost': {'amount': '1041.0', 'currency': 'RUB'},
              'created': '2018-10-17T16:10:42.631000+00:00',
              'discount': {
                  'method': 'subvention-fix',
                  'rate': 0.01,
                  'limit_id': 'discount_limit_id_2',
                  'value': {
                      'amount': '10.51',
                      'currency': 'RUB',
                  },
                  'declines': []
              },
              'driver_cost': None,
              'due': '2018-10-17T16:14:00.000000+00:00',
              'has_co_branding': False,
              'has_lightbox': False,
              'has_sticker': False,
              'is_mqc': False,
              'order_id': 'order_id_3',
              'payment_type': 'card',
              'park': {
                  'brandings': []
              },
              'performer': {
                  'activity_points': 82,
                  'unique_driver_id': '5bcf22169830073fda1ebc2c',
                  'driver_license': 'AAA007X',
                  'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                  'driver_id': 'park-without-active-brandings_driveruuid',
                  'db_id': 'dead0000food0000beef0000dead0000',
                  'tariff_category_id': 'category_id_order_3',
                  'available_tariff_classes': [],
                  'profile_payment_type_restrictions': 'none',
                  'zone': 'some_geoarea_from_db',
                  'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
              },
              'source': None,
              'status': 'finished',
              'subvention_geoareas': [
                  'geoarea_1',
                  'geoarea_2',
                  'geoarea_no_area',
              ],
              'tags': ['fleet_park_rating'],
              'tariff_class': 'econom',
              'taxi_status': 'expired',
              'total_distance': 0,
              'total_time': 0,
              'park_corp_vat': None,
              'zone': 'moscow',
              'price_modifiers': [],
              'updated': '2018-11-01T00:00:00.000000+00:00',
              'park_ride_sum': '0',
              'coupon': {
                  'amount': '0',
                  'currency': 'RUB',
                  'netting_allowed': True,
                  'for_support': None,
              },
              'reason': None,
              'driver_workshift_ids': [],
              'fleet_subscription_level': (
                  'fleet_subscription_level'
              ),
              'oebs_mvp_id': 'MSKc',
              'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
          },
          {},
          False,
          False,
      ),
      (
          'order_completed',
          'order_id_4',
          None,
          None,
          None,  # Unique driver does not exist
          None,
          False,
          False,
      ),
      (
          'order_completed',
          'order_id_8',
          None,
          None,
          {
              'alias_id': 'alias_id_8',
              'billing_at': '2018-10-17T16:14:00.000000+00:00',
              'billing_contract_is_set': False,
              'closed_without_accept': False,
              'completed_at': '2018-10-12T23:05:39.404000+00:00',
              'completed_by_dispatcher': False,
              'cost': {'amount': '1041.0', 'currency': 'RUB'},
              'created': '2018-10-17T16:10:42.631000+00:00',
              'discount': {
                  'method': 'subvention-fix',
                  'rate': 0.01,
              },
              'driver_cost': None,
              'due': '2018-10-17T16:14:00.000000+00:00',
              'has_co_branding': False,
              'has_lightbox': False,
              'has_sticker': False,
              'is_mqc': False,
              'order_id': 'order_id_8',
              'payment_type': 'card',
              'park': {
                  'brandings': []
              },
              'performer': {
                  'activity_points': 82,
                  'unique_driver_id': '5bcf22169830073fda1ebc2c',
                  'driver_license': 'AAA007X',
                  'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                  'driver_id': 'park-without-active-brandings_driveruuid1',
                  'db_id': 'dead0000food0000beef0000dead0000',
                  'tariff_category_id': 'category_id',
                  'available_tariff_classes': [],
                  'profile_payment_type_restrictions': 'none',
                  'zone': 'some_geoarea_from_db',
                  'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
              },
              'source': None,
              'status': 'finished',
              'subvention_geoareas': [
                  'geoarea_1',
                  'geoarea_2',
                  'geoarea_no_area',
              ],
              'tags': ['fleet_park_rating'],
              'tariff_class': 'econom',
              'taxi_status': 'expired',
              'total_distance': 0,
              'total_time': 0,
              'park_corp_vat': None,
              'zone': 'moscow',
              'price_modifiers': [],
              'updated': '2018-11-01T00:00:00.000000+00:00',
              'park_ride_sum': '0',
              'coupon': {
                  'amount': '0',
                  'currency': 'RUB',
                  'netting_allowed': True,
                  'for_support': None,
              },
              'reason': None,
              'driver_workshift_ids': [
                  'no_usages_driver_workshift_id',
                  'usages_driver_workshift_id',
              ],
              'driver_promocode': {
                  'id': 'promo_id1',
                  'is_support_series': True,
              },
              'fleet_subscription_level': (
                  'fleet_subscription_level'
              ),
              'oebs_mvp_id': 'MSKc',
              'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
          },
          {
              'usages_driver_workshift_id': ['order_id_8']
          },
          False,
          False,
      ),
      # tags/subvention_geoareas are fetched from tags-service/mongo
      (
        'order_completed',
        'order_id_9',
        None,
        None,
        {
            'accepted_by_driver_at': '2018-10-17T16:10:53.921000+00:00',
            'billing_at': '2018-10-17T16:10:53.921000+00:00',
            'alias_id': 'alias_id_9',
            'billing_contract_is_set': True,
            'billing_contract': {
                'donate_multiplier': '1',
                'offer_currency': 'RUB',
                'currency_rate': '1',
                'offer_currency_rate': '1',
                'currency': 'RUB',
                'acquiring_percent': '0',
                'rebate_percent': '0',
                'ind_bel_nds_percent': None,
                'subventions_hold_delay': 0
            },
            'closed_without_accept': False,
            'completed_at': '2018-10-17T17:59:38.834000+00:00',
            'completed_by_dispatcher': False,
            'cost': {'amount': '1041.0', 'currency': 'RUB'},
            'created': '2018-10-17T16:10:42.631000+00:00',
            'discount': {
                'method': 'subvention-fix',
                'rate': 0.01,
            },
            'driver_cost': None,
            'due': '2018-10-17T16:14:00.000000+00:00',
            'has_co_branding': False,
            'has_lightbox': True,
            'has_sticker': True,
            'is_mqc': False,
            'order_id': 'order_id_9',
            'payment_type': 'card',
            'park': {
                'brandings': ["lightbox", "franchise"]
            },
            'performer': {
                'activity_points': 82,
                'unique_driver_id': '5bcf22169830073fda1ebc2c',
                'driver_license': 'AAA007X',
                'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                'driver_id': 'park-with-several-brandings_driveruuid',
                'db_id': 'dead0000food0000beef0000dead0000',
                'tariff_category_id': 'category_id',
                'hired_at': '2018-09-19T18:19:14.743000+00:00',
                'hiring_type': 'commercial',
                'available_tariff_classes': [
                    "econom",
                    "comfort"
                ],
                'profile_payment_type_restrictions': 'none',
                'zone': 'some_geoarea_from_db',
                'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
            },
            'source': None,
            'status': 'finished',
            'subvention_geoareas': [
                'geoarea_1',
                'geoarea_2',
                'geoarea_no_area',
            ],
            'tags': ["some_tag", "fleet_park_rating"],
            'tariff_class': 'econom',
            'taxi_status': 'complete',
            'total_distance': 41882.9765625,
            'total_time': 6107.596,
            'park_corp_vat': None,
            'zone': 'moscow',
            'price_modifiers': [],
            'updated': '2018-10-17T17:14:00.000000+00:00',
            'park_ride_sum': '100',
            'coupon': {
                'amount': '75.6',
                'currency': 'RUB',
                'netting_allowed': False,
                'for_support': False,
            },
            'reason': None,
            'childseat_rental': {
                'count': 1,
                'cost': "51"
            },
            'driver_workshift_ids': [],
            'fleet_subscription_level': (
                'fleet_subscription_level'
            ),
            'oebs_mvp_id': 'MSKc',
            'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
        },
        {},
        False,
        False,
      ),
      # decoupling
      (
        'order_completed',
        'order_id_10_decoupling',
        None,
        None,
        {
            'accepted_by_driver_at': '2018-10-17T16:10:53.921000+00:00',
            'billing_at': '2018-10-17T16:10:53.921000+00:00',
            'alias_id': 'alias_id_10_decoupling',
            'billing_contract_is_set': True,
            'billing_contract': {
                'donate_multiplier': '1',
                'offer_currency': 'RUB',
                'currency_rate': '1',
                'offer_currency_rate': '1',
                'currency': 'RUB',
                'acquiring_percent': '0',
                'rebate_percent': '0',
                'ind_bel_nds_percent': None,
                'subventions_hold_delay': 0
            },
            'closed_without_accept': False,
            'completed_at': '2018-10-17T17:59:38.834000+00:00',
            'completed_by_dispatcher': False,
            'cost': {'amount': '1041.0', 'currency': 'RUB'},
            'created': '2018-10-17T16:10:42.631000+00:00',
            'discount': {
                'method': 'subvention-fix',
                'rate': 0.01,
            },
            'driver_cost': None,
            'due': '2018-10-17T16:14:00.000000+00:00',
            'has_co_branding': False,
            'has_lightbox': True,
            'has_sticker': True,
            'is_mqc': False,
            'order_id': 'order_id_10_decoupling',
            'payment_type': 'corp',
            'park': {
                'brandings': ["lightbox", "franchise"]
            },
            'performer': {
                'activity_points': 82,
                'unique_driver_id': '5bcf22169830073fda1ebc2c',
                'driver_license': 'AAA007X',
                'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                'driver_id': 'park-with-several-brandings_driveruuid',
                'db_id': 'dead0000food0000beef0000dead0000',
                'tariff_category_id': 'category_id',
                'hired_at': '2018-09-19T18:19:14.743000+00:00',
                'hiring_type': 'commercial',
                'available_tariff_classes': [
                    "econom",
                    "comfort"
                ],
                'profile_payment_type_restrictions': 'none',
                'zone': 'some_geoarea_from_db',
                'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
            },
            'source': None,
            'status': 'finished',
            'subvention_geoareas': [
                'geoarea_1',
                'geoarea_2',
                'geoarea_no_area',
            ],
            'tags': ["some_tag", "fleet_park_rating", "cargo_order_tag"],
            'tariff_class': 'econom',
            'taxi_status': 'complete',
            'total_distance': 41882.9765625,
            'total_time': 6107.596,
            'park_corp_vat': None,
            'zone': 'moscow',
            'price_modifiers': [],
            'updated': '2018-10-17T17:14:00.000000+00:00',
            'park_ride_sum': '100',
            'coupon': {
                'amount': '75.6',
                'currency': 'RUB',
                'netting_allowed': False,
                'for_support': True,
            },
            'reason': None,
            'childseat_rental': {
                'count': 1,
                'cost': "51"
            },
            'driver_workshift_ids': [],
            'cost_for_driver': '90',
            'fleet_subscription_level': (
                'fleet_subscription_level'
            ),
            'oebs_mvp_id': 'MSKc',
            'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
        },
        {},
        False,
        False,
      ),
      # decoupling with rebate
      (  # rebate add enabled
        'order_completed',
        'order_id_10_decoupling_with_rebate',
        None,
        None,
        {
            'accepted_by_driver_at': '2018-10-17T16:10:53.921000+00:00',
            'billing_at': '2018-10-17T16:10:53.921000+00:00',
            'alias_id': 'alias_id_10_decoupling_with_rebate',
            'billing_contract_is_set': True,
            'billing_contract': {
                'donate_multiplier': '1',
                'offer_currency': 'RUB',
                'currency_rate': '1',
                'offer_currency_rate': '1',
                'currency': 'RUB',
                'acquiring_percent': '0',
                'rebate_percent': '0.01',
                'ind_bel_nds_percent': None,
                'subventions_hold_delay': 0
            },
            'closed_without_accept': False,
            'completed_at': '2018-10-17T17:59:38.834000+00:00',
            'completed_by_dispatcher': False,
            'cost': {'amount': '1041.0', 'currency': 'RUB'},
            'created': '2018-10-17T16:10:42.631000+00:00',
            'discount': {
                'method': 'subvention-fix',
                'rate': 0.01,
            },
            'driver_cost': None,
            'due': '2018-10-17T16:14:00.000000+00:00',
            'has_co_branding': False,
            'has_lightbox': True,
            'has_sticker': True,
            'is_mqc': False,
            'order_id': 'order_id_10_decoupling_with_rebate',
            'payment_type': 'corp',
            'park': {
                'brandings': ["lightbox", "franchise"]
            },
            'performer': {
                'activity_points': 82,
                'unique_driver_id': '5bcf22169830073fda1ebc2c',
                'driver_license': 'AAA007X',
                'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                'driver_id': 'park-with-several-brandings_driveruuid',
                'db_id': 'dead0000food0000beef0000dead0000',
                'tariff_category_id': 'category_id',
                'hired_at': '2018-09-19T18:19:14.743000+00:00',
                'hiring_type': 'commercial',
                'available_tariff_classes': [
                    "econom",
                    "comfort"
                ],
                'profile_payment_type_restrictions': 'none',
                'zone': 'some_geoarea_from_db',
                'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
            },
            'source': None,
            'status': 'finished',
            'subvention_geoareas': [
                'geoarea_1',
                'geoarea_2',
                'geoarea_no_area',
            ],
            'tags': ["some_tag", "fleet_park_rating"],
            'tariff_class': 'econom',
            'taxi_status': 'complete',
            'total_distance': 41882.9765625,
            'total_time': 6107.596,
            'park_corp_vat': None,
            'zone': 'moscow',
            'price_modifiers': [],
            'updated': '2018-10-17T17:14:00.000000+00:00',
            'park_ride_sum': '100',
            'coupon': {
                'amount': '75.6',
                'currency': 'RUB',
                'netting_allowed': False,
                'for_support': True,
            },
            'reason': None,
            'childseat_rental': {
                'count': 1,
                'cost': "51"
            },
            'driver_workshift_ids': [],
            'cost_for_driver': '90',
            'fleet_subscription_level': (
                'fleet_subscription_level'
            ),
            'oebs_mvp_id': 'MSKc',
            'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
        },
        {},
        True,
        False,
      ),
      (  # rebate add disabled
        'order_completed',
        'order_id_10_decoupling_with_rebate',
        None,
        None,
        {
            'accepted_by_driver_at': '2018-10-17T16:10:53.921000+00:00',
            'billing_at': '2018-10-17T16:10:53.921000+00:00',
            'alias_id': 'alias_id_10_decoupling_with_rebate',
            'billing_contract_is_set': True,
            'billing_contract': {
                'donate_multiplier': '1',
                'offer_currency': 'RUB',
                'currency_rate': '1',
                'offer_currency_rate': '1',
                'currency': 'RUB',
                'acquiring_percent': '0',
                'rebate_percent': '0.01',
                'ind_bel_nds_percent': None,
                'subventions_hold_delay': 0
            },
            'closed_without_accept': False,
            'completed_at': '2018-10-17T17:59:38.834000+00:00',
            'completed_by_dispatcher': False,
            'cost': {'amount': '1041.0', 'currency': 'RUB'},
            'created': '2018-10-17T16:10:42.631000+00:00',
            'discount': {
                'method': 'subvention-fix',
                'rate': 0.01,
            },
            'driver_cost': None,
            'due': '2018-10-17T16:14:00.000000+00:00',
            'has_co_branding': False,
            'has_lightbox': True,
            'has_sticker': True,
            'is_mqc': False,
            'order_id': 'order_id_10_decoupling_with_rebate',
            'payment_type': 'corp',
            'park': {
                'brandings': ["lightbox", "franchise"]
            },
            'performer': {
                'activity_points': 82,
                'unique_driver_id': '5bcf22169830073fda1ebc2c',
                'driver_license': 'AAA007X',
                'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                'driver_id': 'park-with-several-brandings_driveruuid',
                'db_id': 'dead0000food0000beef0000dead0000',
                'tariff_category_id': 'category_id',
                'hired_at': '2018-09-19T18:19:14.743000+00:00',
                'hiring_type': 'commercial',
                'available_tariff_classes': [
                    "econom",
                    "comfort"
                ],
                'profile_payment_type_restrictions': 'none',
                'zone': 'some_geoarea_from_db',
                'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
            },
            'source': None,
            'status': 'finished',
            'subvention_geoareas': [
                'geoarea_1',
                'geoarea_2',
                'geoarea_no_area',
            ],
            'tags': ["some_tag", "fleet_park_rating"],
            'tariff_class': 'econom',
            'taxi_status': 'complete',
            'total_distance': 41882.9765625,
            'total_time': 6107.596,
            'park_corp_vat': None,
            'zone': 'moscow',
            'price_modifiers': [],
            'updated': '2018-10-17T17:14:00.000000+00:00',
            'park_ride_sum': '90',
            'coupon': {
                'amount': '75.6',
                'currency': 'RUB',
                'netting_allowed': False,
                'for_support': True,
            },
            'reason': None,
            'childseat_rental': {
                'count': 1,
                'cost': "51"
            },
            'driver_workshift_ids': [],
            'cost_for_driver': '81',
            'fleet_subscription_level': (
                'fleet_subscription_level'
            ),
            'oebs_mvp_id': 'MSKc',
            'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
        },
        {},
        False,
        False,
      ),
      # vendor_id
      (
          'order_completed',
          'order_id_11_vendor_id',
          None,
          None,
          {
              'accepted_by_driver_at': '2018-10-17T16:10:53.921000+00:00',
              'billing_at': '2018-10-17T16:10:53.921000+00:00',
              'alias_id': 'alias_id_11_vendor_id',
              'billing_contract_is_set': True,
              'billing_contract': {
                  'donate_multiplier': '1',
                  'offer_currency': 'RUB',
                  'currency_rate': '1',
                  'offer_currency_rate': '1',
                  'currency': 'RUB',
                  'acquiring_percent': '0',
                  'rebate_percent': '0',
                  'ind_bel_nds_percent': None,
                  'subventions_hold_delay': 0
              },
              'closed_without_accept': False,
              'completed_at': '2018-10-17T17:59:38.834000+00:00',
              'completed_by_dispatcher': False,
              'cost': {'amount': '1041.0', 'currency': 'RUB'},
              'created': '2018-10-17T16:10:42.631000+00:00',
              'discount': {
                  'method': 'subvention-fix',
                  'rate': 0.01,
              },
              'driver_cost': None,
              'due': '2018-10-17T16:14:00.000000+00:00',
              'has_co_branding': False,
              'has_lightbox': True,
              'has_sticker': True,
              'is_mqc': False,
              'order_id': 'order_id_11_vendor_id',
              'payment_type': 'card',
              'park': {
                  'brandings': ["lightbox", "franchise"]
              },
              'performer': {
                  'activity_points': 82,
                  'unique_driver_id': '5bcf22169830073fda1ebc2c',
                  'driver_license': 'AAA007X',
                  'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                  'driver_id': 'park-with-several-brandings_driveruuid',
                  'db_id': 'dead0000food0000beef0000dead0000',
                  'tariff_category_id': 'category_id',
                  'hired_at': '2018-09-19T18:19:14.743000+00:00',
                  'hiring_type': 'commercial',
                  'available_tariff_classes': [
                      "econom",
                      "comfort"
                  ],
                  'profile_payment_type_restrictions': 'none',
                  'zone': 'some_geoarea_from_db',
                  'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
              },
              'source': None,
              'status': 'finished',
              'subvention_geoareas': [
                  'geoarea_1',
                  'geoarea_2',
                  'geoarea_no_area',
              ],
              'tags': ["some_tag", "fleet_park_rating"],
              'tariff_class': 'econom',
              'taxi_status': 'complete',
              'total_distance': 41882.9765625,
              'total_time': 6107.596,
              'park_corp_vat': None,
              'zone': 'moscow',
              'price_modifiers': [],
              'updated': '2018-10-17T17:14:00.000000+00:00',
              'park_ride_sum': '100',
              'coupon': {
                  'amount': '75.6',
                  'currency': 'RUB',
                  'netting_allowed': False,
                  'for_support': None,
              },
              'reason': None,
              'childseat_rental': {
                  'count': 1,
                  'cost': "51"
              },
              'driver_workshift_ids': [],
              'fleet_subscription_level': (
                  'fleet_subscription_level'
              ),
              'oebs_mvp_id': 'MSKc',
              'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
          },
          {},
          False,
          False,
      ),
      (
          'order_completed',
          'order_with_no_driver_zone',
          {'kind': 'completed', 'data': {}},
          None,
          {
              'accepted_by_driver_at': '2018-10-17T16:10:53.921000+00:00',
              'billing_at': '2018-10-17T16:10:53.921000+00:00',
              'alias_id': 'alias_id_1',
              'billing_contract_is_set': True,
              'billing_contract': {
                  'donate_multiplier': '1',
                  'offer_currency': 'RUB',
                  'currency_rate': '1',
                  'offer_currency_rate': '1',
                  'currency': 'RUB',
                  'acquiring_percent': '0',
                  'rebate_percent': '0',
                  'ind_bel_nds_percent': None,
                  'subventions_hold_delay': 0
              },
              'closed_without_accept': False,
              'completed_at': '2018-10-17T17:59:38.834000+00:00',
              'completed_by_dispatcher': False,
              'cost': {'amount': '1041.0', 'currency': 'RUB'},
              'created': '2018-10-17T16:10:42.631000+00:00',
              'discount': {
                  'method': 'subvention-fix',
                  'rate': 0.01,
              },
              'driver_cost': None,
              'due': '2018-10-17T16:14:00.000000+00:00',
              'has_co_branding': False,
              'has_lightbox': True,
              'has_sticker': True,
              'is_mqc': False,
              'order_id': 'order_with_no_driver_zone',
              'payment_type': 'card',
              'park': {
                  'brandings': ["lightbox", "franchise"]
              },
              'performer': {
                  'activity_points': 82,
                  'unique_driver_id': '5bcf22169830073fda1ebc2c',
                  'driver_license': 'AAA007X',
                  'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                  'driver_id': 'park-with-several-brandings_driveruuid',
                  'db_id': 'dead0000food0000beef0000dead0000',
                  'tariff_category_id': 'category_id',
                  'hired_at': '2018-09-19T18:19:14.743000+00:00',
                  'hiring_type': 'commercial',
                  'available_tariff_classes': [
                      "econom",
                      "comfort"
                  ],
                  'profile_payment_type_restrictions': 'none',
                  'zone': 'moscow',
                  'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm/moscow',
              },
              'source': None,
              'status': 'finished',
              'subvention_geoareas': [
                  'geoarea_1',
                  'geoarea_2',
                  'geoarea_no_area',
              ],
              'tags': ["some_tag", "fleet_park_rating"],
              'tariff_class': 'econom',
              'taxi_status': 'complete',
              'total_distance': 41882.9765625,
              'total_time': 6107.596,
              'park_corp_vat': None,
              'zone': 'moscow',
              'price_modifiers': [],
              'updated': '2018-10-17T17:14:00.000000+00:00',
              'park_ride_sum': '100',
              'coupon': {
                  'amount': '75.6',
                  'currency': 'RUB',
                  'netting_allowed': False,
                  'for_support': None,
              },
              'reason': {
                  'kind': 'completed',
                  'data': {}
              },
              'childseat_rental': {
                  'count': 1,
                  'cost': "51"
              },
              'driver_workshift_ids': [],
              'fleet_subscription_level': (
                  'fleet_subscription_level'
              ),
              'oebs_mvp_id': 'MSKc',
              'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
          },
          {},
          False,
          False,
      ),
      (
          'order_amended',
          'order_id_1',
          {'kind': 'completed', 'data': {}},
          None,
          {
              'status': 'finished',
              'total_time': 6107.596,
              'updated': '2018-10-17T17:14:00.000000+00:00',
              'performer': {
                  'db_id': 'dead0000food0000beef0000dead0000',
                  'tariff_category_id': 'category_id',
                  'driver_id': 'park-with-several-brandings_driveruuid',
                  'driver_license': 'AAA007X',
                  'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                  'hired_at': '2018-09-19T18:19:14.743000+00:00',
                  'zone': 'some_geoarea_from_db',
                  'profile_payment_type_restrictions': 'none',
                  'hiring_type': 'commercial',
                  'unique_driver_id': '5bcf22169830073fda1ebc2c',
                  'activity_points': 82,
                  'available_tariff_classes': ['econom', 'comfort'],
                  'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
              },
              'has_co_branding': False,
              'tags': ['some_tag', 'fleet_park_rating'],
              'order_id': 'order_id_1',
              'has_lightbox': True,
              'alias_id': 'alias_id_1',
              'subvention_geoareas': [
                  'geoarea_1',
                  'geoarea_2',
                  'geoarea_no_area',
              ],
              'completed_at': '2018-10-17T17:59:38.834000+00:00',
              'taxi_status': 'complete',
              'cost': {'currency': 'RUB', 'amount': '1041.0'},
              'childseat_rental': {'count': 1, 'cost': '51'},
              'total_distance': 41882.9765625,
              'billing_contract_is_set': True,
              'closed_without_accept': False,
              'has_sticker': True,
              'completed_by_dispatcher': False,
              'driver_cost': None,
              'zone': 'moscow',
              'created': '2018-10-17T16:10:42.631000+00:00',
              'driver_workshift_ids': [],
              'park_ride_sum': '100',
              'due': '2018-10-17T16:14:00.000000+00:00',
              'is_mqc': False,
              'billing_at': '2018-10-17T16:10:53.921000+00:00',
              'source': None,
              'billing_contract': {
                  'currency': 'RUB',
                  'acquiring_percent': '0',
                  'donate_multiplier': '1',
                  'offer_currency': 'RUB',
                  'currency_rate': '1',
                  'rebate_percent': '0',
                  'ind_bel_nds_percent': None,
                  'subventions_hold_delay': 0,
                  'offer_currency_rate': '1',
              },
              'accepted_by_driver_at': '2018-10-17T16:10:53.921000+00:00',
              'coupon': {
                  'currency': 'RUB',
                  'amount': '75.6',
                  'netting_allowed': False,
                  'for_support': None,
              },
              'payment_type': 'card',
              'price_modifiers': [],
              'reason': {'kind': 'completed', 'data': {}},
              'park_corp_vat': None,
              'tariff_class': 'econom',
              'discount': {
                  'rate': 0.01,
                  'method': 'subvention-fix',
              },
              'park': {'brandings': ['lightbox', 'franchise']},
              'fleet_subscription_level': (
                  'fleet_subscription_level'
              ),
              'oebs_mvp_id': 'MSKc',
              'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
          },
          {},
          False,
          False,
      ),
      (
          'order_completed',
          'order_id_12',
          {'kind': 'completed', 'data': {}},
          None,
          {
              'accepted_by_driver_at': '2018-10-17T16:10:53.921000+00:00',
              'billing_at': '2018-10-17T16:10:53.921000+00:00',
              'alias_id': 'alias_id_1',
              'billing_contract_is_set': True,
              'billing_contract': {
                  'donate_multiplier': '1',
                  'offer_currency': 'RUB',
                  'currency_rate': '1',
                  'offer_currency_rate': '1',
                  'currency': 'RUB',
                  'acquiring_percent': '0',
                  'rebate_percent': '0',
                  'ind_bel_nds_percent': None,
                  'subventions_hold_delay': 0
              },
              'closed_without_accept': False,
              'completed_at': '2018-10-17T17:59:38.834000+00:00',
              'completed_by_dispatcher': False,
              'cost': {'amount': '1041.0', 'currency': 'RUB'},
              'created': '2018-10-17T16:10:42.631000+00:00',
              'discount': {
                  'method': 'subvention-fix',
                  'rate': 0.01,
              },
              'driver_cost': None,
              'due': '2018-10-17T16:14:00.000000+00:00',
              'has_co_branding': False,
              'has_lightbox': True,
              'has_sticker': True,
              'is_mqc': False,
              'order_id': 'order_id_12',
              'payment_type': 'card',
              'park': {
                  'brandings': ["lightbox", "franchise"]
              },
              'performer': {
                  'activity_points': 82,
                  'unique_driver_id': '5bcf22169830073fda1ebc2c',
                  'driver_license': 'AAA007X',
                  'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                  'driver_id': 'park-with-several-brandings_driveruuid',
                  'db_id': 'dead0000food0000beef0000dead0000',
                  'tariff_category_id': 'category_id',
                  'hired_at': '2018-09-19T18:19:14.743000+00:00',
                  'hiring_type': 'commercial',
                  'available_tariff_classes': [
                      "econom",
                      "comfort"
                  ],
                  'profile_payment_type_restrictions': 'none',
                  'zone': 'some_geoarea_from_db',
                  'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
              },
              'source': None,
              'status': 'finished',
              'subvention_geoareas': [
                  'geoarea_1',
                  'geoarea_2',
                  'geoarea_no_area',
              ],
              'tags': ["some_tag", "fleet_park_rating"],
              'tariff_class': 'econom',
              'taxi_status': 'complete',
              'total_distance': 41882.9765625,
              'total_time': 6107.596,
              'park_corp_vat': None,
              'zone': 'moscow',
              'price_modifiers': [],
              'updated': '2018-10-17T17:14:00.000000+00:00',
              'park_ride_sum': '100',
              'coupon': {
                  'amount': '75.6',
                  'currency': 'RUB',
                  'netting_allowed': False,
                  'for_support': None,
              },
              'reason': {
                  'kind': 'completed',
                  'data': {}
              },
              'childseat_rental': {
                  'count': 1,
                  'cost': "51"
              },
              'driver_workshift_ids': [],
              'fleet_subscription_level': (
                  'fleet_subscription_level'
              ),
              'oebs_mvp_id': 'MSKc',
              'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
          },
          {},
          False,
          False,
      ),
      (
          'order_completed',
          'order_with_just_partner_payments',
          {'kind': 'completed', 'data': {}},
          None,
          {
              'accepted_by_driver_at': '2018-10-17T16:10:53.921000+00:00',
              'billing_at': '2018-10-17T16:10:53.921000+00:00',
              'alias_id': 'alias_id_1',
              'billing_contract_is_set': True,
              'billing_contract': {
                  'donate_multiplier': '1',
                  'offer_currency': 'RUB',
                  'currency_rate': '1',
                  'offer_currency_rate': '1',
                  'currency': 'RUB',
                  'acquiring_percent': '0',
                  'rebate_percent': '0',
                  'ind_bel_nds_percent': None,
                  'subventions_hold_delay': 0
              },
              'closed_without_accept': False,
              'completed_at': '2018-10-17T17:59:38.834000+00:00',
              'completed_by_dispatcher': False,
              'cost': {'amount': '1041.0', 'currency': 'RUB'},
              'created': '2018-10-17T16:10:42.631000+00:00',
              'discount': {
                  'method': 'subvention-fix',
                  'rate': 0.01,
              },
              'driver_cost': None,
              'due': '2018-10-17T16:14:00.000000+00:00',
              'has_co_branding': False,
              'has_lightbox': True,
              'has_sticker': True,
              'is_mqc': False,
              'order_id': 'order_with_just_partner_payments',
              'payment_type': 'card',
              'park': {
                  'brandings': ["lightbox", "franchise"]
              },
              'performer': {
                  'activity_points': 82,
                  'unique_driver_id': '5bcf22169830073fda1ebc2c',
                  'driver_license': 'AAA007X',
                  'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                  'driver_id': 'park-with-several-brandings_driveruuid',
                  'db_id': 'dead0000food0000beef0000dead0000',
                  'tariff_category_id': 'category_id',
                  'hired_at': '2018-09-19T18:19:14.743000+00:00',
                  'hiring_type': 'commercial',
                  'available_tariff_classes': [
                      "econom",
                      "comfort"
                  ],
                  'profile_payment_type_restrictions': 'none',
                  'zone': 'some_geoarea_from_db',
                  'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
              },
              'source': None,
              'status': 'finished',
              'subvention_geoareas': [
                  'geoarea_1',
                  'geoarea_2',
                  'geoarea_no_area',
              ],
              'tags': ["some_tag", "fleet_park_rating"],
              'tariff_class': 'econom',
              'taxi_status': 'complete',
              'total_distance': 41882.9765625,
              'total_time': 6107.596,
              'park_corp_vat': None,
              'zone': 'moscow',
              'price_modifiers': [],
              'updated': '2018-10-17T17:14:00.000000+00:00',
              'park_ride_sum': '100',
              'coupon': {
                  'amount': '75.6',
                  'currency': 'RUB',
                  'netting_allowed': False,
                  'for_support': None,
              },
              'reason': {
                  'kind': 'completed',
                  'data': {}
              },
              'childseat_rental': {
                  'count': 1,
                  'cost': "51"
              },
              'driver_workshift_ids': [],
              'fleet_subscription_level': (
                  'fleet_subscription_level'
              ),
              'oebs_mvp_id': 'MSKc',
              'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
          },
          {},
          False,
          False,
      ),
      (
          'order_completed',
          'order_id_with_new_pricing_meta',
          {'kind': 'completed', 'data': {}},
          None,
          {
              'accepted_by_driver_at': '2018-10-17T16:10:53.921000+00:00',
              'billing_at': '2018-10-17T16:10:53.921000+00:00',
              'alias_id': 'alias_id_order_id_with_new_pricing_meta',
              'billing_contract_is_set': True,
              'billing_contract': {
                  'donate_multiplier': '1',
                  'offer_currency': 'RUB',
                  'currency_rate': '1',
                  'offer_currency_rate': '1',
                  'currency': 'RUB',
                  'acquiring_percent': '0',
                  'rebate_percent': '0',
                  'ind_bel_nds_percent': None,
                  'subventions_hold_delay': 0
              },
              'closed_without_accept': False,
              'completed_at': '2018-10-17T17:59:38.834000+00:00',
              'completed_by_dispatcher': False,
              'cost': {'amount': '1116.6', 'currency': 'RUB'},
              'created': '2018-10-17T16:10:42.631000+00:00',
              'discount': {
                  'method': 'subvention-fix',
                  'rate': 0.01,
              },
              'driver_cost': None,
              'due': '2018-10-17T16:14:00.000000+00:00',
              'has_co_branding': False,
              'has_lightbox': True,
              'has_sticker': True,
              'is_mqc': False,
              'order_id': 'order_id_with_new_pricing_meta',
              'payment_type': 'card',
              'park': {
                  'brandings': ["lightbox", "franchise"]
              },
              'performer': {
                  'activity_points': 82,
                  'unique_driver_id': '5bcf22169830073fda1ebc2c',
                  'driver_license': 'AAA007X',
                   'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                  'driver_id': 'park-with-several-brandings_driveruuid',
                  'db_id': 'dead0000food0000beef0000dead0000',
                  'tariff_category_id': 'category_id',
                  'hired_at': '2018-09-19T18:19:14.743000+00:00',
                  'hiring_type': 'commercial',
                  'available_tariff_classes': [
                      "econom",
                      "comfort"
                  ],
                  'profile_payment_type_restrictions': 'none',
                  'zone': 'some_geoarea_from_db',
                  'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
              },
              'source': None,
              'status': 'finished',
              'subvention_geoareas': [
                  'geoarea_1',
                  'geoarea_2',
                  'geoarea_no_area',
              ],
              'tags': ["some_tag", "fleet_park_rating"],
              'tariff_class': 'econom',
              'taxi_status': 'complete',
              'total_distance': 41882.9765625,
              'total_time': 6107.596,
              'park_corp_vat': None,
              'zone': 'moscow',
              'price_modifiers': [],
              'updated': '2018-10-17T17:14:00.000000+00:00',
              'park_ride_sum': '100',
              'coupon': {
                  'amount': '75.6',
                  'currency': 'RUB',
                  'netting_allowed': False,
                  'for_support': None,
              },
              'reason': {
                  'kind': 'completed',
                  'data': {}
              },
              'childseat_rental': {
                  'count': 1,
                  'cost': "51"
              },
              'driver_workshift_ids': [],
              'fleet_subscription_level': (
                  'fleet_subscription_level'
              ),
              'oebs_mvp_id': 'MSKc',
              'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
          },
          {},
          False,
          False,
      ),
      (
          'order_completed',
          'archive_only',
          {'kind': 'completed', 'data': {}},
          None,
          {
              'accepted_by_driver_at': '2018-10-17T16:10:53.921000+00:00',
              'billing_at': '2018-10-17T16:10:53.921000+00:00',
              'alias_id': 'alias_id_order_id_with_new_pricing_meta',
              'billing_contract_is_set': True,
              'billing_contract': {
                  'donate_multiplier': '1',
                  'offer_currency': 'RUB',
                  'currency_rate': '1',
                  'offer_currency_rate': '1',
                  'currency': 'RUB',
                  'acquiring_percent': '0',
                  'rebate_percent': '0',
                  'ind_bel_nds_percent': None,
                  'subventions_hold_delay': 0
              },
              'closed_without_accept': False,
              'completed_at': '2018-10-17T17:59:38.834000+00:00',
              'completed_by_dispatcher': False,
              'cost': {'amount': '1116.6', 'currency': 'RUB'},
              'created': '2018-10-17T16:10:42.631000+00:00',
              'discount': {
                  'method': 'subvention-fix',
                  'rate': 0.01,
              },
              'driver_cost': None,
              'due': '2018-10-17T16:14:00.000000+00:00',
              'has_co_branding': False,
              'has_lightbox': True,
              'has_sticker': True,
              'is_mqc': False,
              'order_id': 'archive_only',
              'payment_type': 'card',
              'park': {
                  'brandings': ["lightbox", "franchise"]
              },
              'performer': {
                  'activity_points': 82,
                  'unique_driver_id': '5bcf22169830073fda1ebc2c',
                  'driver_license': 'AAA007X',
                   'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                  'driver_id': 'park-with-several-brandings_driveruuid',
                  'db_id': 'dead0000food0000beef0000dead0000',
                  'tariff_category_id': 'category_id',
                  'hired_at': '2018-09-19T18:19:14.743000+00:00',
                  'hiring_type': 'commercial',
                  'available_tariff_classes': [
                      "econom",
                      "comfort"
                  ],
                  'profile_payment_type_restrictions': 'none',
                  'zone': 'some_geoarea_from_db',
                  'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
              },
              'source': None,
              'status': 'finished',
              'subvention_geoareas': [
                  'geoarea_1',
                  'geoarea_2',
                  'geoarea_no_area',
              ],
              'tags': ["some_tag", "fleet_park_rating"],
              'tariff_class': 'econom',
              'taxi_status': 'complete',
              'total_distance': 41882.9765625,
              'total_time': 6107.596,
              'park_corp_vat': None,
              'zone': 'moscow',
              'price_modifiers': [],
              'updated': '2018-10-17T17:14:00.000000+00:00',
              'park_ride_sum': '100',
              'coupon': {
                  'amount': '75.6',
                  'currency': 'RUB',
                  'netting_allowed': False,
                  'for_support': None,
              },
              'reason': {
                  'kind': 'completed',
                  'data': {}
              },
              'childseat_rental': {
                  'count': 1,
                  'cost': "51"
              },
              'driver_workshift_ids': [],
              'fleet_subscription_level': (
                  'fleet_subscription_level'
              ),
              'oebs_mvp_id': 'MSKc',
              'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
          },
          {},
          False,
          False,
      ),
      (
          'order_completed',
          'order_id_cash',
          {'kind': 'completed', 'data': {}},
          {'payment_type_restrictions': 'cash'},
          {
              'accepted_by_driver_at': '2018-10-17T16:10:53.921000+00:00',
              'billing_at': '2018-10-17T16:10:53.921000+00:00',
              'alias_id': 'alias_id_1',
              'billing_contract_is_set': True,
              'billing_contract': {
                  'donate_multiplier': '1',
                  'offer_currency': 'RUB',
                  'currency_rate': '1',
                  'offer_currency_rate': '1',
                  'currency': 'RUB',
                  'acquiring_percent': '0',
                  'rebate_percent': '0',
                  'ind_bel_nds_percent': None,
                  'subventions_hold_delay': 0
              },
              'closed_without_accept': False,
              'completed_at': '2018-10-17T17:59:38.834000+00:00',
              'completed_by_dispatcher': False,
              'cost': {'amount': '1041.0', 'currency': 'RUB'},
              'created': '2018-10-17T16:10:42.631000+00:00',
              'discount': {
                  'method': 'subvention-fix',
                  'rate': 0.01,
              },
              'driver_cost': None,
              'due': '2018-10-17T16:14:00.000000+00:00',
              'has_co_branding': False,
              'has_lightbox': True,
              'has_sticker': True,
              'is_mqc': False,
              'order_id': 'order_id_cash',
              'payment_type': 'cash',
              'park': {
                  'brandings': ["lightbox", "franchise"]
              },
              'performer': {
                  'activity_points': 82,
                  'unique_driver_id': '5bcf22169830073fda1ebc2c',
                  'driver_license': 'AAA007X',
                  'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                  'driver_id': 'park-with-several-brandings_driveruuid',
                  'db_id': 'dead0000food0000beef0000dead0000',
                  'tariff_category_id': 'category_id',
                  'hired_at': '2018-09-19T18:19:14.743000+00:00',
                  'hiring_type': 'commercial',
                  'available_tariff_classes': [
                      "econom",
                      "comfort"
                  ],
                  'profile_payment_type_restrictions': 'cash',
                  'zone': 'some_geoarea_from_db',
                  'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
              },
              'source': None,
              'status': 'finished',
              'subvention_geoareas': [
                  'geoarea_1',
                  'geoarea_2',
                  'geoarea_no_area',
              ],
              'tags': ["some_tag", "fleet_park_rating"],
              'tariff_class': 'econom',
              'taxi_status': 'complete',
              'toll_road_payment_price': '50.0',
              'total_distance': 41882.9765625,
              'total_time': 6107.596,
              'park_corp_vat': None,
              'zone': 'moscow',
              'price_modifiers': [],
              'updated': '2018-10-17T17:14:00.000000+00:00',
              'park_ride_sum': '100',
              'coupon': {
                  'amount': '75.6',
                  'currency': 'RUB',
                  'netting_allowed': False,
                  'for_support': None,
              },
              'reason': {
                  'kind': 'completed',
                  'data': {}
              },
              'childseat_rental': {
                  'count': 1,
                  'cost': "51"
              },
              'driver_workshift_ids': [],
              'fleet_subscription_level': (
                  'fleet_subscription_level'
              ),
              'oebs_mvp_id': 'MSKc',
              'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
          },
          {},
          False,
          False,
      ),
      (
          'order_amended',
          'archive_only',
          {'kind': 'completed', 'data': {}},
          None,
          {
              'accepted_by_driver_at': '2018-10-17T16:10:53.921000+00:00',
              'billing_at': '2018-10-17T16:10:53.921000+00:00',
              'alias_id': 'alias_id_order_id_with_new_pricing_meta',
              'billing_contract_is_set': True,
              'billing_contract': {
                  'donate_multiplier': '1',
                  'offer_currency': 'RUB',
                  'currency_rate': '1',
                  'offer_currency_rate': '1',
                  'currency': 'RUB',
                  'acquiring_percent': '0',
                  'rebate_percent': '0',
                  'ind_bel_nds_percent': None,
                  'subventions_hold_delay': 0
              },
              'closed_without_accept': False,
              'completed_at': '2018-10-17T17:59:38.834000+00:00',
              'completed_by_dispatcher': False,
              'cost': {'amount': '1116.6', 'currency': 'RUB'},
              'created': '2018-10-17T16:10:42.631000+00:00',
              'discount': {
                  'method': 'subvention-fix',
                  'rate': 0.01,
              },
              'driver_cost': None,
              'due': '2018-10-17T16:14:00.000000+00:00',
              'has_co_branding': False,
              'has_lightbox': True,
              'has_sticker': True,
              'is_mqc': False,
              'order_id': 'archive_only',
              'payment_type': 'card',
              'park': {
                  'brandings': ["lightbox", "franchise"]
              },
              'performer': {
                  'activity_points': 82,
                  'unique_driver_id': '5bcf22169830073fda1ebc2c',
                  'driver_license': 'AAA007X',
                   'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                  'driver_id': 'park-with-several-brandings_driveruuid',
                  'db_id': 'dead0000food0000beef0000dead0000',
                  'tariff_category_id': 'category_id',
                  'hired_at': '2018-09-19T18:19:14.743000+00:00',
                  'hiring_type': 'commercial',
                  'available_tariff_classes': [
                      "econom",
                      "comfort"
                  ],
                  'profile_payment_type_restrictions': 'none',
                  'zone': 'some_geoarea_from_db',
                  'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
              },
              'source': None,
              'status': 'finished',
              'subvention_geoareas': [
                  'geoarea_1',
                  'geoarea_2',
                  'geoarea_no_area',
              ],
              'tags': ["some_tag", "fleet_park_rating"],
              'tariff_class': 'econom',
              'taxi_status': 'complete',
              'total_distance': 41882.9765625,
              'total_time': 6107.596,
              'park_corp_vat': None,
              'zone': 'moscow',
              'price_modifiers': [],
              'updated': '2018-10-17T17:14:00.000000+00:00',
              'park_ride_sum': '100',
              'coupon': {
                  'amount': '75.6',
                  'currency': 'RUB',
                  'netting_allowed': False,
                  'for_support': None,
              },
              'reason': {
                  'kind': 'completed',
                  'data': {}
              },
              'childseat_rental': {
                  'count': 1,
                  'cost': "51"
              },
              'driver_workshift_ids': [],
              'fleet_subscription_level': (
                  'fleet_subscription_level'
              ),
              'oebs_mvp_id': 'MSKc',
              'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
          },
          {},
          False,
          False,
      ),
      (
        'order_completed',
        'cargo_order',
        {'kind': 'completed', 'data': {}},
        None,
        {
            'accepted_by_driver_at': '2018-10-17T16:10:53.921000+00:00',
            'billing_at': '2018-10-17T16:10:53.921000+00:00',
            'alias_id': 'alias_id_cargo_order',
            'billing_contract_is_set': True,
            'billing_contract': {
                'donate_multiplier': '1',
                'offer_currency': 'RUB',
                'currency_rate': '1',
                'offer_currency_rate': '1',
                'currency': 'RUB',
                'acquiring_percent': '0',
                'rebate_percent': '0',
                'ind_bel_nds_percent': None,
                'subventions_hold_delay': 0
            },
            'closed_without_accept': False,
            'completed_at': '2018-10-17T17:59:38.834000+00:00',
            'completed_by_dispatcher': False,
            'cost': {'amount': '1116.6', 'currency': 'RUB'},
            'created': '2018-10-17T16:10:42.631000+00:00',
            'discount': {
                'method': 'subvention-fix',
                'rate': 0.01,
            },
            'driver_cost': None,
            'due': '2018-10-17T16:14:00.000000+00:00',
            'has_co_branding': False,
            'has_lightbox': True,
            'has_sticker': True,
            'is_mqc': False,
            'order_id': 'cargo_order',
            'payment_type': 'card',
            'park': {
                'brandings': ["lightbox", "franchise"]
            },
            'performer': {
                'activity_points': 82,
                'unique_driver_id': '5bcf22169830073fda1ebc2c',
                'driver_license': 'AAA007X',
                'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                'driver_id': 'park-with-several-brandings_driveruuid',
                'db_id': 'dead0000food0000beef0000dead0000',
                'tariff_category_id': 'category_id',
                'hired_at': '2018-09-19T18:19:14.743000+00:00',
                'hiring_type': 'commercial',
                'available_tariff_classes': [
                    "econom",
                    "comfort"
                ],
                'profile_payment_type_restrictions': 'none',
                'zone': 'some_geoarea_from_db',
                'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
            },
            'source': None,
            'status': 'finished',
            'subvention_geoareas': [
                'geoarea_1',
                'geoarea_2',
                'geoarea_no_area',
            ],
            'tags': ["some_tag", "fleet_park_rating"],
            'tariff_class': 'econom',
            'taxi_status': 'complete',
            'total_distance': 41882.9765625,
            'total_time': 6107.596,
            'park_corp_vat': None,
            'zone': 'moscow',
            'price_modifiers': [],
            'updated': '2018-10-17T17:14:00.000000+00:00',
            'park_ride_sum': '100',
            'coupon': {
                'amount': '75.6',
                'currency': 'RUB',
                'netting_allowed': False,
                'for_support': None,
            },
            'reason': {
                'kind': 'completed',
                'data': {}
            },
            'childseat_rental': {
                'count': 1,
                'cost': "51"
            },
            'driver_workshift_ids': [],
            'fleet_subscription_level': (
                    'fleet_subscription_level'
            ),
            'oebs_mvp_id': 'MSKc',
            'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
        },
        {},
        False,
        False,
      ),
      (
        'order_completed',
        'cargo_order',
        {'kind': 'completed', 'data': {}},
        None,
        {
            'accepted_by_driver_at': '2018-10-17T16:10:53.921000+00:00',
            'billing_at': '2018-10-17T16:10:53.921000+00:00',
            'alias_id': 'alias_id_cargo_order',
            'billing_contract_is_set': True,
            'billing_contract': {
                'donate_multiplier': '1',
                'offer_currency': 'RUB',
                'currency_rate': '1',
                'offer_currency_rate': '1',
                'currency': 'RUB',
                'acquiring_percent': '0',
                'rebate_percent': '0',
                'ind_bel_nds_percent': None,
                'subventions_hold_delay': 0
            },
            'closed_without_accept': False,
            'completed_at': '2018-10-17T17:59:38.834000+00:00',
            'completed_by_dispatcher': False,
            'cost': {'amount': '1116.6', 'currency': 'RUB'},
            'created': '2018-10-17T16:10:42.631000+00:00',
            'discount': {
                'method': 'subvention-fix',
                'rate': 0.01,
            },
            'driver_cost': None,
            'due': '2018-10-17T16:14:00.000000+00:00',
            'has_co_branding': False,
            'has_lightbox': True,
            'has_sticker': True,
            'is_mqc': False,
            'order_id': 'cargo_order',
            'payment_type': 'card',
            'cargo': {
                'visited_endpoints_count': 2
            },
            'park': {
                'brandings': ["lightbox", "franchise"]
            },
            'performer': {
                'activity_points': 82,
                'unique_driver_id': '5bcf22169830073fda1ebc2c',
                'driver_license': 'AAA007X',
                'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                'driver_id': 'park-with-several-brandings_driveruuid',
                'db_id': 'dead0000food0000beef0000dead0000',
                'tariff_category_id': 'category_id',
                'hired_at': '2018-09-19T18:19:14.743000+00:00',
                'hiring_type': 'commercial',
                'available_tariff_classes': [
                    "econom",
                    "comfort"
                ],
                'profile_payment_type_restrictions': 'none',
                'zone': 'some_geoarea_from_db',
                'geo_hierarchy': 'br_root/br_country/br_town/some_geoarea_from_db',
            },
            'source': None,
            'status': 'finished',
            'subvention_geoareas': [
                'geoarea_1',
                'geoarea_2',
                'geoarea_no_area',
            ],
            'tags': ["some_tag", "fleet_park_rating"],
            'tariff_class': 'econom',
            'taxi_status': 'complete',
            'total_distance': 41882.9765625,
            'total_time': 6107.596,
            'park_corp_vat': None,
            'zone': 'moscow',
            'price_modifiers': [],
            'updated': '2018-10-17T17:14:00.000000+00:00',
            'park_ride_sum': '100',
            'coupon': {
                'amount': '75.6',
                'currency': 'RUB',
                'netting_allowed': False,
                'for_support': None,
            },
            'reason': {
                'kind': 'completed',
                'data': {}
            },
            'childseat_rental': {
                'count': 1,
                'cost': "51"
            },
            'driver_workshift_ids': [],
            'fleet_subscription_level': (
                    'fleet_subscription_level'
            ),
            'oebs_mvp_id': 'MSKc',
            'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
        },
        {},
        False,
        True,
      ),
    ]
)
@pytest.mark.config(
    USE_ARCHIVE_FOR_ORDER_EVENTS=True,
    BRANDING_DISCOUNT_ENABLED=True,
    ENABLE_DRIVER_TAGS_FETCHING=True,
    ENABLE_GEOAREAS_SUBVENTIONS_FETCHING=True,
    ENABLE_GEOAREAS_SUBVENTIONS_SORT_BY_AREA_ASCENDING=True,
    USE_CANDIDATE_META=True,
    ADD_PERFORMER_ZONE_IN_ORDER_COMPLETED_EVENT=True,
    BILLING_AGGLOMERATION_DATA_TO_ORDER_COMPLETED=True,
    ADD_BILLING_AT_IN_ORDER_COMPLETED_EVENT=True,
    DRIVER_PROMOCODES_V2_BILLING_ENABLED=True,
    BILLING_WORKSHIFT_USAGES_IN_ORDER_EVENTS=True,
    BILLING_SAVE_PARK_CATEGORY_TO_ORDER_EVENT=True,
    BILLING_SAVE_PARK_RATING_TAG_TO_ORDER_EVENT=True,
    ADD_PERFORMER_GEOHIERARCHY_IN_ORDER_COMPLETED_EVENT=True,
    BILLING_ORDER_ADD_CALL_CENTER_COST=True,
)
@pytest.inline_callbacks
def test_prepare_event(
        patch, mocked_send_event, mocked_min_due, mocked_metadata_storage, event_type, proc_id, reason,
        candidate_meta, expected_event_data, expected_workshift_usages,
        mock, areq_request, add_rebate_to_decoupling, retrieve_cargo_info):

    @patch('taxi.external.archive.get_order_proc_by_id')
    @async.inline_callbacks
    def get_order_proc_by_id(order_id, lookup_yt=True, src_tvm_service=None,
                             log_extra=None):
        doc = yield dbh.order_proc.Doc.find_one_by_id('ARCHIVE-' + order_id)
        doc['_id'] = doc['_id'][8:]
        async.return_value({'doc': doc})

    @patch('taxi.external.archive.get_order')
    @async.inline_callbacks
    def get_order(order_id, lookup_yt=True, src_tvm_service=None,
                  log_extra=None):
        doc = yield dbh.orders.Doc.find_one_by_id('ARCHIVE-' + order_id)
        doc['_id'] = doc['_id'][8:]
        yield async.return_value({'doc': doc})

    @patch('taxi.config.ADD_REBATE_TO_DECOUPLING_IN_ORDER_COMPLETED_EVENT.get')
    @async.inline_callbacks
    def get():
        yield
        async.return_value(add_rebate_to_decoupling)

    @patch('taxi.config.SEND_CARGO_INFO_IN_ORDER_COMPLETED_AMENDED.get')
    @async.inline_callbacks
    def get_cargo_config():
        yield
        async.return_value(retrieve_cargo_info)

    order = yield archive.get_order(proc_id, as_dbh=True)
    proc = yield archive.get_order_proc_by_id(proc_id, as_dbh=True)

    @patch('taxi.external.driver_tags_service.drivers_tags_by_profile_match')
    @async.inline_callbacks
    def driver_tags_drivers_tags_by_profile_match(
            dbid, uuid, src_service, log_extra=None):
        assert proc.chosen_candidate.db_id == dbid
        assert proc.chosen_candidate.driver_uuid == uuid
        assert src_service == settings.STQ_TVM_SERVICE_NAME
        yield async.return_value(['some_tag'])

    @patch('taxi.external.candidate_meta.metadata_get')
    @async.inline_callbacks
    def metadata_get(
            order_id, park_id, driver_profile_id, log_extra=None):
        assert order_id == proc_id
        assert park_id == proc.chosen_candidate.db_id
        assert driver_profile_id == proc.chosen_candidate.driver_uuid
        yield async.return_value(candidate_meta)

    @patch('taxi.internal.dbh.subvention_geoareas.Doc.'
           'find_active_geoareas_in_point')
    @async.inline_callbacks
    def find_active_geoareas_in_point(point, fields=None):
        # there's only one proc that'll get here
        assert point == [
            37.6659699,
            55.7675672
        ]
        assert fields == ['_id', 'name', 'created', 'area']
        yield async.return_value([{'name': 'some_subvention_geoarea_from_db', 'area': 42.0}])

    @patch('taxi.external.taxi_protocol.nearest_zone')
    @async.inline_callbacks
    def nearest_zone(point, client_id=None, log_extra=None):
        assert(isinstance(point, list))
        if point == [37.0, 55.0]:
            # only for order with id 'order_with_no_driver_zone'
            raise taxi_protocol.NotFoundError()
        yield async.return_value('some_geoarea_from_db')

    @patch('taxi.external.driver_promocodes.get_active_promocodes')
    @async.inline_callbacks
    def get_active_promocodes(filters, src_service, log_extra=None):
        yield async.return_value([{
            'filter_id': 'alias_id_8',
            'is_support_series': True,
            'id': 'promo_id1',
            'entity_id':
                'dead0000food0000beef0000dead0000_park-without-active-brandings_driveruuid1'}])

    @patch('taxi.external.fleet_payouts.get_fleet_subscription_level')
    @async.inline_callbacks
    def get_fleet_subscription_level(*args, **kwargs):
        yield async.return_value({
                  'fleet_subscription_level': 'fleet_subscription_level',
                  'park_rating': 'park_rating',
              })

    @patch('taxi.external.driver_promocodes.add_order_usage')
    @async.inline_callbacks
    def add_order_usage(usages, src_service, log_extra=None):
        assert usages == [{
            'order_id': 'alias_id_8',
            'promocode_id': 'promo_id1'}]
        yield

    @patch('taxi.external.agglomerations.get_ancestors')
    @async.inline_callbacks
    def get_ancestors(tariff_zone, log_extra=None):
        yield async.return_value(
            [
                {"name": "br_town"},
                {"name": "br_country"},
                {"name": "br_root"},
            ],
        )

    @patch('taxi.internal.dbh.driver_workshifts.Doc.add_many')
    @async.inline_callbacks
    def add_many(workshift_usages):
        assert workshift_usages == expected_workshift_usages
        yield

    @patch('taxi.external.cargo_orders.retrieve_waybill_info')
    @async.inline_callbacks
    def retrieve_waybill_info(retrieve_waybill_info_request, log_extra=None):
        response = {
            'visited_endpoints_count': 2
        }
        yield async.return_value(response)

    yield order_events.prepare_event(
        event_type=event_type,
        order_id=proc_id,
        order_version=order.version,
        reason=reason,
    )
    if expected_event_data is None:
        expected_send_event_calls = []
    else:
        if event_type == 'order_completed':
            order_event_ref = event_type
        else:
            updated_str = expected_event_data['updated']
            updated = datetime.datetime.strptime(
                updated_str, '%Y-%m-%dT%H:%M:%S.%f+00:00'
            )
            order_event_ref = event_type + '/' + updated.isoformat()
        expected_send_event_calls = [
            {
                'args': (),
                'kwargs': {
                    'order_event_ref': order_event_ref,
                    'type_': event_type,
                    'data': expected_event_data,
                    'tvm_src_service': 'stq',
                    'log_extra': None,
                }
            }
        ]
        assert len(add_many.calls) == 1
    actual_send_event_calls = mocked_send_event.calls
    assert actual_send_event_calls == expected_send_event_calls


@pytest.mark.config(BILLING_ORDER_ADD_CALL_CENTER_COST=True)
@pytest.inline_callbacks
def test_call_center_info_filled_when_needed(
        mocked_send_event,
        mocked_min_due,
        mocked_metadata_storage,
):
    yield order_events.prepare_event(
        'order_completed',
        'call_center_order',
        3,
        None,
    )
    actual = mocked_send_event.calls[0]['kwargs']['data']
    assert actual['call_center'] == {'cost': '2.79179621983'}


@pytest.mark.config(
    USE_ARCHIVE_FOR_ORDER_EVENTS=True,
    BRANDING_DISCOUNT_ENABLED=True
)
@pytest.inline_callbacks
def test_old_order_is_ignored(mocked_send_event, mocked_prepare_event, mocked_min_due):
    order_id = 'order_id_7'
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    yield order_events.prepare_event(
        'order_completed', order_id, order.version, None)
    assert mocked_send_event.calls == []  # Not sent
    assert mocked_prepare_event.calls == []  # And not rescheduled


@pytest.mark.config(
    USE_ARCHIVE_FOR_ORDER_EVENTS=True,
    BRANDING_DISCOUNT_ENABLED=True
)
@pytest.inline_callbacks
def test_order_without_performer_is_ignored(
        mocked_send_event, mocked_prepare_event, mocked_min_due):
    order_id = 'order_without_performer_id'
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    yield order_events.prepare_event(
        'order_completed', order_id, order.version, None
    )
    assert mocked_send_event.calls == []  # Not sent
    assert mocked_prepare_event.calls == []  # And not rescheduled


@pytest.mark.config(
    USE_ARCHIVE_FOR_ORDER_EVENTS=True,
    BRANDING_DISCOUNT_ENABLED=True,
    ORDER_EVENT_PERFORMER_CHECK='proc_order',
)
@pytest.inline_callbacks
def test_order_without_performer_in_proc_order_is_ignored(
        mocked_send_event, mocked_prepare_event, mocked_min_due):
    order_id = 'no_proc_order_performer'
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    yield order_events.prepare_event(
        'order_completed', order_id, order.version, None
    )
    assert mocked_send_event.calls == []  # Not sent
    assert mocked_prepare_event.calls == []  # And not rescheduled


@pytest.mark.parametrize(
    'event_type,order_id',
    [('order_completed', 'order_id_1')]
)
@pytest.inline_callbacks
def test_order_version_mismatch(
        mocked_prepare_event, mocked_min_due, event_type, order_id):
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    yield order_events.prepare_event(
        event_type, order_id, 999, 'completed')
    expected_prepare_event_calls = [
        {
            'args': (),
            'kwargs': {
                'order_id': order.pk,
                'order_version': 999,
                'event_type': 'order_completed',
                'reason': 'completed',
                'log_extra': None,
            }
        }
    ]
    assert mocked_prepare_event.calls == expected_prepare_event_calls


@pytest.mark.parametrize(
    'event_type,order_id',
    [('order_completed', 'order_id_5')]
)
@pytest.inline_callbacks
def test_finish_not_handled(mocked_prepare_event, mocked_min_due, event_type, order_id):
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    yield order_events.prepare_event(event_type, order_id, order.version, None)
    expected_prepare_event_calls = [
        {
            'args': (),
            'kwargs': {
                'order_id': order.pk,
                'order_version': order.version,
                'event_type': 'order_completed',
                'reason': None,
                'log_extra': None,
            }
        }
    ]
    assert mocked_prepare_event.calls == expected_prepare_event_calls


@pytest.mark.parametrize(
    'event_type,order_id',
    [('order_completed', 'order_id_6')]
)
@pytest.inline_callbacks
def test_billing_contract_not_finalized(
        mocked_prepare_event, mocked_min_due, event_type, order_id):
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    yield order_events.prepare_event(event_type, order_id, order.version, None)
    expected_prepare_event_calls = [
        {
            'args': (),
            'kwargs': {
                'order_id': order.pk,
                'order_version': order.version,
                'event_type': 'order_completed',
                'reason': None,
                'log_extra': None,
            }
        }
    ]
    assert mocked_prepare_event.calls == expected_prepare_event_calls


@pytest.inline_callbacks
def test_unknown_order_event_type(mocked_min_due):
    with pytest.raises(order_events.UnknownOrderEventTypeError):
        yield order_events.prepare_event(
            'foobar', 'order_id_1', 3, None)


@pytest.mark.parametrize('event_type,can_use_secondary', [
    (order_events.ORDER_COMPLETED_EVENT_TYPE, True),
    (order_events.ORDER_AMENDED_EVENT_TYPE, False),
])
@pytest.mark.filldb(_fill=False)
def test_can_use_secondary(event_type, can_use_secondary):
    assert order_events._can_use_secondary(event_type) is can_use_secondary


@pytest.mark.filldb(_fill=False)
def test_can_use_secondary_on_unknown_event_type():
    with pytest.raises(order_events.UnknownOrderEventTypeError):
        order_events._can_use_secondary('some_unknown_event')


def _make_workshift(id_, created, usages):
    return dbh.driver_workshifts.Doc(
        {'_id': id_, 'created': created, 'usages': usages}
    )


@pytest.mark.parametrize('order_id,workshifts,expected_ids', [
    (
        'some_order_id',
        [
            _make_workshift(
                'old_no_usages_id',
                datetime.datetime(2020, 1, 1),
                [],
            ),
            _make_workshift(
                'new_no_usages_id',
                datetime.datetime(2020, 1, 2),
                [],
            ),
        ],
        ['old_no_usages_id'],
    ),
    (
        'some_order_id',
        [
            _make_workshift(
                'old_no_usages_id',
                datetime.datetime(2020, 1, 1),
                ['another_order_id'],
            ),
            _make_workshift(
                'old_usages_id',
                datetime.datetime(2020, 1, 1, 10),
                ['some_order_id'],
            ),
            _make_workshift(
                'new_usages_id',
                datetime.datetime(2020, 1, 2),
                ['some_order_id'],
            ),
        ],
        ['old_usages_id'],
    ),
    (
        'some_order_id',
        [],
        [],
    ),
])
@pytest.mark.filldb(_fill=False)
def test_select_workshifts_for_usages(order_id, workshifts, expected_ids):
    picked = order_events.select_workshifts_for_usages(order_id, workshifts)
    actual_ids = dbh.driver_workshifts.Doc.get_ids(picked)
    assert actual_ids == expected_ids


@pytest.mark.config(
    USE_ARCHIVE_FOR_ORDER_EVENTS=True,
    SEND_REASON_IN_ORDER_COMPLETED_AMENDED=True,
)
@pytest.mark.parametrize('reason,expected', [
    (
        {'kind': 'completed', 'data': {}},
        {'kind': 'completed', 'data': {}},
    ),
])
@pytest.inline_callbacks
def test_get_order_event_reason_enabled_config(reason, expected):
    actual = yield order_events.get_order_event_reason(reason)
    assert actual == expected


@pytest.mark.config(
    USE_ARCHIVE_FOR_ORDER_EVENTS=True,
    SEND_REASON_IN_ORDER_COMPLETED_AMENDED=False,
)
@pytest.mark.parametrize('reason,expected', [
    (
        {'kind': 'completed', 'data': {}},
        None
    ),
])
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_get_order_event_reason_disabled_config(reason, expected):
    actual = yield order_events.get_order_event_reason(reason)
    assert actual == expected


@pytest.mark.filldb(_fill=False)
def test_make_reasons():
    assert order_events.make_completed_reason() == {
        'kind': 'completed',
        'data': {},
    }
    assert (
        order_events.make_cost_changed_reason('chatterbox', 'some_id') ==
        {
            'kind': 'cost_changed',
            'data': {
                'ticket_type': 'chatterbox',
                'ticket_id': 'some_id'
            }
        }
    )

    assert (
        order_events.make_cost_accepted_reason('chatterbox', 'some_id') ==
        {
            'kind': 'cost_accepted',
            'data': {
                'ticket_type': 'chatterbox',
                'ticket_id': 'some_id'
            }
        }
    )

    disp_cost_reason = (
        order_events.make_disp_cost_accepted_reason('chatterbox', 'some_id')
    )
    assert disp_cost_reason == {
            'kind': 'disp_cost_accepted',
            'data': {
                'ticket_type': 'chatterbox',
                'ticket_id': 'some_id'
            }
        }


@pytest.mark.config(
    USE_ARCHIVE_FOR_ORDER_EVENTS=True,
    BRANDING_DISCOUNT_ENABLED=True,
    ENABLE_DRIVER_TAGS_FETCHING=True,
    ENABLE_GEOAREAS_SUBVENTIONS_FETCHING=True,
    USE_CANDIDATE_META=True,
)
@pytest.inline_callbacks
def test_candidate_meta_fallback(patch, mocked_send_event, mocked_min_due, mocked_metadata_storage):
    @patch('taxi.external.driver_tags_service.drivers_tags_by_profile_match')
    @async.inline_callbacks
    def driver_tags_drivers_tags_by_profile_match(
            dbid, uuid, src_service, log_extra=None):
        yield async.return_value(['some_tag'])

    @patch('taxi.external.candidate_meta.metadata_get')
    @async.inline_callbacks
    def metadata_get(
            order_id, park_id, driver_profile_id, log_extra=None):
        raise candidate_meta_client.CandidateMetaRequestError

    yield order_events.prepare_event(
        event_type='order_completed',
        order_id='order_id_1',
        order_version=3,
        reason={'kind': 'completed', 'data': {}},
    )


@pytest.mark.parametrize(
    'event_type,proc_id,reason,candidate_meta,expected_event_data,'
    'expected_workshift_usages, add_rebate_to_decoupling',
    [
      (
          'order_completed',
          'order_id_12',
          {'kind': 'completed', 'data': {}},
          None,
          {
              'accepted_by_driver_at': '2018-10-17T16:10:53.921000+00:00',
              'billing_at': '2018-10-17T16:10:53.921000+00:00',
              'alias_id': 'alias_id_1',
              'billing_contract_is_set': True,
              'billing_contract': {
                  'donate_multiplier': '1',
                  'offer_currency': 'RUB',
                  'currency_rate': '1',
                  'offer_currency_rate': '1',
                  'currency': 'RUB',
                  'acquiring_percent': '0',
                  'rebate_percent': '0',
                  'ind_bel_nds_percent': None,
                  'subventions_hold_delay': 0
              },
              'closed_without_accept': False,
              'completed_at': '2018-10-17T17:59:38.834000+00:00',
              'completed_by_dispatcher': False,
              'cost': {'amount': '1041.0', 'currency': 'RUB'},
              'created': '2018-10-17T16:10:42.631000+00:00',
              'discount': {
                  'method': 'subvention-fix',
                  'rate': 0.01,
              },
              'driver_cost': None,
              'due': '2018-10-17T16:14:00.000000+00:00',
              'has_co_branding': False,
              'has_lightbox': True,
              'has_sticker': True,
              'is_mqc': False,
              'order_id': 'order_id_12',
              'payment_type': 'card',
              'park': {
                  'brandings': ["lightbox", "franchise"]
              },
              'performer': {
                  'activity_points': 82,
                  'unique_driver_id': '5bcf22169830073fda1ebc2c',
                  'driver_license': 'AAA007X',
                  'driver_license_personal_id': '4956728e3f284552925b4a39befa3f3c',
                  'driver_id': 'park-with-several-brandings_driveruuid',
                  'db_id': 'dead0000food0000beef0000dead0000',
                  'tariff_category_id': 'category_id',
                  'hired_at': '2018-09-19T18:19:14.743000+00:00',
                  'hiring_type': 'commercial',
                  'available_tariff_classes': [
                      "econom",
                      "comfort"
                  ],
                  'profile_payment_type_restrictions': 'none',
                  'zone': 'moscow',
              },
              'source': None,
              'status': 'finished',
              'subvention_geoareas': [
                  'geoarea_1',
                  'geoarea_2',
                  'geoarea_no_area',
              ],
              'tags': ['fleet_park_rating'],
              'tariff_class': 'econom',
              'taxi_status': 'complete',
              'total_distance': 41882.9765625,
              'total_time': 6107.596,
              'park_corp_vat': None,
              'zone': 'moscow',
              'price_modifiers': [],
              'updated': '2018-10-17T17:14:00.000000+00:00',
              'park_ride_sum': '100',
              'coupon': {
                  'amount': '75.6',
                  'currency': 'RUB',
                  'netting_allowed': False,
                  'for_support': None,
              },
              'reason': {
                  'kind': 'completed',
                  'data': {}
              },
              'childseat_rental': {
                  'count': 1,
                  'cost': "51"
              },
              'driver_workshift_ids': [],
              'fleet_subscription_level': (
                  'fleet_subscription_level'
              ),
              'oebs_mvp_id': 'MSKc',
              'geo_hierarchy': 'br_root/br_moscow/br_moscow_adm',
          },
          {},
          False,
      ),
    ]
)
@pytest.mark.config(
    USE_ARCHIVE_FOR_ORDER_EVENTS=True,
    BRANDING_DISCOUNT_ENABLED=True,
    ENABLE_DRIVER_TAGS_FETCHING=True,
    ENABLE_GEOAREAS_SUBVENTIONS_FETCHING=True,
    ENABLE_GEOAREAS_SUBVENTIONS_SORT_BY_AREA_ASCENDING=True,
    USE_CANDIDATE_META=True,
    ADD_PERFORMER_ZONE_IN_ORDER_COMPLETED_EVENT=True,
    ADD_BILLING_AT_IN_ORDER_COMPLETED_EVENT=True,
    ADD_GEO_EXP_TAG_IN_ORDER_COMPLETED_EVENT=True,
    DRIVER_PROMOCODES_V2_BILLING_ENABLED=True,
    BILLING_AGGLOMERATION_DATA_TO_ORDER_COMPLETED=True,
    BILLING_WORKSHIFT_USAGES_IN_ORDER_EVENTS=True,
    BILLING_SAVE_PARK_CATEGORY_TO_ORDER_EVENT=True,
)
@pytest.mark.parametrize(
    'geo_experiments_settings, expected_geo_tags',
    [
        ({'geo_experiment_ok_1': 'geo_exp_tag_1'}, ['geo_exp_tag_1']),
        ({'geo_experiment_ok_1': 'geo_exp_tag_1',
          'geo_experiment_ok_2': 'geo_exp_tag_2'}, ['geo_exp_tag_1', 'geo_exp_tag_2']),
    ],
)
@pytest.inline_callbacks
def test_prepare_event_with_geo_exp(
        patch, mocked_send_event, mocked_min_due, mocked_metadata_storage, event_type, proc_id, reason,
        candidate_meta, expected_event_data, expected_workshift_usages,
        mock, areq_request, add_rebate_to_decoupling, geo_experiments_settings, expected_geo_tags):

    @patch('taxi.config.ADD_REBATE_TO_DECOUPLING_IN_ORDER_COMPLETED_EVENT.get')
    @async.inline_callbacks
    def get():
        yield
        async.return_value(add_rebate_to_decoupling)

    order = yield dbh.orders.Doc.find_one_by_id(proc_id)
    proc = yield dbh.order_proc.Doc.find_one_by_id(proc_id)

    @patch('taxi.external.driver_tags_service.drivers_tags_by_profile_match')
    @ async.inline_callbacks
    def driver_tags_drivers_tags_by_profile_match(
            dbid, uuid, src_service, log_extra=None):
        assert proc.chosen_candidate.db_id == dbid
        assert proc.chosen_candidate.driver_uuid == uuid
        assert src_service == settings.STQ_TVM_SERVICE_NAME
        yield async.return_value(['geo_exp_stop_tag_1'])

    expected_tags = ['geo_exp_stop_tag_1']
    for expected_geo_tag in expected_geo_tags:
        expected_tags.append(expected_geo_tag)
    expected_event_data['tags'] = expected_tags

    @patch('taxi.external.experiments3.get_values')
    @async.inline_callbacks
    def mock_exp3_get_values(consumer, args, **kwargs):
        yield
        assert consumer == 'geo_experiment_consumer'
        assert len(args) == 3
        assert args[0].name == 'unique_driver_id'
        assert args[0].value == '5bcf22169830073fda1ebc2c'
        assert args[1].name == 'zone'
        assert args[1].value == 'moscow'
        assert args[2].name == 'tags'
        assert args[2].value == ['geo_exp_stop_tag_1']
        answer = []
        for experiment in geo_experiments_settings:
            tag = geo_experiments_settings[experiment]
            answer.append(experiments3.ExperimentsValue(
                name=experiment,
                value={'geo_exp_tag': tag})
            )
        async.return_value(answer)

    @patch('taxi.external.candidate_meta.metadata_get')
    @async.inline_callbacks
    def metadata_get(
            order_id, park_id, driver_profile_id, log_extra=None):
        assert order_id == proc_id
        assert park_id == proc.chosen_candidate.db_id
        assert driver_profile_id == proc.chosen_candidate.driver_uuid
        yield async.return_value(candidate_meta)

    @patch('taxi.internal.dbh.subvention_geoareas.Doc.'
           'find_active_geoareas_in_point')
    @async.inline_callbacks
    def find_active_geoareas_in_point(point, fields=None):
        # there's only one proc that'll get here
        assert point == [
            37.6659699,
            55.7675672
        ]
        assert fields == ['_id', 'name', 'created', 'area']
        yield async.return_value([{'name': 'some_subvention_geoarea_from_db', 'area': 42.0}])

    @patch('taxi.external.taxi_protocol.nearest_zone')
    @async.inline_callbacks
    def nearest_zone(point, client_id=None, log_extra=None):
        assert(isinstance(point, list))
        if point == [37.0, 55.0]:
            # only for order with id 'order_with_no_driver_zone'
            raise taxi_protocol.NotFoundError()
        yield async.return_value('moscow')

    @patch('taxi.external.driver_promocodes.get_active_promocodes')
    @async.inline_callbacks
    def get_active_promocodes(filters, src_service, log_extra=None):
        yield async.return_value([{
            'filter_id': 'alias_id_8',
            'is_support_series': True,
            'id': 'promo_id1',
            'entity_id':
                'dead0000food0000beef0000dead0000_park-without-active-brandings_driveruuid1'}])

    @patch('taxi.external.fleet_payouts.get_fleet_subscription_level')
    @async.inline_callbacks
    def get_fleet_subscription_level(*args, **kwargs):
        yield async.return_value({
                  'fleet_subscription_level': 'fleet_subscription_level',
                  'park_rating': 'park_rating',
              })

    @patch('taxi.external.driver_promocodes.add_order_usage')
    @async.inline_callbacks
    def add_order_usage(usages, src_service, log_extra=None):
        assert usages == [{
            'order_id': 'alias_id_8',
            'promocode_id': 'promo_id1'}]
        yield

    @patch('taxi.internal.dbh.driver_workshifts.Doc.add_many')
    @async.inline_callbacks
    def add_many(workshift_usages):
        assert workshift_usages == expected_workshift_usages
        yield

    yield order_events.prepare_event(
        event_type=event_type,
        order_id=proc_id,
        order_version=order.version,
        reason=reason,
    )
    if expected_event_data is None:
        expected_send_event_calls = []
    else:
        if event_type == 'order_completed':
            order_event_ref = event_type
        else:
            updated_str = expected_event_data['updated']
            updated = datetime.datetime.strptime(
                updated_str, '%Y-%m-%dT%H:%M:%S.%f+00:00'
            )
            order_event_ref = event_type + '/' + updated.isoformat()
        expected_send_event_calls = [
            {
                'args': (),
                'kwargs': {
                    'order_event_ref': order_event_ref,
                    'type_': event_type,
                    'data': expected_event_data,
                    'tvm_src_service': 'stq',
                    'log_extra': None,
                }
            }
        ]
        assert len(add_many.calls) == 1
    actual_send_event_calls = mocked_send_event.calls

    actual_send_event_calls[0]['kwargs']['data']['tags'].sort()
    expected_send_event_calls[0]['kwargs']['data']['tags'].sort()

    assert actual_send_event_calls == expected_send_event_calls


@pytest.mark.parametrize(
    'event_type',
    [
        'order_completed',
        'order_amended',
    ]
)
@pytest.mark.parametrize(
    'agglomerations_response,expected_performer_geohierarchy',
    [
        (404, 'geo_nodes/from/point_a/moscow'),
        ([], 'geo_nodes/from/point_a/moscow'),
    ]
)
@pytest.mark.config(
    ADD_PERFORMER_ZONE_IN_ORDER_COMPLETED_EVENT=True,
    ADD_PERFORMER_GEOHIERARCHY_IN_ORDER_COMPLETED_EVENT=True,
    BILLING_AGGLOMERATION_DATA_TO_ORDER_COMPLETED=True,
)
@pytest.inline_callbacks
def test_performer_geo_hierarchy_fallback(
        patch, mocked_send_event, mocked_min_due,
        mock, areq_request, event_type,
        agglomerations_response, expected_performer_geohierarchy):

    kProcId = 'order_id_1'

    order = yield dbh.orders.Doc.find_one_by_id(kProcId)

    @patch('taxi.external.taxi_protocol.nearest_zone')
    @async.inline_callbacks
    def nearest_zone(point, client_id=None, log_extra=None):
        yield async.return_value('moscow')

    @patch('taxi.external.metadata_storage.v1_metadata_retrieve')
    @async.inline_callbacks
    def v1_metadata_retrieve(
        meta_id, namespace, last_known_updated=None, try_archive=False, log_extra=None):
        if namespace == 'taxi:order_agglomeration':
            yield async.return_value({
                'value': {
                    'additional_data': {
                        'geo_nodes': [
                            'point_a', 'from', 'geo_nodes',
                        ],
                        'mvp': 'MSKc'
                    }
                },
                'updated': '2020-06-19T06:39:26.898+00:00'
            })
        elif namespace == 'taxi:subvention_geoareas':
            yield async.return_value({
                    'value': {
                        'additional_data': {
                            'subvention_geoareas': []
                        }
                    },
                    'updated': '2020-06-19T06:39:26.898+00:00'
            })

    @patch('taxi.external.agglomerations.get_ancestors')
    @async.inline_callbacks
    def get_ancestors(tariff_zone, log_extra=None):
        if agglomerations_response == 404:
            raise agglomerations.NothingFoundError()

        yield async.return_value(agglomerations_response)

    yield order_events.prepare_event(
        event_type=event_type,
        order_id=kProcId,
        order_version=order.version,
        reason={'kind': 'completed', 'data': {}},
    )

    event_data = mocked_send_event.calls[0]['kwargs']['data']
    assert event_data['performer']['geo_hierarchy'] == expected_performer_geohierarchy


@pytest.mark.parametrize(
    'event_type,reason,candidate_meta,'
    'expected_workshift_usages, add_rebate_to_decoupling',
    [
      (
          'order_completed',
          {'kind': 'completed', 'data': {}},
          None,
          {},
          False,
      ),
    ]
)
@pytest.mark.config(
    USE_ARCHIVE_FOR_ORDER_EVENTS=True,
    BRANDING_DISCOUNT_ENABLED=True,
    ENABLE_DRIVER_TAGS_FETCHING=True,
    ENABLE_GEOAREAS_SUBVENTIONS_FETCHING=True,
    ENABLE_GEOAREAS_SUBVENTIONS_SORT_BY_AREA_ASCENDING=True,
    USE_CANDIDATE_META=True,
    ADD_PERFORMER_ZONE_IN_ORDER_COMPLETED_EVENT=True,
    ADD_BILLING_AT_IN_ORDER_COMPLETED_EVENT=True,
    ADD_GEO_EXP_TAG_IN_ORDER_COMPLETED_EVENT=True,
    DRIVER_PROMOCODES_V2_BILLING_ENABLED=True,
    BILLING_AGGLOMERATION_DATA_TO_ORDER_COMPLETED=True,
    BILLING_WORKSHIFT_USAGES_IN_ORDER_EVENTS=True,
    BILLING_SAVE_PARK_CATEGORY_TO_ORDER_EVENT=True,
)
@pytest.mark.parametrize(
    'order_id, ms_response, ms_geoareas, expected_geoareas',
    [
        (
            'order_id_12',
            True,
            [
                {
                    '_id': '2',
                    'name': 'geoarea_2',
                    'area': '2',
                },
                {
                    '_id': '3',
                    'name': 'geoarea_no_area',
                },
                {
                    '_id': '1',
                    'name': 'geoarea_1',
                    'area': '1',
                },
            ],
            [
                'geoarea_1',
                'geoarea_2',
                'geoarea_no_area',
            ]
        ),
        (
            'order_id_12',
            True,
            None,
            [
                'from_geoareas_service'
            ],
        ),
        (
            'order_id_12',
            True,
            [],
            []
        ),
        (
            'order_id_3',  # has only seen point (no driving)
            True,
            None,
            ['from_geoareas_service'],
        ),
    ],
)
@pytest.inline_callbacks
def test_prepare_event_with_sg_from_metadata_storage(
        patch, mocked_send_event, mocked_min_due, event_type, order_id, reason,
        candidate_meta, expected_workshift_usages,
        mock, areq_request, add_rebate_to_decoupling, ms_response,
        ms_geoareas, expected_geoareas):

    @patch('taxi.config.ADD_REBATE_TO_DECOUPLING_IN_ORDER_COMPLETED_EVENT.get')
    @async.inline_callbacks
    def get():
        yield
        async.return_value(add_rebate_to_decoupling)

    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)

    @patch('taxi.external.driver_tags_service.drivers_tags_by_profile_match')
    @ async.inline_callbacks
    def driver_tags_drivers_tags_by_profile_match(
            dbid, uuid, src_service, log_extra=None):
        assert proc.chosen_candidate.db_id == dbid
        assert proc.chosen_candidate.driver_uuid == uuid
        assert src_service == settings.STQ_TVM_SERVICE_NAME
        yield async.return_value(['fleet_park_rating'])

    @patch('taxi.external.candidate_meta.metadata_get')
    @async.inline_callbacks
    def metadata_get(
            order_id, park_id, driver_profile_id, log_extra=None):
        assert order_id == order_id
        assert park_id == proc.chosen_candidate.db_id
        assert driver_profile_id == proc.chosen_candidate.driver_uuid
        yield async.return_value(candidate_meta)

    @patch('taxi.external.taxi_protocol.nearest_zone')
    @async.inline_callbacks
    def nearest_zone(point, client_id=None, log_extra=None):
        assert(isinstance(point, list))
        if point == [37.0, 55.0]:
            # only for order with id 'order_with_no_driver_zone'
            raise taxi_protocol.NotFoundError()
        yield async.return_value('moscow')

    @patch('taxi.external.driver_promocodes.get_active_promocodes')
    @async.inline_callbacks
    def get_active_promocodes(filters, src_service, log_extra=None):
        yield async.return_value([{
            'filter_id': 'alias_id_8',
            'is_support_series': True,
            'id': 'promo_id1',
            'entity_id':
                'dead0000food0000beef0000dead0000_park-without-active-brandings_driveruuid1'}])

    @patch('taxi.external.fleet_payouts.get_fleet_subscription_level')
    @async.inline_callbacks
    def get_fleet_subscription_level(*args, **kwargs):
        yield async.return_value({
                  'fleet_subscription_level': 'fleet_subscription_level',
                  'park_rating': 'park_rating',
              })

    @patch('taxi.external.driver_promocodes.add_order_usage')
    @async.inline_callbacks
    def add_order_usage(usages, src_service, log_extra=None):
        assert usages == [{
            'order_id': 'alias_id_8',
            'promocode_id': 'promo_id1'}]
        yield

    @patch('taxi.internal.dbh.driver_workshifts.Doc.add_many')
    @async.inline_callbacks
    def add_many(workshift_usages):
        assert workshift_usages == expected_workshift_usages
        yield

    @patch('taxi.external.metadata_storage.v1_metadata_retrieve')
    @async.inline_callbacks
    def v1_metadata_retrieve(
        meta_id, namespace, last_known_updated=None, try_archive=False, log_extra=None):
        if namespace == 'taxi:order_agglomeration':
            assert meta_id == order_id
            yield async.return_value({
                'value': {
                    'additional_data': {
                        'geo_nodes': [
                            'br_moscow_adm', 'br_moscow', 'br_root',
                        ],
                        'mvp': 'MSKc'
                    }
                },
                'updated': '2020-06-19T06:39:26.898+00:00'
            })
        elif namespace == 'taxi:subvention_geoareas':
            dbid = proc.chosen_candidate.db_id
            uuid = proc.chosen_candidate.driver_uuid
            assert meta_id == '{}_{}_{}'.format(order_id, dbid, uuid)
            if ms_response is True:
                if ms_geoareas is not None:
                    yield async.return_value({
                        'value': {
                            'additional_data': {
                                'subvention_geoareas': ms_geoareas
                            }
                        },
                        'updated': '2020-06-19T06:39:26.898+00:00'
                    })
                else:
                    raise metadata_storage.NotFoundError()
            else:
                raise metadata_storage.ServerError("500")
        else:
            assert False

    @patch('taxi.external.geoareas.find_active_geoareas_in_point')
    @async.inline_callbacks
    def find_active_geoareas_in_point(driver_point, log_extra):
        assert driver_point is not None
        yield async.return_value([{'_id': '1', 'name': 'from_geoareas_service', 'created': 1641823768}])

    yield order_events.prepare_event(
        event_type=event_type,
        order_id=order_id,
        order_version=order.version,
        reason=reason,
    )

    assert len(add_many.calls) == 1
    sent_data = mocked_send_event.calls[0]['kwargs']['data']
    assert sent_data['subvention_geoareas'] == expected_geoareas


@pytest.mark.config(
    ADD_PERFORMER_ZONE_IN_ORDER_COMPLETED_EVENT=True,
    BILLING_WORKSHIFT_USAGES_IN_ORDER_EVENTS=True,
    DISABLE_FALLBACK_TO_SEEN_POINT=True,
)
@pytest.inline_callbacks
def test_disable_fallback_to_seen_point(
        patch, mocked_send_event, mocked_min_due, mock, areq_request,
):
    order_id = 'order_id_3'  # has only seen point (no driving)

    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)

    @patch('taxi.external.metadata_storage.v1_metadata_retrieve')
    @async.inline_callbacks
    def v1_metadata_retrieve(
        meta_id, namespace, last_known_updated=None, try_archive=False, log_extra=None):
        if namespace == 'taxi:order_agglomeration':
            assert meta_id == order_id
            yield async.return_value({
                'value': {
                    'additional_data': {
                        'geo_nodes': [
                            'br_moscow_adm', 'br_moscow', 'br_root',
                        ],
                        'mvp': 'MSKc'
                    }
                },
                'updated': '2020-06-19T06:39:26.898+00:00'
            })
        elif namespace == 'taxi:subvention_geoareas':
            raise metadata_storage.NotFoundError()

    yield order_events.prepare_event(
        event_type='order_completed',
        order_id=order_id,
        order_version=order.version,
        reason={'kind': 'completed', 'data': {}},
    )

    sent_data = mocked_send_event.calls[0]['kwargs']['data']
    assert sent_data['subvention_geoareas'] == []
    assert sent_data['performer']['zone'] == proc.order.nearest_zone


@pytest.mark.parametrize(
    'use_subvention_order_context',
    {
        'comparing',
        'comparing_required',
        'enabled',
    }
)
@pytest.mark.config(
    ADD_PERFORMER_ZONE_IN_ORDER_COMPLETED_EVENT=True,
    BILLING_WORKSHIFT_USAGES_IN_ORDER_EVENTS=True,
    DISABLE_FALLBACK_TO_SEEN_POINT=True,
    ADD_GEO_EXP_TAG_IN_ORDER_COMPLETED_EVENT=True,
    BILLING_AGGLOMERATION_DATA_TO_ORDER_COMPLETED=True,
    ADD_PERFORMER_GEOHIERARCHY_IN_ORDER_COMPLETED_EVENT=True,
    ADD_BILLING_AT_IN_ORDER_COMPLETED_EVENT=True,
    USE_SUBVENTION_ORDER_CONTEXT_FOR_ORDERS_SINCE='2018-10-17T00:00:00+00:00',
)
@pytest.inline_callbacks
def test_use_subvention_order_context(
        patch, mocked_send_event, mocked_min_due, mock, areq_request, use_subvention_order_context,
):
    order_id = 'order_id_3'
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    shared = {}

    @patch('taxi.internal.order_events._print_subvention_order_context_diffs')
    def _print_subvention_order_context_diffs(diffs, log_extra):
        shared['diffs'] = diffs

    @patch('taxi.config.USE_SUBVENTION_ORDER_CONTEXT.get')
    @async.inline_callbacks
    def get():
        yield async.return_value(use_subvention_order_context)

    @patch('taxi.external.metadata_storage.v1_metadata_retrieve')
    @async.inline_callbacks
    def v1_metadata_retrieve(
        meta_id, namespace, last_known_updated=None, try_archive=False, log_extra=None):
        if namespace == 'taxi:order_agglomeration':
            assert meta_id == order_id
            yield async.return_value({
                'value': {
                    'additional_data': {
                        'geo_nodes': [
                            'br_moscow_adm', 'br_moscow', 'br_root',
                        ],
                        'mvp': 'MSKc'
                    }
                },
                'updated': '2020-06-19T06:39:26.898+00:00'
            })
        elif namespace == 'taxi:subvention_geoareas':
            raise metadata_storage.NotFoundError()

    @patch('taxi.external.subvention_order_context.v1_context_get')
    @async.inline_callbacks
    def v1_context_get(order_id, park_id, driver_profile_id, log_extra=None):
        yield async.return_value({
            'activity_points': 91,
            'subvention_geoareas': ['geoarea1', 'geoarea2'],
            'branding': {'has_sticker': True, 'has_lightbox': False},
            'ref_time': '2020-01-01T12:00:00.000000+0000',
            'tags': ['tag1', 'tag2'],
            'tariff_class': 'superclass',
            'tariff_zone': 'zone',
            'geonodes': 'br_root/br_node/zone',
            'time_zone': 'Europe/Moscow',
            'unique_driver_id': 'unique_driver_id1',
        })

    yield order_events.prepare_event(
        event_type='order_completed',
        order_id=order_id,
        order_version=order.version,
        reason={'kind': 'completed', 'data': {}},
    )

    sent_data = mocked_send_event.calls[0]['kwargs']['data']

    if (use_subvention_order_context == 'enabled'):
        assert (sent_data['performer']['unique_driver_id']
             == '5bcf22169830073fda1ebc2c')  # use old
        assert sent_data['tariff_class'] == 'econom'  # use old
        assert sent_data['performer']['activity_points'] == 91
        assert sent_data['performer']['zone'] == 'zone'
        assert sent_data['performer']['geo_hierarchy'] == 'br_root/br_node/zone'
        assert sent_data['subvention_geoareas'] == ['geoarea1', 'geoarea2']
        assert sent_data['has_sticker'] is True
        assert sent_data['has_lightbox'] is False
        assert sent_data['billing_at'] == '2020-01-01T12:00:00.000000+00:00'
        assert sent_data['tags'] == ['tag1', 'tag2']
    else:
        assert shared['diffs'] == [
            'activity_points (new: 91, old: 82)',
            "subvention_geoareas (new: [u'geoarea1', u'geoarea2'], old: [])",
            (
                "branding (new: {u'has_lightbox': False, u'has_sticker': True},"
                " old: {'has_lightbox': False, 'has_sticker': False})"
            ),
            'ref_time (new: 2020-01-01 12:00:00, old: 2018-10-17 16:14:00)',
            "tags (new: set([u'tag1', u'tag2']), old: set([]))",
            'tariff_class (new: superclass, old: econom)',
            'tariff_zone (new: zone, old: moscow)',
            'geonodes (new: br_root/br_node/zone, old: br_root/br_moscow/br_moscow_adm/moscow)',
            'unique_driver_id (new: unique_driver_id1, old: 5bcf22169830073fda1ebc2c)',
        ]
