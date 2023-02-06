from typing import Dict

from taxi_pyml.eats.cart_eta.constants import FALLBACK_ORDERS_NUM_THRESHOLD
from taxi_pyml.eats.cart_eta.features_extractors.primar import (
    FeaturesExtractor,
)
from taxi_pyml.eats.cart_eta.views.v1 import view
from taxi_pyml.eats.cart_eta.views.v1 import objects
from taxi_pyml.eats.cart_eta.views.v1.view import (
    StatsResources,
    FALLBACK_PREDICTOR_NAME,
)
from taxi_pyml.eats.cart_eta.views.v1.view import _create_fallback_predictor
from taxi_pyml.eats.cart_eta.predictors import BasePredictor


def _mock_statistics() -> StatsResources:
    return StatsResources(resource_place={}, resource_brand={})


def _mock_predictors() -> Dict[str, BasePredictor]:
    return {FALLBACK_PREDICTOR_NAME: _create_fallback_predictor()}


def get_fallback_predictor():
    predictors = _mock_predictors()
    predictor_name = view.FALLBACK_PREDICTOR_NAME
    return predictors[predictor_name]


def test_request(load_json):
    predictors = _mock_predictors()
    request = load_json('v1/request.json')
    ml_request = objects.MLRequest.from_dict(request)

    for key in predictors:
        assert predictors[key](ml_request) is not None


def test_lavka_request(load_json):
    predictor = get_fallback_predictor()
    ml_request = objects.MLRequest.from_dict(
        load_json('v1/lavka_request.json'),
    )
    assert (
        predictor(ml_request).cooking_time
        == ml_request.place.average_preparation_time
    )


def test_marketplace_request(load_json):
    predictor = get_fallback_predictor()
    ml_request = objects.MLRequest.from_dict(
        load_json('v1/marketplace_request.json'),
    )
    assert (
        predictor(ml_request).cooking_time
        == ml_request.place.average_preparation_time
    )


def test_short_cooking_time_request(load_json):
    predictor = get_fallback_predictor()
    ml_request = objects.MLRequest.from_dict(
        load_json('v1/short_cooking_time_request.json'),
    )
    assert predictor(ml_request).cooking_time >= FALLBACK_ORDERS_NUM_THRESHOLD


def test_request_with_extra_fields(load_json):
    assert (
        objects.MLRequest.from_dict(
            load_json('v1/request_with_extra_fields.json'),
        )
        is not None
    )


def test_request_with_missing_fields(load_json):
    ml_request = objects.MLRequest.from_dict(
        load_json('v1/request_with_missing_fields.json'),
    )

    assert ml_request is not None
    assert isinstance(ml_request.stats_place, objects.StatsByID)
    assert isinstance(ml_request.stats_brand, objects.StatsByID)
    assert isinstance(ml_request.mean_subtotal, float)


def test_request_without_missing_fields(load_json):
    ml_request = objects.MLRequest.from_dict(
        load_json('v1/request_without_missing_fields.json'),
    )

    assert ml_request is not None
    assert isinstance(ml_request.stats_place, objects.StatsByID)
    assert isinstance(ml_request.stats_brand, objects.StatsByID)
    assert isinstance(ml_request.mean_subtotal, float)


def test_postprocessor_corner_cases(load_json):
    post_processor = _create_fallback_predictor().post_processor
    request = load_json('v1/request.json')
    ml_request = objects.MLRequest.from_dict(request)

    result = post_processor(0.3, ml_request)
    assert result.cooking_time >= FALLBACK_ORDERS_NUM_THRESHOLD
    assert result.boundaries.min >= 0.0

    result = post_processor(-20, ml_request)
    assert result.cooking_time >= FALLBACK_ORDERS_NUM_THRESHOLD
    assert result.boundaries.min >= 0.0

    result = post_processor(0.0, ml_request)
    assert result.cooking_time >= FALLBACK_ORDERS_NUM_THRESHOLD
    assert result.boundaries.min >= 0.0


def test_postprocessor(load_json):
    post_processor = _create_fallback_predictor().post_processor
    request = load_json('v1/request_without_missing_fields.json')
    ml_request = objects.MLRequest.from_dict(request)

    result = post_processor(
        ml_request.place.average_preparation_time * 1.5, ml_request,
    )
    assert (
        result.cooking_time == ml_request.place.average_preparation_time * 1.5
    )


def test_feature_extractor(load_json):
    request = load_json('v1/request_without_missing_fields.json')
    ml_request = objects.MLRequest.from_dict(request)
    extractor = FeaturesExtractor()

    features_verctor = load_json('v1/features_vectors.json')[
        'request_without_missing_fields'
    ]

    assert extractor(ml_request) == features_verctor
