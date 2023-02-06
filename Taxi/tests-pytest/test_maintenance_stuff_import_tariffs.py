# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import json

import pytest

from taxi.core import async
from taxi.core import db
from taxi_maintenance.stuff import import_tariffs


@pytest.mark.now('2018-08-02 18:04:00+05')
@pytest.mark.filldb
@pytest.inline_callbacks
def test_import_tariffs(patch, load):

    @patch('taxi.external.taximeter.tariffs')
    @async.inline_callbacks
    def _taxi_external_taximeter_tariffs(*args, **kwargs):
        yield
        async.return_value(json.loads(load('tariffs.json')))

    assert (yield db.zone_tariff_settings.count()) == 1
    assert (yield db.tariff_folders.find().count()) == 1
    assert (yield db.tariff_categories.find().count()) == 1

    yield import_tariffs.do_stuff()

    tariff_settings_list = yield db.zone_tariff_settings.find().run()
    assert len(tariff_settings_list) == 1
    tariff_settings = tariff_settings_list[0]
    assert isinstance(tariff_settings['_id'], basestring)
    for key in ('_id', 'updated_at'):
        tariff_settings.pop(key)
    assert tariff_settings == {
        'kind': 'taximeter',
        'external_ref': 'c52e88b724674ef7917ee0f8fa4627de',
        'checksum': 183391638,
        'properties': {
            'home_zone': 'moscow',
            'categories': [
                {'client_requirements': ['waiting_in_transit'], 'category_name': 'econom'},
                {'client_requirements': ['waiting_in_transit'], 'category_name': 'business'},
                {'client_requirements': ['waiting_in_transit'], 'category_name': 'vip'},
                {'client_requirements': ['waiting_in_transit'], 'category_name': 'minivan'},
                {'client_requirements': ['waiting_in_transit'], 'category_name': 'comfortplus'},
                {'client_requirements': ['waiting_in_transit'], 'category_name': 'pool'},
                {'client_requirements': ['waiting_in_transit'], 'category_name': 'start'},
                {'client_requirements': ['waiting_in_transit'], 'category_name': 'standart'},
                {'client_requirements': ['waiting_in_transit'], 'category_name': 'childtariff'},
                {'client_requirements': ['waiting_in_transit'], 'category_name': 'ultimate'},
                {'client_requirements': ['waiting_in_transit'], 'category_name': 'mkk'}
            ],
            'fixed_price_show_in_taximeter': True,
            'hide_dest_for_driver': False,
        }
    }

    tariff_folders = yield db.tariff_folders.find().run()
    assert len(tariff_folders) == 1
    tariff_folder = tariff_folders[0]
    tariff_folder_id = tariff_folder.pop('_id')
    assert isinstance(tariff_folder_id, basestring)
    tariff_folder.pop('updated_at')
    assert tariff_folder == {
        'kind': 'taximeter',
        'external_ref': 'c52e88b724674ef7917ee0f8fa4627de',
        'properties': {
            'name': 'Свои',
            'hide': False,
        }
    }

    tariff_categories = yield db.tariff_categories.find().run()
    assert len(tariff_categories) == 1
    tariff_category = tariff_categories[0]
    assert isinstance(tariff_category['_id'], basestring)
    for key in ('_id', 'updated_at'):
        tariff_category.pop(key)
    assert tariff_category == {
        'kind': 'taximeter',
        'parent_id': None,
        'external_ref': 'c52e88b724674ef7917ee0f8fa4627de',
        'external_id': '21d729e7f80e4acdb50e4ce938e77f70',
        'date_from': datetime.datetime(2018, 8, 2, 13, 4),
        'properties': {
            'category_name': 'econom',
            'currency': 'RUB',
            'day_type': 2,
            'description': '99/5М/ОЖ5 {ГОРОД/10М}',
            'folder_id': tariff_folder_id,
            'from_time': '00:00',
            'home_zone': 'moscow',
            'meters': [
                {'prepaid': 0, 'trigger': 3},
                {'prepaid': 0, 'trigger': 3},
                {'prepaid': 0, 'trigger': 3},
                {'prepaid': 0, 'trigger': 3},
                {'prepaid': 0, 'trigger': 3},
                {'prepaid': 0, 'trigger': 2},
                {'prepaid': 0, 'trigger': 2}
            ],
            'minimal': 99,
            'name_key': 'interval.day',
            'paid_dispatch_distance_price_intervals': [
                {'begin': 0, 'price': 20}
            ],
            'paid_dispatch_distance_price_intervals_meter_id': 4,
            'related_zones': ['dme', 'eao', 'moscow', 'seao', 'swao', 'vko'],
            'special_taximeters': [
                {
                    'price': {
                        'distance_price_intervals': [{'begin': 0, 'price': 20}],
                        'distance_price_intervals_meter_id': 6,
                        'time_price_intervals': [{'begin': 5, 'price': 10}],
                        'time_price_intervals_meter_id': 5
                    },
                    'zone_name': 'moscow'
                },
                {
                    'price': {
                        'distance_price_intervals': [{'begin': 0, 'price': 20}],
                        'distance_price_intervals_meter_id': 6,
                        'time_price_intervals': [{'begin': 5, 'price': 10}],
                        'time_price_intervals_meter_id': 5
                    },
                    'zone_name': 'suburb'
                }
            ],
            'summable_requirements': [
                {'max_price': 4, 'type': 'waiting_in_transit'}
            ],
            'title': 'Эконом',
            'to_time': '23:59',
            'waiting_included': 5,
            'waiting_price': 3,
            'waiting_price_type': 'per_minute',
            'zonal_prices': [
                {
                    'destination': 'vko',
                    'price': {
                        'distance_price_intervals': [{'begin': 100, 'price': 20}],
                        'distance_price_intervals_meter_id': 6,
                        'minimal': 1500.0,
                        'time_price_intervals': [{'begin': 7, 'price': 10}],
                        'time_price_intervals_meter_id': 5,
                        'waiting_included': 60
                    },
                    'route_without_jams': False,
                    'source': 'dme'
                },
                {
                    'destination': 'swao',
                    'price': {
                        'distance_price_intervals': [{'begin': 100, 'price': 20}],
                        'distance_price_intervals_meter_id': 6,
                        'minimal': 1050.0,
                        'time_price_intervals': [{'begin': 7, 'price': 10}],
                        'time_price_intervals_meter_id': 5,
                        'waiting_included': 60
                    },
                    'route_without_jams': False,
                    'source': 'vko'
                },
                {
                    'destination': 'vko',
                    'price': {
                        'distance_price_intervals': [{'begin': 100, 'price': 20}],
                        'distance_price_intervals_meter_id': 6,
                        'minimal': 900.0,
                        'time_price_intervals': [{'begin': 7, 'price': 10}],
                        'time_price_intervals_meter_id': 5,
                        'waiting_included': 60
                    },
                    'route_without_jams': False,
                    'source': 'seao'
                },
                {
                    'destination': 'eao',
                    'price': {
                        'distance_price_intervals': [{'begin': 100, 'price': 20}],
                        'distance_price_intervals_meter_id': 6,
                        'minimal': 1200.0,
                        'time_price_intervals': [{'begin': 7, 'price': 10}],
                        'time_price_intervals_meter_id': 5,
                        'waiting_included': 60
                    },
                    'route_without_jams': False,
                    'source': 'dme'
                }
            ]
        }
    }
