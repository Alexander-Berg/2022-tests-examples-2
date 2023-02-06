# pylint: disable=import-only-modules
import datetime
import json

import bson
from dateutil.parser import parse as parse_datetime
import pytest


def apply_mongo_mapping_config(target_obj, config):
    if isinstance(target_obj, list):
        for value in target_obj:
            apply_mongo_mapping_config(value, config)
        return target_obj
    if isinstance(target_obj, dict):
        if 'in' in config:
            for key, value in target_obj.items():
                if key in config['in']:
                    apply_mongo_mapping_config(value, config['in'][key])
        if '__replace__' in config:
            for old_name, new_name in config['__replace__'].items():
                if old_name in target_obj:
                    target_obj[new_name] = target_obj.pop(old_name)
    return target_obj


def _serialize(value):
    if isinstance(value, datetime.datetime):
        return datetime.datetime.strftime(value, '%Y-%m-%dT%H:%M:%S+00:00')
    if isinstance(value, bson.ObjectId):
        return str(value)
    raise Exception('Invalid type for value ' + repr(value))


def _add_required_fields(value):
    if 'updated' not in value:
        value['updated'] = value['date_from']
    if 'activation_zone' not in value:
        value['activation_zone'] = value['home_zone']
    if 'related_zones' not in value:
        value['related_zones'] = []
    for i, cat in enumerate(value['categories']):
        if 'category_name' not in cat:
            cat['category_name'] = f'category{i}'
        if 'category_type' not in cat:
            cat['category_type'] = 'application'
        if 'name_key' not in cat:
            cat['name_key'] = f'name_key{i}'
        if 'day_type' not in cat:
            cat['day_type'] = 0
        if 'minimal' not in cat:
            cat['minimal'] = 0
        for zp in cat.get('zonal_prices', []):
            if 'route_without_jams' not in zp:
                zp['route_without_jams'] = False
    return value


@pytest.fixture(autouse=True)
def mock_individual_tariffs(mockserver, mongodb, load_json):
    class IndividualTariffsHandlers:
        def set_tariffs_file(self, filename):
            self.tariffs_file = filename

        def __init__(self):
            self.tariffs_file = 'db_tariffs.json'

            @mockserver.json_handler(
                '/individual_tariffs/internal/v1/tariffs/list',
            )
            def tariffs_list(request):
                now_time = parse_datetime(request.json['active_at_time'])
                if 'tariffs' in mongodb.get_aliases():
                    tariffs_docs = mongodb.tariffs.find(
                        {
                            '$and': [
                                {'date_from': {'$lte': now_time}},
                                {
                                    '$or': [
                                        {'date_to': {'$exists': False}},
                                        {'date_to': {'$gte': now_time}},
                                    ],
                                },
                            ],
                        },
                    )
                else:
                    all_tariffs = load_json(self.tariffs_file)
                    tariffs_docs = [
                        tariff
                        for tariff in all_tariffs
                        if (tariff['date_from'] <= now_time)
                        and (
                            'date_to' not in tariff
                            or tariff['date_to'] >= now_time
                        )
                    ]
                map_config = load_json('mongo_tariffs_mapping.json')
                tariffs = [
                    _add_required_fields(
                        apply_mongo_mapping_config(
                            tariff, map_config['tariffs'],
                        ),
                    )
                    for tariff in tariffs_docs
                ]
                tariffs = json.loads(json.dumps(tariffs, default=_serialize))
                return {'tariffs': tariffs}

            self.tariffs_list = tariffs_list

    return IndividualTariffsHandlers()
