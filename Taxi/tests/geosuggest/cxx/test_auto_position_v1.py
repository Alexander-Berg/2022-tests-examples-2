from ctaxi_pyml.geosuggest.auto_position import v1 as cxx

METHODS = [
    'userplace',
    'phone_history.source',
    'pickup_points.auto',
    'graph.adjusted_position',
    'request.position',
    'request.location',
    'phone_history.intermediate',
    'phone_history.destination',
    'phone_history.completion_point',
]


def test_serializations(load):
    request = cxx.Request.from_json(load('request.json'))
    request.userplaces[0].to_json()
    request.orders[0].to_json()
    request.orders[0].source.to_json()
    request.pickup_points[0].to_json()


def test_rec_sys(load):
    request = cxx.Request.from_json(load('request.json'))

    config = cxx.RecommenderConfig.from_json(load('config.json'))
    candidates_extractor = cxx.CandidatesExtractor(
        config=config.candidates_config,
    )
    feature_extractor = cxx.FeaturesExtractor(config=config.features_config)

    method_configs = dict()
    for method_name in METHODS:
        method_configs[method_name] = cxx.MethodConfig(max_distance=1000)
    params = cxx.Params(method_configs, 100, 5, True)
    assert request
    assert candidates_extractor
    assert feature_extractor
    assert params
