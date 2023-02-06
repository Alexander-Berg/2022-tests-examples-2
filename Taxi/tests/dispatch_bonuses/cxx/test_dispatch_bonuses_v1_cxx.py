from ctaxi_pyml.dispatch_bonuses import v1 as cxx


def test_serialization(load):
    request = cxx.Request.from_json(load('request.json'))
    request.to_json()


def test_features_extractor(load):
    request = cxx.Request.from_json(load('request.json'))
    config = cxx.PredictorConfig.from_json(load('config.json'))
    features_extractor = cxx.FeaturesExtractor(config=config.features_config)
    features = features_extractor(request)
    assert len(features.numerical) == 47


def test_features_extractor_prolongations(load):
    request_first = cxx.Request.from_json(load('request_prolongations.json'))
    request_json = request_first.to_json()
    request = cxx.Request.from_json(request_json)
    config = cxx.PredictorConfig.from_json(load('config_prolongations.json'))
    features_extractor = cxx.FeaturesExtractor(config=config.features_config)
    features = features_extractor(request)
    assert len(features.numerical) == 59
    assert features.numerical[-12:] == [
        400.0,
        378.0,
        2000.1,
        1859.1,
        5.000249999999999,
        0.199990000499975,
        300.0,
        278.0,
        1000.1,
        859.1,
        3.333666666666667,
        0.2999700029997,
    ]
