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


def append_required_fields(tariff):
    if 'updated' not in tariff:
        tariff['updated'] = datetime.datetime.now()
    return tariff


class CategoryWrapper:
    def __init__(self, cat):
        self._cat = cat

    def remove_requirement_price(self, req_type):
        req_prices = self._cat['summable_requirements']
        self._cat['summable_requirements'] = [
            req for req in req_prices if req['type'] != req_type
        ]

    def add_requirement_price(self, req_type, price):
        self._cat['summable_requirements'].append(
            {'type': req_type, 'max_price': price},
        )

    def set_requirement_price(self, req_type, new_price):
        for req_price in self._cat['summable_requirements']:
            if req_price['type'] == req_type:
                req_price['max_price'] = new_price
                return
        raise Exception(
            f'No requirement price with type {req_type} '
            f'and price {new_price} found',
        )


@pytest.fixture(autouse=True)
def mock_individual_tariffs(mockserver, mongodb, load_json):
    class IndividualTariffsHandlers:
        def _fetch_tariffs(self, filter_function):
            return json.loads(
                json.dumps(
                    list(filter(filter_function, self._all_tariffs)),
                    default=_serialize,
                ),
            )

        def get_tariff_category(self, tariff_id, category_id):
            tariff = [
                tariff
                for tariff in self._all_tariffs
                if str(tariff['id']) == tariff_id
            ][0]
            category = [
                cat for cat in tariff['categories'] if cat['id'] == category_id
            ][0]
            return CategoryWrapper(category)

        def set_tariffs_file(self, filename):
            self.tariffs_file = filename
            self._all_tariffs = self._load_all_tariffs()

        def _load_all_tariffs(self):
            map_config = load_json('mongo_tariffs_mapping.json')
            if 'tariffs' in mongodb:
                raw_tariffs = mongodb.tariffs.find({})
            else:
                raw_tariffs = load_json(self.tariffs_file)
            return [
                append_required_fields(
                    apply_mongo_mapping_config(tariff, map_config['tariffs']),
                )
                for tariff in raw_tariffs
            ]

        def __init__(self):
            self.tariffs_file = 'db_tariffs.json'
            self._all_tariffs = self._load_all_tariffs()

            @mockserver.json_handler(
                '/individual-tariffs/v1/tariff/by_category',
            )
            # pylint: disable=unused-variable
            def tariffs_by_category(request):
                requested_cat = request.args['category_id']

                def filter_function(tariff):
                    return any(
                        cat['id'] == requested_cat
                        for cat in tariff['categories']
                    )

                result_tariffs = self._fetch_tariffs(filter_function)

                if not result_tariffs:
                    return mockserver.make_response('No tariff found', 404)

                result_tariff = result_tariffs[0]
                result_categories = result_tariff['categories']
                if (
                        request.args.get('requested_categories', 'ALL')
                        == 'SELECTED_ONLY'
                ):
                    result_categories = [
                        cat
                        for cat in result_tariff['categories']
                        if cat['id'] == requested_cat
                    ]
                result_tariff = json.loads(
                    json.dumps(result_tariff, default=_serialize),
                )
                return {
                    'id': result_tariff['id'],
                    'home_zone': result_tariff['home_zone'],
                    'activation_zone': result_tariff['activation_zone'],
                    'date_from': result_tariff['date_from'],
                    'categories': result_categories,
                }

            @mockserver.json_handler(
                '/individual-tariffs/internal/v1/tariffs/list',
            )
            # pylint: disable=unused-variable
            def tariffs_list(request):
                time_point = parse_datetime(request.json['active_at_time'])
                request_mode = request.json.get('request_mode', 'only_active')
                now_time = time_point.replace(tzinfo=None)

                def filter_function(tariff):
                    date_from_valid = tariff['date_from'] <= now_time
                    date_to_valid = (
                        'date_to' not in tariff
                        or tariff['date_to'] >= now_time
                    )
                    return (
                        date_from_valid or request_mode != 'only_active'
                    ) and date_to_valid

                return {'tariffs': self._fetch_tariffs(filter_function)}

    return IndividualTariffsHandlers()
