import json

from taxi_pyml.common import time_utils
from ctaxi_pyml.surge_statistics import v1 as cxx
from ctaxi_pyml.common import geo as cxx_geo


def test_serialization(load):
    request = cxx.Request.from_json(load('request.json'))
    request.to_json()


def test_initialization(load):
    loaded_dict = json.loads(load('request.json'))
    by_category_dict = loaded_dict['by_category']
    by_category = {}
    for category, surge_info in by_category_dict.items():
        reposition_dict = surge_info['reposition']
        reposition = cxx.RepositionStats(**reposition_dict)
        surge_info.pop('reposition')
        by_category[category] = cxx.SurgeInfoItem(
            **surge_info, reposition=reposition,
        )
    request = cxx.Request(
        time=time_utils.ensure_datetime(loaded_dict['time']),
        point_a=cxx_geo.GeoPoint(*loaded_dict['point_a']),
        point_b=cxx_geo.GeoPoint(*loaded_dict['point_b']),
        distance=loaded_dict['distance'],
        payment_type=loaded_dict['payment_type'],
        tariff_zone=loaded_dict['tariff_zone'],
        by_category=by_category,
    )
    assert request.distance == loaded_dict['distance']


def test_features_extractor(load):
    request = cxx.Request.from_json(load('request.json'))
    config = cxx.FeaturesConfig.from_json(load('config.json'))
    features_extractor = cxx.FeaturesExtractor(config=config)
    features = features_extractor(request)
    assert len(features.to_list()) == len(request.by_category.keys())
