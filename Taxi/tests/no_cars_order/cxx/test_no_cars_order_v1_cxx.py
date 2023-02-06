import json

from taxi_pyml.common import time_utils
from ctaxi_pyml.no_cars_order import v1 as cxx
from ctaxi_pyml.common import geo as cxx_geo

SURGE_INFO_OPTIONAL_FIELDS = [
    'pins',
    'pins_b',
    'pins_order',
    'prev_pins',
    'free',
    'free_chain',
    'total',
    'prev_eta',
    'prev_free',
    'prev_chain',
    'prev_total',
    'prev_surge',
    'radius',
    'surge_value',
    'surge_value_smooth',
    'found_share',
]


def test_serialization(load):
    request = cxx.Request.from_json(load('request.json'))
    request.to_json()


def test_initialization(load):
    loaded_dict = json.loads(load('request.json'))
    classes_info_dict = loaded_dict['classes_info']
    for tariff_class, class_info in classes_info_dict.items():
        for field in SURGE_INFO_OPTIONAL_FIELDS:
            class_info['surge_info'][field] = class_info['surge_info'].get(
                field,
            )
        class_info['surge_info'] = cxx.SurgeInfo(**class_info['surge_info'])
        candidates = []
        for candidate in class_info['candidates']:
            candidate['position'] = cxx_geo.GeoPoint(*candidate['position'])
            chain_info = candidate['chain_info']
            chain_info['destination'] = (
                None
                if chain_info.get('destination') is None
                else cxx_geo.GeoPoint(*chain_info['destination'])
            )
            candidate['chain_info'] = cxx.ChainInfo(
                destination=chain_info['destination'],
                order_id=chain_info.get('order_id'),
                left_dist=chain_info.get('left_dist'),
                left_time=chain_info.get('left_time'),
            )
            candidate['score'] = candidate.get('score')
            candidates.append(cxx.CandidateInfo(**candidate))
        class_info['candidates'] = candidates
        class_info['cost'] = class_info.get('cost')
        class_info['cost_driver'] = class_info.get('cost_driver')
        class_info['cost_original'] = class_info.get('cost_original')
        class_info['requirements'] = set(class_info['requirements'])
        class_info['actual_time'] = class_info.get('actual_time')
        class_info['actual_distance'] = class_info.get('actual_distance')
        class_info['actual_line_distance'] = class_info.get(
            'actual_line_distance',
        )
        classes_info_dict[tariff_class] = cxx.ClassInfo(**class_info)
    route_points = []
    for point in loaded_dict['route_points']:
        route_points.append(cxx_geo.GeoPoint(*point))
    loaded_dict.pop('route_points')
    loaded_dict['route_distance'] = loaded_dict.get('route_distance')
    loaded_dict['route_duration'] = loaded_dict.get('route_duration')
    loaded_dict['currency'] = loaded_dict.get('currency')
    loaded_dict['surge_id'] = loaded_dict.get('surge_id')
    loaded_dict['payment_method'] = loaded_dict.get('payment_method')
    loaded_dict['time'] = time_utils.ensure_datetime(loaded_dict['time'])
    request = cxx.Request(**loaded_dict, route_points=route_points)
    assert len(request.classes_info) == len(classes_info_dict)


def test_features_extractor(load):
    request = cxx.Request.from_json(load('request.json'))
    config = cxx.FeaturesConfig.from_json(load('config.json'))
    features_extractor = cxx.FeaturesExtractor(config=config)
    features = features_extractor(request)
    assert len(features.to_list()) == len(request.classes_info.keys())
