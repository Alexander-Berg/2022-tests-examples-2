from ctaxi_pyml.common.models import mock_catboost
from ctaxi_pyml.geosuggest.scenario_prediction import v2 as cxx


def test_serializations(load):
    request = cxx.Request.from_json(load('request.json'))
    request.userplaces[0].to_json()
    request.orders[0].to_json()
    request.search_routes[0].to_json()
    request.orders[0].source.to_json()


def test_rec_sys(load):
    request = cxx.Request.from_json(load('request.json'))

    config = cxx.PredictorConfig.from_json_string(load('config.json'))
    scenarios_extractor = cxx.ScenariosExtractor(
        scenarios_config=config.scenarios_config,
    )
    feature_extractor = cxx.FeaturesExtractor(config=config.features_config)
    params = cxx.Params()
    postprocessor = cxx.PostProcessor()
    prediction_extractor = mock_catboost(
        feature_extractor.get_num_features_size(),
        feature_extractor.get_cat_features_size(),
    )
    predictor = cxx.Predictor(
        scenarios_extractor,
        feature_extractor,
        prediction_extractor,
        postprocessor,
    )
    response = predictor(request, params)

    assert request
    assert feature_extractor
    assert params
    assert response.results[0].relevance
    assert 0 < response.results[0].relevance < 1
