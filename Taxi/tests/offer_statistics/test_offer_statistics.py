from ctaxi_pyml.offer_statistics.v1 import objects_pybind as cxx_objects
from ctaxi_pyml.offer_statistics.v1 import predictor as cxx_predictor
import pytest


@pytest.fixture
def resources_path(get_directory_path):
    return get_directory_path('')


def test_feature_extractor(load):
    request = cxx_objects.Request.from_json_string(load('request.json'))
    config = cxx_objects.PredictorConfig.from_json_string(load('config.json'))
    features_extractor = cxx_predictor.FeaturesExtractor(
        config=config.features_config,
    )
    features = features_extractor(request)
    assert len(features.numerical) == 25
    assert len(features.categorical) == 0


def test_create_score_extractor(load, resources_path):
    request = cxx_objects.Request.from_json_string(load('request.json'))
    score_extractor = cxx_predictor.create_catboost_score_extractor(
        resources_path + '/config.json',
        resources_path + '/model.cbm',
        mock_mode=True,
    )
    score = score_extractor(request=request)
    assert score == 0


def test_create_predictor(load, resources_path):
    request = cxx_objects.Request.from_json_string(load('request.json'))
    predictor = cxx_predictor.create_predictor(
        resources_path + '/config.json',
        resources_path + '/model.cbm',
        mapping_path=resources_path + '/mapping.json',
        mock_mode=True,
    )
    response = predictor(request=request)
    assert response.value == 1

    predictor = cxx_predictor.create_predictor(
        resources_path + '/config_no_mapping.json',
        resources_path + '/model.cbm',
        mock_mode=True,
    )
    response = predictor(request=request)
    assert response.value == 0
